from app.core.logger import logger
from app.api.handlers import get_async_session
from app.api.dto import NotificationCreateRequest, NotificationGetRequest
from app.db.repositories import NotificationRepository
from app.tasks.producer import send_notification

from datetime import datetime
from dateutil.tz import tzutc
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/", response_class=JSONResponse)
async def create_notification(
    req: NotificationCreateRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        send_at = datetime.fromisoformat(req.send_at)
        now = datetime.now(tzutc())
        delay_seconds = max(int((send_at - now).total_seconds()), 0)
        await send_notification(req.telegram_id, req.message, delay_seconds=delay_seconds)
        notification = await NotificationRepository.add_one(session, req.model_dump())
        data = {
            "notification_id": notification.id,
            "delay_seconds": delay_seconds,
        }
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"msg": "ok", "data": data})
    except Exception as e:
        logger.error(f"Error creating notification: {e}, {str(req.model_dump())}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})


@router.get("/", response_class=JSONResponse)
async def get_notifications(
    req: NotificationGetRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        filters = {key: value for key, value in req.model_dump().items() if value is not None}
        notifications = await NotificationRepository.select_all_by_filter_get_list(session, **filters)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "ok", "data": [notification.model_dump() for notification in notifications]})
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})
