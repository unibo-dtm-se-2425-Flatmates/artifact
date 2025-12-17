import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import sys
import os
from streamlit_calendar import calendar

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_events, create_event, get_house_settings

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")

st.title("📅 Flatmate Calendar")

# Get users
settings = get_house_settings()
USERS = settings.get("flatmates", [])

# Fetch events
events = get_events()
calendar_events = []
for event in events:
    # Construct start and end strings
    start_str = event['date']
    if event.get('start_time'):
        start_str += f"T{event['start_time']}"
    
    end_str = None
    if event.get('end_time'):
        end_str = event['date'] + f"T{event['end_time']}"
    
    # Color coding based on assignment
    color = "#3788d8" # default blue
    assignees = event.get('assigned_to', [])
    
    # Handle legacy data where assigned_to might be a string or None
    if isinstance(assignees, str):
        assignees = [assignees]
    elif assignees is None:
        assignees = []
        
    if assignees:
        # Use color of first assignee for consistency
        first_person = assignees[0]
        if first_person in USERS:
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD"]
            try:
                idx = USERS.index(first_person)
                color = colors[idx % len(colors)]
            except:
                pass

    assignee_str = ", ".join(assignees) if assignees else "Everyone"

    calendar_events.append({
        "title": f"{event['title']} ({assignee_str})",
        "start": start_str,
        "end": end_str,
        "backgroundColor": color,
        "borderColor": color,
        "extendedProps": {
            "description": event.get('description'),
            "assigned_to": assignees
        }
    })

# Calendar Options
calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth",
    },
    "initialView": "dayGridMonth",
    "selectable": True,
    "editable": False, # Read-only for drag/drop for now
}

# Display Calendar
cal_state = calendar(events=calendar_events, options=calendar_options, key="calendar")

# Handle Interactions
selected_date = date.today()
default_start_time = time(9, 0)
default_end_time = time(10, 0)

if cal_state.get("dateClick"):
    clicked_date_str = cal_state["dateClick"]["dateStr"]
    # dateStr can be YYYY-MM-DD or ISO with time depending on view
    try:
        selected_date = datetime.fromisoformat(clicked_date_str.split("T")[0]).date()
    except:
        pass
    st.toast(f"Selected date: {selected_date}")

# Add Event Form (Always visible or in expander, pre-filled with selection)
st.divider()
st.subheader("Add New Event")

with st.form("add_event_form"):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Event Title")
        event_date = st.date_input("Date", value=selected_date)
        assigned_to = st.multiselect("Assign To", USERS, help="Leave empty for Everyone")
    
    with col2:
        use_time = st.checkbox("Add Time?")
        start_t = st.time_input("Start Time", value=default_start_time)
        end_t = st.time_input("End Time", value=default_end_time)
    
    description = st.text_area("Description")
    
    submitted = st.form_submit_button("Add Event")
    
    if submitted:
        if title:
            payload = {
                "title": title,
                "date": str(event_date),
                "description": description,
                "assigned_to": assigned_to
            }
            
            if use_time:
                payload["start_time"] = str(start_t)
                payload["end_time"] = str(end_t)
            
            create_event(payload)
            st.success("Event added!")
            st.rerun()
        else:
            st.error("Please enter a title.")

# Show details of clicked event if any
if cal_state.get("eventClick"):
    event_data = cal_state["eventClick"]["event"]
    props = event_data.get("extendedProps", {})
    
    st.info(f"**Selected Event:** {event_data['title']}")
    if props.get("description"):
        st.write(f"**Description:** {props['description']}")
    
    assignees = props.get("assigned_to")
    if assignees:
        st.write(f"**Assigned to:** {', '.join(assignees)}")
    else:
        st.write("**Assigned to:** Everyone")
