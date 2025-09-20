from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ================
# AUTH SCHEMAS
# ================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = Field(..., pattern="^(ADMIN|FIELD_WORKER|USER)$", description="User role: ADMIN, FIELD_WORKER, or USER")

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    is_approved: bool
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # For compatibility if later using ORM, but works with dict too