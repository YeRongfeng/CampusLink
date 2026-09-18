from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.common.config import get_settings

settings = get_settings()
database_url = URL.create(
    'mysql+pymysql',
    username=settings.database_user,
    password=settings.database_password.get_secret_value(),
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
    query={'charset': 'utf8mb4'},
)
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={
        'connect_timeout': 3, 'read_timeout': 3, 'write_timeout': 3,
        'init_command': "SET time_zone = '+00:00'",
    },
    hide_parameters=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
