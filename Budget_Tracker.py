
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# -------------------------
# Data Model
# -------------------------
class Expense(BaseModel):
    description: str
    amount: float

# Temporary storage (we'll improve this later)
expenses = []

# -------------------------
# Routes
# -------------------------
@app.get("/")
def home():
    return {"message": "Budget Tracker is running"}

@app.post("/add-expense")
def add_expense(expense: Expense):
    expenses.append(expense)
    return {"status": "Expense added", "expense": expense}

@app.get("/total-expenses")
def total_expenses():
    total = sum(e.amount for e in expenses)
    return {"total_expenses": total}

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine
from models import Base, Expense
from deps import get_db

# Create tables (safe to call multiple times)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# -------------------------
# Pydantic Schema
# -------------------------
class ExpenseCreate(BaseModel):
    description: str
    amount: float

# -------------------------
# Routes
# -------------------------
@app.get("/")
def home():
    return {"message": "Budget Tracker is running with DB"}

@app.post("/add-expense")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(
        description=expense.description,
        amount=expense.amount
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"status": "Expense added", "expense_id": db_expense.id}

@app.get("/total-expenses")
def total_expenses(db: Session = Depends(get_db)):
    total = db.query(Expense).with_entities(Expense.amount).all()
    total_sum = sum(amount for (amount,) in total)
    return {"total_expenses": total_sum}