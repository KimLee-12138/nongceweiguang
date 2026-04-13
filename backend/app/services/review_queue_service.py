from __future__ import annotations

import datetime as dt
import threading
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_sessionmaker
from app.models.business_models import PolicyORM
from app.models.policy_review_models import PolicyReviewEventORM, PolicyReviewTaskORM
from app.schemas.policy import Policy, PolicyConditionNode
from app.services.condition_tree_service import extract_condition_tree_metadata, normalize_condition_tree
from app.services.policy_compile_service import (
    build_stub_condition_tree,
    compile_policy_text as compile_policy_text_by_model,
    suggest_summary_from_text,
)
from app.services.review_ai_service import generate_review_ai_payload


def _build_failed_condition_tree(message: str) -> dict[str, Any]:
    return normalize_condition_tree(
        {},
        generated_by='deepseek',
        compile_quality='failed',
        missing_information=['DeepSeek 条件树生成失败'],
        uncertain_points=[],
        applicable_subjects=[],
        reason=message,
    )


def compile_policy_text(raw_text: str, title: str | None = None, source: str | None = None) -> Policy:
    compiled = compile_policy_text_by_model(raw_text=raw_text, title=title, source=source)
    return Policy(
        policy_id=None,
        title=title or '未命名政策',
        source=source or '',
        summary=compiled.get('summary') or '',
        raw_text_ref=None,
        root_condition=_build_condition_node(compiled.get('condition_tree') or {}),
    )


def _append_event(
    db: Session,
    *,
    task_id: int,
    event_type: str,
    operator: str | None,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    comment: str | None = None,
) -> None:
    db.add(
        PolicyReviewEventORM(
            task_id=task_id,
            event_type=event_type,
            operator=operator,
            before_snapshot_json=before,
            after_snapshot_json=after,
            comment=comment,
        )
    )


def _bootstrap_task_draft(task: PolicyReviewTaskORM) -> None:
    task.draft_title = task.title
    task.draft_source = task.source or ''
    task.draft_summary = suggest_summary_from_text(task.raw_text)
    task.draft_category = task.draft_category or '其他'
    task.draft_condition_tree = build_stub_condition_tree(task.raw_text, task.title)
    task.ai_risk_points_json = list(task.ai_risk_points_json or [])
    task.ai_evidence_json = list(task.ai_evidence_json or [])


def _compile_task_draft(task: PolicyReviewTaskORM) -> dict[str, Any]:
    draft_policy = compile_policy_text(task.raw_text, title=task.title, source=task.source)
    return {
        'title': draft_policy.title or task.title,
        'source': draft_policy.source or task.source or '',
        'summary': draft_policy.summary or '',
        'category': task.draft_category or '其他',
        'condition_tree': normalize_condition_tree(draft_policy.to_condition_tree()),
        'draft_policy': draft_policy,
    }


def _apply_model_enrichment(task: PolicyReviewTaskORM) -> None:
    draft_payload = _compile_task_draft(task)
    draft_policy = draft_payload['draft_policy']
    task.draft_status = 'success'
    task.draft_title = draft_payload['title']
    task.draft_source = draft_payload['source']
    task.draft_summary = draft_payload['summary']
    task.draft_category = draft_payload['category']
    task.draft_condition_tree = draft_payload['condition_tree']

    try:
        ai_payload = generate_review_ai_payload(
            raw_text=task.raw_text,
            draft_policy=draft_policy,
            draft_summary=task.draft_summary,
            draft_condition_tree=task.draft_condition_tree,
            title=task.title,
            source=task.source,
            draft_file_type=task.draft_file_type,
            draft_validity_status=task.draft_validity_status,
            draft_effective_date=task.draft_effective_date,
            draft_expiry_date=task.draft_expiry_date,
        )
        task.ai_status = 'success'
        task.ai_summary = ai_payload.get('summary')
        task.ai_category = ai_payload.get('category')
        task.ai_suggestion = ai_payload.get('suggestion')
        task.ai_risk_points_json = list(ai_payload.get('risk_points') or [])
        task.ai_evidence_json = list(ai_payload.get('evidence') or [])
        task.ai_recommendation = ai_payload.get('recommendation')
        task.ai_error = None
        if ai_payload.get('category'):
            task.draft_category = ai_payload['category']
    except Exception as exc:  # pragma: no cover
        task.ai_status = 'failed'
        task.ai_error = str(exc)
        task.ai_evidence_json = []


