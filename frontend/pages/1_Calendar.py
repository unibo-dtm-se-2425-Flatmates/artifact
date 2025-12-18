import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import sys
import os
from streamlit_calendar import calendar

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    create_event,
    get_events,
    get_house_settings,
    render_sidebar,
    require_auth,
    update_event,
)

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
render_sidebar()

st.title("📅 Flatmate Calendar")

profile = require_auth()

# --- STATE MANAGEMENT ---
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "list" # list, day, details, create, edit

if "selected_event" not in st.session_state:
    st.session_state.selected_event = None
if "selected_event_id" not in st.session_state:
    st.session_state.selected_event_id = None
if "skip_event_id" not in st.session_state:
    st.session_state.skip_event_id = None

# --- DATA LOADING ---
settings = profile.get("house", get_house_settings())
USERS = settings.get("flatmates", [])

if not USERS:
    st.warning("🏠 House setup required before using the calendar.")
    if st.button("⚙️ Go to Settings"):
        st.switch_page("pages/0_Settings.py")
    st.stop()

events = get_events()

def _extract_date(value):
    """Normalize a date-like value into a `date` object.

    Args:
        value: Date, datetime, or ISO string value from calendar callbacks.

    Returns:
        date | None: Parsed date if possible, otherwise None.
    """
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        cleaned = value.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo:
                return dt.astimezone().date()
            return dt.date()
        except:
            # Fall back to simple split
            try:
                return datetime.fromisoformat(cleaned.split("T")[0]).date()
            except:
                return None
    return None

def _parse_calendar_payload(payload, keys):
    """Pull the first valid date from a calendar callback payload.

    Args:
        payload (dict): FullCalendar callback payload.
        keys (list): Candidate keys that may contain a date value.

    Returns:
        date | None: Parsed date if present and valid.
    """
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if key in payload:
            parsed = _extract_date(payload[key])
            if parsed:
                return parsed
    return None

# Prepare Calendar Events
calendar_events = []
for event in events:
    start_str = event['date']
    if event.get('start_time'):
        start_str += f"T{event['start_time']}"
    
    end_str = None
    if event.get('end_time'):
        end_str = event['date'] + f"T{event['end_time']}"
    
    # Color logic
    color = "#3788d8"
    assignees = event.get('assigned_to', [])
    if isinstance(assignees, str): assignees = [assignees]
    elif assignees is None: assignees = []
    
    if assignees:
        first_person = assignees[0]
        if first_person in USERS:
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD"]
            try:
                idx = USERS.index(first_person)
                color = colors[idx % len(colors)]
            except: pass

    assignee_str = ", ".join(assignees) if assignees else "Everyone"

    calendar_events.append({
        "id": str(event['id']), # Ensure ID is string for FullCalendar
        "title": f"{event['title']} ({assignee_str})",
        "start": start_str,
        "end": end_str,
        "backgroundColor": color,
        "borderColor": color,
        "extendedProps": {
            "description": event.get('description'),
            "assigned_to": assignees,
            "full_title": event['title'],
            "original_event": event # Store full event object for editing
        }
    })

calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,listMonth",
    },
    "initialView": "dayGridMonth",
    "selectable": True,
    "editable": False,
    "height": 650,
}

# --- LAYOUT ---
col_cal, col_panel = st.columns([2, 1], gap="medium")

with col_cal:
    st.markdown("### Schedule")
    cal_state = calendar(
        events=calendar_events, 
        options=calendar_options, 
        key="calendar_widget",
        callbacks=['dateClick', 'select', 'eventClick']
    )

# --- INTERACTION LOGIC ---
# Check for Event Click
if cal_state.get("eventClick"):
    clicked_event = cal_state["eventClick"]["event"]
    event_id = clicked_event.get("id")
    if st.session_state.skip_event_id and event_id == st.session_state.skip_event_id:
        # Ignore this click once; user just closed the panel
        st.session_state.skip_event_id = None
    else:
        if st.session_state.selected_event_id != event_id or st.session_state.view_mode != "details":
            st.session_state.selected_event = clicked_event
            st.session_state.selected_event_id = event_id
            st.session_state.view_mode = "details"
            st.rerun()

# Check for Date Click or Selection
new_date = None

