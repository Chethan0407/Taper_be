from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Notification, NotificationPreference
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationPreferenceCreate, NotificationPreferenceUpdate

def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False
) -> List[Notification]:
    query = db.query(Notification).filter(Notification.recipient_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_notification(
    db: Session,
    notification_in: NotificationCreate
) -> Notification:
    # Check if user has enabled this notification type
    preference = db.query(NotificationPreference)\
        .filter(
            NotificationPreference.user_id == notification_in.recipient_id,
            NotificationPreference.notification_type == notification_in.type,
            NotificationPreference.is_enabled == True
        ).first()
    
    if not preference:
        return None  # Skip notification if disabled
    
    db_notification = Notification(**notification_in.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def update_notification(
    db: Session,
    notification_id: int,
    notification_in: NotificationUpdate,
    user_id: int
) -> Optional[Notification]:
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Verify recipient
    if db_notification.recipient_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in notification_in.dict().items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notification_preference(
    db: Session,
    user_id: int,
    notification_type: str
) -> Optional[NotificationPreference]:
    return db.query(NotificationPreference)\
        .filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == notification_type
        ).first()

def create_notification_preference(
    db: Session,
    preference_in: NotificationPreferenceCreate
) -> NotificationPreference:
    db_preference = NotificationPreference(**preference_in.dict())
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def update_notification_preference(
    db: Session,
    user_id: int,
    notification_type: str,
    preference_in: NotificationPreferenceUpdate
) -> Optional[NotificationPreference]:
    db_preference = get_notification_preference(db, user_id, notification_type)
    if not db_preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification preference not found"
        )
    
    for field, value in preference_in.dict().items():
        setattr(db_preference, field, value)
    
    db.commit()
    db.refresh(db_preference)
    return db_preference 