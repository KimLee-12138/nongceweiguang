from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine, select

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import admin_models, auth_models, business_models, policy_review_models  # noqa: F401
from app.models.auth_models import EndUserORM
from app.services.passwords import hash_password


@pytest.fixture
def client_and_db():
    old_env = os.environ.get("ENV")
    os.environ["ENV"] = "test"
    get_settings.cache_clear()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with Session(engine) as db:
        db.add(EndUserORM(username="farmer", password_hash=hash_password("farmer123")))
        db.commit()

    with TestClient(app) as test_client:
        yield test_client, testing_session_local

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    get_settings.cache_clear()
    if old_env is None:
        os.environ.pop("ENV", None)
    else:
        os.environ["ENV"] = old_env


def test_profile_crud_roundtrip(client_and_db):
    client, session_local = client_and_db
    login = client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})
    assert login.status_code == 200

    body = {
        "name": "测试农户",
        "type": "家庭农场",
        "area": 40.0,
        "green_cert": False,
        "irrigation": "滴灌",
        "extra_data": {"crops": ["小麦"]},
    }
    created = client.post("/api/v1/profiles", json=body)
    assert created.status_code == 200
    pid = created.json()["id"]
    assert created.json()["name"] == "测试农户"

    listed = client.get("/api/v1/profiles")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = client.get(f"/api/v1/profiles/{pid}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "测试农户"
    assert detail.json()["match_records"] == []

    updated = client.put(
        f"/api/v1/profiles/{pid}",
        json={
            "name": "测试农户二",
            "type": "家庭农场",
            "area": 45.0,
            "green_cert": True,
            "irrigation": "滴灌",
            "extra_data": {"crops": ["水稻"]},
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "测试农户二"
    assert updated.json()["green_cert"] is True

    with session_local() as db:
        row = db.scalar(select(EndUserORM).where(EndUserORM.username == "farmer"))
        assert row is not None


def test_profile_create_conflict_when_exists(client_and_db):
    client, _ = client_and_db
    client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})
    body = {
        "name": "甲",
        "type": "合作社",
        "area": 10.0,
        "green_cert": False,
        "irrigation": "",
        "extra_data": {},
    }
    assert client.post("/api/v1/profiles", json=body).status_code == 200
    second = client.post("/api/v1/profiles", json=body)
    assert second.status_code == 409
