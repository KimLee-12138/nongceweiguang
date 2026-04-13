from __future__ import annotations

import datetime as dt
import json

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemConfigORM(Base):
    __tablename__ = "system_config"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    def get_json_value(self) -> dict:
        try:
            data = json.loads(self.value or "{}")
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def set_json_value(self, data: dict) -> None:
        self.value = json.dumps(data or {}, ensure_ascii=False)


class AdminOperationRunORM(Base):
    __tablename__ = "admin_operation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, default="pending", nullable=False)  # pending/running/success/partial/failed
    trigger_source: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)

    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    summary_message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    progress_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class AdminOperationRunItemORM(Base):
    __tablename__ = "admin_operation_run_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("admin_operation_runs.id"), index=True, nullable=False)
    item_index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, default="pending", nullable=False)  # pending/running/success/failed

    input_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )


class TelemetryEventORM(Base):
    __tablename__ = "telemetry_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), index=True, default="info", nullable=False)  # info/success/error/partial/failed
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason_code: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)


class AutoCrawlerRunORM(Base):
    __tablename__ = "auto_crawler_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    source_ids_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    max_pages: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    summary_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

