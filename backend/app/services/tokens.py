from __future__ import annotations

import datetime as dt
import hashlib
import secrets
from dataclasses import dataclass

import jwt

from app.core.config import get_settings


def _utcnow() -> dt.datetime:
    # 使用 timezone-aware UTC，避免 naive datetime.timestamp() 采用“本地时区”导致 iat/exp 偏移
    return dt.datetime.now(dt.timezone.utc)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_jti: str


def issue_access_token(*, session_id: str, principal_role: str, principal_id: int) -> str:
    settings = get_settings()
    now = _utcnow()
    payload = {
        "typ": "access",
        "sid": session_id,
        "role": principal_role,
        "pid": principal_id,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(seconds=settings.ACCESS_TOKEN_TTL_SECONDS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def issue_refresh_token(*, session_id: str, principal_role: str, principal_id: int) -> tuple[str, str]:
    settings = get_settings()
    now = _utcnow()
    jti = secrets.token_hex(16)
    payload = {
        "typ": "refresh",
        "jti": jti,
        "sid": session_id,
        "role": principal_role,
        "pid": principal_id,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(seconds=settings.REFRESH_TOKEN_TTL_SECONDS)).timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token, jti


def hash_refresh_token(token: str) -> str:
    # 使用 hex 字符串存库，避免 MySQL 将列建成 utf8 文本时无法写入原始二进制（1366 Incorrect string value）
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

