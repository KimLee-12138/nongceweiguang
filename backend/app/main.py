from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1.auth_routes import router as admin_auth_router
from app.api.v1.admin_ops_routes import router as admin_ops_router
from app.api.v1.chat_routes import router as chat_router
from app.api.v1.compass_routes import router as compass_router
from app.api.v1.insights_routes import router as insights_router
from app.api.v1.policy_routes import router as policy_router
from app.api.v1.policy_review_routes import router as policy_review_router
from app.api.v1.profile_routes import router as profile_router
from app.api.v1.user_auth_routes import router as user_auth_router
from app.core.config import get_settings
from app.db.init_db import create_all_tables
from app.db.schema_align import ensure_auth_schema
from app.db.session import get_engine
from app.services.dependency_service import collect_dependency_status


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="农策微光 API", version="0.1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(admin_auth_router, prefix="/api/v1")
    app.include_router(user_auth_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(policy_router, prefix="/api/v1")
    app.include_router(policy_review_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(admin_ops_router, prefix="/api/v1")
    app.include_router(compass_router, prefix="/api/v1")
    app.include_router(insights_router, prefix="/api/v1")

    @app.on_event("startup")
    def _startup():
        # 目前仓库无 Alembic 迁移历史；为便于课程开发先在 development 自动建表。
        # 后续补齐 Alembic 后，该逻辑可替换为迁移命令或运行时 schema 校验。
        if settings.ENV == "development":
            create_all_tables()
        if settings.SCHEMA_AUTO_PATCH:
            ensure_auth_schema(get_engine())

    @app.get("/api/v1/health")
    def health():
        return {"ok": True, "env": settings.ENV}

    @app.get("/api/v1/health/dependencies")
    def health_dependencies(live: bool = False):
        engine = get_engine()
        with Session(engine) as db:
            return collect_dependency_status(db, live=live)

    return app


app = create_app()

