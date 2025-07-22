import json
import asyncio
import pika

from app.core.logger import logger
from app.core.config import settings
from app.core.tg_bot import bot


async def send_telegram_message(chat_id: int, text: str):
    try:
        await bot.send_message(chat_id, text)
        logger.info(f"Sent message to {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def callback(ch, method, properties, body):
    data = json.loads(body)
    telegram_id = data.get('telegram_id')
    message = data.get('message')

    # Запускаем асинхронную отправку из sync-контекста
    asyncio.run(send_telegram_message(telegram_id, message))
    ch.basic_ack(delivery_tag=method.delivery_tag)


async def consume_notifications():
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URI))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RABBITMQ_QUEUE_NAME, on_message_callback=callback)

    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
