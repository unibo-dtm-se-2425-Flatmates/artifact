import os
import requests
import streamlit as st

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
API_URL = _resolve_api_url() or "http://localhost:8000"

def render_sidebar():
    """Render the Streamlit sidebar navigation and styling."""
    with st.sidebar:
        st.title("🏠 Flatmate Manager")
        
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
        response = requests.get(f"{API_URL}/calendar/")
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
    requests.post(f"{API_URL}/calendar/", json=event_data)

def update_event(event_id, event_data):
    """Update an existing event by ID.

    Args:
        event_id (int): Target event identifier.
        event_data (dict): Updated event payload.
    """
    requests.put(f"{API_URL}/calendar/{event_id}", json=event_data)

def get_shopping_list():
    """Fetch the shopping list from the backend.

    Returns:
        list: Shopping items or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/shopping/")
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
    requests.post(f"{API_URL}/shopping/", json=item_data)

def remove_shopping_item(item_id):
    """Remove a shopping item by ID.

    Args:
        item_id (int): Identifier of the item to delete.
    """
    requests.delete(f"{API_URL}/shopping/{item_id}")

def get_expenses():
    """Fetch all expenses.

    Returns:
        list: Expense records or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/expenses/")
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
    requests.post(f"{API_URL}/expenses/", json=expense_data)

def get_debts():
    """Fetch simplified debt suggestions from the backend.

    Returns:
        list: Debt records or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/expenses/debts")
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
        response = requests.get(f"{API_URL}/house/")
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
    requests.post(f"{API_URL}/house/", json=settings)


def reset_house_data():
    """Request a full reset of house data."""
    try:
        response = requests.delete(f"{API_URL}/house/reset")
        return response.status_code == 200
    except:
        return False


def get_reimbursements():
    """Fetch reimbursement history.

    Returns:
        list: Reimbursement records or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/expenses/reimbursements")
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
    requests.post(f"{API_URL}/expenses/reimbursements", json=reimbursement_data)
