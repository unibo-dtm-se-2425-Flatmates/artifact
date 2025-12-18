from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException

from ..db import db
from ..models import Debt, Expense, Reimbursement
from .auth import UserContext, get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.get("/", response_model=List[Expense])
def get_expenses(current_user: UserContext = Depends(get_current_user)):
    """Retrieve all expenses for the user's house."""
    return db.get_expenses(current_user.house_id)

@router.post("/", response_model=Expense)
def add_expense(expense: Expense, current_user: UserContext = Depends(get_current_user)):
    """Create a new expense entry.

    Args:
        expense (Expense): Expense data to persist.

    Returns:
        Expense: Stored expense with ID.
    """
    return db.add_expense(expense, current_user.house_id)

@router.get("/debts", response_model=List[Debt])
def get_debts(current_user: UserContext = Depends(get_current_user)):
    """Compute simplified debt settlements from expenses and reimbursements."""
    expenses = db.get_expenses(current_user.house_id)
    balances: Dict[str, float] = {}

    # Calculate net balances
    for expense in expenses:
        amount = expense.amount
        payer = expense.payer
        involved = expense.involved_people
        
        if not involved:
            continue
            
        split_amount = amount / len(involved)
        
        # Payer paid the full amount, so they are effectively "up" by that amount initially
        # But we can just think in terms of net flow.
        # Payer gets +amount
        balances[payer] = balances.get(payer, 0) + amount
        
        # Everyone involved (including payer if they are in the list) "pays" the split amount
        for person in involved:
            balances[person] = balances.get(person, 0) - split_amount

    reimbursements = db.get_reimbursements(current_user.house_id)
    for reimbursement in reimbursements:
        amount = max(reimbursement.amount, 0)
        if amount <= 0:
            continue
        payer = reimbursement.from_person
        receiver = reimbursement.to_person
        balances[payer] = balances.get(payer, 0) + amount
        balances[receiver] = balances.get(receiver, 0) - amount

    # Separate into debtors and creditors
    debtors = []
    creditors = []
    
    for person, amount in balances.items():
        # Round to 2 decimal places to avoid floating point issues
        amount = round(amount, 2)
        if amount < -0.01:
            debtors.append({"person": person, "amount": amount})
        elif amount > 0.01:
            creditors.append({"person": person, "amount": amount})
            
    # Sort by magnitude to optimize (greedy approach)
    debtors.sort(key=lambda x: x["amount"]) # Ascending (most negative first)
    creditors.sort(key=lambda x: x["amount"], reverse=True) # Descending (most positive first)
    
    debts = []
    
    i = 0 # debtor index
    j = 0 # creditor index
    
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        # The amount to settle is the minimum of what the debtor owes and what the creditor is owed
        amount = min(abs(debtor["amount"]), creditor["amount"])
        
        debts.append(Debt(debtor=debtor["person"], creditor=creditor["person"], amount=round(amount, 2)))
        
        # Update balances
        debtor["amount"] += amount
        creditor["amount"] -= amount
        
        # Move indices if settled
        if abs(debtor["amount"]) < 0.01:
            i += 1
        if creditor["amount"] < 0.01:
            j += 1
            
    return debts


@router.get("/reimbursements", response_model=List[Reimbursement])
def get_reimbursements(current_user: UserContext = Depends(get_current_user)):
    """Fetch all recorded reimbursements."""
    return db.get_reimbursements(current_user.house_id)


@router.post("/reimbursements", response_model=Reimbursement)
def add_reimbursement(reimbursement: Reimbursement, current_user: UserContext = Depends(get_current_user)):
    """Record a reimbursement transaction.

    Args:
        reimbursement (Reimbursement): Transfer details.

    Returns:
        Reimbursement: Stored reimbursement with ID.

    Raises:
        HTTPException: If the amount is not positive or parties match.
    """
    if reimbursement.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if reimbursement.from_person == reimbursement.to_person:
        raise HTTPException(status_code=400, detail="People involved must be different")
    return db.add_reimbursement(reimbursement, current_user.house_id)