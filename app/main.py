from app.api.router import router as notifications_router
from app.core.logger import logger
from app.db.database import async_session_maker
from app.core.config import settings
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dateutil.tz import tzutc
import uvicorn
from datetime import datetime
from sqlalchemy import text



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_maker() as session:
        await session.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    logger.info(f"API version: {settings.API_VERSION}")
    yield


app = FastAPI(title="api/v1", version=settings.API_VERSION, root_path=settings.ROOT_PATH, lifespan=lifespan)

app.include_router(notifications_router)


@app.get("/health")
async def healthcheck() -> JSONResponse:
    """
    Healthcheck
    """
    try:
        res = {
            "data": "ok",
            "datetime": datetime.now(tz=tzutc()).isoformat(),
            "msg": "ok",
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        msg = f"Unknown Exc: Cannot get healthcheck, {e}"
        logger.error(msg, exc_info=True)
        return JSONResponse(status_code=500, content={"error": msg})


@app.get("/health/db")
async def database_healthcheck() -> JSONResponse:
    """
    Проверка состояния базы данных
    """
    try:
        async with async_session_maker() as session:
            # Проверяем соединение
            await session.execute(text("SELECT 1"))

        res = {
            "data": {
                "status": "connected",
            },
            "datetime": datetime.now(tz=tzutc()).isoformat(),
            "msg": "Database is healthy",
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        msg = f"Database health check failed: {e}"
        logger.error(msg, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": msg,
                "data": {"status": "disconnected"},
                "datetime": datetime.now(tz=tzutc()).isoformat(),
            },
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["token"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
