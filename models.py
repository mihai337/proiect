from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name : str
    password : str
    balance : Optional[float] = 0

class PartialUser(BaseModel):
    name : str
    balance : Optional[str] = None