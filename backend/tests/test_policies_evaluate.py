from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import admin_models, auth_models, business_models, policy_review_models  # noqa: F401


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

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    get_settings.cache_clear()
    if old_env is None:
        os.environ.pop("ENV", None)
    else:
        os.environ["ENV"] = old_env


def test_evaluate_returns_match_summary(client):
    payload = {
        "condition_tree": {
            "id": "root",
            "logic": "and",
            "must": True,
            "children": [
                {"id": "a1", "field": "area", "operator": ">=", "value": 30, "must": True},
            ],
        },
        "profile": {"area": 50, "type": "家庭农场", "green_cert": False, "irrigation": "", "extra_data": {}},
    }
    response = client.post("/api/v1/policies/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["fully_matched"] is True
    assert data["summary"]["must_failed"] == 0
