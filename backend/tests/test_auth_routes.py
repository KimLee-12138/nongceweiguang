from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import admin_models, auth_models, business_models, policy_review_models  # noqa: F401
from app.models.auth_models import AdminUserORM, EndUserORM
from app.services.passwords import hash_password


class BrokenSession:
    def scalar(self, *_args, **_kwargs):
        raise OperationalError("SELECT 1", {}, Exception("db down"))

    def get(self, *_args, **_kwargs):
        raise OperationalError("SELECT 1", {}, Exception("db down"))

    def rollback(self):
        return None


@pytest.fixture
def client():
    old_env = os.environ.get("ENV")
    os.environ["ENV"] = "test"
    get_settings.cache_clear()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with Session(engine) as db:
        db.add(AdminUserORM(username="admin", password_hash=hash_password("admin123")))
        db.add(EndUserORM(username="farmer", password_hash=hash_password("farmer123")))
        db.commit()

    with TestClient(app) as test_client:
        yield test_client, app

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    get_settings.cache_clear()
    if old_env is None:
        os.environ.pop("ENV", None)
    else:
        os.environ["ENV"] = old_env


def test_user_login_sets_cookie_and_me_roundtrip(client):
    test_client, _app = client

    response = test_client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})

    assert response.status_code == 200
    assert response.json()["role"] == "user"
    assert "ncwg_user_access" in response.cookies

    me = test_client.get("/api/v1/user-auth/me")
    assert me.status_code == 200
    assert me.json()["authenticated"] is True
    assert me.json()["username"] == "farmer"


def test_admin_login_sets_cookie_and_me_roundtrip(client):
    test_client, _app = client

    response = test_client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    assert "ncwg_admin_access" in response.cookies

    me = test_client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["authenticated"] is True
    assert me.json()["username"] == "admin"


def test_user_login_returns_503_when_database_unavailable(client):
    test_client, app = client

    def override_broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = override_broken_db

    response = test_client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})

    assert response.status_code == 503
    assert response.json()["detail"] == "认证服务暂时不可用，请检查数据库连接后重试。"


def test_admin_me_returns_503_when_database_unavailable(client):
    test_client, app = client

    login = test_client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert login.status_code == 200

    def override_broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = override_broken_db

    response = test_client.get("/api/v1/auth/me")

    assert response.status_code == 503
    assert response.json()["detail"] == "认证状态暂时不可用，请检查数据库连接后重试。"
