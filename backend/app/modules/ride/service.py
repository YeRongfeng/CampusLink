from datetime import datetime, time, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import func, select
from app.modules.ride.models import RideMember, RideTrip
from app.user.models import User

UTC = timezone.utc
CHINA = timezone(timedelta(hours=8))


def now():
    return datetime.now(UTC).replace(tzinfo=None)


def stamp(value):
    return value.replace(tzinfo=UTC)


def get_trip(db, trip_id, lock=False):
    query = select(RideTrip).where(RideTrip.id == trip_id)
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    trip = db.scalar(query)
    if trip is None:
        raise HTTPException(404, '行程不存在')
    return trip


def members(db, trip_id, lock=False):
    query = select(RideMember).where(RideMember.trip_id == trip_id)
    if lock:
        # Current reads avoid an authentication SELECT's earlier MySQL snapshot.
        query = query.with_for_update().execution_options(populate_existing=True)
    return list(db.scalars(query))


def person(user):
    return {'id': user.id, 'nickname': user.nickname, 'avatar': user.avatar}


def summary(trip, owner, count):
    display = trip.status if trip.status != 'scheduled' else (
        'departed' if trip.departure_at <= now() else 'full' if count >= trip.recruit_seats else 'open'
    )
    return dict(id=trip.id, owner=person(owner), origin=trip.origin, destination=trip.destination,
                meeting_point=trip.meeting_point, departure_at=stamp(trip.departure_at),
                recruit_seats=trip.recruit_seats, joined_count=count,
                remaining_seats=max(0, trip.recruit_seats-count),
                estimated_cost=f'{trip.estimated_cost:.2f}' if trip.estimated_cost is not None else None,
                status=trip.status, display_status=display, created_at=stamp(trip.created_at))


def detail(db, trip):
    count = db.scalar(select(func.count()).select_from(RideMember).where(
        RideMember.trip_id == trip.id, RideMember.status == 'joined'))
    return dict(**summary(trip, db.get(User, trip.owner_id), count),
                origin_location=trip.origin_location, destination_location=trip.destination_location,
                meeting_location=trip.meeting_location, meeting_note=trip.meeting_note,
                note=trip.note, updated_at=stamp(trip.updated_at), server_time=datetime.now(UTC))


def distance_km(location, point):
    # Haversine on the same GCJ-02 coordinate system; clamp roundoff at endpoints.
    lng, lat = location['longitude'].as_float(), location['latitude'].as_float()
    a = func.pow(func.sin(func.radians(lat - point[1]) / 2), 2) + func.cos(func.radians(lat)) * func.cos(func.radians(point[1])) * func.pow(func.sin(func.radians(lng - point[0]) / 2), 2)
    return 12742 * func.asin(func.sqrt(func.least(1, func.greatest(0, a))))


def list_trips(db, page, page_size, user_id=None, scope=None, origin='', destination='', departure_date=None, available_only=False,
               origin_point=None, destination_point=None, radius_km=3):
    distances = {}
    counts = select(RideMember.trip_id, func.count().label('n')).where(
        RideMember.status == 'joined').group_by(RideMember.trip_id).subquery()
    query = select(RideTrip, User, func.coalesce(counts.c.n, 0)).join(User, User.id == RideTrip.owner_id).outerjoin(counts, counts.c.trip_id == RideTrip.id)
    if scope == 'published':
        query = query.where(RideTrip.owner_id == user_id)
    elif scope == 'participating':
        query = query.join(RideMember, RideMember.trip_id == RideTrip.id).where(RideMember.user_id == user_id).add_columns(RideMember.status)
    else:
        query = query.where(RideTrip.status == 'scheduled', RideTrip.departure_at > now())
        for endpoint, name, point in [('origin', origin, origin_point), ('destination', destination, destination_point)]:
            if point is not None:
                location = getattr(RideTrip, endpoint + '_location')
                distance = distance_km(location, point)
                distances[endpoint] = distance
                query = query.where(location.is_not(None), distance <= radius_km).add_columns(distance.label(endpoint + '_distance_km'))
            elif name.strip():
                query = query.where(getattr(RideTrip, endpoint).contains(name.strip(), autoescape=True))
        if departure_date:
            start = datetime.combine(departure_date, time(), CHINA).astimezone(UTC).replace(tzinfo=None)
            query = query.where(RideTrip.departure_at >= start, RideTrip.departure_at < start + timedelta(days=1))
        if available_only:
            query = query.where(func.coalesce(counts.c.n, 0) < RideTrip.recruit_seats)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.order_by(RideTrip.created_at.desc(), RideTrip.id.desc()) if scope else query.order_by(RideTrip.departure_at, RideTrip.id)
    items = []
    for row in db.execute(query.offset((page-1)*page_size).limit(page_size)):
        item = summary(row[0], row[1], row[2])
        item['member_status'] = row[3] if scope == 'participating' else None
        for endpoint in distances:
            item[endpoint + '_distance_km'] = round(float(row._mapping[endpoint + '_distance_km']), 2)
        items.append(item)
    return dict(items=items, total=total, page=page, page_size=page_size)


