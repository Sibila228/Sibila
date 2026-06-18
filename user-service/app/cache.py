import os
import uuid

import redis

from app.schemas import UserOut

CACHE_PREFIX = "user:v1:"
TTL_SECONDS = 60

_client = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
)


def get_from_cache(user_id: uuid.UUID) -> UserOut | None:
    raw = _client.get(CACHE_PREFIX + str(user_id))
    if raw is None:
        return None
    return UserOut.model_validate_json(raw)


def save_to_cache(user: UserOut) -> None:
    _client.set(CACHE_PREFIX + str(user.id), user.model_dump_json(), ex=TTL_SECONDS)


def remove_from_cache(user_id: uuid.UUID) -> None:
    _client.delete(CACHE_PREFIX + str(user_id))
