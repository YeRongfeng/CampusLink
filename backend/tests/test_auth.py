from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.common.config import get_settings
from app.common.exceptions import register_exception_handlers
from app.common.security import verify_password
from app.user.models import User

PASSWORD = 'CampusLinkTest123!'


def credentials():
    return {'username': 't_' + uuid4().hex[:20], 'password': PASSWORD}


def signed_in(client):
    body = credentials()
    user = client.post('/api/auth/register', json=body).json()['data']
    response = client.post('/api/auth/login', json=body)
    assert response.status_code == 200
    result = response.json()['data']
    assert result['token_type'] == 'bearer'
    assert result['expires_in'] == 86400
    return user, {'Authorization': 'Bearer ' + result['access_token']}, body


def test_registration_normalizes_and_hashes(client, db):
    body = credentials()
    body['username'] = body['username'].upper()
    response = client.post('/api/auth/register', json=body)
    assert response.status_code == 200
    user = response.json()['data']
    assert user['username'] == body['username'].lower()
    assert user['nickname'] == user['username']
    assert user['avatar'] is None
    assert user['created_at'].endswith('Z')
    assert set(user) == {'id', 'username', 'nickname', 'avatar', 'created_at', 'updated_at'}
    stored = db.get(User, user['id'])
    assert stored.password_hash.startswith('$argon2id$')
    assert verify_password(PASSWORD, stored.password_hash)
    assert PASSWORD not in response.text
    body['username'] = body['username'].lower()
    duplicate = client.post('/api/auth/register', json=body)
    assert duplicate.status_code == 409
    assert duplicate.json()['data'] is None


@pytest.mark.parametrize('change', [
    {'username': 'ab'}, {'username': 'x' * 33}, {'username': 'hello-world'},
    {'username': '校园同学'}, {'password': 'short'}, {'password': 'x' * 129},
    {'nickname': ''}, {'nickname': '   '}, {'nickname': '中' * 33}, {'admin': True},
])
def test_invalid_registration(client, change):
    response = client.post('/api/auth/register', json={**credentials(), **change})
    assert response.status_code == 422
    assert response.json()['data'] is None
    assert PASSWORD not in response.text


def test_login_and_user_isolation(client, db):
    user, headers, body = signed_in(client)
    other, other_headers, _ = signed_in(client)
    wrong = client.post('/api/auth/login', json={**body, 'password': 'incorrect-password'})
    missing = client.post('/api/auth/login', json=credentials())
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json() == missing.json()
    assert wrong.headers['www-authenticate'] == 'Bearer'
    assert client.get('/api/users/me', headers=headers).json()['data']['id'] == user['id']
    saved = client.put('/api/users/me', headers=headers, json={'nickname': '  校园同学  '})
    assert saved.status_code == 200
    assert saved.json()['data']['nickname'] == '校园同学'
    assert saved.json()['data']['username'] == body['username']
    assert saved.json()['data']['updated_at'] >= user['updated_at']
    assert client.get('/api/users/me', headers=other_headers).json()['data']['nickname'] == other['nickname']
    assert client.get('/api/users/me', headers=headers).json()['data']['nickname'] == '校园同学'
    assert client.put('/api/users/me', headers=headers, json={}).json()['data']['nickname'] == '校园同学'
    assert client.put('/api/users/me', headers=headers, json={'avatar': None}).status_code == 200


@pytest.mark.parametrize('payload', [
    {'username': 'changed'}, {'id': 1}, {'password_hash': 'changed'}, {'password': PASSWORD},
    {'nickname': None}, {'nickname': ''}, {'nickname': ' '}, {'nickname': 'x' * 33},
    {'avatar': 'https://example.com/avatar.jpg'}, {'avatar': '/uploads/../../secret'},
    {'avatar': '/uploads/' + 'a' * 32 + '.png'},
])
def test_protected_profile_fields(client, payload):
    _, headers, _ = signed_in(client)
    assert client.put('/api/users/me', headers=headers, json=payload).status_code == 422


@pytest.mark.parametrize('header', [None, 'Basic abc', 'Bearer invalid', 'Bearer'])
def test_anonymous_and_malformed_tokens(client, header):
    headers = {'Authorization': header} if header else {}
    for response in [client.get('/api/users/me', headers=headers), client.put('/api/users/me', headers=headers, json={'nickname': 'name'})]:
        assert response.status_code == 401
        assert response.json()['code'] == 401
        assert response.headers['www-authenticate'] == 'Bearer'


@pytest.mark.parametrize('case', ['expired', 'missing_exp', 'wrong_key', 'wrong_algorithm', 'bad_sub', 'future_iat', 'deleted_user'])
def test_invalid_signed_tokens(client, case):
    user, _, _ = signed_in(client)
    now = datetime.now(timezone.utc)
    claims = {'sub': str(user['id']), 'iat': now, 'exp': now + timedelta(hours=24)}
    secret = get_settings().jwt_secret.get_secret_value()
    algorithm = 'HS256'
    if case == 'expired': claims['exp'] = now - timedelta(seconds=1)
    if case == 'missing_exp': del claims['exp']
    if case == 'wrong_key': secret = 'different-secret-with-more-than-32-characters'
    if case == 'wrong_algorithm': algorithm = 'HS384'
    if case == 'bad_sub': claims['sub'] = '-1'
    if case == 'future_iat': claims['iat'] = now + timedelta(hours=1)
    if case == 'deleted_user': claims['sub'] = str(2**63 - 1)
    token = jwt.encode(claims, secret, algorithm=algorithm)
    assert client.get('/api/users/me', headers={'Authorization': 'Bearer ' + token}).status_code == 401


def test_unified_404_405_and_500():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get('/failure')
    def failure():
        raise RuntimeError('password=private-do-not-leak')

    with TestClient(app, raise_server_exceptions=False) as client:
        for response, expected in [(client.get('/missing'), 404), (client.post('/failure'), 405), (client.get('/failure'), 500)]:
            assert response.status_code == response.json()['code'] == expected
            assert response.json()['data'] is None
            assert 'private-do-not-leak' not in response.text
