import re
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.common.config import BACKEND_DIR


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nickname: str
    avatar: str | None
    created_at: datetime
    updated_at: datetime

    @field_validator('created_at', 'updated_at')
    @classmethod
    def utc_timestamp(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nickname: str | None = Field(default=None, min_length=1, max_length=32)
    avatar: str | None = Field(default=None, max_length=255)

    @field_validator('nickname', mode='before')
    @classmethod
    def trim_nickname(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator('avatar')
    @classmethod
    def local_avatar_only(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not re.fullmatch(r'/uploads/[0-9a-f]{32}\.(jpg|jpeg|png|webp)', value):
            raise ValueError('头像必须来自本站上传服务')
        uploads = (BACKEND_DIR / 'uploads').resolve()
        path = (uploads / value.removeprefix('/uploads/')).resolve()
        if path.parent != uploads or not path.is_file():
            raise ValueError('头像文件不存在')
        return value

    @model_validator(mode='after')
    def nickname_cannot_be_null(self):
        if 'nickname' in self.model_fields_set and self.nickname is None:
            raise ValueError('昵称不能为空')
        return self
