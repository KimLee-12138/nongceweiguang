from __future__ import annotations

from app.db.base import Base
from app.db.session import get_engine

# 确保模型被导入注册到 Base.metadata
from app.models import auth_models  # noqa: F401
from app.models import business_models  # noqa: F401
from app.models import admin_models  # noqa: F401
from app.models import policy_review_models  # noqa: F401


def create_all_tables() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

