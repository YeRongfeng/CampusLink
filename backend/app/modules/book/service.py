from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from app.modules.book.models import BookFavorite, BookListing
from app.user.models import User

UTC = timezone.utc


def now():
    return datetime.now(UTC).replace(tzinfo=None)


def stamp(value):
    return value.replace(tzinfo=UTC)


def get_listing(db, listing_id, lock=False):
    query = select(BookListing).where(BookListing.id == listing_id)
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    listing = db.scalar(query)
    if listing is None:
        raise HTTPException(404, '书籍不存在或已下架')
    return listing


def person(user):
    return {'id': user.id, 'nickname': user.nickname, 'avatar': user.avatar}


def discount_percent(original, price):
    if original is None or original <= 0:
        return None
    percent = round((1 - float(price) / float(original)) * 100)
    return percent if percent > 0 else None


def summary(listing, seller, favorite_count):
    return dict(id=listing.id, seller=person(seller), title=listing.title, author=listing.author,
                category=listing.category, condition_grade=listing.condition_grade,
                cover_image=listing.cover_images[0], price=f'{listing.price:.2f}',
                original_price=f'{listing.original_price:.2f}' if listing.original_price is not None else None,
                discount_percent=discount_percent(listing.original_price, listing.price),
                is_negotiable=listing.is_negotiable, status=listing.status, trade_method=listing.trade_method,
                favorite_count=favorite_count, view_count=listing.view_count, created_at=stamp(listing.created_at))


def detail(db, listing):
    favorite_count = db.scalar(select(func.count()).select_from(BookFavorite).where(BookFavorite.listing_id == listing.id))
    seller = db.get(User, listing.seller_id)
    return dict(**summary(listing, seller, favorite_count), isbn=listing.isbn, description=listing.description,
                cover_images=listing.cover_images, trade_location=listing.trade_location, updated_at=stamp(listing.updated_at))


def touch_view(db, listing):
    # Atomic increment avoids a lost update under concurrent viewers; no row lock needed for a view counter.
    try:
        db.execute(update(BookListing).where(BookListing.id == listing.id).values(view_count=BookListing.view_count + 1))
        db.commit()
        listing.view_count += 1
    except Exception:
        db.rollback()
        raise


def list_listings(db, page, page_size, user_id=None, scope=None, keyword='', category=None, condition_grade=None,
                   trade_method=None, price_min=None, price_max=None, negotiable_only=False, available_only=False,
                   sort='latest'):
    favorite_counts = select(BookFavorite.listing_id, func.count().label('n')).group_by(BookFavorite.listing_id).subquery()
    query = (select(BookListing, User, func.coalesce(favorite_counts.c.n, 0))
             .join(User, User.id == BookListing.seller_id)
             .outerjoin(favorite_counts, favorite_counts.c.listing_id == BookListing.id))
    favorites_scope = scope == 'favorites'
    if scope == 'selling':
        query = query.where(BookListing.seller_id == user_id)
    elif favorites_scope:
        query = query.join(BookFavorite, BookFavorite.listing_id == BookListing.id).where(
            BookFavorite.user_id == user_id).add_columns(BookFavorite.created_at)
    else:
        query = query.where(BookListing.status.in_(['listed'] if available_only else ['listed', 'reserved']))
        term = keyword.strip()
        if term:
            query = query.where(or_(BookListing.title.contains(term, autoescape=True),
                                     BookListing.author.contains(term, autoescape=True)))
        if category:
            query = query.where(BookListing.category == category)
        if condition_grade:
            query = query.where(BookListing.condition_grade == condition_grade)
        if trade_method:
            query = query.where(BookListing.trade_method == trade_method)
        if price_min is not None:
            query = query.where(BookListing.price >= price_min)
        if price_max is not None:
            query = query.where(BookListing.price <= price_max)
        if negotiable_only:
            query = query.where(BookListing.is_negotiable.is_(True))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    if favorites_scope:
        query = query.order_by(BookFavorite.created_at.desc(), BookListing.id.desc())
    elif scope == 'selling':
        query = query.order_by(BookListing.created_at.desc(), BookListing.id.desc())
    elif sort == 'price_asc':
        query = query.order_by(BookListing.price.asc(), BookListing.id.asc())
    elif sort == 'price_desc':
        query = query.order_by(BookListing.price.desc(), BookListing.id.asc())
    else:
        query = query.order_by(BookListing.created_at.desc(), BookListing.id.desc())
    items = []
    for row in db.execute(query.offset((page - 1) * page_size).limit(page_size)):
        item = summary(row[0], row[1], row[2])
        if favorites_scope:
            item['favorited_at'] = stamp(row[3])
        items.append(item)
    return dict(items=items, total=total, page=page, page_size=page_size)


