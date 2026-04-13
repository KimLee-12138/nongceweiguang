from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_admin
from app.db.session import get_db
from app.models.admin_models import AdminOperationRunItemORM, AdminOperationRunORM
from app.models.auth_models import AdminUserORM
from app.models.policy_review_models import PolicyReviewTaskORM
from app.services.condition_tree_service import extract_condition_tree_metadata, normalize_condition_tree
from app.services.admin_operation_service import consume_run_by_id_in_background, create_run
from app.services.review_queue_service import (
    approve_review_task,
    create_review_task,
    list_review_events,
    mark_review_task_ai_pending,
    reject_review_task,
    refresh_review_task_condition_tree,
    save_review_draft,
)

router = APIRouter(prefix='/policies/review', tags=['policy-review'])


class ReviewTaskCreate(BaseModel):
    source_type: str = Field(default='manual', description='manual | file | crawler')
    title: str
    source: str | None = None
    raw_text: str = ''
    source_ref: str | None = None
    raw_text_ref: str | None = None
    raw_policy_id: int | None = None
    draft_file_type: str | None = None
    draft_validity_status: str | None = None
    draft_effective_date: dt.date | None = None
    draft_expiry_date: dt.date | None = None


class ReviewDraftPatch(BaseModel):
    draft_title: str | None = None
    draft_source: str | None = None
    draft_summary: str | None = None
    draft_category: str | None = None
    draft_file_type: str | None = None
    draft_validity_status: str | None = None
    draft_effective_date: dt.date | None = None
    draft_expiry_date: dt.date | None = None
    draft_condition_tree: dict[str, Any] | None = None


class ApproveBody(BaseModel):
    comment: str | None = None


class RejectBody(BaseModel):
    reason: str


def _task_to_dict(task: PolicyReviewTaskORM) -> dict[str, Any]:
    condition_tree = normalize_condition_tree(task.draft_condition_tree or {})
    condition_tree_meta = extract_condition_tree_metadata(condition_tree)
    return {
        'id': task.id,
        'source_type': task.source_type,
        'source_ref': task.source_ref,
        'raw_policy_id': task.raw_policy_id,
        'title': task.title,
        'source': task.source,
        'raw_text': task.raw_text,
        'raw_text_ref': task.raw_text_ref,
        'review_status': task.review_status,
        'draft_status': task.draft_status,
        'ai_status': task.ai_status,
        'created_by': task.created_by,
        'draft_title': task.draft_title,
        'draft_source': task.draft_source,
        'draft_summary': task.draft_summary,
        'draft_category': task.draft_category,
        'draft_file_type': task.draft_file_type,
        'draft_validity_status': task.draft_validity_status,
        'draft_effective_date': task.draft_effective_date.isoformat() if task.draft_effective_date else None,
        'draft_expiry_date': task.draft_expiry_date.isoformat() if task.draft_expiry_date else None,
        'draft_condition_tree': condition_tree,
        'condition_tree_meta': condition_tree_meta,
        'condition_tree_schema_version': condition_tree_meta.get('schema_version'),
        'condition_tree_compile_quality': condition_tree_meta.get('compile_quality'),
        'condition_tree_missing_information': condition_tree_meta.get('missing_information'),
        'condition_tree_uncertain_points': condition_tree_meta.get('uncertain_points'),
        'condition_tree_generated_by': condition_tree_meta.get('generated_by'),
        'condition_tree_reason': condition_tree_meta.get('reason'),
        'condition_tree_error': condition_tree_meta.get('reason') if task.draft_status == 'failed' else None,
        'condition_tree_applicable_subjects': condition_tree_meta.get('applicable_subjects'),
        'condition_tree_node_count': condition_tree_meta.get('node_count'),
        'condition_tree_predicate_count': condition_tree_meta.get('predicate_count'),
        'ai_summary': task.ai_summary,
        'ai_category': task.ai_category,
        'ai_suggestion': task.ai_suggestion,
        'ai_recommendation': task.ai_recommendation,
        'ai_risk_points_json': task.ai_risk_points_json or [],
        'ai_evidence_json': task.ai_evidence_json or [],
        'ai_error': task.ai_error,
        'approved_policy_id': task.approved_policy_id,
        'reviewed_by': task.reviewed_by,
        'review_comment': task.review_comment,
        'rejection_reason': task.rejection_reason,
        'reviewed_at': task.reviewed_at.isoformat() if task.reviewed_at else None,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat(),
    }


