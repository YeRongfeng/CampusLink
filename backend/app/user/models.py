from datetime import datetime

from sqlalchemy import BigInteger, String, text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column

from app.common.database import Base


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_0900_ai_ci'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32, collation='utf8mb4_bin'), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(32))
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'),
    )
