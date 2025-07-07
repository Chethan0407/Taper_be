from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.crud import notification as crud_notification
from app.schemas.notification import NotificationPreferenceOut, NotificationPreferenceUpdate, NotificationPreferencesOut, NotificationType

router = APIRouter()

@router.get("/", response_model=NotificationPreferencesOut)
def get_notifications(
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
):
    """Get all notification preferences for the current user."""
    prefs = db.query(crud_notification.NotificationPreference) \
        .filter(crud_notification.NotificationPreference.user_id == current_user.id).all()
    # If no preferences exist, return all enabled by default
    if not prefs:
        prefs = [
            crud_notification.NotificationPreference(
                user_id=current_user.id,
                notification_type=nt,
                is_enabled=True
            ) for nt in NotificationType
        ]
    return {"preferences": prefs}

@router.put("/", response_model=NotificationPreferencesOut)
def update_notifications(
    preferences: List[NotificationPreferenceUpdate],
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
):
    """Replace all notification preferences for the current user."""
    # Remove all existing
    db.query(crud_notification.NotificationPreference).filter(
        crud_notification.NotificationPreference.user_id == current_user.id
    ).delete()
    # Add new
    for pref in preferences:
        db_pref = crud_notification.NotificationPreference(
            user_id=current_user.id,
            notification_type=pref.notification_type,
            is_enabled=pref.is_enabled
        )
        db.add(db_pref)
    db.commit()
    new_prefs = db.query(crud_notification.NotificationPreference).filter(
        crud_notification.NotificationPreference.user_id == current_user.id
    ).all()
    return {"preferences": new_prefs}

@router.patch("/", response_model=NotificationPreferencesOut)
def patch_notifications(
    preferences: List[NotificationPreferenceUpdate],
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
):
    """Partially update notification preferences for the current user."""
    for pref in preferences:
        db_pref = db.query(crud_notification.NotificationPreference).filter(
            crud_notification.NotificationPreference.user_id == current_user.id,
            crud_notification.NotificationPreference.notification_type == pref.notification_type
        ).first()
        if db_pref:
            db_pref.is_enabled = pref.is_enabled
        else:
            db_pref = crud_notification.NotificationPreference(
                user_id=current_user.id,
                notification_type=pref.notification_type,
                is_enabled=pref.is_enabled
            )
            db.add(db_pref)
    db.commit()
    updated_prefs = db.query(crud_notification.NotificationPreference).filter(
        crud_notification.NotificationPreference.user_id == current_user.id
    ).all()
    return {"preferences": updated_prefs}