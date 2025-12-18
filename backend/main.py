from fastapi import FastAPI

from .routers import auth, calendar, expenses, house, shopping

app = FastAPI(title="Flatmate App API")

app.include_router(auth.router)
app.include_router(calendar.router)
app.include_router(shopping.router)
app.include_router(expenses.router)
app.include_router(house.router)

@app.get("/")
def read_root():
    """Return a simple welcome message for the API root endpoint.

    Returns:
        dict: Welcome payload with a static message.
    """
    return {"message": "Welcome to the Flatmate App API"}