import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Database Connection Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite if DATABASE_URL is not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./payment.db"
elif DATABASE_URL.startswith("postgres://"):
    # Fix Render's legacy postgres:// prefix for SQLAlchemy
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. Database Models (SQLAlchemy ORM)
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Create tables automatically on startup
Base.metadata.create_all(bind=engine)


# 3. Pydantic Schemas for Request Validation
class AccountCreate(BaseModel):
    name: str
    email: str
    initial_balance: float = Field(gt=0, description="Balance must be greater than 0")


class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float = Field(gt=0, description="Transfer amount must be greater than 0")


# Dependency to manage database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 4. FastAPI App Initialization
app = FastAPI(
    title="Payment Engine API",
    description="High-concurrency backend engine with SELECT FOR UPDATE row locking and ACID compliance.",
    version="1.0.0"
)


# Root route
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Payment Engine Service is running.",
        "docs": "/docs"
    }


# Route 1: Create a new account
@app.post("/accounts", status_code=status.HTTP_201_CREATED)
def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Account).filter(Account.email == account_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_account = Account(
        name=account_data.name,
        email=account_data.email,
        balance=account_data.initial_balance
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


# Route 2: Get account details
@app.get("/accounts/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# Route 3: Money Transfer with SELECT FOR UPDATE (Row Locking)
@app.post("/transfer")
def transfer_funds(payload: TransferRequest, db: Session = Depends(get_db)):
    if payload.sender_id == payload.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to yourself")

    try:
        with db.begin():  # Start explicit ACID transaction block
            # Order IDs deterministically to prevent database deadlocks
            first_id, second_id = sorted([payload.sender_id, payload.receiver_id])

            # Lock rows using with_for_update() (Generates SELECT FOR UPDATE in SQL)
            accounts = {
                acc.id: acc
                for acc in db.query(Account)
                .filter(Account.id.in_([first_id, second_id]))
                .with_for_update()
                .all()
            }

            sender = accounts.get(payload.sender_id)
            receiver = accounts.get(payload.receiver_id)

            if not sender or not receiver:
                raise HTTPException(status_code=404, detail="One or both accounts not found")

            if sender.balance < payload.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")

            # Perform debit and credit
            sender.balance -= payload.amount
            receiver.balance += payload.amount

            # Record transaction in ledger
            record = Transaction(
                sender_id=payload.sender_id,
                receiver_id=payload.receiver_id,
                amount=payload.amount
            )
            db.add(record)

        return {
            "status": "success",
            "message": f"Transferred ${payload.amount:.2f} successfully.",
            "sender_new_balance": sender.balance,
            "receiver_new_balance": receiver.balance
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")