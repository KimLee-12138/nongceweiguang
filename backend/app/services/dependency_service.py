from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.crawler_service import check_crawler_readiness
from app.services.model_provider import check_model_readiness
from app.services.ocr_service import check_ocr_readiness


def check_mysql_readiness(db: Session) -> dict[str, Any]:
    try:
        value = db.execute(text("SELECT 1")).scalar()
    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "message": f"MySQL 连通失败：{exc}",
            "detail": {},
        }
    return {
        "ok": bool(value == 1),
        "status": "ready",
        "message": "MySQL 连通成功",
        "detail": {"result": value},
    }


def collect_dependency_status(db: Session, *, live: bool = False) -> dict[str, Any]:
    mysql = check_mysql_readiness(db)
    model = check_model_readiness(live=live).to_dict()
    ocr = check_ocr_readiness(live=live).to_dict()
    crawler = check_crawler_readiness(live=live).to_dict()
    items = {
        "mysql": mysql,
        "model": model,
        "ocr": ocr,
        "crawler": crawler,
    }
    ok = all(bool(item.get("ok")) for item in items.values())
    return {"ok": ok, "items": items}
