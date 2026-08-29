from pydantic import BaseModel, Field

# Schema for creating a new user
class UserCreate(BaseModel):
    name: str
    balance: float = Field(default=0.0, ge=0.0)  # ge=0.0 ensures balance cannot be negative

# Schema for returning user data in responses
class UserResponse(BaseModel):
    id: int
    name: str
    balance: float

    class Config:
        from_attributes = True


# Schema for transferring money between two accounts
class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float = Field(gt=0.0)  # gt=0.0 ensures transfer amount must be greater than 0


# Schema for returning transaction logs
class TransactionResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    amount: float
    status: str

    class Config:
        from_attributes = True