from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

class NotificationType(str, Enum):
    COMMENT = "comment"
    UPDATE = "update"
    MENTION = "mention"

class NotificationPreferenceBase(BaseModel):
    notification_type: NotificationType
    is_enabled: bool

class NotificationPreferenceCreate(NotificationPreferenceBase):
    pass

class NotificationPreferenceUpdate(BaseModel):
    is_enabled: bool
    notification_type: NotificationType

class NotificationPreferenceOut(NotificationPreferenceBase):
    class Config:
        orm_mode = True

class NotificationPreferencesOut(BaseModel):
    preferences: List[NotificationPreferenceOut]

# Add NotificationCreate and NotificationUpdate for Notification model
class NotificationCreate(BaseModel):
    recipient_id: int
    type: NotificationType
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    message: str

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    message: Optional[str] = None