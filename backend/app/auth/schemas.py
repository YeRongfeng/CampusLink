import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Credentials(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128, repr=False)

    @field_validator('username', mode='before')
    @classmethod
    def normalize_username(cls, value):
        if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_]{3,32}', value):
            raise ValueError('用户名需为 3–32 位字母、数字或下划线')
        return value.lower()


class RegisterRequest(Credentials):
    nickname: str | None = Field(default=None, min_length=1, max_length=32)

    @field_validator('nickname', mode='before')
    @classmethod
    def trim_nickname(cls, value):
        return value.strip() if isinstance(value, str) else value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int
