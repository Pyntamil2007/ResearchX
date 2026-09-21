import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    VerifyResetTokenRequest,
    VerifyResetTokenResponse,
    ResetPasswordRequest
)
from app.schemas.common import StandardResponse

logger = logging.getLogger("researchx.auth")

router = APIRouter(prefix="/auth", tags=["Authentication & Password Recovery"])

@router.post("/register", response_model=StandardResponse[TokenResponse])
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user account and dispatch in-app notifications for user and admins."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # If this is admin@researchx.com or the first registered account in the system, elevate to ADMIN
    is_admin_email = user_in.email.lower().strip() == "admin@researchx.com"
    is_first_user = db.query(User).count() == 0
    assigned_role = "ADMIN" if (is_admin_email or is_first_user) else "USER"

    user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=get_password_hash(user_in.password),
        role=assigned_role,
        auth_provider="local",
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 1. User In-App Notification: Account created successfully
    NotificationService.create_user_notification(
        db=db,
        user_id=user.id,
        title="Account created successfully",
        message=f"Welcome to ResearchX, {user.name}! Your account has been initialized successfully.",
        notification_type="account_created"
    )

    # 2. Admin In-App Notification: New user registered
    NotificationService.notify_admins(
        db=db,
        title="New user registered",
        message=f"New user {user.name} ({user.email}) registered on the ResearchX platform.",
        notification_type="admin_new_user"
    )

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
    
    return StandardResponse(
        success=True,
        message="Account created successfully.",
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    )

@router.post("/login", response_model=StandardResponse[TokenResponse])
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support or an administrator."
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    return StandardResponse(
        success=True,
        message="Login successful.",
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    )

@router.get("/me", response_model=StandardResponse[UserResponse])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve the currently authenticated user's profile."""
    return StandardResponse(
        success=True,
        message="Profile retrieved.",
        data=UserResponse.from_orm(current_user)
    )

@router.post("/forgot-password", response_model=StandardResponse[ForgotPasswordResponse])
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generate a secure single-use password reset token for account recovery.
    """
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address."
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Password reset is not permitted."
        )

    # Invalidate any previously unused reset tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})

    # Generate secure URL-safe reset token
    import secrets
    token_str = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)

    reset_record = PasswordResetToken(
        user_id=user.id,
        token=token_str,
        expires_at=expires_at,
        used=False
    )
    db.add(reset_record)
    db.commit()

    frontend_base = (settings.FRONTEND_URL or "http://127.0.0.1:5173").rstrip('/')
    reset_link = f"{frontend_base}/reset-password?token={token_str}"

    return StandardResponse(
        success=True,
        message="Password reset instructions and recovery link have been generated.",
        data=ForgotPasswordResponse(
            message="Password reset link generated successfully.",
            reset_token=token_str,
            reset_link=reset_link,
            expires_in_minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
        )
    )

@router.post("/verify-reset-token", response_model=StandardResponse[VerifyResetTokenResponse])
def verify_reset_token(req: VerifyResetTokenRequest, db: Session = Depends(get_db)):
    """
    Verify whether a given password reset token is valid, unused, and not expired.
    """
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == req.token.strip()
    ).first()

    if not reset_record:
        return StandardResponse(
            success=False,
            message="Invalid password reset token.",
            data=VerifyResetTokenResponse(
                valid=False,
                message="Password reset link is invalid or has expired."
            )
        )

    if reset_record.used:
        return StandardResponse(
            success=False,
            message="This password reset token has already been used.",
            data=VerifyResetTokenResponse(
                valid=False,
                message="This password reset link has already been used. Please request a new one."
            )
        )

    if datetime.utcnow() > reset_record.expires_at:
        return StandardResponse(
            success=False,
            message="This password reset token has expired.",
            data=VerifyResetTokenResponse(
                valid=False,
                message="This password reset link has expired. Please request a new one."
            )
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    return StandardResponse(
        success=True,
        message="Password reset token is valid.",
        data=VerifyResetTokenResponse(
            valid=True,
            email=user.email if user else None,
            message="Token is valid. You may now enter your new password."
        )
    )

@router.post("/reset-password", response_model=StandardResponse[dict])
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Set a new password using a verified single-use reset token.
    Prevents token reuse, hashes the new password securely with bcrypt, and sends in-app notification.
    """
    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long."
        )

    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == req.token.strip()
    ).first()

    if not reset_record or reset_record.used or datetime.utcnow() > reset_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid, used, or expired. Please request a new reset link."
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user account not found."
        )

    # Update password hash
    user.password_hash = get_password_hash(req.new_password)
    # Mark token as used to prevent replay
    reset_record.used = True
    
    # In-App Notification: Password changed
    NotificationService.create_user_notification(
        db=db,
        user_id=user.id,
        title="Password changed",
        message="Your ResearchX account password has been updated successfully.",
        notification_type="password_changed"
    )

    db.commit()

    return StandardResponse(
        success=True,
        message="Your password has been reset successfully. You can now log in with your new password.",
        data={"reset": True}
    )
