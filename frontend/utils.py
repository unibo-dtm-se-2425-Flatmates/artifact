import os
import requests
import streamlit as st
from typing import Optional, Dict, Any

try:
    # Raised when no secrets file is present; makes imports crash under pytest.
    from streamlit.errors import StreamlitSecretNotFoundError
except Exception:  # pragma: no cover - fallback for older Streamlit versions
    class StreamlitSecretNotFoundError(Exception):
        pass


def _resolve_api_url():
    """Safely resolve the backend API URL without requiring secrets during tests."""
    env_url = os.environ.get("API_URL")
    if env_url:
        return env_url

    try:
        return st.secrets.get("API_URL")
    except StreamlitSecretNotFoundError:
        return None
    except Exception:
        # Avoid import-time crashes if secrets cannot be parsed for any reason.
        return None


# Allow configuring the backend URL via secrets or environment variables while staying test-friendly.
# API_URL = _resolve_api_url() or "http://localhost:8000"
API_URL = "http://localhost:8000"

def _auth_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Build authorization headers from the provided token or session state."""
    active_token = token or st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {active_token}"} if active_token else {}


def register_user(username: str, password: str, house_name: Optional[str] = None, house_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    payload = {"username": username, "password": password, "house_name": house_name, "house_code": house_code}
    try:
        resp = requests.post(f"{API_URL}/auth/register", json=payload)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None


def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    payload = {"username": username, "password": password}
    try:
        resp = requests.post(f"{API_URL}/auth/login", json=payload)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None


def fetch_profile(token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        resp = requests.get(f"{API_URL}/auth/me", headers=_auth_headers(token))
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None


def require_auth() -> Dict[str, Any]:
    """Ensure the user is authenticated; stop the app otherwise and offer a login link."""
    token = st.session_state.get("auth_token")
    if not token:
        st.warning("Please login to continue.")
        if st.button("Go to Login", type="primary"):
            st.switch_page("app.py")
        st.stop()

    if "profile" not in st.session_state or not st.session_state["profile"]:
        profile = fetch_profile(token)
        if profile:
            st.session_state["profile"] = profile
        else:
            st.warning("Session expired. Please login again.")
            if st.button("Go to Login", type="primary"):
                st.switch_page("app.py")
            st.stop()

    return st.session_state["profile"]

def render_sidebar():
    """Render the Streamlit sidebar navigation and styling."""
    with st.sidebar:
        st.title("🏠 Flatmate Manager")

        profile = st.session_state.get("profile") or {}
        user = profile.get("user", {}) if isinstance(profile, dict) else {}
        house = profile.get("house", {}) if isinstance(profile, dict) else {}
        username = user.get("username")
        house_name = house.get("name")

        st.markdown(f"**User:** {username if username else 'Guest'}")
        if house_name:
            st.markdown(f"**House:** {house_name}")

        if username:
            if st.button("Logout", use_container_width=True):
                for key in ("auth_token", "profile"):
                    st.session_state.pop(key, None)
                st.rerun()
        else:
            if st.button("Login", use_container_width=True):
                st.switch_page("app.py")
        
        st.markdown("---")
        
        # Custom Navigation
        st.subheader("Navigation")
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/0_Settings.py", label="Settings", icon="⚙️")
        st.page_link("pages/1_Calendar.py", label="Calendar", icon="📅")
        st.page_link("pages/2_Shopping_List.py", label="Shopping List", icon="🛒")
        st.page_link("pages/3_Expenses.py", label="Expenses", icon="💸")
        
        st.markdown("---")

    # Hide default navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

def get_events():
    """Fetch calendar events from the backend.

    Returns:
        list: List of event dictionaries, empty on failure.
    """
    try:
        response = requests.get(f"{API_URL}/calendar/", headers=_auth_headers())
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def create_event(event_data):
    """Post a new event to the API.

    Args:
        event_data (dict): Event payload matching backend schema.
    """
    requests.post(f"{API_URL}/calendar/", json=event_data, headers=_auth_headers())

def update_event(event_id, event_data):
    """Update an existing event by ID.

    Args:
        event_id (int): Target event identifier.
        event_data (dict): Updated event payload.
    """
    requests.put(f"{API_URL}/calendar/{event_id}", json=event_data, headers=_auth_headers())

def get_shopping_list():
    """Fetch the shopping list from the backend.

    Returns:
        list: Shopping items or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/shopping/", headers=_auth_headers())
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def add_shopping_item(item_data):
    """Create a shopping item via the API.

    Args:
        item_data (dict): Item fields required by the backend.
    """
    requests.post(f"{API_URL}/shopping/", json=item_data, headers=_auth_headers())

def remove_shopping_item(item_id):
    """Remove a shopping item by ID.

    Args:
        item_id (int): Identifier of the item to delete.
    """
    requests.delete(f"{API_URL}/shopping/{item_id}", headers=_auth_headers())

def get_expenses():
    """Fetch all expenses.

    Returns:
        list: Expense records or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/expenses/", headers=_auth_headers())
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def add_expense(expense_data):
    """Create a new expense.

    Args:
        expense_data (dict): Expense payload expected by backend.
    """
    requests.post(f"{API_URL}/expenses/", json=expense_data, headers=_auth_headers())

def get_debts():
    """Fetch simplified debt suggestions from the backend.

    Returns:
        list: Debt records or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/expenses/debts", headers=_auth_headers())
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def get_house_settings():
    """Retrieve the saved house settings.

    Returns:
        dict: House name and flatmates, with defaults on failure.
    """
    try:
        response = requests.get(f"{API_URL}/house/", headers=_auth_headers())
        if response.status_code == 200:
            return response.json()
    except:
        return {"name": "My Flat", "flatmates": []}
    return {"name": "My Flat", "flatmates": []}

def update_house_settings(settings):
    """Persist house configuration.

    Args:
        settings (dict): House name and flatmates payload.
    """
    requests.post(f"{API_URL}/house/", json=settings, headers=_auth_headers())


def reset_house_data():
    """Request a full reset of house data."""
    try:
        response = requests.delete(f"{API_URL}/house/reset", headers=_auth_headers())
        return response.status_code == 200
    except:
        return False


def delete_house():
    """Delete the current house and all its users/data."""
    try:
        response = requests.delete(f"{API_URL}/house/delete", headers=_auth_headers())
        return response.status_code == 200
    except:
        return False


def get_reimbursements():
    """Fetch reimbursement history.

    Returns:
        list: Reimbursement records or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/expenses/reimbursements", headers=_auth_headers())
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []


def add_reimbursement(reimbursement_data):
    """Record a reimbursement via the API.

    Args:
        reimbursement_data (dict): Reimbursement payload expected by backend.
    """
    requests.post(f"{API_URL}/expenses/reimbursements", json=reimbursement_data, headers=_auth_headers())
