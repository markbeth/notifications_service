import pika
import json

from app.core.config import settings
from app.core.logger import logger


async def send_notification(telegram_id: int, message: str, delay_seconds: int = 0):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URI))
    channel = connection.channel()
    channel.exchange_declare(
        exchange='delayed',
        exchange_type='x-delayed-message',
        arguments={'x-delayed-type': 'direct'}
    )
    durable = settings.MODE == "PROD"
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=durable)
    channel.queue_bind(exchange='delayed', queue=settings.RABBITMQ_QUEUE_NAME, routing_key=settings.RABBITMQ_QUEUE_NAME)

    payload = {
        'telegram_id': telegram_id,
        'message': message,
        'type': 'telegram'
    }
    delay_ms = delay_seconds * 1000
    channel.basic_publish(
        exchange='delayed',
        routing_key=settings.RABBITMQ_QUEUE_NAME,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            headers={'x-delay': delay_ms},
            delivery_mode=2  # make message persistent
        )
    )
    logger.info(f"Sent notification to user {telegram_id} with delay {delay_seconds}s")
    connection.close()
