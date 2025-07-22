from app.db.base_repo import BaseRepository
from app.db.models import Notification


class NotificationRepository(BaseRepository):
    model = Notification