def create_review_task(
    db: Session,
    *,
    source_type: str,
    title: str,
    source: str | None,
    raw_text: str,
    source_ref: str | None,
    raw_text_ref: str | None,
    raw_policy_id: int | None,
    operator: str | None,
    draft_file_type: str | None = None,
    draft_validity_status: str | None = None,
    draft_effective_date: dt.date | str | None = None,
    draft_expiry_date: dt.date | str | None = None,
    defer_enrichment: bool = False,
) -> PolicyReviewTaskORM:
    if source_type == 'crawler' and source_ref:
        existing = db.scalar(
            select(PolicyReviewTaskORM).where(
                PolicyReviewTaskORM.source_type == 'crawler',
                PolicyReviewTaskORM.source_ref == source_ref,
                PolicyReviewTaskORM.review_status == 'pending',
            )
        )
        if existing:
            existing.raw_text = raw_text
            existing.raw_text_ref = raw_text_ref
            existing.raw_policy_id = raw_policy_id
            existing.title = title
            existing.source = source
            existing.draft_file_type = draft_file_type
            existing.draft_validity_status = draft_validity_status
            existing.draft_effective_date = _normalize_optional_date(draft_effective_date)
            existing.draft_expiry_date = _normalize_optional_date(draft_expiry_date)
            if defer_enrichment:
                existing.draft_status = 'pending'
                existing.ai_status = 'pending'
                existing.ai_error = None
                _bootstrap_task_draft(existing)
            db.commit()
            db.refresh(existing)
            return existing

    task = PolicyReviewTaskORM(
        source_type=source_type,
        source_ref=source_ref,
        raw_policy_id=raw_policy_id,
        title=title,
        source=source,
        raw_text=raw_text,
        raw_text_ref=raw_text_ref,
        review_status='pending',
        draft_status='pending',
        ai_status='pending',
        ai_risk_points_json=[],
        ai_evidence_json=[],
        created_by=operator,
        draft_file_type=draft_file_type,
        draft_validity_status=draft_validity_status,
        draft_effective_date=_normalize_optional_date(draft_effective_date),
        draft_expiry_date=_normalize_optional_date(draft_expiry_date),
    )
    db.add(task)
    db.flush()
    _bootstrap_task_draft(task)
    if not defer_enrichment:
        _apply_model_enrichment(task)

    db.flush()
    _append_event(
        db,
        task_id=task.id,
        event_type='created',
        operator=operator,
        before=None,
        after={'id': task.id, 'status': task.review_status},
    )
    db.commit()
    db.refresh(task)
    return task


def enrich_review_task(db: Session, *, task_id: int, operator: str | None = None) -> PolicyReviewTaskORM | None:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        return None
    before = {
        'draft_status': task.draft_status,
        'ai_status': task.ai_status,
        'draft_summary': task.draft_summary,
        'ai_suggestion': task.ai_suggestion,
    }
    try:
        _apply_model_enrichment(task)
        event_type = 'enriched'
        comment = None
    except Exception as exc:  # pragma: no cover
        task.draft_status = 'failed'
        task.ai_status = 'failed'
        task.ai_error = str(exc)
        task.draft_condition_tree = _build_failed_condition_tree(str(exc))
        event_type = 'enrich_failed'
        comment = str(exc)
    db.flush()
    _append_event(
        db,
        task_id=task.id,
        event_type=event_type,
        operator=operator,
        before=before,
        after={
            'draft_status': task.draft_status,
            'ai_status': task.ai_status,
            'draft_summary': task.draft_summary,
            'ai_suggestion': task.ai_suggestion,
        },
        comment=comment,
    )
    db.commit()
    db.refresh(task)
    return task


def mark_review_task_ai_pending(db: Session, *, task_id: int, operator: str | None = None) -> PolicyReviewTaskORM:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        raise ValueError('task not found')
    before = {
        'ai_status': task.ai_status,
        'ai_error': task.ai_error,
    }
    task.ai_status = 'pending'
    task.ai_error = None
    db.flush()
    _append_event(
        db,
        task_id=task.id,
        event_type='ai_refresh_requested',
        operator=operator,
        before=before,
        after={'ai_status': task.ai_status, 'ai_error': task.ai_error},
    )
    db.commit()
    db.refresh(task)
    return task


def refresh_review_task_ai(db: Session, *, task_id: int, operator: str | None = None) -> PolicyReviewTaskORM | None:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        return None
    before = {
        'ai_status': task.ai_status,
        'ai_summary': task.ai_summary,
        'ai_suggestion': task.ai_suggestion,
        'ai_recommendation': task.ai_recommendation,
    }
    try:
        _apply_model_enrichment(task)
        event_type = 'ai_refreshed'
        comment = None
    except Exception as exc:  # pragma: no cover
        task.ai_status = 'failed'
        task.ai_error = str(exc)
        event_type = 'ai_refresh_failed'
        comment = str(exc)
    db.flush()
    _append_event(
        db,
        task_id=task.id,
        event_type=event_type,
        operator=operator,
        before=before,
        after={
            'ai_status': task.ai_status,
            'ai_summary': task.ai_summary,
            'ai_suggestion': task.ai_suggestion,
            'ai_recommendation': task.ai_recommendation,
        },
        comment=comment,
    )
    db.commit()
    db.refresh(task)
    return task


