import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_expenses, add_expense, get_debts, get_house_settings

st.set_page_config(page_title="Expenses", page_icon="💸")

st.title("💸 Expense Manager")

# Get users from settings
settings = get_house_settings()
USERS = settings.get("flatmates", [])

if not USERS:
    st.warning("🏠 House setup required before tracking expenses.")
    if st.button("⚙️ Go to Settings"):
        st.switch_page("pages/0_Settings.py")
    st.stop()

tab1, tab2 = st.tabs(["Add Expense", "Debt Overview"])

with tab1:
    st.subheader("Add New Expense")
    with st.form("expense_form"):
        title = st.text_input("Description", placeholder="e.g., Electricity Bill")
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
        payer = st.selectbox("Paid By", USERS)
        involved = st.multiselect("Split With", USERS, default=USERS)
        
        submitted = st.form_submit_button("Add Expense")
        
        if submitted:
            if title and amount > 0 and involved:
                add_expense({
                    "title": title,
                    "amount": amount,
                    "payer": payer,
                    "involved_people": involved
                })
                st.success("Expense added!")
            else:
                st.error("Please fill in all fields.")

    st.divider()
    st.subheader("Recent Expenses")
    expenses = get_expenses()
    if expenses:
        # Reverse to show newest first
        for exp in reversed(expenses):
            with st.container():
                st.write(f"**{exp['title']}** - ${exp['amount']:.2f}")
                st.caption(f"Paid by {exp['payer']} | Split with: {', '.join(exp['involved_people'])}")
                st.divider()
    else:
        st.info("No expenses recorded yet.")

with tab2:
    st.subheader("Debt Simplification")
    st.markdown("Who owes what to whom (simplified):")
    
    debts = get_debts()
    
    if debts:
        for debt in debts:
            st.info(f"**{debt['debtor']}** owes **{debt['creditor']}**: ${debt['amount']:.2f}")
    else:
        st.success("No debts! Everyone is settled up.")