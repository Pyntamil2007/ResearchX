from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse, NotificationListResponse
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/notifications", tags=["In-App Notifications"])

@router.get("", response_model=StandardResponse[NotificationListResponse])
def get_my_notifications(
    unread_only: bool = Query(False, description="Filter to unread notifications only"),
    limit: int = Query(50, ge=1, le=100, description="Max notifications to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve in-app notifications for the authenticated user.
    Standard users see only their own notifications.
    Admins see their own administrator alerts and notifications.
    """
    data = NotificationService.get_user_notifications(
        db=db,
        user=current_user,
        unread_only=unread_only,
        limit=limit
    )
    
    items = [NotificationResponse.from_orm(n) for n in data["items"]]
    
    return StandardResponse(
        success=True,
        message="Notifications retrieved successfully.",
        data=NotificationListResponse(
            items=items,
            unread_count=data["unread_count"],
            total=data["total"]
        )
    )

@router.patch("/{id}/read", response_model=StandardResponse[dict])
def mark_notification_as_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an individual notification as read."""
    success = NotificationService.mark_as_read(db=db, user=current_user, notification_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or access denied."
        )
    return StandardResponse(
        success=True,
        message="Notification marked as read.",
        data={"id": id, "is_read": True}
    )

@router.patch("/read-all", response_model=StandardResponse[dict])
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all unread notifications for the authenticated user as read."""
    count = NotificationService.mark_all_as_read(db=db, user=current_user)
    return StandardResponse(
        success=True,
        message=f"{count} notification(s) marked as read.",
        data={"marked_count": count}
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_single_notification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an individual notification."""
    success = NotificationService.delete_notification(db=db, user=current_user, notification_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or access denied."
        )
    return StandardResponse(
        success=True,
        message="Notification deleted successfully.",
        data={"id": id, "deleted": True}
    )

@router.delete("", response_model=StandardResponse[dict])
def clear_all_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear/delete all notifications for the authenticated user."""
    count = NotificationService.clear_all_notifications(db=db, user=current_user)
    return StandardResponse(
        success=True,
        message=f"All {count} notification(s) cleared.",
        data={"cleared_count": count}
    )
