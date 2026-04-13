from __future__ import annotations

import datetime as dt

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PolicyReviewTaskORM(Base):
    __tablename__ = "policy_review_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw_policy_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    raw_text_ref: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    review_status: Mapped[str] = mapped_column(String(16), index=True, default="pending", nullable=False)
    draft_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    ai_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)

    ai_risk_points_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    ai_evidence_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    draft_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    draft_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    draft_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    draft_file_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    draft_validity_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    draft_effective_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    draft_expiry_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    draft_condition_tree: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ai_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    approved_policy_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("policies.id"), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class PolicyReviewEventORM(Base):
    __tablename__ = "policy_review_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("policy_review_tasks.id"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    operator: Mapped[str | None] = mapped_column(String(64), nullable=True)
    before_snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
