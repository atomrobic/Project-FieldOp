from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = Field(..., pattern="^(ADMIN|FIELD_WORKER|USER)$")

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_active: bool
    is_approved: bool
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None