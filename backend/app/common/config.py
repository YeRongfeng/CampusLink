from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / '.env', env_file_encoding='utf-8', extra='ignore'
    )

    database_host: str = '127.0.0.1'
    database_port: int = Field(default=3306, ge=1, le=65535)
    database_name: str = 'campuslink'
    database_user: str = 'campuslink'
    database_password: SecretStr
    jwt_secret: SecretStr

    @field_validator('jwt_secret')
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if len(secret) < 32 or secret.lower().startswith(('change', 'replace', 'your_')):
            raise ValueError('JWT_SECRET must be a generated secret of at least 32 characters')
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
