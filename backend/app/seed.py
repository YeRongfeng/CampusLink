"""Explicitly create development accounts without overwriting existing users."""
from app.auth.schemas import RegisterRequest
from app.auth.service import register
from app.common.database import SessionLocal
from app.user.service import find_by_username


def main():
    with SessionLocal() as db:
        for name in ('user01', 'user02', 'user03'):
            if find_by_username(db, name):
                print(f'{name}: already exists, unchanged')
                continue
            register(db, RegisterRequest(username=name, password='CampusLink123!', nickname=name))
            print(f'{name}: created')


if __name__ == '__main__':
    main()
