from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from pydantic import BaseModel

# =======================
# APP
# =======================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# DATABASE
# =======================
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

# =======================
# MODELS
# =======================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    category = Column(String)
    amount = Column(Float)

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    month = Column(String)
    amount = Column(Float)

Base.metadata.create_all(bind=engine)

# =======================
# SECURITY
# =======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p): return pwd_context.hash(p)
def verify_password(p, h): return pwd_context.verify(p, h)

# =======================
# SCHEMAS
# =======================
class Auth(BaseModel):
    email: str
    password: str

class ExpenseCreate(BaseModel):
    description: str
    category: str
    amount: float

class BudgetCreate(BaseModel):
    month: str
    amount: float

# =======================
# AUTH API
# =======================
@app.post("/api/register")
def register(data: Auth, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "User already exists")
    db.add(User(email=data.email, password=hash_password(data.password)))
    db.commit()
    return {"message": "Registered"}

@app.post("/api/login")
def login(data: Auth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": str(user.id)}

# =======================
# BUSINESS API
# =======================
@app.post("/api/expenses")
def add_expense(exp: ExpenseCreate, db: Session = Depends(get_db)):
    db.add(Expense(**exp.dict()))
    db.commit()
    return {"message": "Expense added"}

@app.get("/api/expenses-by-category")
def expenses_by_category(db: Session = Depends(get_db)):
    rows = (
        db.query(Expense.category, func.sum(Expense.amount))
        .group_by(Expense.category)
        .all()
    )
    return [{"category": c, "total": t} for c, t in rows]

@app.post("/api/budget")
def set_budget(b: BudgetCreate, db: Session = Depends(get_db)):
    db.query(Budget).filter(Budget.month == b.month).delete()
    db.add(Budget(**b.dict()))
    db.commit()
    return {"message": "Budget saved"}

@app.get("/api/budget-status/{month}")
def budget_status(month: str, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.month == month).first()
    spent = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()
    return {
        "budget": budget.amount if budget else 0,
        "spent": spent
    }

@app.get("/api/net-balance")
def net_balance(db: Session = Depends(get_db)):
    income = db.query(func.coalesce(func.sum(Budget.amount), 0)).scalar()
    expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net_balance": income - expenses
    }

# =======================
# FRONTEND ROUTES (THIS FIXES 404)
# =======================
@app.get("/")
def login_page():
    return FileResponse("frontend/index.html")

@app.get("/dashboard")
def dashboard_page():
    return FileResponse("frontend/dashboard.html")

@app.get("/expenses")
def expenses_page():
    return FileResponse("frontend/expenses.html")

@app.get("/budget")
def budget_page():
    return FileResponse("frontend/budget.html")

@app.get("/reports")
def reports_page():
    return FileResponse("frontend/reports.html")

# =======================
# STATIC FILES
# =======================
app.mount("/static", StaticFiles(directory="frontend"), name="static")
