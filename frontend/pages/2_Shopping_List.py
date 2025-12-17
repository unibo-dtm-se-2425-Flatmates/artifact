import streamlit as st
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_shopping_list, add_shopping_item, remove_shopping_item, get_house_settings

st.set_page_config(page_title="Shopping List", page_icon="🛒")

st.title("🛒 Shopping List")

# Get users
settings = get_house_settings()
USERS = settings.get("flatmates", [])

if not USERS:
    st.warning("🏠 House setup required before using the shopping list.")
    if st.button("⚙️ Go to Settings"):
        st.switch_page("pages/0_Settings.py")
    st.stop()

# Add item
col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
with col1:
    new_item = st.text_input("Item Name", placeholder="e.g., Milk")
with col2:
    if USERS:
        added_by = st.selectbox("Added By", USERS)
    else:
        added_by = st.text_input("Added By", value="User")
with col3:
    quantity = st.number_input("Qty", min_value=1, value=1)
with col4:
    add_btn = st.button("Add")

if add_btn and new_item:
    add_shopping_item({
        "name": new_item,
        "quantity": quantity,
        "added_by": added_by
    })
    st.rerun()

st.divider()

# List items
items = get_shopping_list()

if items:
    for item in items:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.caption(f"By: {item['added_by']}")
        with col3:
            st.write(f"Qty: {item['quantity']}")
        with col4:
            if st.button("🗑️", key=item['id']):
                remove_shopping_item(item['id'])
                st.rerun()
else:
    st.info("Shopping list is empty!")