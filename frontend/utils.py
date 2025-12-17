import requests

API_URL = "http://localhost:8000"

def get_events():
    try:
        response = requests.get(f"{API_URL}/calendar/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def create_event(event_data):
    requests.post(f"{API_URL}/calendar/", json=event_data)

def get_shopping_list():
    try:
        response = requests.get(f"{API_URL}/shopping/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def add_shopping_item(item_data):
    requests.post(f"{API_URL}/shopping/", json=item_data)

def remove_shopping_item(item_id):
    requests.delete(f"{API_URL}/shopping/{item_id}")

def get_expenses():
    try:
        response = requests.get(f"{API_URL}/expenses/")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def add_expense(expense_data):
    requests.post(f"{API_URL}/expenses/", json=expense_data)

def get_debts():
    try:
        response = requests.get(f"{API_URL}/expenses/debts")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []