import streamlit as st
import pandas as pd
import altair as alt
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    get_expenses,
    add_expense,
    get_debts,
    get_house_settings,
    get_reimbursements,
    add_reimbursement,
    render_sidebar,
    require_auth,
)

st.set_page_config(page_title="Expenses", page_icon="💸", layout="wide")
render_sidebar()

st.title("💸 Expense Manager")
require_auth()


def _format_currency(value: float) -> str:
    """Render a numeric value as a currency string.

    Args:
        value (float): Amount to format.

    Returns:
        str: Value formatted with a dollar sign and two decimals.
    """
    return f"${value:,.2f}"


def _rerun_page() -> None:
    """Trigger a Streamlit rerun while handling API changes gracefully."""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


# Get users from settings
settings = get_house_settings()
USERS = settings.get("flatmates", [])

if not USERS:
    st.warning("🏠 House setup required before tracking expenses.")
    if st.button("⚙️ Go to Settings"):
        st.switch_page("pages/0_Settings.py")
    st.stop()

expenses_data = get_expenses()
debts_data = get_debts()
reimbursements_data = get_reimbursements()

if len(st.session_state.get("_expense_default_split", [])) != len(USERS):
    st.session_state["_expense_default_split"] = USERS.copy()

st.session_state.setdefault("_show_reimbursement_form", False)
st.session_state.setdefault("_reimbursement_selection_idx", 0)
st.session_state.setdefault("_reimbursement_note", "")
st.session_state.setdefault("_active_expense_tab", "add")

if st.session_state.pop("_reset_reimbursement_state", False):
    st.session_state["_show_reimbursement_form"] = False
    st.session_state["_reimbursement_note"] = ""
    st.session_state["_reimbursement_selection_idx"] = 0

if st.session_state.pop("_open_reimbursement_now", False):
    st.session_state["_show_reimbursement_form"] = True
    st.session_state["_active_expense_tab"] = "debt"

if st.session_state.get("_show_reimbursement_form"):
    st.session_state["_active_expense_tab"] = "debt"

for notice_key in ("_expense_notice", "_reimbursement_notice"):
    if message := st.session_state.pop(notice_key, None):
        st.success(message)

expenses_df = pd.DataFrame(expenses_data) if expenses_data else pd.DataFrame(
    columns=["id", "title", "amount", "payer", "involved_people"]
)
if not expenses_df.empty:
    expenses_df["amount"] = pd.to_numeric(expenses_df["amount"], errors="coerce").fillna(0.0)

TAB_LABELS = {
    "add": "➕ Add Expense",
    "debt": "🤝 Debt Overview",
}

tab_sequence = [TAB_LABELS["add"], TAB_LABELS["debt"]]
default_index = 0 if st.session_state.get("_active_expense_tab") != "debt" else 1
tab_choice = st.radio(
    "View",
    tab_sequence,
    index=default_index,
    horizontal=True,
    label_visibility="collapsed",
)
st.session_state["_active_expense_tab"] = "debt" if tab_choice == TAB_LABELS["debt"] else "add"

if st.session_state["_active_expense_tab"] == "add":
    st.subheader("Add New Expense")
    st.caption("Capture a new shared cost and we’ll update the household stats instantly.")

    form_col, info_col = st.columns((1.1, 0.9))

    with form_col:
        with st.form("expense_form", clear_on_submit=True):
            title = st.text_input("Description", placeholder="e.g., Electricity Bill")
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            payer = st.selectbox("Paid By", USERS)
            default_split = st.session_state.get("_expense_default_split", USERS)
            involved = st.multiselect(
                "Split With",
                USERS,
                default=default_split,
                help="Everyone selected shares the cost equally.",
            )

            submitted = st.form_submit_button("Add Expense")

            if submitted:
                if title and amount > 0 and involved:
                    payload = {
                        "title": title.strip(),
                        "amount": float(amount),
                        "payer": payer,
                        "involved_people": involved,
                    }
                    try:
                        add_expense(payload)
                        st.session_state["_expense_notice"] = "Expense added successfully."
                        st.session_state["_expense_default_split"] = involved.copy()
                        _rerun_page()
                    except Exception:
                        st.error("Could not save the expense. Please try again.")
                else:
                    st.error("Please provide a description, amount, and at least one person to split with.")

    with info_col:
        st.subheader("Household Snapshot")
        if expenses_df.empty:
            st.info("No expenses recorded yet. Add the first expense to unlock the summary.")
        else:
            total_spent = float(expenses_df["amount"].sum())
            total_expenses = len(expenses_df)
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric("Total Recorded", _format_currency(total_spent))
            metric_col2.metric("Number of Expenses", f"{total_expenses}")

