from __future__ import annotations

import datetime as dt
from typing import Any

from app.schemas.policy import Policy
from app.services.model_provider import generate_review_payload


def generate_review_ai_payload(
    *,
    raw_text: str,
    draft_policy: Policy,
    draft_summary: str | None,
    draft_condition_tree: dict[str, Any],
    title: str | None,
    source: str | None,
    draft_file_type: str | None,
    draft_validity_status: str | None,
    draft_effective_date: dt.date | None,
    draft_expiry_date: dt.date | None,
) -> dict[str, Any]:
    _ = draft_policy
    return generate_review_payload(
        raw_text=raw_text,
        draft_summary=draft_summary,
        draft_condition_tree=draft_condition_tree,
        title=title,
        source=source,
        draft_file_type=draft_file_type,
        draft_validity_status=draft_validity_status,
        draft_effective_date=draft_effective_date,
        draft_expiry_date=draft_expiry_date,
    )
