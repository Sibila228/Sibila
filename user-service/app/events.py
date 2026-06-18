import json
import os
import uuid

import pika

USER_EXCHANGE = "user.exchange"


def publish_user_created(user_id: uuid.UUID, name: str, email: str) -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.environ["RABBITMQ_HOST"],
            port=int(os.environ.get("RABBITMQ_PORT", 5672)),
            credentials=pika.PlainCredentials(
                os.environ.get("RABBITMQ_USER", "guest"),
                os.environ.get("RABBITMQ_PASSWORD", "guest"),
            ),
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=USER_EXCHANGE, exchange_type="topic", durable=True)

    payload = json.dumps({"id": str(user_id), "name": name, "email": email})
    channel.basic_publish(exchange=USER_EXCHANGE, routing_key="user.created", body=payload)

    connection.close()
