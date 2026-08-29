from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Base is the parent class that SQLAlchemy uses to track all your database tables
Base = declarative_base()


class User(Base):
    """
    Represents the 'users' table in PostgreSQL.
    """
    __tablename__ = "users"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (Optional helper to easily access user transactions in Python)
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_id")
    received_transactions = relationship("Transaction", foreign_keys="Transaction.receiver_id")


class Transaction(Base):
    """
    Represents the 'transactions' table in PostgreSQL.
    """
    __tablename__ = "transactions"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)  # SUCCESS, FAILED, PENDING
    timestamp = Column(DateTime, default=datetime.utcnow)