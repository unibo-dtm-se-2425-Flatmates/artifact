# Flatmate App

A web application for flatmates to manage their shared living space.

## Features
- **Calendar**: Schedule events.
- **Shopping List**: Manage shared shopping items.
- **Expense Manager**: Split expenses and simplify debts.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

You need to run the backend and frontend in separate terminals.

### 1. Start the Backend
From the root directory:
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend
From the root directory (in a new terminal):
```bash
streamlit run frontend/app.py
```
The web app will open in your browser (usually at `http://localhost:8501`).