else:
    st.subheader("Debt Simplification")
    st.markdown("Track every expense, understand the split, and settle balances with a tap.")

    expenses_section, settlements_section = st.columns((1.1, 0.9))

    with expenses_section:
        with st.container(border=True):
            st.markdown("### 📜 Expense Log")
            if expenses_df.empty:
                st.info("No expenses yet. Record the first one to populate this view.")
            else:
                expense_table = expenses_df.sort_values(by="id", ascending=False).copy()
                expense_table["Split With"] = expense_table["involved_people"].apply(lambda p: ", ".join(p))
                display_expenses = expense_table[
                    ["title", "payer", "amount", "Split With"]
                ].rename(columns={"title": "Description", "payer": "Paid By", "amount": "Amount ($)"})
                display_expenses["Amount ($)"] = display_expenses["Amount ($)"].map(_format_currency)
                st.dataframe(display_expenses, use_container_width=True, hide_index=True)

    with settlements_section:
        with st.container(border=True):
            st.markdown("### ⚖️ Settlements")
            if not debts_data:
                st.info("No debts detected. You're all square!")
                debts_df = pd.DataFrame(columns=["debtor", "creditor", "amount"])
            else:
                debts_df = pd.DataFrame(debts_data).sort_values(by="amount", ascending=False)
                debts_df["amount"] = debts_df["amount"].astype(float)

            st.markdown("**Suggested Settlements**")
            if debts_df.empty:
                st.caption("Add a reimbursement once new settlements appear.")
            else:
                settlements_table = debts_df.copy()
                settlements_table["amount"] = settlements_table["amount"].map(_format_currency)
                st.dataframe(
                    settlements_table.rename(
                        columns={"debtor": "Debtor", "creditor": "Creditor", "amount": "Amount"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            st.divider()
            with st.container(border=True):
                st.markdown("#### Record a Reimbursement")
                if debts_df.empty:
                    st.info("No outstanding settlements available to reimburse.")
                    st.session_state["_reset_reimbursement_state"] = True
                else:
                    debt_records = debts_df.to_dict("records")
                    option_labels = [
                        f"{record['debtor']} → {record['creditor']} ({_format_currency(record['amount'])})"
                        for record in debt_records
                    ]
                    if not st.session_state["_show_reimbursement_form"]:
                        if st.button("Record reimbursement", key="open_reimbursement"):
                            st.session_state["_show_reimbursement_form"] = True
                            st.session_state["_reimbursement_selection_idx"] = 0
                            st.session_state["_reimbursement_note"] = ""
                            st.session_state["_open_reimbursement_now"] = True
                            _rerun_page()

                    if st.session_state["_show_reimbursement_form"]:
                        max_index = max(len(debt_records) - 1, 0)
                        default_index = min(st.session_state["_reimbursement_selection_idx"], max_index)

                        selected_index = st.selectbox(
                            "Choose a settlement to reimburse",
                            list(range(len(debt_records))),
                            index=default_index,
                            format_func=lambda idx: option_labels[idx],
                        )
                        st.session_state["_reimbursement_selection_idx"] = selected_index

                        chosen_debt = debt_records[selected_index]
                        amount_due = float(chosen_debt["amount"])
                        st.info(
                            f"{chosen_debt['debtor']} will reimburse {chosen_debt['creditor']} "
                            f"{_format_currency(amount_due)}"
                        )

                        note_input = st.text_input(
                            "Note (optional)",
                            key="_reimbursement_note",
                            placeholder="e.g., Bank transfer",
                        )

                        confirm_col, cancel_col = st.columns(2)
                        if confirm_col.button(
                            "Confirm reimbursement", type="primary", key="confirm_reimbursement"
                        ):
                            note_value = note_input.strip()
                            payload = {
                                "from_person": chosen_debt["debtor"],
                                "to_person": chosen_debt["creditor"],
                                "amount": amount_due,
                                "note": note_value or None,
                            }
                            try:
                                add_reimbursement(payload)
                                st.session_state["_reimbursement_notice"] = (
                                    "Reimbursement recorded. Debts updated."
                                )
                                st.session_state["_reset_reimbursement_state"] = True
                                st.session_state["_active_expense_tab"] = "debt"
                                _rerun_page()
                            except Exception:
                                st.error("Unable to record the reimbursement. Please retry in a moment.")

                        if cancel_col.button("Cancel", key="cancel_reimbursement"):
                            st.session_state["_reset_reimbursement_state"] = True
                            st.session_state["_active_expense_tab"] = "debt"
                            _rerun_page()

    st.divider()

    if not expenses_df.empty:
        st.markdown("### 📊 Visual Snapshot")
        chart_cols = st.columns(2)

        with chart_cols[0]:
            with st.container(border=True):
                payer_totals = (
                    expenses_df.groupby("payer", dropna=True)["amount"].sum().reset_index()
                )
                if not payer_totals.empty:
                    payer_totals["amount"] = payer_totals["amount"].astype(float)
                    payer_base = alt.Chart(payer_totals)
                    payer_bars = (
                        payer_base.mark_bar(cornerRadiusTopRight=10, cornerRadiusBottomRight=10)
                        .encode(
                            y=alt.Y("payer:N", sort="-x", title=""),
                            x=alt.X(
                                "amount:Q",
                                title="Total Paid ($)",
                                axis=alt.Axis(format="$,.2f"),
                            ),
                            color=alt.value("#4F8EF7"),
                            tooltip=[
                                alt.Tooltip("payer:N", title="Payer"),
                                alt.Tooltip("amount:Q", title="Total Paid", format="$,.2f"),
                            ],
                        )
                        .properties(height=280, title="Contributions by Payer")
                    )
                    payer_text = (
                        payer_base.mark_text(
                            align="left",
                            baseline="middle",
                            dx=6,
                            color="#1f2a44",
                            fontWeight="bold",
                        )
                        .encode(
                            y=alt.Y("payer:N", sort="-x"),
                            x=alt.X("amount:Q"),
                            text=alt.Text("amount:Q", format="$,.2f"),
                        )
                    )
                    payer_chart = (payer_bars + payer_text).configure_axis(
                        labelColor="#4a4a4a", titleColor="#4a4a4a"
                    ).configure_view(strokeOpacity=0)
                    st.altair_chart(payer_chart, use_container_width=True)
                else:
                    st.caption("Expenses by payer will appear here once recorded.")

        with chart_cols[1]:
            with st.container(border=True):
                if not debts_df.empty:
                    debtor_totals = (
                        debts_df.groupby("debtor", dropna=True)["amount"].sum().reset_index()
                    )
                    debtor_totals["amount"] = debtor_totals["amount"].astype(float)
                    debtor_base = alt.Chart(debtor_totals)
                    debtor_bars = (
                        debtor_base.mark_bar(cornerRadiusTopRight=10, cornerRadiusBottomRight=10)
                        .encode(
                            y=alt.Y("debtor:N", sort="-x", title=""),
                            x=alt.X(
                                "amount:Q",
                                title="Amount Owed ($)",
                                axis=alt.Axis(format="$,.2f"),
                            ),
                            color=alt.value("#F76F6F"),
                            tooltip=[
                                alt.Tooltip("debtor:N", title="Debtor"),
                                alt.Tooltip("amount:Q", title="Owes", format="$,.2f"),
                            ],
                        )
                        .properties(height=280, title="Outstanding Debts by Debtor")
                    )
                    debtor_text = (
                        debtor_base.mark_text(
                            align="left",
                            baseline="middle",
                            dx=6,
                            color="#401818",
                            fontWeight="bold",
                        )
                        .encode(
                            y=alt.Y("debtor:N", sort="-x"),
                            x=alt.X("amount:Q"),
                            text=alt.Text("amount:Q", format="$,.2f"),
                        )
                    )
                    debtor_chart = (debtor_bars + debtor_text).configure_axis(
                        labelColor="#4a4a4a", titleColor="#4a4a4a"
                    ).configure_view(strokeOpacity=0)
                    st.altair_chart(debtor_chart, use_container_width=True)
                else:
                    st.caption("Outstanding debts chart will populate when someone owes money.")

    if reimbursements_data:
        with st.container(border=True):
            st.markdown("### 🕰️ Reimbursement History")
            history_df = pd.DataFrame(reimbursements_data)
            if not history_df.empty:
                history_df["Amount"] = history_df["amount"].apply(_format_currency)
                history_df = history_df.rename(
                    columns={
                        "from_person": "From",
                        "to_person": "To",
                        "note": "Details",
                    }
                )
                history_df["Details"] = history_df["Details"].fillna("")
                display_history = history_df[["From", "To", "Amount", "Details"]]
                st.dataframe(display_history, use_container_width=True, hide_index=True)
    else:
        st.caption("Record a reimbursement to see the history here.")