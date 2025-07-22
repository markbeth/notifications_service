from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

engine_params = {
    "echo": False,
}

if settings.MODE != "DEV":
    engine_params.update(
        {
            "poolclass": AsyncAdaptedQueuePool,
            "pool_size": 20,  # Maximum number of connections in the pool
            "max_overflow": 10,  # Maximum number of connections that can be created beyond pool_size
            "pool_timeout": 30,  # Seconds to wait before giving up on getting a connection from the pool
            "pool_recycle": 1800,  # Recycle connections after 30 minutes
        }
    )
else:
    engine_params["poolclass"] = NullPool

engine = create_async_engine(settings.DB_URI, **engine_params)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

Base = declarative_base()
