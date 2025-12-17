import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_events, create_event

st.set_page_config(page_title="Calendar", page_icon="📅")

st.title("📅 Flatmate Calendar")

# Form to add event
with st.expander("Add New Event"):
    with st.form("add_event_form"):
        title = st.text_input("Event Title")
        event_date = st.date_input("Date", min_value=date.today())
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Event")
        
        if submitted:
            if title:
                create_event({
                    "title": title,
                    "date": str(event_date),
                    "description": description
                })
                st.success("Event added!")
                st.rerun()
            else:
                st.error("Please enter a title.")

# Display events
events = get_events()

if events:
    # Convert to DataFrame for nicer display
    df = pd.DataFrame(events)
    # Rename columns for display
    df = df.rename(columns={"title": "Event", "date": "Date", "description": "Description"})
    # Sort by date
    df = df.sort_values(by="Date")
    
    st.dataframe(
        df[["Date", "Event", "Description"]],
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No upcoming events.")