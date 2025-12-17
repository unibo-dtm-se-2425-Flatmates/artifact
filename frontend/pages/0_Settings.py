import streamlit as st
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_house_settings, update_house_settings, render_sidebar

st.set_page_config(page_title="Settings", page_icon="⚙️")
render_sidebar()

st.title("⚙️ Settings")

settings = get_house_settings()
current_flatmates = settings.get("flatmates", [])
house_name = settings.get("name", "My Flat")

# Initialize session state for edit mode
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# Force edit mode if no flatmates are configured (first time setup)
if not current_flatmates:
    st.session_state.edit_mode = True

if not st.session_state.edit_mode:
    # --- READ-ONLY VIEW (RECAP) ---
    st.markdown("Here is your current house configuration.")
    
    with st.container(border=True):
        st.subheader(f"🏡 {house_name}")
        st.caption("House Name")
        
        st.divider()
        
        st.subheader("👥 Flatmates")
        
        # Display flatmates in a nice grid
        cols = st.columns(3)
        for idx, mate in enumerate(current_flatmates):
            with cols[idx % 3]:
                st.info(f"**{mate}**", icon="👤")
                
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("✏️ Edit Setup", use_container_width=True):
            st.session_state.edit_mode = True
            st.rerun()

else:
    # --- EDIT VIEW ---
    st.markdown("Configure your shared living space.")
    
    with st.container(border=True):
        st.subheader("✍🏼 Edit Configuration")
        
        # Number of flatmates (Outside form to trigger dynamic UI update)
        default_count = len(current_flatmates) if current_flatmates else 2
        num_flatmates = st.number_input(
            "How many people live here?", 
            min_value=1, 
            max_value=20,
            value=default_count,
            step=1,
            help="Change this number to add or remove flatmate slots."
        )
        
        st.divider()

        with st.form("setup_form"):
            st.subheader("📝 Details")
            
            new_house_name = st.text_input("House Name", value=house_name, placeholder="e.g. Via Roma 42")
            
            st.markdown("### 👥 Flatmates")
            flatmate_names = []
            
            # Grid for names
            cols = st.columns(2)
            for i in range(int(num_flatmates)):
                # Pre-fill logic: use existing name if available, otherwise empty
                default_val = current_flatmates[i] if i < len(current_flatmates) else ""
                
                with cols[i % 2]:
                    name = st.text_input(
                        f"Name of Flatmate {i+1}", 
                        value=default_val, 
                        key=f"flatmate_{i}",
                        placeholder="e.g. Alice"
                    )
                    flatmate_names.append(name)
            
            st.markdown("---")
            
            col_submit, col_cancel = st.columns([1, 1])
            with col_submit:
                submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
            
            # Note: Cancel button inside form submits the form, so we handle it carefully or put it outside.
            # Streamlit forms are tricky with multiple buttons. 
            # Actually, standard practice is to put Cancel outside or just rely on the user navigating away.
            # But let's try to make it nice.
            
            if submitted:
                valid_names = [name.strip() for name in flatmate_names if name.strip()]
                
                if not valid_names:
                    st.error("⚠️ You must have at least one flatmate!")
                else:
                    new_settings = {
                        "name": new_house_name,
                        "flatmates": valid_names
                    }
                    update_house_settings(new_settings)
                    st.success("✅ Settings saved successfully!")
                    st.session_state.edit_mode = False
                    st.rerun()

    # Cancel button outside the form
    if current_flatmates: # Only show cancel if we have a valid state to go back to
        if st.button("❌ Cancel", use_container_width=False):
            st.session_state.edit_mode = False
            st.rerun()
