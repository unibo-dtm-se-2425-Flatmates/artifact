import streamlit as st
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_house_settings, update_house_settings

st.set_page_config(page_title="Settings", page_icon="⚙️")

st.title("⚙️ House Settings")

settings = get_house_settings()

with st.form("settings_form"):
    house_name = st.text_input("House Name", value=settings.get("name", "My Flat"))
    
    current_flatmates = settings.get("flatmates", [])
    flatmates_str = st.text_area(
        "Flatmates (one per line)", 
        value="\n".join(current_flatmates),
        help="Enter the names of all flatmates, one on each line."
    )
    
    submitted = st.form_submit_button("Save Settings")
    
    if submitted:
        # Process flatmates list
        new_flatmates = [name.strip() for name in flatmates_str.split("\n") if name.strip()]
        
        new_settings = {
            "name": house_name,
            "flatmates": new_flatmates
        }
        
        update_house_settings(new_settings)
        st.success("Settings updated successfully!")
        st.rerun()

st.divider()
st.subheader("Current Configuration")
st.write(f"**House Name:** {settings.get('name')}")
st.write("**Flatmates:**")
for mate in settings.get("flatmates", []):
    st.write(f"- {mate}")