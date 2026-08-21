import os
import math
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.database import get_db
from app.core.security import get_current_user, require_admin, get_password_hash, verify_password
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.paper import ResearchPaper
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
    PasswordResetRequest,
    DeleteAccountRequest
)
from app.schemas.common import StandardResponse, PaginatedData, PaginationMeta

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.get("", response_model=StandardResponse[PaginatedData[UserResponse]])
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = "newest",  # newest, oldest, name, email, role
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users with search, filtering, and pagination (Admin only)."""
    query = db.query(User)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    if role:
        query = query.filter(User.role == role.upper())

    if status:
        query = query.filter(User.status == status.lower())

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(User.id.asc())
    elif sort_by == "name":
        query = query.order_by(User.name.asc())
    elif sort_by == "email":
        query = query.order_by(User.email.asc())
    elif sort_by == "role":
        query = query.order_by(User.role.asc(), User.id.desc())
    else:  # "newest"
        query = query.order_by(User.id.desc())

    total = query.count()
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit
    
    users = query.offset(offset).limit(limit).all()
    user_responses = [UserResponse.from_orm(u) for u in users]

    meta = PaginationMeta(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

    return StandardResponse(
        success=True,
        message="Users list retrieved successfully.",
        data=PaginatedData(items=user_responses, meta=meta)
    )

@router.post("", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new user directly (Admin only) and dispatch in-app notifications."""
    existing = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=get_password_hash(user_in.password),
        role=user_in.role.upper() if user_in.role else "USER",
        status=user_in.status.lower() if user_in.status else "active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 1. User In-App Notification: Account created successfully
    NotificationService.create_user_notification(
        db=db,
        user_id=new_user.id,
        title="Account created successfully",
        message=f"Welcome to ResearchX, {new_user.name}! Your account has been initialized successfully.",
        notification_type="account_created"
    )

    # 2. Admin In-App Notification: New user registered
    NotificationService.notify_admins(
        db=db,
        title="New user registered",
        message=f"New user {new_user.name} ({new_user.email}) was created by administrator.",
        notification_type="admin_new_user"
    )

    return StandardResponse(
        success=True,
        message="User created successfully.",
        data=UserResponse.from_orm(new_user)
    )

@router.delete("/me", response_model=StandardResponse[dict])
@router.post("/me/delete", response_model=StandardResponse[dict])
def delete_my_account(
    del_req: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Self-service account deletion for normal users with password confirmation.
    Permanently deletes user, uploaded paper files, analyses, and history.
    Admin accounts cannot be deleted through self-service.
    """
    if current_user.role == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator accounts cannot be deleted through self-service. Please use the administrative management console."
        )

    # Verify password
    if not verify_password(del_req.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Account deletion cancelled."
        )

    # Delete physical uploaded files on disk
    user_papers = db.query(ResearchPaper).filter(ResearchPaper.user_id == current_user.id).all()
    for p in user_papers:
        if p.file_path:
            try:
                fp = Path(p.file_path)
                if fp.exists() and fp.is_file():
                    fp.unlink(missing_ok=True)
            except Exception as e:
                print(f"Warning deleting paper file {p.file_path}: {e}")

    user_name = current_user.name
    user_email = current_user.email
    user_id = current_user.id

    # Admin In-App Notification: User account deleted
    NotificationService.notify_admins(
        db=db,
        title="User account deleted",
        message=f"User account {user_name} ({user_email}) was deleted from the system.",
        notification_type="admin_user_deleted"
    )

    # Delete user record from database (cascade deletes papers, analyses, history, reset tokens)
    db.delete(current_user)
    db.commit()

    return StandardResponse(
        success=True,
        message="Your account has been deleted successfully.",
        data={"deleted": True, "user_id": user_id, "user_name": user_name}
    )

@router.get("/{id}", response_model=StandardResponse[UserResponse])
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (Admin or own profile)."""
    if current_user.role != "ADMIN" and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    return StandardResponse(
        success=True,
        message="User details retrieved.",
        data=UserResponse.from_orm(user)
    )

@router.put("/{id}", response_model=StandardResponse[UserResponse])
def update_user(
    id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information (Admin or own account)."""
    if current_user.role != "ADMIN" and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    if user_update.name is not None:
        user.name = user_update.name.strip()
        
    if user_update.email is not None and user_update.email.lower() != user.email.lower():
        existing = db.query(User).filter(User.email == user_update.email.lower().strip()).first()
        if existing and existing.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use by another account."
            )
        user.email = user_update.email.lower().strip()

    if user_update.password:
        user.password_hash = get_password_hash(user_update.password)

    # Role and Status changes require ADMIN
    if current_user.role == "ADMIN":
        if user_update.role:
            user.role = user_update.role.upper()
        if user_update.status:
            user.status = user_update.status.lower()

    db.commit()
    db.refresh(user)

    return StandardResponse(
        success=True,
        message="User updated successfully.",
        data=UserResponse.from_orm(user)
    )

@router.patch("/{id}/status", response_model=StandardResponse[UserResponse])
def update_user_status(
    id: int,
    status_in: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Activate or deactivate a user (Admin only)."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )
    
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot deactivate their own account."
        )

    user.status = status_in.status.lower()
    db.commit()
    db.refresh(user)

    return StandardResponse(
        success=True,
        message=f"User status updated to {user.status}.",
        data=UserResponse.from_orm(user)
    )

@router.patch("/{id}/role", response_model=StandardResponse[UserResponse])
def update_user_role(
    id: int,
    role_in: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Change a user's role between ADMIN and USER (Admin only)."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    if user.id == admin.id and role_in.role.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot demote their own account role."
        )

    user.role = role_in.role.upper()
    db.commit()
    db.refresh(user)

    return StandardResponse(
        success=True,
        message=f"User role updated to {user.role}.",
        data=UserResponse.from_orm(user)
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a user account and associated records (Admin only)."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete their own account."
        )

    del_name = user.name
    del_email = user.email

    # Admin In-App Notification: User account deleted
    NotificationService.notify_admins(
        db=db,
        title="User account deleted",
        message=f"User account {del_name} ({del_email}) was deleted by administrator {admin.name}.",
        notification_type="admin_user_deleted"
    )

    db.delete(user)
    db.commit()

    return StandardResponse(
        success=True,
        message=f"User '{del_name}' has been successfully deleted.",
        data={"deleted_user_id": id}
    )

@router.post("/{id}/reset-password", response_model=StandardResponse[dict])
def reset_user_password(
    id: int,
    reset_in: PasswordResetRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin: Reset a user's password securely without exposing any existing credentials."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    user.password_hash = get_password_hash(reset_in.password)
    
    # User In-App Notification: Password changed
    NotificationService.create_user_notification(
        db=db,
        user_id=user.id,
        title="Password changed",
        message="Your ResearchX account password was updated by system administrator.",
        notification_type="password_changed"
    )

    db.commit()

    return StandardResponse(
        success=True,
        message=f"Password for user '{user.name}' has been securely reset.",
        data={"user_id": user.id, "email": user.email}
    )

