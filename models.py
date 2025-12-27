from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    category = Column(String)
    amount = Column(Float)
    date = Column(Date)
    user_id = Column(Integer)



class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)
    amount = Column(Float)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="income")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String)
    amount = Column(Float)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="budgets")

