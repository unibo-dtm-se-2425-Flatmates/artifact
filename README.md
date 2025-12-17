# Flatmate Manager App 🏠

A comprehensive web application designed to help flatmates manage their shared living space efficiently. Built with FastAPI for the backend and Streamlit for the frontend.

## ✨ Features

- **📅 Calendar**: Schedule and track shared events, cleaning duties, or house parties.
- **🛒 Shopping List**: Collaborative shopping list to keep track of what's needed.
- **💰 Expense Manager**: Track shared expenses, split bills, and simplify debt settlement.
- **⚙️ House Settings**: Configure house details and manage user profiles.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Streamlit, Altair, Pandas
- **Database**: SQLite (via Python `sqlite3`)
- **Testing**: Pytest
- **HTTP Client**: Requests, HTTPX
- **Language**: Python 3.8+

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Flatmate-Manager-TEST
   ```

2. **Create and activate a virtual environment** (Recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃‍♂️ Running the Application

The application consists of two parts that need to run simultaneously.

### 1. Start the Backend API
Open a terminal and run:
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`. You can view the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

The SQLite database is created automatically at first run in `backend/db/flatmate.db`.

### 2. Start the Frontend Interface
Open a new terminal and run:
```bash
streamlit run frontend/app.py
```
The web application will open automatically in your default browser at [http://localhost:8501](http://localhost:8501).

## 📂 Project Structure

```
Flatmate-Manager-TEST/
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── README.md
├── requirements.txt           # Python dependencies
├── run_tests.py               # Helper to run test suite
├── backend/                   # FastAPI backend
│   ├── main.py                # Backend entry point
│   ├── models.py              # Pydantic models / schemas
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py        # Database configuration/connection
│   └── routers/               # API routes
│       ├── calendar.py
│       ├── expenses.py
│       ├── house.py
│       └── shopping.py
├── frontend/                  # Streamlit frontend
│   ├── app.py                 # Frontend entry point
│   ├── utils.py               # Helpers and UI utilities
│   └── pages/                 # Multi-page app screens
│       ├── 0_Settings.py
│       ├── 1_Calendar.py
│       ├── 2_Shopping_List.py
│       └── 3_Expenses.py
└── test/                      # Unit tests
   ├── test_backend.py
   ├── test_database.py
   └── test_frontend.py
```

## 🧪 Tests

Run all tests with:

```bash
python run_tests.py
```