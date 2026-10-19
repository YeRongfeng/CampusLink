import re
import unicodedata
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.common.config import BACKEND_DIR

UPLOAD_PATTERN = re.compile(r'^/uploads/[0-9a-f]{32}\.(jpg|jpeg|png|webp)$')
Category = Literal['textbook', 'reference', 'exam', 'literature', 'other']
Condition = Literal['new', 'like_new', 'good', 'worn']
TradeMethod = Literal['meetup', 'delivery', 'either']
Status = Literal['listed', 'reserved', 'sold', 'removed']


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


def validate_upload_path(value: str) -> str:
    if not UPLOAD_PATTERN.fullmatch(value):
        raise ValueError('图片必须来自本站上传服务')
    uploads = (BACKEND_DIR / 'uploads').resolve()
    path = (uploads / value.removeprefix('/uploads/')).resolve()
    if path.parent != uploads or not path.is_file():
        raise ValueError('图片文件不存在')
    return value


class Contact(StrictModel):
    contact_type: Literal['wechat', 'qq', 'phone']
    contact_value: str = Field(min_length=3, max_length=64)

    @field_validator('contact_value')
    @classmethod
    def no_control_characters(cls, value):
        if any(unicodedata.category(c).startswith('C') for c in value):
            raise ValueError('联系方式不能包含换行或控制字符')
        return value


class BookWrite(Contact):
    title: str = Field(min_length=1, max_length=120)
    author: str = Field(min_length=1, max_length=80)
    isbn: str | None = Field(default=None, max_length=20)
    category: Category
    condition_grade: Condition
    description: str = Field(min_length=5, max_length=1000)
    cover_images: list[str] = Field(min_length=1, max_length=6)
    original_price: Decimal | None = Field(default=None, ge=0, le=Decimal('9999.99'), decimal_places=2)
    price: Decimal = Field(ge=0, le=Decimal('9999.99'), decimal_places=2)
    is_negotiable: bool = False
    trade_method: TradeMethod
    trade_location: str = Field(min_length=2, max_length=160)

    @field_validator('isbn')
    @classmethod
    def valid_isbn(cls, value):
        if value is not None and not re.fullmatch(r'[0-9Xx-]{10,20}', value):
            raise ValueError('ISBN 格式不正确，请输入数字、X 或连字符')
        return value

    @field_validator('cover_images')
    @classmethod
    def valid_images(cls, value):
        return [validate_upload_path(item) for item in value]

    @model_validator(mode='after')
    def price_not_above_original(self):
        if self.original_price is not None and self.original_price < self.price:
            raise ValueError('原价不能低于现价')
        return self


class PublicPerson(BaseModel):
    id: int
    nickname: str
    avatar: str | None


class BookSummary(BaseModel):
    id: int
    seller: PublicPerson
    title: str
    author: str
    category: Category
    condition_grade: Condition
    cover_image: str
    price: str
    original_price: str | None
    discount_percent: int | None
    is_negotiable: bool
    status: Status
    trade_method: TradeMethod
    favorite_count: int
    view_count: int
    created_at: datetime


class BookDetail(BookSummary):
    isbn: str | None
    description: str
    cover_images: list[str]
    trade_location: str
    updated_at: datetime


class MineBookItem(BookSummary):
    favorited_at: datetime | None = None


class BookRelation(BaseModel):
    listing_id: int
    is_owner: bool
    is_favorited: bool
    can_edit: bool
    can_reserve: bool
    can_unreserve: bool
    can_mark_sold: bool
    can_remove: bool
    can_contact: bool


class SellerContact(PublicPerson, Contact):
    pass


class FavoriteResult(BaseModel):
    listing_id: int
    is_favorited: bool
    favorite_count: int
