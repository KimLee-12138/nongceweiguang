from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1 import chat_routes
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import admin_models, auth_models, business_models, policy_review_models  # noqa: F401
from app.models.auth_models import AdminUserORM, EndUserORM
from app.models.business_models import ChatMessageORM, PolicyORM, UserProfileORM
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
        db.add(AdminUserORM(username="admin", password_hash=hash_password("admin123")))
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


def _seed_profile_and_policies(session_local):
    with session_local() as db:
        user = db.scalar(select(EndUserORM).where(EndUserORM.username == "farmer"))
        assert user is not None
        profile = UserProfileORM(
            owner_user_id=user.id,
            name="王大哥",
            type="家庭农场",
            area=58,
            green_cert=False,
            irrigation="滴灌",
            extra_data={"crops": ["水稻"]},
        )
        good = PolicyORM(
            title="高标准农田提升项目",
            source="demo",
            summary="支持面积达到门槛的经营主体",
            raw_text_ref="local://good",
            condition_tree={
                "id": "root",
                "logic": "and",
                "must": True,
                "children": [
                    {"id": "a1", "field": "area", "operator": ">=", "value": 30, "must": True},
                    {"id": "a2", "field": "type", "operator": "in", "value": ["家庭农场", "合作社"], "must": True},
                ],
            },
        )
        hard = PolicyORM(
            title="绿色认证跃升项目",
            source="demo",
            summary="绿色认证优先支持",
            raw_text_ref="local://hard",
            condition_tree={
                "id": "root",
                "logic": "and",
                "must": True,
                "children": [
                    {"id": "b1", "field": "green_cert", "operator": "=", "value": True, "must": True},
                    {"id": "b2", "field": "area", "operator": ">=", "value": 100, "must": True},
                ],
            },
        )
        db.add_all([profile, good, hard])
        db.commit()
        db.refresh(profile)
        db.refresh(good)
        db.refresh(hard)
        return profile.id, good.id, hard.id


def test_suggested_policies_returns_scored_items(client_and_db):
    client, session_local = client_and_db
    profile_id, good_id, _ = _seed_profile_and_policies(session_local)

    login = client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})
    assert login.status_code == 200

    response = client.get(f"/api/v1/profiles/{profile_id}/suggested-policies?limit=10")
    assert response.status_code == 200
    payload = response.json()
    items = payload["items"]

    assert len(items) >= 2
    assert items[0]["policy_id"] == good_id
    assert items[0]["score"] >= items[1]["score"]
    assert "match_summary" in items[0]
    assert "fit_label" in items[0]


def test_chat_stream_emits_policy_and_interpretation_events(monkeypatch, client_and_db):
    client, session_local = client_and_db
    profile_id, good_id, _ = _seed_profile_and_policies(session_local)

    def fake_generate_chat_interpretation_payload(**_kwargs):
        return {
            "answer": "这是模型解读回答。",
            "interpretation_report": {
                "eligibility_level": "high",
                "key_points": ["满足面积门槛"],
                "next_steps": ["准备申报材料"],
                "risk_warnings": [],
                "provider": "deepseek",
            },
        }

    monkeypatch.setattr(chat_routes, "generate_chat_interpretation_payload", fake_generate_chat_interpretation_payload)

    login = client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})
    assert login.status_code == 200

    response = client.post(
        "/api/v1/chat/stream",
        json={
            "conversation_id": None,
            "message": "我该怎么申报？",
            "mode": "match",
            "profile_id": profile_id,
            "policy_id": good_id,
        },
    )
    assert response.status_code == 200
    body = response.text

    assert "event: message_meta" in body
    assert "event: policy_context" in body
    assert "event: policy_report" in body
    assert "event: interpretation_report" in body
    assert "event: content_done" in body
    assert "这是模型解读回答" in body


def test_interpret_mode_requires_policy(client_and_db):
    client, session_local = client_and_db
    profile_id, _, _ = _seed_profile_and_policies(session_local)

    login = client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})
    assert login.status_code == 200

    response = client.post(
        "/api/v1/chat/stream",
        json={
            "conversation_id": None,
            "message": "请帮我解读",
            "mode": "interpret",
            "profile_id": profile_id,
            "policy_id": None,
        },
    )
    assert response.status_code == 400
    assert "必须先选择政策" in response.json()["detail"]


def test_agri_llm_stream_supports_optional_context(monkeypatch, client_and_db):
    client, session_local = client_and_db
    _profile_id, good_id, _ = _seed_profile_and_policies(session_local)

    def fake_generate_agri_policy_qa_payload(**_kwargs):
        return {
            "answer": "这是农业政策大模型回答。",
            "qa_report": {
                "in_scope": True,
                "key_points": ["先确认申报主体资格"],
                "followups": ["你可以补充所在县区"],
                "provider": "deepseek",
            },
        }

    monkeypatch.setattr(chat_routes, "generate_agri_policy_qa_payload", fake_generate_agri_policy_qa_payload)

    login = client.post("/api/v1/user-auth/login", json={"username": "farmer", "password": "farmer123"})
    assert login.status_code == 200

    response = client.post(
        "/api/v1/chat/agri-llm/stream",
        json={
            "conversation_id": None,
            "message": "家庭农场如何申请补贴？",
            "mode": "agri_llm",
            "profile_id": None,
            "policy_id": good_id,
        },
    )
    assert response.status_code == 200
    body = response.text
    assert "event: message_meta" in body
    assert "event: content" in body
    assert "event: agri_qa_report" in body
    assert "event: content_done" in body

    with session_local() as db:
        latest = db.scalar(select(ChatMessageORM).order_by(ChatMessageORM.id.desc()))
        assert latest is not None
        assert latest.role == "assistant"
        assert latest.mode == "agri_llm"
        assert latest.content == "这是农业政策大模型回答。"
        assert "agri_qa_report" in (latest.render_payload_json or {})