def enrich_review_tasks_in_background(task_ids: list[int], *, operator: str | None = None) -> None:
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        for task_id in task_ids:
            try:
                enrich_review_task(db, task_id=task_id, operator=operator)
            except Exception:
                db.rollback()
    finally:
        db.close()


def queue_review_task_enrichment(task_ids: list[int], *, operator: str | None = None) -> None:
    if not task_ids:
        return
    thread = threading.Thread(
        target=enrich_review_tasks_in_background,
        args=(list(task_ids),),
        kwargs={'operator': operator},
        daemon=True,
    )
    thread.start()


def save_review_draft(
    db: Session,
    *,
    task_id: int,
    operator: str | None,
    draft_title: str | None = None,
    draft_source: str | None = None,
    draft_summary: str | None = None,
    draft_category: str | None = None,
    draft_file_type: str | None = None,
    draft_validity_status: str | None = None,
    draft_effective_date: dt.date | str | None = None,
    draft_expiry_date: dt.date | str | None = None,
    draft_condition_tree: dict[str, Any] | None = None,
) -> PolicyReviewTaskORM:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        raise ValueError('task not found')
    if task.review_status != 'pending':
        raise ValueError('只能编辑待审核任务')
    before = {
        'draft_title': task.draft_title,
        'draft_source': task.draft_source,
        'draft_summary': task.draft_summary,
        'draft_category': task.draft_category,
        'draft_file_type': task.draft_file_type,
        'draft_validity_status': task.draft_validity_status,
        'draft_effective_date': task.draft_effective_date.isoformat() if task.draft_effective_date else None,
        'draft_expiry_date': task.draft_expiry_date.isoformat() if task.draft_expiry_date else None,
        'draft_condition_tree': task.draft_condition_tree,
    }
    if draft_title is not None:
        task.draft_title = draft_title
    if draft_source is not None:
        task.draft_source = draft_source
    if draft_summary is not None:
        task.draft_summary = draft_summary
    if draft_category is not None:
        task.draft_category = draft_category
    if draft_file_type is not None:
        task.draft_file_type = draft_file_type
    if draft_validity_status is not None:
        task.draft_validity_status = draft_validity_status
    if draft_effective_date is not None:
        task.draft_effective_date = _normalize_optional_date(draft_effective_date)
    if draft_expiry_date is not None:
        task.draft_expiry_date = _normalize_optional_date(draft_expiry_date)
    if draft_condition_tree is not None:
        task.draft_condition_tree = normalize_condition_tree(draft_condition_tree)
    after = {
        'draft_title': task.draft_title,
        'draft_source': task.draft_source,
        'draft_summary': task.draft_summary,
        'draft_category': task.draft_category,
        'draft_file_type': task.draft_file_type,
        'draft_validity_status': task.draft_validity_status,
        'draft_effective_date': task.draft_effective_date.isoformat() if task.draft_effective_date else None,
        'draft_expiry_date': task.draft_expiry_date.isoformat() if task.draft_expiry_date else None,
        'draft_condition_tree': task.draft_condition_tree,
    }
    _append_event(
        db,
        task_id=task.id,
        event_type='draft_saved',
        operator=operator,
        before=before,
        after=after,
    )
    db.commit()
    db.refresh(task)
    return task


def approve_review_task(db: Session, *, task_id: int, operator: str, comment: str | None = None) -> PolicyReviewTaskORM:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        raise ValueError('task not found')
    if task.review_status != 'pending':
        raise ValueError('只能审批待审核任务')
    before = {'review_status': task.review_status, 'approved_policy_id': task.approved_policy_id}
    policy = PolicyORM(
        title=task.draft_title or task.title,
        source=task.draft_source or task.source or '',
        version=None,
        summary=task.draft_summary or '',
        raw_text_ref=task.raw_text_ref,
        file_type=task.draft_file_type,
        validity_status=task.draft_validity_status or '有效',
        effective_date=task.draft_effective_date,
        expiry_date=task.draft_expiry_date,
        condition_tree=normalize_condition_tree(deepcopy(task.draft_condition_tree or {})),
    )
    db.add(policy)
    db.flush()
    task.review_status = 'approved'
    task.approved_policy_id = policy.id
    task.reviewed_by = operator
    task.review_comment = comment
    task.reviewed_at = datetime.now(UTC)
    _append_event(
        db,
        task_id=task.id,
        event_type='approved',
        operator=operator,
        before=before,
        after={'review_status': task.review_status, 'approved_policy_id': policy.id},
        comment=comment,
    )
    db.commit()
    db.refresh(task)
    return task


