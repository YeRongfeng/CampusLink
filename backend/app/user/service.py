from sqlalchemy import select
from sqlalchemy.orm import Session

from app.user.models import User
from app.user.schemas import UserUpdate


def find_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def update_profile(db: Session, user: User, payload: UserUpdate) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