@router.get('/tasks')
def list_tasks(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    review_status: str | None = Query(None, description='pending | approved | rejected'),
    source_type: str | None = Query(None),
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    file_type: str | None = Query(None),
    validity_status: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    _ = admin
    stmt = select(PolicyReviewTaskORM)
    if source_type:
        stmt = stmt.where(PolicyReviewTaskORM.source_type == source_type)
    if category:
        stmt = stmt.where(
            or_(
                PolicyReviewTaskORM.draft_category == category,
                PolicyReviewTaskORM.ai_category == category,
            )
        )
    if keyword:
        keyword_expr = f'%{keyword.strip()}%'
        stmt = stmt.where(
            or_(
                PolicyReviewTaskORM.title.ilike(keyword_expr),
                PolicyReviewTaskORM.source.ilike(keyword_expr),
                PolicyReviewTaskORM.draft_title.ilike(keyword_expr),
                PolicyReviewTaskORM.draft_source.ilike(keyword_expr),
                PolicyReviewTaskORM.draft_summary.ilike(keyword_expr),
                PolicyReviewTaskORM.ai_summary.ilike(keyword_expr),
            )
        )
    if file_type:
        stmt = stmt.where(PolicyReviewTaskORM.draft_file_type == file_type)
    if validity_status:
        stmt = stmt.where(PolicyReviewTaskORM.draft_validity_status == validity_status)
    stats_stmt = stmt
    if review_status:
        stmt = stmt.where(PolicyReviewTaskORM.review_status == review_status)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(desc(PolicyReviewTaskORM.id)).offset(offset).limit(limit)).all()
    stats = {
        'pending': db.scalar(
            select(func.count()).select_from(stats_stmt.where(PolicyReviewTaskORM.review_status == 'pending').subquery())
        )
        or 0,
        'approved': db.scalar(
            select(func.count()).select_from(stats_stmt.where(PolicyReviewTaskORM.review_status == 'approved').subquery())
        )
        or 0,
        'rejected': db.scalar(
            select(func.count()).select_from(stats_stmt.where(PolicyReviewTaskORM.review_status == 'rejected').subquery())
        )
        or 0,
        'ai_failed': db.scalar(
            select(func.count()).select_from(stats_stmt.where(PolicyReviewTaskORM.ai_status == 'failed').subquery())
        )
        or 0,
    }
    return {'items': [_task_to_dict(task) for task in rows], 'total': total, 'stats': stats}


