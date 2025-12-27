from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import date
import hashlib

# =========================
# APP
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DATABASE
# =========================
DATABASE_URL = "sqlite:///./budget.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# MODELS
# =========================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, unique=True)
    amount = Column(Float)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    category = Column(String)
    amount = Column(Float)
    date = Column(String)

Base.metadata.create_all(bind=engine)

# =========================
# SCHEMAS
# =========================
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class BudgetCreate(BaseModel):
    month: str
    amount: float

class ExpenseCreate(BaseModel):
    description: str
    category: str
    amount: float
    date: str

# =========================
# HELPERS
# =========================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(raw, hashed):
    return hash_password(raw) == hashed

# =========================
# AUTH
# =========================
@app.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    u = User(
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(u)
    db.commit()
    return {"status": "registered"}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": str(user.id),
        "token_type": "bearer"
    }

# =========================
# BUSINESS LOGIC
# =========================
@app.post("/budget")
def set_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    existing = db.query(Budget).filter(Budget.month == budget.month).first()
    if existing:
        existing.amount = budget.amount
    else:
        db.add(Budget(month=budget.month, amount=budget.amount))
    db.commit()
    return {"status": "budget saved"}

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
    return {"status": "expense saved"}

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
    return [{"category": r.category, "total": r.total} for r in results]

@app.get("/net-balance")
def net_balance(db: Session = Depends(get_db)):
    total_budget = db.query(func.coalesce(func.sum(Budget.amount), 0)).scalar()
    total_expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()

    net = total_budget - total_expenses
    utilisation = (total_expenses / total_budget * 100) if total_budget else 0

    day = max(date.today().day, 1)
    avg_daily = total_expenses / day if total_expenses else 0
    forecast = int(total_budget / avg_daily) if avg_daily else None

    return {
        "total_income": total_budget,
        "total_expenses": total_expenses,
        "net_balance": net,
        "budget_utilisation": round(utilisation, 1),
        "forecast_days": forecast
    }

# =========================
# FRONTEND SERVING
# =========================
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")
