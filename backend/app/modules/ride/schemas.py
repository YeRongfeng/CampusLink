from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal
import unicodedata
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Location(StrictModel):
    address: str = Field(default='', max_length=300)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    poi_id: str | None = Field(default=None, max_length=64)
    adcode: str | None = Field(default=None, pattern=r'^\d{6}$')
    source: Literal['poi', 'map', 'geolocation']
    coordinate_system: Literal['gcj02']

    @field_validator('longitude', 'latitude')
    @classmethod
    def round_coordinate(cls, value: float):
        return round(value, 6)


class Contact(StrictModel):
    contact_type: Literal['wechat', 'qq', 'phone']
    contact_value: str = Field(min_length=3, max_length=64)

    @field_validator('contact_value')
    @classmethod
    def no_control_characters(cls, value):
        if any(unicodedata.category(c).startswith('C') for c in value):
            raise ValueError('联系方式不能包含换行或控制字符')
        return value


class RideWrite(Contact):
    origin: str = Field(min_length=2, max_length=80)
    destination: str = Field(min_length=2, max_length=80)
    meeting_point: str = Field(min_length=2, max_length=160)
    origin_location: Location | None = None
    destination_location: Location | None = None
    meeting_location: Location | None = None
    meeting_note: str = Field(default='', max_length=200)
    departure_at: datetime
    recruit_seats: int = Field(ge=1, le=6, strict=True)
    estimated_cost: Decimal | None = Field(default=None, ge=0, le=Decimal('9999.99'), decimal_places=2)
    note: str = Field(default='', max_length=500)

    @field_validator('departure_at')
    @classmethod
    def future_departure(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('出发时间必须包含时区')
        value = value.astimezone(timezone.utc)
        if not datetime.now(timezone.utc) < value <= datetime.now(timezone.utc) + timedelta(days=90):
            raise ValueError('请选择未来 90 天内的出发时间')
        return value

    @model_validator(mode='after')
    def different_endpoints(self):
        a, b = self.origin_location, self.destination_location
        same = (a.longitude, a.latitude) == (b.longitude, b.latitude) if a and b else (
            self.origin.casefold(), a.address.casefold() if a else ''
        ) == (self.destination.casefold(), b.address.casefold() if b else '')
        if same:
            raise ValueError('出发地与目的地不能是同一地点')
        return self


class PublicPerson(BaseModel):
    id: int
    nickname: str
    avatar: str | None


class RideSummary(BaseModel):
    id: int
    owner: PublicPerson
    origin: str
    destination: str
    meeting_point: str
    departure_at: datetime
    recruit_seats: int
    joined_count: int
    remaining_seats: int
    estimated_cost: str | None
    status: Literal['scheduled', 'cancelled', 'completed']
    display_status: Literal['open', 'full', 'departed', 'cancelled', 'completed']
    created_at: datetime
    member_status: Literal['joined', 'withdrawn'] | None = None
    origin_distance_km: float | None = None
    destination_distance_km: float | None = None


class RideDetail(RideSummary):
    origin_location: Location | None
    destination_location: Location | None
    meeting_location: Location | None
    meeting_note: str
    note: str
    updated_at: datetime
    server_time: datetime


class Membership(BaseModel):
    trip_id: int
    role: Literal['owner', 'member', 'visitor']
    member_status: Literal['joined', 'withdrawn'] | None
    can_join: bool
    can_leave: bool
    can_edit: bool
    can_cancel: bool
    can_complete: bool


class PersonContact(PublicPerson, Contact):
    pass


class Contacts(BaseModel):
    owner: PersonContact
    active_members: list[PersonContact] = Field(default_factory=list)