def relation(db, listing, user_id):
    is_owner = listing.seller_id == user_id
    is_favorited = db.scalar(select(BookFavorite.id).where(
        BookFavorite.listing_id == listing.id, BookFavorite.user_id == user_id)) is not None
    active = listing.status in ('listed', 'reserved')
    return dict(listing_id=listing.id, is_owner=is_owner, is_favorited=is_favorited,
                can_edit=is_owner and listing.status == 'listed',
                can_reserve=is_owner and listing.status == 'listed',
                can_unreserve=is_owner and listing.status == 'reserved',
                can_mark_sold=is_owner and active, can_remove=is_owner and active,
                can_contact=not is_owner and active)


def write_listing(db, user_id, payload, listing_id=None):
    try:
        if listing_id is None:
            listing = BookListing(seller_id=user_id, status='listed', **payload.model_dump())
            db.add(listing)
        else:
            listing = get_listing(db, listing_id, True)
            if listing.seller_id != user_id:
                raise HTTPException(403, '只能编辑自己发布的书籍')
            if listing.status != 'listed':
                raise HTTPException(409, '仅在售状态的书籍可以编辑')
            for key, value in payload.model_dump().items():
                setattr(listing, key, value)
        db.commit()
        db.refresh(listing)
        return detail(db, listing)
    except Exception:
        db.rollback()
        raise


TRANSITIONS = {
    'reserve': (('listed',), 'reserved'),
    'unreserve': (('reserved',), 'listed'),
    'sold': (('listed', 'reserved'), 'sold'),
    'remove': (('listed', 'reserved'), 'removed'),
}


def act(db, listing_id, user_id, action):
    try:
        listing = get_listing(db, listing_id, True)
        if listing.seller_id != user_id:
            raise HTTPException(403, '只能管理自己发布的书籍')
        valid_from, target = TRANSITIONS[action]
        if listing.status != target:
            if listing.status not in valid_from:
                raise HTTPException(409, '当前状态不支持此操作')
            listing.status = target
        db.commit()
        db.refresh(listing)
        return detail(db, listing)
    except Exception:
        db.rollback()
        raise


def toggle_favorite(db, listing_id, user_id, favorite):
    try:
        listing = get_listing(db, listing_id)
        if listing.seller_id == user_id:
            raise HTTPException(403, '不能收藏自己发布的书籍')
        existing = db.scalar(select(BookFavorite).where(
            BookFavorite.listing_id == listing_id, BookFavorite.user_id == user_id))
        if favorite and not existing:
            try:
                db.add(BookFavorite(listing_id=listing_id, user_id=user_id))
                db.commit()
            except IntegrityError:
                db.rollback()  # concurrent favorite already recorded it; treat as success
        elif not favorite and existing:
            db.delete(existing)
            db.commit()
        count = db.scalar(select(func.count()).select_from(BookFavorite).where(BookFavorite.listing_id == listing_id))
        return dict(listing_id=listing_id, is_favorited=favorite, favorite_count=count)
    except Exception:
        db.rollback()
        raise


def seller_contact(db, listing_id, user_id):
    listing = get_listing(db, listing_id)
    is_owner = listing.seller_id == user_id
    if not is_owner and listing.status not in ('listed', 'reserved'):
        raise HTTPException(403, '该书籍已下架或交易完成，无法查看联系方式')
    seller = db.get(User, listing.seller_id)
    return dict(**person(seller), contact_type=listing.contact_type, contact_value=listing.contact_value)
