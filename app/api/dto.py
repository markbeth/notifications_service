from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationCreateRequest(BaseModel):
    telegram_id: int
    message: str
    send_at: str  # ISO8601 datetime string
    repeat: str | None = None  # None, 'daily', 'weekly', 'monthly'


class NotificationGetRequest(BaseModel):
    notification_id: int | None = None
    telegram_id: int | None = None
    is_sent: bool | None = None
    limit: int = 100
    offset: int = 0
    repeat: str | None = None
    send_at_from: datetime | None = None
    send_at_to: datetime | None = None
    dt_created_from: datetime | None = None
    dt_created_to: datetime | None = None
    dt_updated_from: datetime | None = None
    dt_updated_to: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
