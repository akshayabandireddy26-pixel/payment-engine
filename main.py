from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Transaction Engine")

# Dependency to open and close database sessions per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------
# 1. CREATE USER ENDPOINT
# -------------------------------------------------------------
@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, balance=user.balance)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# -------------------------------------------------------------
# 2. GET USER BALANCE ENDPOINT
# -------------------------------------------------------------
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------------------------------------------
# 3. TRANSFER MONEY ENDPOINT (WITH DATABASE LOCKING)
# -------------------------------------------------------------
@app.post("/transfer", response_model=schemas.TransactionResponse)
def transfer_money(transfer: schemas.TransferRequest, db: Session = Depends(get_db)):
    if transfer.sender_id == transfer.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to yourself")

    try:
        # Lock rows during transaction to prevent race conditions
        sender = db.query(models.User).filter(models.User.id == transfer.sender_id).with_for_update().first()
        receiver = db.query(models.User).filter(models.User.id == transfer.receiver_id).with_for_update().first()

        if not sender:
            raise HTTPException(status_code=404, detail="Sender not found")
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")

        # Check for insufficient funds
        if sender.balance < transfer.amount:
            # Record failed transaction in database
            failed_tx = models.Transaction(
                sender_id=transfer.sender_id,
                receiver_id=transfer.receiver_id,
                amount=transfer.amount,
                status="FAILED"
            )
            db.add(failed_tx)
            db.commit()
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Perform balance transfer
        sender.balance -= transfer.amount
        receiver.balance += transfer.amount

        # Record successful transaction
        success_tx = models.Transaction(
            sender_id=transfer.sender_id,
            receiver_id=transfer.receiver_id,
            amount=transfer.amount,
            status="SUCCESS"
        )
        db.add(success_tx)
        
        # Commit both balance updates and transaction record atomically
        db.commit()
        db.refresh(success_tx)
        return success_tx

    except Exception as e:
        db.rollback()  # Rollback changes if any database error occurs
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Transaction failed due to server error")