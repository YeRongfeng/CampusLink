from datetime import date
from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, Path, Query, Response
from app.auth.dependencies import CurrentUser, DatabaseSession
from app.common.response import ApiResponse, PageData
from app.modules.ride import service
from app.modules.ride.schemas import Contact, Contacts, Membership, RideDetail, RideSummary, RideWrite

router = APIRouter(prefix='/api/rides', tags=['rides'])
RideId = Annotated[int, Path(gt=0, le=2**63-1)]
Page = Annotated[int, Query(ge=1, le=100000)]
PageSize = Annotated[int, Query(ge=1, le=50)]


@router.get('', response_model=ApiResponse[PageData[RideSummary]])
def browse(db: DatabaseSession, page: Page = 1, page_size: PageSize = 12,
           origin: Annotated[str, Query(max_length=80)] = '', destination: Annotated[str, Query(max_length=80)] = '',
           departure_date: date | None = None, available_only: bool = False,
           origin_lng: Annotated[float | None, Query(ge=-180, le=180, allow_inf_nan=False)] = None,
           origin_lat: Annotated[float | None, Query(ge=-90, le=90, allow_inf_nan=False)] = None,
           destination_lng: Annotated[float | None, Query(ge=-180, le=180, allow_inf_nan=False)] = None,
           destination_lat: Annotated[float | None, Query(ge=-90, le=90, allow_inf_nan=False)] = None,
           radius_km: Annotated[float, Query(ge=0.5, le=20, allow_inf_nan=False)] = 3):
    if (origin_lng is None) != (origin_lat is None) or (destination_lng is None) != (destination_lat is None):
        raise HTTPException(422, '经纬度必须成对提供')
    return ApiResponse(data=service.list_trips(db, page, page_size, origin=origin, destination=destination,
        departure_date=departure_date, available_only=available_only,
        origin_point=(origin_lng, origin_lat) if origin_lng is not None else None,
        destination_point=(destination_lng, destination_lat) if destination_lng is not None else None, radius_km=radius_km))


@router.post('', response_model=ApiResponse[RideDetail])
def create(payload: RideWrite, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.write_trip(db, user.id, payload))


@router.get('/mine', response_model=ApiResponse[PageData[RideSummary]])
def mine(user: CurrentUser, db: DatabaseSession, response: Response, scope: Literal['published', 'participating'] = 'published', page: Page = 1, page_size: PageSize = 12):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.list_trips(db, page, page_size, user_id=user.id, scope=scope))


@router.get('/{ride_id}', response_model=ApiResponse[RideDetail])
def get_detail(ride_id: RideId, db: DatabaseSession):
    return ApiResponse(data=service.detail(db, service.get_trip(db, ride_id)))


@router.put('/{ride_id}', response_model=ApiResponse[RideDetail])
def edit(ride_id: RideId, payload: RideWrite, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.write_trip(db, user.id, payload, ride_id))


@router.get('/{ride_id}/membership', response_model=ApiResponse[Membership])
def membership(ride_id: RideId, user: CurrentUser, db: DatabaseSession, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.membership(service.get_trip(db, ride_id), service.members(db, ride_id), user.id))


@router.get('/{ride_id}/contacts', response_model=ApiResponse[Contacts])
def contacts(ride_id: RideId, user: CurrentUser, db: DatabaseSession, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.contacts(db, ride_id, user.id))


@router.post('/{ride_id}/join', response_model=ApiResponse[Membership])
def join(ride_id: RideId, payload: Contact, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, ride_id, user.id, 'join', payload))


@router.post('/{ride_id}/leave', response_model=ApiResponse[Membership])
def leave(ride_id: RideId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, ride_id, user.id, 'leave'))


@router.post('/{ride_id}/cancel', response_model=ApiResponse[RideDetail])
def cancel(ride_id: RideId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, ride_id, user.id, 'cancel'))


@router.post('/{ride_id}/complete', response_model=ApiResponse[RideDetail])
def complete(ride_id: RideId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, ride_id, user.id, 'complete'))
