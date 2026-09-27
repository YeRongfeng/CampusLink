from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, JSON, Numeric, SmallInteger, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from app.common.database import Base


class RideTrip(Base):
    __tablename__ = 'ride_trip'
    __table_args__ = (
        CheckConstraint('recruit_seats BETWEEN 1 AND 6', name='ck_ride_seats'),
        CheckConstraint("status IN ('scheduled','cancelled','completed')", name='ck_ride_status'),
        CheckConstraint('estimated_cost IS NULL OR estimated_cost BETWEEN 0 AND 9999.99', name='ck_ride_cost'),
        Index('ix_ride_departure', 'status', 'departure_at', 'id'),
        Index('ix_ride_owner', 'owner_id', 'created_at', 'id'),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='RESTRICT'))
    origin: Mapped[str] = mapped_column(String(80))
    destination: Mapped[str] = mapped_column(String(80))
    meeting_point: Mapped[str] = mapped_column(String(160))
    origin_location: Mapped[dict | None] = mapped_column(JSON(none_as_null=True), nullable=True)
    destination_location: Mapped[dict | None] = mapped_column(JSON(none_as_null=True), nullable=True)
    meeting_location: Mapped[dict | None] = mapped_column(JSON(none_as_null=True), nullable=True)
    meeting_note: Mapped[str] = mapped_column(String(200), default='')
    departure_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6))
    recruit_seats: Mapped[int] = mapped_column(SmallInteger)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    contact_type: Mapped[str] = mapped_column(String(16))
    contact_value: Mapped[str] = mapped_column(String(64))
    note: Mapped[str] = mapped_column(String(500), default='')
    status: Mapped[str] = mapped_column(String(16), default='scheduled')
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'))


class RideMember(Base):
    __tablename__ = 'ride_member'
    __table_args__ = (
        UniqueConstraint('trip_id', 'user_id', name='uq_ride_member'),
        CheckConstraint("status IN ('joined','withdrawn')", name='ck_ride_member_status'),
        Index('ix_ride_members', 'trip_id', 'status'),
        Index('ix_ride_member_user', 'user_id', 'created_at', 'id'),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey('ride_trip.id', ondelete='RESTRICT'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='RESTRICT'))
    status: Mapped[str] = mapped_column(String(16), default='joined')
    contact_type: Mapped[str] = mapped_column(String(16))
    contact_value: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6)'))
    updated_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), server_default=text('CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'))
