from fastapi import FastAPI
from .routers import calendar, shopping, expenses

app = FastAPI(title="Flatmate App API")

app.include_router(calendar.router)
app.include_router(shopping.router)
app.include_router(expenses.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Flatmate App API"}