@router.post('/tasks', status_code=status.HTTP_201_CREATED)
async def create_task(
    body: ReviewTaskCreate,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    task = create_review_task(
        db,
        source_type=body.source_type,
        title=body.title,
        source=body.source,
        raw_text=body.raw_text,
        source_ref=body.source_ref,
        raw_text_ref=body.raw_text_ref,
        raw_policy_id=body.raw_policy_id,
        operator=admin.username,
        draft_file_type=body.draft_file_type,
        draft_validity_status=body.draft_validity_status,
        draft_effective_date=body.draft_effective_date,
        draft_expiry_date=body.draft_expiry_date,
    )
    return _task_to_dict(task)


@router.get('/tasks/{task_id}')
def get_task(task_id: int, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    task = db.get(PolicyReviewTaskORM, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    return {'task': _task_to_dict(task), 'events': _events_to_json(list_review_events(db, task_id=task_id))}


def _events_to_json(events: list) -> list[dict]:
    return [
        {
            'id': event.id,
            'event_type': event.event_type,
            'operator': event.operator,
            'before_snapshot_json': event.before_snapshot_json,
            'after_snapshot_json': event.after_snapshot_json,
            'comment': event.comment,
            'created_at': event.created_at.isoformat(),
        }
        for event in events
    ]


@router.patch('/tasks/{task_id}/draft')
def patch_draft(
    task_id: int,
    body: ReviewDraftPatch,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    try:
        task = save_review_draft(
            db,
            task_id=task_id,
            operator=admin.username,
            draft_title=body.draft_title,
            draft_source=body.draft_source,
            draft_summary=body.draft_summary,
            draft_category=body.draft_category,
            draft_file_type=body.draft_file_type,
            draft_validity_status=body.draft_validity_status,
            draft_effective_date=body.draft_effective_date,
            draft_expiry_date=body.draft_expiry_date,
            draft_condition_tree=body.draft_condition_tree,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _task_to_dict(task)


@router.post('/tasks/{task_id}/approve')
def approve_task(
    task_id: int,
    body: ApproveBody,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    try:
        task = approve_review_task(db, task_id=task_id, operator=admin.username, comment=body.comment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _task_to_dict(task)


@router.post('/tasks/{task_id}/reject')
def reject_task(
    task_id: int,
    body: RejectBody,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    try:
        task = reject_review_task(db, task_id=task_id, operator=admin.username, reason=body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _task_to_dict(task)


@router.post('/tasks/{task_id}/refresh-ai')
def refresh_task_ai(
    task_id: int,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    task = db.get(PolicyReviewTaskORM, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    candidate_runs = db.scalars(
        select(AdminOperationRunORM)
        .where(
            AdminOperationRunORM.operation_type == 'policy_review_ai_refresh',
            AdminOperationRunORM.status.in_(('pending', 'running')),
        )
        .order_by(desc(AdminOperationRunORM.id))
        .limit(50)
    ).all()
    for run in candidate_runs:
        if (run.payload_json or {}).get('task_id') == task_id:
            if task.ai_status != 'pending':
                task.ai_status = 'pending'
                task.ai_error = None
                db.commit()
            return {'run_id': run.id, 'status': run.status, 'reused': True}

    mark_review_task_ai_pending(db, task_id=task_id, operator=admin.username)
    run = create_run(
        db,
        operation_type='policy_review_ai_refresh',
        payload={'task_id': task_id, 'operator': admin.username},
        items=[{'task_id': task_id}],
    )
    consume_run_by_id_in_background(run.id)
    return {'run_id': run.id, 'status': run.status, 'reused': False}


@router.post('/tasks/{task_id}/refresh-condition-tree')
def refresh_task_condition_tree(
    task_id: int,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    task = db.get(PolicyReviewTaskORM, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    candidate_runs = db.scalars(
        select(AdminOperationRunORM)
        .where(
            AdminOperationRunORM.operation_type == 'policy_condition_tree_backfill',
            AdminOperationRunORM.status.in_(('pending', 'running')),
        )
        .order_by(desc(AdminOperationRunORM.id))
        .limit(100)
    ).all()
    for run in candidate_runs:
        for run_item in db.scalars(select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id)).all():
            if (run_item.input_json or {}).get('target_type') == 'review_task' and (run_item.input_json or {}).get('entity_id') == task_id:
                if task.draft_status != 'pending':
                    task.draft_status = 'pending'
                    db.commit()
                return {'run_id': run.id, 'status': run.status, 'reused': True}

    task.draft_status = 'pending'
    db.commit()
    run = create_run(
        db,
        operation_type='policy_condition_tree_backfill',
        payload={'task_id': task_id, 'operator': admin.username, 'target_type': 'review_task'},
        items=[{'target_type': 'review_task', 'entity_id': task_id}],
    )
    consume_run_by_id_in_background(run.id)
    return {'run_id': run.id, 'status': run.status, 'reused': False}
