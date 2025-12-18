import streamlit as st
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    add_shopping_item,
    get_house_settings,
    get_shopping_list,
    render_sidebar,
    remove_shopping_item,
    require_auth,
)

st.set_page_config(page_title="Shopping List", page_icon="🛒")
render_sidebar()

st.title("🛒 Shopping List")

require_auth()

# Get users
settings = get_house_settings()
USERS = settings.get("flatmates", [])

if not USERS:
    st.warning("🏠 House setup required before using the shopping list.")
    if st.button("⚙️ Go to Settings"):
        st.switch_page("pages/0_Settings.py")
    st.stop()

# Add item
with st.container(border=True):
    st.subheader("Add New Item")
    with st.form("add_item_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            new_item = st.text_input("Item Name", placeholder="e.g., Milk, Eggs...")
        with col2:
            if USERS:
                added_by = st.selectbox("Added By", USERS)
            else:
                added_by = st.text_input("Added By", value="User")
        with col3:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        
        submitted = st.form_submit_button("Add to List", use_container_width=True, type="primary")
        
        if submitted and new_item:
            add_shopping_item({
                "name": new_item,
                "quantity": quantity,
                "added_by": added_by
            })
            st.rerun()

st.markdown("### Your List")

# List items
items = get_shopping_list()

if items:
    for item in items:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([4, 3, 2, 1])
            with col1:
                st.markdown(f"##### {item['name']}")
            with col2:
                st.caption(f"Added by: {item['added_by']}")
            with col3:
                st.markdown(f"**Qty:** {item['quantity']}")
            with col4:
                if st.button("🗑️", key=f"del_{item['id']}", help="Remove item"):
                    remove_shopping_item(item['id'])
                    st.rerun()
else:
    st.info("The shopping list is empty! 🎉")