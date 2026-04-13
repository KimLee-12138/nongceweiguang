from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserProfileORM(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("end_users.id"), index=True, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    area: Mapped[float] = mapped_column(nullable=False)
    green_cert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    irrigation: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class PolicyORM(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    raw_text_ref: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    validity_status: Mapped[str] = mapped_column(String(32), default="有效", nullable=False)
    effective_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    condition_tree: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class MatchRecordORM(Base):
    __tablename__ = "match_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profiles.id"), index=True, nullable=False)
    policy_id: Mapped[int] = mapped_column(Integer, ForeignKey("policies.id"), index=True, nullable=False)

    fully_matched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    match_detail: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # SRS 数据字典中保留的历史字段（当前实现不做 ROI 计算）
    expected_subsidy: Mapped[float] = mapped_column(default=0.0, nullable=False)
    total_cost_to_comply: Mapped[float] = mapped_column(default=0.0, nullable=False)
    roi: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)


class ChatConversationORM(Base):
    __tablename__ = "chat_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("end_users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="新会话", nullable=False)
    last_message_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    last_mode: Mapped[str] = mapped_column(String(32), default="interpret", nullable=False)
    last_profile_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_profiles.id"), nullable=True)
    draft_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class ChatMessageORM(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_conversations.id"), index=True, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user/assistant/system
    status: Mapped[str] = mapped_column(String(16), default="done", nullable=False)  # done/streaming/failed/cancelled

    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    profile_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user_profiles.id"), nullable=True)
    profile_snapshot_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    citation_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    render_payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class CompassReportORM(Base):
    __tablename__ = "compass_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    published_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)


class CompassGlossaryORM(Base):
    __tablename__ = "compass_glossary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="政策主题", nullable=False)
    aliases_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    published_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class HubeiPolicyRawORM(Base):
    __tablename__ = "hubei_policies_raw"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doc_no: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publish_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    column_name: Mapped[str | None] = mapped_column("column", String(100), nullable=True)
    file_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    topic_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    validity_status: Mapped[str] = mapped_column(String(32), default="有效", nullable=False)
    effective_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    page_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    attachment_urls: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    html_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )

