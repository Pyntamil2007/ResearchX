from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: Optional[str] = "USER"
    status: Optional[str] = "active"

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)

class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(ADMIN|USER)$")

class UserStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|inactive)$")

class PasswordResetRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=100)

class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=100)

class UserResponse(UserBase):
    id: int
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
