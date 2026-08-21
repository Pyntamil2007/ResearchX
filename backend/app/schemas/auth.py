from typing import Optional
from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None  # Returned in development for immediate test/link navigation
    reset_link: Optional[str] = None
    expires_in_minutes: Optional[int] = 15

class VerifyResetTokenRequest(BaseModel):
    token: str

class VerifyResetTokenResponse(BaseModel):
    valid: bool
    email: Optional[str] = None
    message: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
