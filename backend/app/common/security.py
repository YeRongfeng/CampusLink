from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import HTTPException

from app.common.config import get_settings

TOKEN_TTL_SECONDS = 24 * 60 * 60
password_hasher = PasswordHasher()
DUMMY_HASH = password_hasher.hash('not-a-real-user-password')


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def unauthorized() -> HTTPException:
    return HTTPException(401, '登录已失效，请重新登录', headers={'WWW-Authenticate': 'Bearer'})


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {'sub': str(user_id), 'iat': now, 'exp': now + timedelta(seconds=TOKEN_TTL_SECONDS)},
        get_settings().jwt_secret.get_secret_value(), algorithm='HS256',
    )


def decode_user_id(token: str) -> int:
    try:
        payload = jwt.decode(
            token, get_settings().jwt_secret.get_secret_value(), algorithms=['HS256'],
            options={'require': ['sub', 'iat', 'exp']},
        )
        subject = payload['sub']
        if not isinstance(subject, str) or not subject.isascii() or not subject.isdecimal():
            raise ValueError('Invalid subject')
        user_id = int(subject)
        if not 0 < user_id <= 2**63 - 1:
            raise ValueError('Invalid subject')
        return user_id
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise unauthorized() from None
