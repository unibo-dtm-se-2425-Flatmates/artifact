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

info_col, house_col = st.columns([1, 2], gap="large")

with info_col:
    with st.container(border=True):
        st.subheader("👤 Profile")
        st.markdown(f"**Username:** {user.get('username', '-')}" )
        st.markdown(f"**House:** {house_name}")
        if join_code:
            st.markdown("**Invite code**")
            st.code(join_code, language="text")
            st.caption("Share this code with flatmates so they can join your house.")

with house_col:
    with st.container(border=True):
        st.subheader("👥 Flatmates")
        if current_flatmates:
            cols = st.columns(3)
            for idx, mate in enumerate(current_flatmates):
                with cols[idx % 3]:
                    st.info(f"**{mate}**", icon="👤")
            st.caption("Flatmates are registered users. Share the invite code so others can join; users who leave should log out.")
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
        "Choose what to remove for this house.",
        icon="⚠️",
    )
    col_reset, col_delete = st.columns(2)

    with col_reset:
        st.markdown("**Clear shared data**")
        confirm_reset = st.checkbox(
            "I understand this erases events, shopping, expenses, reimbursements",
            key="confirm_reset",
            help="Required before the clear button is enabled.",
        )
        if st.button(
            "🗑️ Clear data",
            type="primary",
            use_container_width=True,
            disabled=not confirm_reset,
        ):
            if reset_house_data():
                st.success("House data cleared. Start fresh!")
                st.rerun()
            else:
                st.error("Unable to reset right now. Please try again.")

    with col_delete:
        st.markdown("**Delete house & members**")
        confirm_delete = st.checkbox(
            "I understand this deletes the house, users, and data",
            key="confirm_delete",
            help="All house users will be removed.",
        )
        if st.button(
            "❌ Delete house",
            type="primary",
            use_container_width=True,
            disabled=not confirm_delete,
        ):
            from utils import delete_house

            if delete_house():
                st.success("House deleted. You will need to register or join a house again.")
                for key in ("auth_token", "profile"):
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("Unable to delete the house right now. Please try again.")
