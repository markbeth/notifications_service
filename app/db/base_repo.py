from app.core.logger import logger

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update, func, text
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
    async def add_get_obj(cls, session: AsyncSession, **data) -> Any:
        try:
            query = insert(cls.model).values(**data).returning(cls.model)
            new_obj = await session.execute(query)
            await session.commit()
            return new_obj.scalar()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot add and return row"
            logger.error(msg, extra=data, exc_info=True)

    @classmethod
    async def add_bulk(cls, session: AsyncSession, data: list[dict]) -> None:
        try:
            query = insert(cls.model).values(data)
            await session.execute(query)
            await session.commit()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot add data"
            logger.error(msg, extra=data, exc_info=True)

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
    async def update_get_obj(cls, session: AsyncSession, filter_by: dict, **update_data) -> Any:
        try:
            query = update(cls.model).filter_by(**filter_by).values(**update_data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot update and return data"
            logger.error(msg, extra={"update_data": update_data}, exc_info=True)

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
    async def select_by_id_get_obj(cls, session: AsyncSession, model_id: int) -> Any:
        try:
            query = select(cls.model).filter(cls.model.id == model_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Databse "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find by id"
            extra = {"model_id": model_id}
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def select_by_filter_get_obj(cls, session: AsyncSession, **filter_by) -> Any:
        try:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot find one or none"
            logger.error(msg, extra=filter_by, exc_info=True)

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

    @classmethod
    async def get_version(cls, session: AsyncSession, object_id: int) -> int:
        try:
            query = text(
                f"SELECT version FROM version WHERE object_id = {object_id} and table_reference = '{cls.model.__tablename__}' ORDER BY version DESC LIMIT 1"
            )
            result = await session.execute(query)
            version = result.scalar_one_or_none()
            if not version:
                raise ValueError(f"Version for object {object_id} not found")
            return version
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot get version"
            extra = {"object_id": object_id}
            logger.error(msg, extra=extra, exc_info=True)
            return None

    @classmethod
    async def update_version(cls, session: AsyncSession, object_id: int) -> bool:
        try:
            query = text(
                f"UPDATE version SET version = version + 1 WHERE object_id = {object_id} and table_reference = '{cls.model.__tablename__}'"
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0
        except (SQLAlchemyError, Exception) as e:
            await session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database "
            elif isinstance(e, Exception):
                msg = "Unknown "
            msg += "Exc: Cannot update version"
            extra = {"object_id": object_id}
            logger.error(msg, extra=extra, exc_info=True)
            return None
