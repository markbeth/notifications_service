from app.core.logger import logger

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


class BaseRepository:
    model = None
    date_now = func.now()

    @classmethod
    async def add_one(cls, session: AsyncSession, **data) -> int:
        try:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            res = await session.execute(query)
            await session.commit()
            new_id = res.scalar()
            return new_id
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot add data"
            logger.error(msg, extra={"data": data}, exc_info=True)

    @classmethod
    async def update_get_id(cls, session: AsyncSession, filter_by: dict, **update_data) -> int:
        try:
            query = update(cls.model).filter_by(**filter_by).values(**update_data).returning(cls.model.id)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot update data"
            logger.error(msg, extra=update_data, exc_info=True)

    @classmethod
    async def delete(cls, session: AsyncSession, id: int) -> None:
        try:
            query = cls.model.__table__.delete().where(cls.model.id == id)
            await session.execute(query)
            await session.commit()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot delete by id"
            extra = {"id": id}
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def select_all_by_filter_get_list(cls, session: AsyncSession, **filter_by) -> list[Any]:
        try:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            rows = result.scalars().all()
            return [{k: v for k, v in row.__dict__.items() if not k.startswith("_")} for row in rows]
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find all"
            logger.error(msg, extra=filter_by, exc_info=True)
