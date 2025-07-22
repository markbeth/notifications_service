from aiogram import Bot

from app.core.config import settings


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
