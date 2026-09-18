import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from app.common.config import Settings
from app.common.database import get_db
from app.main import app


class DatabaseProbe:
    def __init__(self, fail=False):
        self.fail = fail
        self.queried = False

    def execute(self, statement):
        assert str(statement) == 'SELECT 1'
        self.queried = True
        if self.fail:
            raise OperationalError('SELECT 1', {}, Exception('private database details'))
        return self

    def scalar_one(self):
        return 1


@pytest.mark.parametrize('fail', [False, True])
def test_health_checks_database_and_returns_envelope(fail):
    probe = DatabaseProbe(fail)
    app.dependency_overrides[get_db] = lambda: probe
    try:
        with TestClient(app) as client:
            response = client.get('/api/health')
        assert probe.queried
        assert response.status_code == (503 if fail else 200)
        assert response.json() == (
            {'code': 503, 'message': '数据库暂时不可用', 'data': None}
            if fail else {'code': 200, 'message': 'success', 'data': {'status': 'ok'}}
        )
        assert 'private database details' not in response.text
    finally:
        app.dependency_overrides.clear()


def test_sample_jwt_secret_is_rejected():
    with pytest.raises(ValidationError):
        Settings(jwt_secret='change_me_generate_at_least_32_random_characters')