def reject_review_task(db: Session, *, task_id: int, operator: str, reason: str) -> PolicyReviewTaskORM:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        raise ValueError('task not found')
    if task.review_status != 'pending':
        raise ValueError('只能驳回待审核任务')
    before = {'review_status': task.review_status}
    task.review_status = 'rejected'
    task.reviewed_by = operator
    task.rejection_reason = reason
    task.reviewed_at = datetime.now(UTC)
    _append_event(
        db,
        task_id=task.id,
        event_type='rejected',
        operator=operator,
        before=before,
        after={'review_status': task.review_status},
        comment=reason,
    )
    db.commit()
    db.refresh(task)
    return task


def list_review_events(db: Session, *, task_id: int) -> list[Any]:
    return list(
        db.scalars(
            select(PolicyReviewEventORM)
            .where(PolicyReviewEventORM.task_id == task_id)
            .order_by(PolicyReviewEventORM.id.asc())
        ).all()
    )


def _build_condition_node(tree: dict[str, Any]) -> PolicyConditionNode:
    normalized = normalize_condition_tree(tree or {})
    return _build_condition_node_from_normalized(normalized)


def _build_condition_node_from_normalized(tree: dict[str, Any]) -> PolicyConditionNode:
    if tree.get('type') == 'predicate' or (tree.get('field') and tree.get('operator')):
        return PolicyConditionNode(
            id=str(tree.get('id') or 'node'),
            description=str(tree.get('description') or ''),
            field=str(tree.get('field')),
            operator=str(tree.get('operator')),
            value=tree.get('value'),
            must=bool(tree.get('must', True)),
            node_type='predicate',
            source_quotes=list(tree.get('source_quotes') or []),
            source_locators=list(tree.get('source_locators') or []),
            notes=list(tree.get('notes') or []),
            confidence=tree.get('confidence'),
        )
    relation = str(tree.get('logic') or 'and').upper()
    node = PolicyConditionNode(
        id=str(tree.get('id') or 'root'),
        description=str(tree.get('description') or ''),
        relation=relation,
        must=bool(tree.get('must', True)),
        node_type='group',
        schema_version=str(tree.get('schema_version') or '') or None,
        compile_metadata=dict(tree.get('compile_metadata') or {}),
        applicable_subjects=list(tree.get('applicable_subjects') or []),
        source_quotes=list(tree.get('source_quotes') or []),
        source_locators=list(tree.get('source_locators') or []),
        notes=list(tree.get('notes') or []),
        confidence=tree.get('confidence'),
    )
    node.children = [_build_condition_node_from_normalized(child) for child in (tree.get('children') or []) if isinstance(child, dict)]
    return node


def refresh_review_task_condition_tree(db: Session, *, task_id: int, operator: str | None = None) -> PolicyReviewTaskORM | None:
    task = db.get(PolicyReviewTaskORM, task_id)
    if task is None:
        return None
    before = {
        'draft_status': task.draft_status,
        'draft_summary': task.draft_summary,
        'draft_category': task.draft_category,
        'draft_condition_tree': task.draft_condition_tree,
    }
    try:
        draft_payload = _compile_task_draft(task)
        task.draft_status = 'success'
        task.draft_title = draft_payload['title']
        task.draft_source = draft_payload['source']
        task.draft_summary = draft_payload['summary']
        task.draft_category = draft_payload['category']
        task.draft_condition_tree = draft_payload['condition_tree']
        event_type = 'condition_tree_refreshed'
        comment = None
    except Exception as exc:  # pragma: no cover
        task.draft_status = 'failed'
        task.draft_condition_tree = _build_failed_condition_tree(str(exc))
        event_type = 'condition_tree_refresh_failed'
        comment = str(exc)
    db.flush()
    _append_event(
        db,
        task_id=task.id,
        event_type=event_type,
        operator=operator,
        before=before,
        after={
            'draft_status': task.draft_status,
            'draft_summary': task.draft_summary,
            'draft_category': task.draft_category,
            'draft_condition_tree': task.draft_condition_tree,
            'condition_tree_meta': extract_condition_tree_metadata(task.draft_condition_tree or {}),
        },
        comment=comment,
    )
    db.commit()
    db.refresh(task)
    return task


def _normalize_optional_date(value: dt.date | str | None) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str) and value:
        return dt.date.fromisoformat(value)
    return None
