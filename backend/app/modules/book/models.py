from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Index, Integer, JSON, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from app.common.database import Base


class BookListing(Base):
    __tablename__ = 'book_listing'
    __table_args__ = (
        CheckConstraint("category IN ('textbook','reference','exam','literature','other')", name='ck_book_category'),
        CheckConstraint("condition_grade IN ('new','like_new','good','worn')", name='ck_book_condition'),
        CheckConstraint('price BETWEEN 0 AND 9999.99', name='ck_book_price'),
        CheckConstraint('original_price IS NULL OR original_price BETWEEN 0 AND 9999.99', name='ck_book_original_price'),
        CheckConstraint('original_price IS NULL OR original_price >= price', name='ck_book_discount'),
        CheckConstraint("trade_method IN ('meetup','delivery','either')", name='ck_book_trade_method'),
        CheckConstraint("status IN ('listed','reserved','sold','removed')", name='ck_book_status'),
        Index('ix_book_browse', 'status', 'category', 'created_at', 'id'),
        Index('ix_book_seller', 'seller_id', 'created_at', 'id'),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='RESTRICT'))
    title: Mapped[str] = mapped_column(String(120))
    author: Mapped[str] = mapped_column(String(80))
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    category: Mapped[str] = mapped_column(String(16))
    condition_grade: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(String(1000))
    cover_images: Mapped[list] = mapped_column(JSON)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    is_negotiable: Mapped[bool] = mapped_column(Boolean, default=False)
    trade_method: Mapped[str] = mapped_column(String(16))
    trade_location: Mapped[str] = mapped_column(String(160))
    contact_type: Mapped[str] = mapped_column(String(16))
    contact_value: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default='listed')
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'))


class BookFavorite(Base):
    __tablename__ = 'book_favorite'
    __table_args__ = (
        UniqueConstraint('listing_id', 'user_id', name='uq_book_favorite'),
        Index('ix_book_favorite_user', 'user_id', 'created_at', 'id'),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey('book_listing.id', ondelete='RESTRICT'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='RESTRICT'))
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6)'))
