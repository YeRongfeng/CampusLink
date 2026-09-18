from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.schemas import Credentials, RegisterRequest, TokenResponse
from app.common.security import DUMMY_HASH, TOKEN_TTL_SECONDS, create_access_token, hash_password, verify_password
from app.user.models import User
from app.user.service import find_by_username


def register(db: Session, payload: RegisterRequest) -> User:
    if find_by_username(db, payload.username):
        raise HTTPException(409, '用户名已被使用')
    user = User(
        username=payload.username, password_hash=hash_password(payload.password),
        nickname=payload.nickname or payload.username,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if getattr(exc.orig, 'args', (None,))[0] == 1062:
            raise HTTPException(409, '用户名已被使用') from None
        raise
    db.refresh(user)
    return user


def login(db: Session, payload: Credentials) -> TokenResponse:
    user = find_by_username(db, payload.username)
    valid = verify_password(payload.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, '用户名或密码错误', headers={'WWW-Authenticate': 'Bearer'})
    return TokenResponse(access_token=create_access_token(user.id), expires_in=TOKEN_TTL_SECONDS)
