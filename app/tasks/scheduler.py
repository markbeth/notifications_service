import asyncio
from datetime import datetime, timedelta
from app.db.database import async_session_maker
from app.db.repositories import NotificationRepository
from app.tasks.producer import send_notification
from dateutil.tz import tzutc

REPEAT_DELTAS = {
    'daily': timedelta(days=1),
    'weekly': timedelta(weeks=1),
    'monthly': timedelta(days=30),  # упрощённо
}


async def process_notifications():
    while True:
        async with async_session_maker() as session:
            now = datetime.now(tzutc())
            notifications = await NotificationRepository.select_all_by_filter_get_list(session, send_at=now, is_sent=False)
            for notif in notifications:
                await send_notification(notif.telegram_id, notif.message)
                if notif.repeat in REPEAT_DELTAS:
                    # Обновляем send_at на следующий раз, is_sent остаётся False
                    next_send = notif.send_at + REPEAT_DELTAS[notif.repeat]
                    await NotificationRepository.update_one(session, notif.id, is_sent=True)  # помечаем как отправлен
                    # Сбросить is_sent и обновить send_at для повторяемых
                    notif.is_sent = False
                    notif.send_at = next_send
                    session.add(notif)
                    await session.commit()
                else:
                    await NotificationRepository.update_one(session, notif.id, is_sent=True)
        await asyncio.sleep(30)  # Проверять каждые 30 секунд
