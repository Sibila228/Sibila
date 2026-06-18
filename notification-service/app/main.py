import json
import logging
import os
import time

import pika

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("notification-service")

USER_EXCHANGE = "user.exchange"
USER_QUEUE = "user.events"
ROUTING_KEY = "user.#"


def connect() -> pika.BlockingConnection:
    params = pika.ConnectionParameters(
        host=os.environ["RABBITMQ_HOST"],
        port=int(os.environ.get("RABBITMQ_PORT", 5672)),
        credentials=pika.PlainCredentials(
            os.environ.get("RABBITMQ_USER", "guest"),
            os.environ.get("RABBITMQ_PASSWORD", "guest"),
        ),
    )
    while True:
        try:
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError:
            logger.info("RabbitMQ not ready yet, retrying in 3s...")
            time.sleep(3)


def on_message(channel, method, properties, body):
    event = json.loads(body)
    logger.info("Notification: user created -> %s", event)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = connect()
    channel = connection.channel()

    channel.exchange_declare(exchange=USER_EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=USER_QUEUE, durable=True)
    channel.queue_bind(queue=USER_QUEUE, exchange=USER_EXCHANGE, routing_key=ROUTING_KEY)

    channel.basic_consume(queue=USER_QUEUE, on_message_callback=on_message)

    logger.info("Waiting for user events on queue '%s'...", USER_QUEUE)
    channel.start_consuming()


if __name__ == "__main__":
    main()
