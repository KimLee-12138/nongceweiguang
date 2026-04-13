from __future__ import annotations

from typing import Any

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_admin
from app.db.session import get_db
from app.models.auth_models import AdminUserORM
from app.models.business_models import CompassGlossaryORM, CompassReportORM
from app.services.compass_service import (
    build_policy_briefing,
    build_compass_signals,
    create_glossary_item,
    delete_glossary_item,
    generate_and_store_compass_report,
    list_glossary_items,
    update_glossary_item,
)


router = APIRouter(prefix='/compass', tags=['compass'])


class GlossaryPayload(BaseModel):
    term: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1)
    category: str = Field(default='政策主题', max_length=64)
    aliases: list[str] = Field(default_factory=list)
    weight: int = Field(default=1, ge=1, le=100)
    enabled: bool = True


def _serialize_report(row: CompassReportORM) -> dict[str, Any]:
    return {
        'id': row.id,
        'title': row.title,
        'category': row.category,
        'summary': row.summary,
        'content': row.content,
        'published_at': row.published_at.isoformat() if row.published_at else None,
    }


def _serialize_glossary(row: CompassGlossaryORM) -> dict[str, Any]:
    return {
        'id': row.id,
        'term': row.term,
        'category': row.category,
        'aliases': list(row.aliases_json or []),
        'weight': row.weight,
        'enabled': bool(row.enabled),
        'description': row.description,
        'published_at': row.published_at.isoformat() if row.published_at else None,
        'updated_at': row.updated_at.isoformat() if row.updated_at else None,
    }


@router.get('/overview')
def overview(months: Annotated[int, Query(ge=3, le=24)] = 6, db: Session = Depends(get_db)):
    return build_compass_signals(db, months=months)


@router.get('/theme-trends')
def theme_trends(months: Annotated[int, Query(ge=3, le=24)] = 6, db: Session = Depends(get_db)):
    signals = build_compass_signals(db, months=months)
    return {
        'generated_at': signals['generated_at'],
        'monthly_trend': signals['monthly_trend'],
        'theme_distribution': signals['theme_distribution'],
        'audience_distribution': signals['audience_distribution'],
        'region_distribution': signals['region_distribution'],
    }


@router.get('/briefing')
def briefing(
    months: Annotated[int, Query(ge=3, le=24)] = 6,
    policy_id: Annotated[int | None, Query()] = None,
    db: Session = Depends(get_db),
):
    return build_policy_briefing(db, months=months, policy_id=policy_id)


@router.get('/reports')
def list_reports(limit: Annotated[int, Query(ge=1, le=100)] = 20, db: Session = Depends(get_db)):
    rows = db.scalars(select(CompassReportORM).order_by(desc(CompassReportORM.published_at)).limit(limit)).all()
    return {'items': [_serialize_report(row) for row in rows]}


@router.get('/reports/{report_id}')
def get_report(report_id: int, db: Session = Depends(get_db)):
    row = db.get(CompassReportORM, report_id)
    if not row:
        raise HTTPException(status_code=404, detail='报告不存在')
    return _serialize_report(row)


@router.get('/glossary')
def glossary(
    keyword: str | None = None,
    category: str | None = None,
    enabled: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    db: Session = Depends(get_db),
):
    rows = list_glossary_items(db, keyword=keyword, category=category, enabled=enabled, limit=limit)
    return {'items': [_serialize_glossary(row) for row in rows]}


@router.post('/glossary')
def create_glossary(
    payload: GlossaryPayload,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    _ = admin
    row = create_glossary_item(
        db,
        term=payload.term,
        description=payload.description,
        category=payload.category,
        aliases=payload.aliases,
        weight=payload.weight,
        enabled=payload.enabled,
    )
    return _serialize_glossary(row)


@router.patch('/glossary/{glossary_id}')
def patch_glossary(
    glossary_id: int,
    payload: GlossaryPayload,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    _ = admin
    row = update_glossary_item(
        db,
        glossary_id=glossary_id,
        term=payload.term,
        description=payload.description,
        category=payload.category,
        aliases=payload.aliases,
        weight=payload.weight,
        enabled=payload.enabled,
    )
    if not row:
        raise HTTPException(status_code=404, detail='词条不存在')
    return _serialize_glossary(row)


@router.delete('/glossary/{glossary_id}')
def remove_glossary(
    glossary_id: int,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    _ = admin
    deleted = delete_glossary_item(db, glossary_id=glossary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='词条不存在')
    return {'ok': True}


@router.post('/generate')
def generate(db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    result = generate_and_store_compass_report(db)
    return {'ok': True, 'report_id': result['report_id'], 'signals': result['signals']}