# Prioritize 'select' (range selection or cell selection)
if cal_state.get("select"):
    new_date = _parse_calendar_payload(cal_state.get("select"), ["startStr", "start", "date", "dateStr"])

# Fallback to 'dateClick' if no selection or selection failed
if not new_date and cal_state.get("dateClick"):
    new_date = _parse_calendar_payload(cal_state.get("dateClick"), ["dateStr", "date", "start"])

if new_date and new_date != st.session_state.selected_date:
    st.session_state.selected_date = new_date
    st.session_state.view_mode = "day"
    st.rerun()


# --- SIDE PANEL ---
with col_panel:
    
    # Helper function to reset view
    def go_home(reset_skip=True):
        """Return to list view and optionally clear the skip flag.

        Args:
            reset_skip (bool): Whether to clear the skip-event guard.

        Returns:
            None
        """
        st.session_state.view_mode = "list"
        st.session_state.selected_date = date.today()
        st.session_state.selected_event = None
        st.session_state.selected_event_id = None
        if reset_skip:
            st.session_state.skip_event_id = None
        st.rerun()

    # 1. DETAILS VIEW
    if st.session_state.view_mode == "details" and st.session_state.selected_event:
        evt = st.session_state.selected_event
        props = evt.get("extendedProps", {})
        
        with st.container(border=True):
            st.subheader(f"📌 {props.get('full_title', evt['title'])}")
            
            # Date formatting
            try:
                d = datetime.fromisoformat(evt['start'].split("T")[0]).strftime("%A, %d %B")
                st.caption(f"📅 {d}")
            except: pass

            st.divider()
            
            if props.get("description"):
                st.markdown("**Description**")
                st.write(props["description"])
            
            st.markdown("**Assigned To**")
            assignees = props.get("assigned_to", [])
            if assignees:
                for person in assignees:
                    st.info(person, icon="👤")
            else:
                st.info("Everyone", icon="🏠")
            
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Edit", use_container_width=True):
                    st.session_state.view_mode = "edit"
                    st.rerun()
            with c2:
                if st.button("❌ Close", use_container_width=True):
                    st.session_state.skip_event_id = st.session_state.selected_event_id
                    go_home(reset_skip=False)

    # 2. EDIT VIEW
    elif st.session_state.view_mode == "edit" and st.session_state.selected_event:
        evt = st.session_state.selected_event
        props = evt.get("extendedProps", {})
        original = props.get("original_event", {})
        
        with st.container(border=True):
            st.subheader("✏️ Edit Event")
            
            # Parse times for default values
            use_time_default = bool(original.get('start_time'))
            
            # Move checkbox OUTSIDE form for interactivity
            event_identifier = original.get('id') or evt.get('id')
            use_time = st.checkbox(
                "Add Time", 
                value=use_time_default, 
                key=f"edit_use_time_{event_identifier}"
            )
            
            with st.form("edit_event_form"):
                title = st.text_input("Title", value=props.get('full_title', evt['title']))
                
                # Parse date
                try:
                    default_date = datetime.fromisoformat(original['date']).date()
                except:
                    default_date = date.today()
                event_date = st.date_input(
                    "Date", 
                    value=default_date, 
                    key=f"edit_date_{event_identifier}"
                )
                
                start_val = time(9,0)
                end_val = time(10,0)
                if original.get('start_time'):
                    try: start_val = time.fromisoformat(original['start_time'])
                    except: pass
                if original.get('end_time'):
                    try: end_val = time.fromisoformat(original['end_time'])
                    except: pass
                
                c1, c2 = st.columns(2)
                with c1:
                    start_t = st.time_input(
                        "Start", 
                        value=start_val, 
                        disabled=not use_time,
                        key=f"edit_start_{event_identifier}"
                    )
                with c2:
                    end_t = st.time_input(
                        "End", 
                        value=end_val, 
                        disabled=not use_time,
                        key=f"edit_end_{event_identifier}"
                    )
                
                assigned_default = props.get("assigned_to", [])
                assigned_to = st.multiselect("Assign To", USERS, default=assigned_default)
                
                desc = st.text_area("Description", value=props.get("description", ""))
                
                st.markdown("---")
                submitted = st.form_submit_button("Update", type="primary", use_container_width=True)
                
            if st.button("Cancel", use_container_width=True):
                st.session_state.view_mode = "details"
                st.rerun()
                
            if submitted:
                if not title:
                    st.error("Title required")
                else:
                    payload = {
                        "title": title,
                        "date": str(event_date),
                        "description": desc,
                        "assigned_to": assigned_to
                    }
                    if use_time:
                        payload["start_time"] = str(start_t)
                        payload["end_time"] = str(end_t)
                    else:
                        # Explicitly clear time if unchecked
                        payload["start_time"] = None
                        payload["end_time"] = None
                    
                    update_event(original['id'], payload)
                    st.success("Updated!")
                    st.session_state.view_mode = "details"
                    st.rerun()

    # 3. DAY VIEW (List of events + Create Form)
    elif st.session_state.view_mode == "day" or st.session_state.view_mode == "create":
        with st.container(border=True):
            d_str = st.session_state.selected_date.strftime('%A, %d %B')
            st.subheader(f"📅 {d_str}")
            
            # Filter events for this day
            day_events = [e for e in events if e['date'] == str(st.session_state.selected_date)]
            
            if day_events:
                st.caption("Events on this day:")
                for e in day_events:
                    with st.container():
                        st.write(f"• **{e['title']}**")
                        if e.get('start_time'):
                            st.caption(f"🕒 {e['start_time']}")
                st.divider()
            else:
                st.info("No events for this day.")
                st.divider()

            st.subheader("➕ Add Event")
            
            # Move checkbox OUTSIDE form for interactivity
            use_time = st.checkbox(
                "Add Time", 
                value=False, 
                key=f"create_use_time_{st.session_state.selected_date.isoformat()}"
            )
            
            with st.form("create_event_form_day"):
                title = st.text_input("Title", placeholder="e.g. Dinner Party")
                
                # Explicit date input to show user what date is being used
                date_input_key = f"create_date_{st.session_state.selected_date.isoformat()}"
                form_date = st.date_input("Date", value=st.session_state.selected_date, key=date_input_key)
                
                assign_key = f"create_assign_{st.session_state.selected_date.isoformat()}"
                assigned_to = st.multiselect(
                    "Assign To", 
                    USERS, 
                    key=assign_key,
                    placeholder="Select flatmates..."
                )
                
                c1, c2 = st.columns(2)
                with c1:
                    start_t = st.time_input(
                        "Start", 
                        value=time(9,0), 
                        disabled=not use_time,
                        key=f"create_start_{st.session_state.selected_date.isoformat()}"
                    )
                with c2:
                    end_t = st.time_input(
                        "End", 
                        value=time(10,0), 
                        disabled=not use_time,
                        key=f"create_end_{st.session_state.selected_date.isoformat()}"
                    )
                
                desc = st.text_area("Description", height=80, placeholder="Add details...")
                
                submitted = st.form_submit_button("Create Event", type="primary", use_container_width=True)
                
                if submitted:
                    if not title:
                        st.error("Please enter a title")
                    else:
                        payload = {
                            "title": title,
                            "date": str(form_date),
                            "description": desc,
                            "assigned_to": assigned_to
                        }
                        if use_time:
                            payload["start_time"] = str(start_t)
                            payload["end_time"] = str(end_t)
                        
                        create_event(payload)
                        st.success("Event Created!")
                        st.rerun()
            
            if st.button("🔙 View All", use_container_width=True):
                go_home()

    # 4. DEFAULT LIST VIEW (Upcoming events)
    else:
        with st.container(border=True):
            st.subheader("🗓️ Upcoming Events")
            
            # Filter for future events
            today_str = str(date.today())
            upcoming = [e for e in events if e['date'] >= today_str]
            upcoming.sort(key=lambda x: x['date'])
            
            if upcoming:
                for e in upcoming[:5]: # Show next 5
                    with st.container():
                        d_obj = datetime.fromisoformat(e['date']).date()
                        st.write(f"**{e['title']}**")
                        st.caption(f"{d_obj.strftime('%d %b')} • {', '.join(e.get('assigned_to', []) or ['Everyone'])}")
                        st.divider()
            else:
                st.info("No upcoming events.")
            
            st.divider()
            if st.button("➕ Create New Event", type="primary", use_container_width=True):
                st.session_state.selected_date = date.today()
                st.session_state.view_mode = "day"
                st.rerun()
