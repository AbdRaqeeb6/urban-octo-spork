from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import date

# ---------------- APP ----------------
app = FastAPI()

# ---------------- DATABASE ----------------
DATABASE_URL = "sqlite:///./budget.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- MODELS ----------------
class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    month = Column(String, unique=True)
    amount = Column(Float)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    category = Column(String)
    amount = Column(Float)
    date = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------- SCHEMAS ----------------
class BudgetCreate(BaseModel):
    month: str
    amount: float

class ExpenseCreate(BaseModel):
    description: str
    category: str
    amount: float
    date: str

# ---------------- STATIC FILES ----------------
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ---------------- PAGE ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def login_page():
    with open("frontend/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    with open("frontend/dashboard.html", encoding="utf-8") as f:
        return f.read()

@app.get("/expenses", response_class=HTMLResponse)
def expenses_page():
    with open("frontend/expenses.html", encoding="utf-8") as f:
        return f.read()

@app.get("/budget", response_class=HTMLResponse)
def budget_page():
    with open("frontend/budget.html", encoding="utf-8") as f:
        return f.read()

@app.get("/reports", response_class=HTMLResponse)
def reports_page():
    with open("frontend/reports.html", encoding="utf-8") as f:
        return f.read()

# ---------------- API: SAVE BUDGET ----------------
@app.post("/budget")
def set_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    existing = db.query(Budget).filter(Budget.month == budget.month).first()

    if existing:
        existing.amount = budget.amount
    else:
        db.add(Budget(month=budget.month, amount=budget.amount))

    db.commit()
    return {"status": "budget saved"}

# ---------------- API: SAVE EXPENSE ----------------
@app.post("/expenses")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    e = Expense(
        description=expense.description,
        category=expense.category,
        amount=expense.amount,
        date=expense.date
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return {"status": "expense saved"}

# ---------------- API: EXPENSES BY CATEGORY ----------------
@app.get("/expenses-by-category")
def expenses_by_category(db: Session = Depends(get_db)):
    results = (
        db.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        )
        .group_by(Expense.category)
        .all()
    )

    return [
        {"category": r.category, "total": round(r.total, 2)}
        for r in results
    ]

# ---------------- API: KPI + FORECAST ----------------
@app.get("/net-balance")
def net_balance(db: Session = Depends(get_db)):
    total_budget = db.query(
        func.coalesce(func.sum(Budget.amount), 0)
    ).scalar()

    total_expenses = db.query(
        func.coalesce(func.sum(Expense.amount), 0)
    ).scalar()

    net = total_budget - total_expenses

    utilisation = (
        (total_expenses / total_budget) * 100
        if total_budget > 0 else 0
    )

    day = max(date.today().day, 1)
    avg_daily = total_expenses / day if total_expenses > 0 else 0
    forecast = int(total_budget / avg_daily) if avg_daily > 0 else None

    return {
        "total_income": round(total_budget, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(net, 2),
        "budget_utilisation": round(utilisation, 1),
        "forecast_days": forecast
    }
