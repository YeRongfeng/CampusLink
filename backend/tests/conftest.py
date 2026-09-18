import os
import re
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session

# The application engine never points at the development database in this process.
os.environ['DATABASE_HOST'] = '127.0.0.1'
os.environ['DATABASE_PORT'] = '1'
os.environ['DATABASE_NAME'] = 'unused_test'
os.environ['DATABASE_USER'] = 'unused_test'
os.environ['DATABASE_PASSWORD'] = 'test-only-password'
os.environ['JWT_SECRET'] = 'test-only-secret-with-at-least-64-characters-for-authentication-tests'

from app.common.database import get_db
from app.main import app

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope='session')
def test_engine():
    config = {**dotenv_values(ROOT / 'backend/.env.test'), **os.environ}
    name = config.get('TEST_DATABASE_NAME', '')
    if not re.fullmatch(r'[a-zA-Z0-9_]+_test', name):
        pytest.fail('Set TEST_DATABASE_NAME to a dedicated database ending in _test. See README.')
    if not config.get('TEST_DATABASE_USER') or not config.get('TEST_DATABASE_PASSWORD'):
        pytest.fail('Separate TEST_DATABASE_USER and TEST_DATABASE_PASSWORD are required.')
    engine = create_engine(URL.create(
        'mysql+pymysql', username=config['TEST_DATABASE_USER'], password=config['TEST_DATABASE_PASSWORD'],
        host=config.get('TEST_DATABASE_HOST', '127.0.0.1'), port=int(config.get('TEST_DATABASE_PORT', '3306')),
        database=name, query={'charset': 'utf8mb4'},
    ), connect_args={'connect_timeout': 3, 'init_command': "SET time_zone = '+00:00'"}, hide_parameters=True)
    try:
        with engine.begin() as conn:
            assert conn.scalar(text('SELECT DATABASE()')) == name
            sql = (ROOT / 'database/init.sql').read_text(encoding='utf-8')
            sql = '\n'.join(line for line in sql.splitlines() if not line.lstrip().startswith('--'))
            for statement in sql.split(';'):
                # Never execute CREATE DATABASE or USE campuslink from the application SQL.
                if statement.strip().upper().startswith('CREATE TABLE'):
                    conn.execute(text(statement))
    except Exception as exc:
        engine.dispose()
        pytest.fail(f'Test database initialization failed ({type(exc).__name__}); check .env.test and MySQL.')
    yield engine
    engine.dispose()


@pytest.fixture
def db(test_engine):
    with test_engine.connect() as conn:
        transaction = conn.begin()
        with Session(bind=conn, join_transaction_mode='create_savepoint', expire_on_commit=False) as session:
            yield session
        transaction.rollback()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
