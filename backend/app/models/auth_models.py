from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdminUserORM(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)


class EndUserORM(Base):
    __tablename__ = "end_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)


class AuthSessionORM(Base):
    __tablename__ = "auth_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    principal_role: Mapped[str] = mapped_column(Enum("admin", "user"), index=True, nullable=False)
    principal_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    last_seen_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)


class AuthRefreshTokenORM(Base):
    __tablename__ = "auth_refresh_tokens"

    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("auth_sessions.session_id"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    rotated_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)


class RequestRateLimitORM(Base):
    __tablename__ = "request_rate_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    window_started_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_until: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=lambda: dt.datetime.utcnow(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=lambda: dt.datetime.utcnow(), onupdate=lambda: dt.datetime.utcnow(), nullable=False
    )