def membership(trip, rows, user_id):
    mine = next((r for r in rows if r.user_id == user_id), None)
    joined = mine is not None and mine.status == 'joined'
    owner = trip.owner_id == user_id
    active = trip.status == 'scheduled' and trip.departure_at > now()
    count = sum(r.status == 'joined' for r in rows)
    return dict(trip_id=trip.id, role='owner' if owner else 'member' if joined else 'visitor',
                member_status=mine.status if mine else None,
                can_join=active and not owner and not joined and count < trip.recruit_seats,
                can_leave=active and joined, can_edit=active and owner and count == 0,
                can_cancel=active and owner,
                can_complete=owner and trip.status == 'scheduled' and trip.departure_at <= now())


def payload_values(payload):
    values = payload.model_dump()
    values['departure_at'] = payload.departure_at.astimezone(UTC).replace(tzinfo=None)
    return values


def write_trip(db, user_id, payload, trip_id=None):
    try:
        if trip_id is None:
            trip = RideTrip(owner_id=user_id, **payload_values(payload))
            db.add(trip)
        else:
            trip = get_trip(db, trip_id, True)
            if trip.owner_id != user_id:
                raise HTTPException(403, '只能编辑自己发布的行程')
            if not membership(trip, members(db, trip.id, True), user_id)['can_edit']:
                raise HTTPException(409, '仅未出发且无人加入的行程可以编辑')
            for key, value in payload_values(payload).items():
                setattr(trip, key, value)
        if trip.departure_at <= now():
            raise HTTPException(409, '出发时间已过，请重新选择')
        db.commit()
        db.refresh(trip)
        return detail(db, trip)
    except Exception:
        db.rollback()
        raise


def act(db, trip_id, user_id, action, contact=None):
    try:
        trip = get_trip(db, trip_id, True)
        rows = members(db, trip_id, True)
        permissions = membership(trip, rows, user_id)
        mine = next((r for r in rows if r.user_id == user_id), None)
        if action in ('cancel', 'complete'):
            if trip.owner_id != user_id:
                raise HTTPException(403, '只能管理自己发布的行程')
            target = 'cancelled' if action == 'cancel' else 'completed'
            if trip.status != target:
                if not permissions['can_' + action]:
                    raise HTTPException(409, '当前行程状态不允许此操作')
                trip.status = target
        elif action == 'join':
            if trip.owner_id == user_id:
                raise HTTPException(403, '发起人无需加入自己的行程')
            if trip.status != 'scheduled' or trip.departure_at <= now():
                raise HTTPException(409, '该行程已结束报名')
            if not mine or mine.status != 'joined':
                if not permissions['can_join']:
                    raise HTTPException(409, '行程已满员，请选择其他行程')
                if mine:
                    mine.status = 'joined'
                    mine.contact_type, mine.contact_value = contact.contact_type, contact.contact_value
                else:
                    db.add(RideMember(trip_id=trip_id, user_id=user_id, **contact.model_dump()))
        elif action == 'leave':
            if not mine:
                raise HTTPException(409, '你尚未加入此行程')
            if mine.status != 'withdrawn':
                if not permissions['can_leave']:
                    raise HTTPException(409, '出发后或行程结束后不能退出')
                mine.status = 'withdrawn'
        db.commit()
        db.refresh(trip)
        return detail(db, trip) if action in ('cancel', 'complete') else membership(trip, members(db, trip_id), user_id)
    except Exception:
        db.rollback()
        raise


def contacts(db, trip_id, user_id):
    trip = get_trip(db, trip_id, True)
    rows = members(db, trip_id, True)
    role = membership(trip, rows, user_id)['role']
    if trip.status == 'cancelled' or role == 'visitor':
        raise HTTPException(403, '当前无法查看行程联系方式')
    result = dict(owner=dict(**person(db.get(User, trip.owner_id)), contact_type=trip.contact_type, contact_value=trip.contact_value), active_members=[])
    if role == 'owner':
        active = [m for m in rows if m.status == 'joined']
        users = {u.id: u for u in db.scalars(select(User).where(User.id.in_([m.user_id for m in active])))}
        result['active_members'] = [dict(**person(users[m.user_id]), contact_type=m.contact_type, contact_value=m.contact_value) for m in active]
    return result
