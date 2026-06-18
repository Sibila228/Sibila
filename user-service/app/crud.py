import logging
import uuid

from sqlalchemy.orm import Session

from app import cache, events
from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate

logger = logging.getLogger(__name__)


def create_user(db: Session, data: UserCreate) -> UserOut:
    user = User(name=data.name, email=data.email)
    db.add(user)
    db.commit()
    db.refresh(user)

    events.publish_user_created(user.id, user.name, user.email)
    return UserOut.model_validate(user)


def list_users(db: Session) -> list[UserOut]:
    users = db.query(User).all()
    return [UserOut.model_validate(u) for u in users]


def get_user(db: Session, user_id: uuid.UUID) -> UserOut | None:
    cached = cache.get_from_cache(user_id)
    if cached is not None:
        logger.info("Cache hit for user %s", user_id)
        return cached

    logger.info("Cache miss for user %s", user_id)
    user = db.get(User, user_id)
    if user is None:
        return None

    user_out = UserOut.model_validate(user)
    cache.save_to_cache(user_out)
    return user_out


def update_user(db: Session, user_id: uuid.UUID, data: UserUpdate) -> UserOut | None:
    user = db.get(User, user_id)
    if user is None:
        return None

    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email

    db.commit()
    db.refresh(user)

    cache.remove_from_cache(user_id)
    return UserOut.model_validate(user)


def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    user = db.get(User, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    cache.remove_from_cache(user_id)
    return True
