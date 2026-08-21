import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.notification import InAppNotification

logger = logging.getLogger("researchx.notifications")

class NotificationService:
    @staticmethod
    def create_user_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "general"
    ) -> Optional[InAppNotification]:
        """Create an in-app notification for a specific user."""
        try:
            notif = InAppNotification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.add(notif)
            db.commit()
            db.refresh(notif)
            logger.info(f"[NOTIFICATION CREATED] User {user_id}: '{title}' (Type: {notification_type})")
            return notif
        except Exception as e:
            db.rollback()
            logger.error(f"[NOTIFICATION ERROR] Failed to create notification for user {user_id}: {e}")
            return None

    @staticmethod
    def notify_admins(
        db: Session,
        title: str,
        message: str,
        notification_type: str = "admin"
    ) -> List[InAppNotification]:
        """Create an in-app notification for all active administrator accounts in SQLite."""
        created_notifs = []
        try:
            admins = db.query(User).filter(User.role == "ADMIN", User.status == "active").all()
            for admin in admins:
                notif = InAppNotification(
                    user_id=admin.id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    is_read=False,
                    created_at=datetime.utcnow()
                )
                db.add(notif)
                created_notifs.append(notif)
            if created_notifs:
                db.commit()
                logger.info(f"[ADMIN NOTIFICATION DISPATCHED] '{title}' sent to {len(created_notifs)} admin accounts.")
        except Exception as e:
            db.rollback()
            logger.error(f"[ADMIN NOTIFICATION ERROR] Failed to notify administrators: {e}")
        return created_notifs

    @staticmethod
    def get_user_notifications(
        db: Session,
        user: User,
        unread_only: bool = False,
        limit: int = 50
    ) -> dict:
        """
        Retrieve notifications for the authenticated user.
        Users only see their own notifications.
        Admins only see their own notifications (which include admin-dispatched alerts).
        """
        query = db.query(InAppNotification).filter(InAppNotification.user_id == user.id)
        
        unread_count = query.filter(InAppNotification.is_read == False).count()
        
        if unread_only:
            query = query.filter(InAppNotification.is_read == False)
            
        notifications = query.order_by(InAppNotification.created_at.desc()).limit(limit).all()
        total = db.query(InAppNotification).filter(InAppNotification.user_id == user.id).count()

        return {
            "items": notifications,
            "unread_count": unread_count,
            "total": total
        }

    @staticmethod
    def mark_as_read(db: Session, user: User, notification_id: int) -> bool:
        """Mark a specific notification as read."""
        notif = db.query(InAppNotification).filter(
            InAppNotification.id == notification_id,
            InAppNotification.user_id == user.id
        ).first()
        if not notif:
            return False
        notif.is_read = True
        db.commit()
        return True

    @staticmethod
    def mark_all_as_read(db: Session, user: User) -> int:
        """Mark all unread notifications for the user as read."""
        unread_notifs = db.query(InAppNotification).filter(
            InAppNotification.user_id == user.id,
            InAppNotification.is_read == False
        ).all()
        for notif in unread_notifs:
            notif.is_read = True
        count = len(unread_notifs)
        if count > 0:
            db.commit()
        return count

    @staticmethod
    def delete_notification(db: Session, user: User, notification_id: int) -> bool:
        """Delete a single notification owned by the user."""
        notif = db.query(InAppNotification).filter(
            InAppNotification.id == notification_id,
            InAppNotification.user_id == user.id
        ).first()
        if not notif:
            return False
        db.delete(notif)
        db.commit()
        return True

    @staticmethod
    def clear_all_notifications(db: Session, user: User) -> int:
        """Clear all notifications for the user."""
        notifs = db.query(InAppNotification).filter(InAppNotification.user_id == user.id).all()
        count = len(notifs)
        for notif in notifs:
            db.delete(notif)
        if count > 0:
            db.commit()
        return count
