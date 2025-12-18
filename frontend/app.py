import streamlit as st
from utils import fetch_profile, login_user, register_user, render_sidebar

st.set_page_config(
    page_title="Flatmate Manager App",
    page_icon="🏠",
    layout="wide"
)

render_sidebar()

# --- Auth Gate ---
if "auth_token" not in st.session_state:
    st.title("Welcome to the Flatmate Manager app! 🏠")
    st.markdown("Login or create an account to continue.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")

        if submitted:
            result = login_user(username, password)
            if result:
                st.session_state["auth_token"] = result.get("token")
                st.session_state["profile"] = result
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with register_tab:
        st.markdown("### Choose how to join")
        col_create, col_join = st.columns(2, gap="large")

        with col_create:
            with st.form("register_create_form"):
                st.subheader("Create new house")
                username_r = st.text_input("Username", key="reg_user_new")
                password_r = st.text_input("Password", type="password", key="reg_pass_new")
                house_name = st.text_input("House name", placeholder="e.g. Via Roma 42")
                submitted_r = st.form_submit_button("Create account", type="primary")

            if submitted_r:
                result = register_user(username_r, password_r, house_name=house_name, house_code=None)
                if result:
                    st.session_state["auth_token"] = result.get("token")
                    st.session_state["profile"] = result
                    st.success("Account created and signed in")
                    st.rerun()
                else:
                    st.error("Registration failed. Try a different username or house name.")

        with col_join:
            with st.form("register_join_form"):
                st.subheader("Join existing house")
                username_j = st.text_input("Username", key="reg_user_join")
                password_j = st.text_input("Password", type="password", key="reg_pass_join")
                house_code = st.text_input("House code", placeholder="Enter invite code")
                submitted_j = st.form_submit_button("Join house", type="primary")

            if submitted_j:
                if not (house_code or "").strip():
                    st.error("Please enter a house code to join an existing house.")
                else:
                    result = register_user(username_j, password_j, house_name=None, house_code=house_code)
                    if result:
                        st.session_state["auth_token"] = result.get("token")
                        st.session_state["profile"] = result
                        st.success("Account created and signed in")
                        st.rerun()
                    else:
                        st.error("Registration failed. Check the invite code or choose another username.")

    st.stop()

# Refresh profile if missing
if "profile" not in st.session_state:
    profile = fetch_profile(st.session_state.get("auth_token"))
    if profile:
        st.session_state["profile"] = profile

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