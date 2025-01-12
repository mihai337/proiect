from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name : str
    password : str
    type : Optional[str] = None
    balance : Optional[float] = 0

class TransferRequest(BaseModel):
    email : str
    amount : Optional[float] = 0

class Bill(BaseModel):
    recipient : str
    amount : float

class CreateUserRequest(BaseModel):
    type : str

class ModifyBalanceRequest(BaseModel):
    amount : float