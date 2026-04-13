from __future__ import annotations

import datetime as dt

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth_models import AdminUserORM, AuthSessionORM, EndUserORM
from app.services.tokens import decode_token


def get_cookie_names(role: str) -> tuple[str, str]:
    if role == "admin":
        return ("ncwg_admin_access", "ncwg_admin_refresh")
    return ("ncwg_user_access", "ncwg_user_refresh")


def _raise_unauthorized(detail: str = "Unauthorized"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def get_current_principal(
    *,
    expected_role: str,
    db: Session,
    request: Request,
    access_token: str | None,
):
    if not access_token:
        _raise_unauthorized("Missing access token")
    try:
        payload = decode_token(access_token)
    except Exception:
        _raise_unauthorized("Invalid access token")

    if payload.get("typ") != "access":
        _raise_unauthorized("Invalid access token type")
    role = payload.get("role")
    if role != expected_role:
        _raise_unauthorized("Role mismatch")

    sid = payload.get("sid")
    pid = payload.get("pid")
    if not sid or pid is None:
        _raise_unauthorized("Invalid token payload")
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        _raise_unauthorized("Invalid token payload")

    session = db.get(AuthSessionORM, sid)
    if not session or session.revoked_at is not None:
        _raise_unauthorized("Session revoked")

    # 与 refresh 令牌生命周期对齐：会话过期后拒绝访问（不依赖仅 JWT exp）
    now = dt.datetime.utcnow()
    if session.expires_at <= now:
        _raise_unauthorized("Session expired")

    if session.principal_role != expected_role or session.principal_id != pid_int:
        _raise_unauthorized("Session principal mismatch")

    try:
        session.last_seen_at = now
    except Exception:
        pass

    if expected_role == "admin":
        user = db.get(AdminUserORM, pid_int)
    else:
        user = db.get(EndUserORM, pid_int)
    if not user:
        _raise_unauthorized("Principal not found")
    return user


def get_current_admin(
    request: Request,
    db: Session = Depends(get_db),
    ncwg_admin_access: str | None = Cookie(default=None),
):
    return get_current_principal(expected_role="admin", db=db, request=request, access_token=ncwg_admin_access)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    ncwg_user_access: str | None = Cookie(default=None),
):
    return get_current_principal(expected_role="user", db=db, request=request, access_token=ncwg_user_access)

