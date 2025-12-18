import os
import sys

import streamlit as st

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_house_settings, render_sidebar, require_auth, reset_house_data, update_house_settings

st.set_page_config(page_title="Settings", page_icon="⚙️")
render_sidebar()

st.title("⚙️ Settings")

profile = require_auth()
house = profile.get("house", get_house_settings())
user = profile.get("user", {})

house_name = house.get("name", "My Flat")
join_code = house.get("join_code")
current_flatmates = house.get("flatmates", [])

with st.container(border=True):
    st.subheader("👤 Profile")
    st.markdown(f"**Username:** {user.get('username', '-')}")

with st.container(border=True):
    st.subheader("🏡 House")
    st.markdown(f"**Name:** {house_name}")
    if join_code:
        st.code(join_code, language="text")

    st.divider()
    st.subheader("👥 Flatmates")
    if current_flatmates:
        cols = st.columns(3)
        for idx, mate in enumerate(current_flatmates):
            with cols[idx % 3]:
                st.info(f"**{mate}**", icon="👤")
    else:
        st.info("No flatmates found yet. Share the code to invite others.")

with st.container(border=True):
    st.subheader("✏️ Update house name")
    with st.form("house_name_form"):
        new_name = st.text_input("House name", value=house_name)
        submitted = st.form_submit_button("Save", type="primary")
    if submitted:
        update_house_settings({"name": new_name})
        st.success("House name updated")
        st.session_state.pop("profile", None)
        st.rerun()

with st.container(border=True):
    st.subheader("🗑️ Danger Zone")
    st.warning(
        "Clearing the house will delete all events, shopping items, expenses, and reimbursements for this house.",
        icon="⚠️",
    )
    confirm_reset = st.checkbox(
        "I understand this will erase all shared data",
        key="confirm_reset",
        help="Required before the delete button is enabled.",
    )
    if st.button(
        "🗑️ Clear house data",
        type="primary",
        use_container_width=True,
        disabled=not confirm_reset,
    ):
        if reset_house_data():
            st.success("House data cleared. Start fresh!")
            st.session_state.pop("profile", None)
            st.rerun()
        else:
            st.error("Unable to reset right now. Please try again.")
