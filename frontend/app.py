import streamlit as st
from utils import render_sidebar

st.set_page_config(
    page_title="Flatmate Manager App",
    page_icon="🏠",
    layout="wide"
)

render_sidebar()

st.markdown("""
    <style>
    section[data-testid="stMain"] [data-testid="stPageLink-NavLink"] {
        background-color: #FF4B4B !important;
        border: 1px solid #FF4B4B !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.20rem 0.5rem !important;
        transition: all 0.3s ease;
        text-align: center;
        text-decoration: none !important;
    }
    section[data-testid="stMain"] [data-testid="stPageLink-NavLink"]:hover {
        background-color: #FF3333 !important;
        border-color: #FF3333 !important;
    }
    section[data-testid="stMain"] [data-testid="stPageLink-NavLink"] p {
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    /* Ensure icon is also white */
    section[data-testid="stMain"] [data-testid="stPageLink-NavLink"] span {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Welcome to the Flatmate Manager app! 🏠")
st.markdown("Manage your shared living space with ease.")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("⚙️ Settings")
        st.write("Configure your house and user profile.")
        st.page_link("pages/0_Settings.py", label="Go to Settings", icon="⚙️")

with col2:
    with st.container(border=True):
        st.subheader("📅 Calendar")
        st.write("Schedule cleaning, events, and more.")
        st.page_link("pages/1_Calendar.py", label="Go to Calendar", icon="📅")

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("🛒 Shopping List")
        st.write("Keep track of what needs to be bought.")
        st.page_link("pages/2_Shopping_List.py", label="Go to Shopping List", icon="🛒")

with col4:
    with st.container(border=True):
        st.subheader("💸 Expenses")
        st.write("Split bills and see who owes what.")
        st.page_link("pages/3_Expenses.py", label="Go to Expenses", icon="💸")