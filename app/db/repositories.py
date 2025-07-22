from app.core.logger import logger
from app.db.base_repo import BaseRepository
from app.db.models import Notification

from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationRepository(BaseRepository):
    model = Notification

    @classmethod
    async def add_one(cls, session: AsyncSession, **data) -> int | None:
        try:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            res = await session.execute(query)
            await session.commit()
            new_id = res.scalar()
            return new_id
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            logger.error(f"Cannot add notification: {e}", extra={"data": data}, exc_info=True)
            return None

    @classmethod
    async def select_all_by_filter_get_list(cls, session: AsyncSession, **filters) -> list[Notification]:
        try:
            query = select(cls.model).where(**filters)
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Cannot get notifications: {e}", exc_info=True)
            return []

    @classmethod
    async def update_one(cls, session: AsyncSession, notification_id: int, **data) -> bool:
        try:
            query = (
                update(cls.model)
                .where(cls.model.id == notification_id)
                .values(**data)
            )
            await session.execute(query)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Cannot update notification: {e}", exc_info=True)
            return False
