from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

# =========================
# CONFIG
# =========================
SECRET_KEY = "change-this-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DATABASE_URL = "sqlite:///./budget.db"

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
from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/ui/login.html")

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")


# =========================
# DATABASE
# =========================
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
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    amount = Column(Float)

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)

Base.metadata.create_all(bind=engine)

# =========================
# SCHEMAS
# =========================
class AuthRequest(BaseModel):
    email: str
    password: str

class ExpenseCreate(BaseModel):
    category: str
    amount: float

class BudgetCreate(BaseModel):
    amount: float

# =========================
# SECURITY
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# AUTH ENDPOINTS (JSON)
# =========================
@app.post("/register")
def register(req: AuthRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=req.email,
        password=hash_password(req.password)
    )
    db.add(user)
    db.commit()
    return {"message": "Registration successful"}

@app.post("/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# =========================
# BUSINESS LOGIC
# =========================
@app.post("/expenses")
def add_expense(exp: ExpenseCreate, db: Session = Depends(get_db)):
    db.add(Expense(category=exp.category, amount=exp.amount))
    db.commit()
    return {"message": "Expense added"}

@app.get("/expenses-by-category")
def expenses_by_category(db: Session = Depends(get_db)):
    rows = (
        db.query(Expense.category, func.sum(Expense.amount))
        .group_by(Expense.category)
        .all()
    )
    return [{"category": c, "total": round(t, 2)} for c, t in rows]

@app.post("/budget")
def set_budget(b: BudgetCreate, db: Session = Depends(get_db)):
    db.query(Budget).delete()
    db.add(Budget(amount=b.amount))
    db.commit()
    return {"message": "Budget saved"}

@app.get("/net-balance")
def net_balance(db: Session = Depends(get_db)):
    total_budget = db.query(func.coalesce(func.sum(Budget.amount), 0)).scalar()
    total_expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()

    return {
        "total_income": round(total_budget, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(total_budget - total_expenses, 2),
        "budget_utilisation": round(
            (total_expenses / total_budget * 100) if total_budget else 0, 1
        )
    }
