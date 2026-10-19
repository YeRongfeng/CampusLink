from typing import Annotated, Literal
from decimal import Decimal
from fastapi import APIRouter, Path, Query, Response
from app.auth.dependencies import CurrentUser, DatabaseSession
from app.common.response import ApiResponse, PageData
from app.modules.book import service
from app.modules.book.schemas import BookDetail, BookRelation, BookSummary, BookWrite, FavoriteResult, MineBookItem, SellerContact

router = APIRouter(prefix='/api/books', tags=['books'])
BookId = Annotated[int, Path(gt=0, le=2**63 - 1)]
Page = Annotated[int, Query(ge=1, le=100000)]
PageSize = Annotated[int, Query(ge=1, le=50)]
Money = Annotated[Decimal, Query(ge=0, le=Decimal('9999.99'), decimal_places=2)]


@router.get('', response_model=ApiResponse[PageData[BookSummary]])
def browse(db: DatabaseSession, page: Page = 1, page_size: PageSize = 12,
           keyword: Annotated[str, Query(max_length=120)] = '',
           category: Literal['textbook', 'reference', 'exam', 'literature', 'other'] | None = None,
           condition_grade: Literal['new', 'like_new', 'good', 'worn'] | None = None,
           trade_method: Literal['meetup', 'delivery', 'either'] | None = None,
           price_min: Money | None = None, price_max: Money | None = None,
           negotiable_only: bool = False, available_only: bool = False,
           sort: Literal['latest', 'price_asc', 'price_desc'] = 'latest'):
    return ApiResponse(data=service.list_listings(
        db, page, page_size, keyword=keyword, category=category, condition_grade=condition_grade,
        trade_method=trade_method, price_min=price_min, price_max=price_max,
        negotiable_only=negotiable_only, available_only=available_only, sort=sort))


@router.post('', response_model=ApiResponse[BookDetail])
def create(payload: BookWrite, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.write_listing(db, user.id, payload))


@router.get('/mine', response_model=ApiResponse[PageData[MineBookItem]])
def mine(user: CurrentUser, db: DatabaseSession, response: Response,
         scope: Literal['selling', 'favorites'] = 'selling', page: Page = 1, page_size: PageSize = 12):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.list_listings(db, page, page_size, user_id=user.id, scope=scope))


@router.get('/{book_id}', response_model=ApiResponse[BookDetail])
def get_detail(book_id: BookId, db: DatabaseSession):
    listing = service.get_listing(db, book_id)
    service.touch_view(db, listing)
    return ApiResponse(data=service.detail(db, listing))


@router.put('/{book_id}', response_model=ApiResponse[BookDetail])
def edit(book_id: BookId, payload: BookWrite, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.write_listing(db, user.id, payload, book_id))


@router.get('/{book_id}/relation', response_model=ApiResponse[BookRelation])
def relation(book_id: BookId, user: CurrentUser, db: DatabaseSession, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.relation(db, service.get_listing(db, book_id), user.id))


@router.get('/{book_id}/contact', response_model=ApiResponse[SellerContact])
def contact(book_id: BookId, user: CurrentUser, db: DatabaseSession, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.seller_contact(db, book_id, user.id))


@router.post('/{book_id}/favorite', response_model=ApiResponse[FavoriteResult])
def favorite(book_id: BookId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.toggle_favorite(db, book_id, user.id, True))


@router.delete('/{book_id}/favorite', response_model=ApiResponse[FavoriteResult])
def unfavorite(book_id: BookId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.toggle_favorite(db, book_id, user.id, False))


@router.post('/{book_id}/reserve', response_model=ApiResponse[BookDetail])
def reserve(book_id: BookId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, book_id, user.id, 'reserve'))


@router.post('/{book_id}/unreserve', response_model=ApiResponse[BookDetail])
def unreserve(book_id: BookId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, book_id, user.id, 'unreserve'))


@router.post('/{book_id}/sold', response_model=ApiResponse[BookDetail])
def mark_sold(book_id: BookId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, book_id, user.id, 'sold'))


@router.post('/{book_id}/remove', response_model=ApiResponse[BookDetail])
def remove(book_id: BookId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, book_id, user.id, 'remove'))
