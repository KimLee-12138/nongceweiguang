from __future__ import annotations

from typing import Any

from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from app.models.business_models import HubeiPolicyRawORM, PolicyORM
from app.models.policy_review_models import PolicyReviewTaskORM
from app.services.condition_tree_service import extract_condition_tree_metadata, normalize_condition_tree
from app.services.crawler_service import _fetch_html, _page_text
from app.services.policy_compile_service import compile_policy_text


class ConditionTreeRefreshError(RuntimeError):
    pass


def refresh_policy_condition_tree(db: Session, *, policy_id: int) -> tuple[PolicyORM | None, dict[str, Any] | None]:
    policy = db.get(PolicyORM, policy_id)
    if policy is None:
        return None, None

    raw_text, source_ref = resolve_policy_raw_text(db, policy)
    if not raw_text:
        raise ConditionTreeRefreshError('缺少可用于生成条件树的政策原文')

    before_meta = extract_condition_tree_metadata(policy.condition_tree or {})
    compiled = compile_policy_text(raw_text, title=policy.title, source=policy.source)
    policy.summary = compiled.get('summary') or policy.summary or ''
    policy.condition_tree = normalize_condition_tree(compiled.get('condition_tree') or {})
    if not policy.raw_text_ref and source_ref:
        policy.raw_text_ref = source_ref
    db.commit()
    db.refresh(policy)
    return policy, {
        'before': before_meta,
        'after': extract_condition_tree_metadata(policy.condition_tree or {}),
        'source_ref': source_ref,
    }


def resolve_policy_raw_text(db: Session, policy: PolicyORM) -> tuple[str, str | None]:
    review_task = db.scalar(
        select(PolicyReviewTaskORM)
        .where(PolicyReviewTaskORM.approved_policy_id == policy.id)
        .order_by(desc(PolicyReviewTaskORM.id))
        .limit(1)
    )
    if review_task and (review_task.raw_text or '').strip():
        return review_task.raw_text, review_task.raw_text_ref or review_task.source_ref

    if policy.raw_text_ref:
        raw_row = db.scalar(select(HubeiPolicyRawORM).where(HubeiPolicyRawORM.page_url == policy.raw_text_ref).limit(1))
        if raw_row and (raw_row.full_text or raw_row.html_text or '').strip():
            return (raw_row.full_text or raw_row.html_text or '').strip(), raw_row.page_url

    raw_by_title = db.scalar(
        select(HubeiPolicyRawORM)
        .where(
            or_(
                HubeiPolicyRawORM.title == policy.title,
                HubeiPolicyRawORM.page_url == policy.raw_text_ref,
            )
        )
        .order_by(desc(HubeiPolicyRawORM.id))
        .limit(1)
    )
    if raw_by_title and (raw_by_title.full_text or raw_by_title.html_text or '').strip():
        return (raw_by_title.full_text or raw_by_title.html_text or '').strip(), raw_by_title.page_url

    if policy.raw_text_ref and str(policy.raw_text_ref).startswith(('http://', 'https://')):
        try:
            html_text = _fetch_html(policy.raw_text_ref)
            plain_text = _page_text(html_text)
            if plain_text.strip():
                return plain_text.strip(), policy.raw_text_ref
        except Exception as exc:  # pragma: no cover
            raise ConditionTreeRefreshError(f'抓取政策原文失败：{exc}') from exc

    return '', policy.raw_text_ref
