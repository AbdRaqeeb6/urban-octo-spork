from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from jose import jwt

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
# DATABASE (ABSOLUTE PATH)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'budget.db')}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

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
    user_id = Column(Integer)
    category = Column(String)
    amount = Column(Float)

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)

Base.metadata.create_all(bind=engine)

# =========================
# AUTH / SECURITY
# =========================
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# DEPENDENCIES
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401)
    return user

# =========================
# AUTH ENDPOINTS
# =========================
@app.post("/register")
def register(data: dict, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data["email"]).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=data["email"],
        password=hash_password(data["password"])
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# =========================
# BUSINESS LOGIC
# =========================
@app.post("/add-expense")
def add_expense(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expense = Expense(
        user_id=user.id,
        category=data["category"],
        amount=data["amount"]
    )
    db.add(expense)
    db.commit()
    return {"message": "Expense added"}

@app.post("/set-budget")
def set_budget(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Budget).filter(Budget.user_id == user.id).delete()
    budget = Budget(user_id=user.id, amount=data["amount"])
    db.add(budget)
    db.commit()
    return {"message": "Budget set"}

@app.get("/summary")
def summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_expenses = (
        db.query(Expense)
        .filter(Expense.user_id == user.id)
        .with_entities(Expense.amount)
        .all()
    )
    total_expenses = sum(x[0] for x in total_expenses)

    budget = (
        db.query(Budget)
        .filter(Budget.user_id == user.id)
        .first()
    )
    budget_amount = budget.amount if budget else 0

    return {
        "budget": budget_amount,
        "expenses": total_expenses,
        "balance": budget_amount - total_expenses
    }
