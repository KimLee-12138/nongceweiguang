from __future__ import annotations

import datetime as dt
import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.api.v1.schemas_auth import LoginRequest, SessionInfo, SessionMeResponse, SessionResponse
from app.core.config import get_settings
from app.db.session import get_db
from app.models.auth_models import AuthRefreshTokenORM, AuthSessionORM, EndUserORM
from app.services.passwords import hash_password, verify_password
from app.services.tokens import decode_token, hash_refresh_token, issue_access_token, issue_refresh_token


router = APIRouter(prefix="/user-auth", tags=["auth-user"])


def _utcnow() -> dt.datetime:
    return dt.datetime.utcnow()


def _set_user_cookies(response: Response, *, access_token: str, refresh_token: str):
    response.set_cookie("ncwg_user_access", access_token, httponly=True, samesite="lax", path="/")
    response.set_cookie("ncwg_user_refresh", refresh_token, httponly=True, samesite="lax", path="/")


def _clear_user_cookies(response: Response):
    response.delete_cookie("ncwg_user_access", path="/")
    response.delete_cookie("ncwg_user_refresh", path="/")


def _rollback_quietly(db: Session) -> None:
    try:
        db.rollback()
    except Exception:
        pass


def _service_unavailable(detail: str, db: Session, error: Exception):
    _rollback_quietly(db)
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail) from error


@router.post("/register", response_model=SessionResponse)
def register(payload: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    username = payload.username.strip()
    if len(username) < 3 or len(username) > 32:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名长度需为 3~32")
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码至少 6 位")
    try:
        exists = db.scalar(select(EndUserORM).where(EndUserORM.username == username))
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        user = EndUserORM(username=username, password_hash=hash_password(payload.password))
        db.add(user)
        db.flush()

        settings = get_settings()
        session_id = secrets.token_hex(16)
        expires_at = _utcnow() + dt.timedelta(seconds=settings.REFRESH_TOKEN_TTL_SECONDS)
        db.add(
            AuthSessionORM(
                session_id=session_id,
                principal_role="user",
                principal_id=user.id,
                expires_at=expires_at,
                user_agent=request.headers.get("user-agent"),
                ip=request.client.host if request.client else None,
            )
        )
        db.flush()

        refresh_token, jti = issue_refresh_token(session_id=session_id, principal_role="user", principal_id=user.id)
        db.add(AuthRefreshTokenORM(jti=jti, session_id=session_id, token_hash=hash_refresh_token(refresh_token), expires_at=expires_at))

        access_token = issue_access_token(session_id=session_id, principal_role="user", principal_id=user.id)
        _set_user_cookies(response, access_token=access_token, refresh_token=refresh_token)
        db.commit()
        return SessionResponse(id=user.id, username=user.username, role="user")
    except HTTPException:
        raise
    except SQLAlchemyError as error:
        _service_unavailable("认证服务暂时不可用，请检查数据库连接后重试。", db, error)


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    username = payload.username.strip()
    if len(username) < 3 or len(username) > 32:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名长度需为 3~32")
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码至少 6 位")
    try:
        user = db.scalar(select(EndUserORM).where(EndUserORM.username == username))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        settings = get_settings()
        session_id = secrets.token_hex(16)
        expires_at = _utcnow() + dt.timedelta(seconds=settings.REFRESH_TOKEN_TTL_SECONDS)
        db.add(
            AuthSessionORM(
                session_id=session_id,
                principal_role="user",
                principal_id=user.id,
                expires_at=expires_at,
                user_agent=request.headers.get("user-agent"),
                ip=request.client.host if request.client else None,
            )
        )
        db.flush()

        refresh_token, jti = issue_refresh_token(session_id=session_id, principal_role="user", principal_id=user.id)
        db.add(AuthRefreshTokenORM(jti=jti, session_id=session_id, token_hash=hash_refresh_token(refresh_token), expires_at=expires_at))

        access_token = issue_access_token(session_id=session_id, principal_role="user", principal_id=user.id)
        _set_user_cookies(response, access_token=access_token, refresh_token=refresh_token)
        db.commit()
        return SessionResponse(id=user.id, username=user.username, role="user")
    except HTTPException:
        raise
    except SQLAlchemyError as error:
        _service_unavailable("认证服务暂时不可用，请检查数据库连接后重试。", db, error)


@router.get("/me", response_model=SessionMeResponse)
def me(db: Session = Depends(get_db), ncwg_user_access: str | None = Cookie(default=None)):
    if not ncwg_user_access:
        return SessionMeResponse(authenticated=False)
    try:
        payload = decode_token(ncwg_user_access)
    except Exception:
        return SessionMeResponse(authenticated=False)
    if payload.get("typ") != "access" or payload.get("role") != "user":
        return SessionMeResponse(authenticated=False)
    sid = payload.get("sid")
    if not sid:
        return SessionMeResponse(authenticated=False)
    try:
        session = db.get(AuthSessionORM, sid)
        if not session or session.revoked_at is not None:
            return SessionMeResponse(authenticated=False)
        if session.expires_at <= _utcnow():
            return SessionMeResponse(authenticated=False)
        pid = payload.get("pid")
        try:
            pid_int = int(pid) if pid is not None else None
        except (TypeError, ValueError):
            return SessionMeResponse(authenticated=False)
        if pid_int is None:
            return SessionMeResponse(authenticated=False)
        end_user = db.get(EndUserORM, pid_int)
        uname = end_user.username if end_user else None
        return SessionMeResponse(authenticated=True, role="user", id=pid_int, username=uname)
    except SQLAlchemyError as error:
        _service_unavailable("认证状态暂时不可用，请检查数据库连接后重试。", db, error)


@router.post("/refresh", response_model=SessionResponse)
def refresh(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    ncwg_user_refresh: str | None = Cookie(default=None),
):
    if not ncwg_user_refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        payload = decode_token(ncwg_user_refresh)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("typ") != "refresh" or payload.get("role") != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token type")

    sid = payload.get("sid")
    jti = payload.get("jti")
    pid = payload.get("pid")
    if not sid or not jti or not pid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")

    try:
        session = db.get(AuthSessionORM, sid)
        if not session or session.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked")
        if session.expires_at <= _utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

        rt = db.get(AuthRefreshTokenORM, jti)
        if not rt or rt.revoked_at is not None or rt.rotated_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
        if rt.expires_at <= _utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        if rt.token_hash != hash_refresh_token(ncwg_user_refresh):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch")

        settings = get_settings()
        now = _utcnow()
        rt.rotated_at = now
        new_refresh_token, new_jti = issue_refresh_token(session_id=sid, principal_role="user", principal_id=int(pid))
        new_expires = now + dt.timedelta(seconds=settings.REFRESH_TOKEN_TTL_SECONDS)
        db.add(AuthRefreshTokenORM(jti=new_jti, session_id=sid, token_hash=hash_refresh_token(new_refresh_token), expires_at=new_expires))

        session.expires_at = new_expires

        new_access_token = issue_access_token(session_id=sid, principal_role="user", principal_id=int(pid))
        _set_user_cookies(response, access_token=new_access_token, refresh_token=new_refresh_token)

        user = db.get(EndUserORM, int(pid))
        if not user:
            _clear_user_cookies(response)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        db.commit()
        return SessionResponse(id=user.id, username=user.username, role="user")
    except HTTPException:
        raise
    except SQLAlchemyError as error:
        _service_unavailable("会话刷新暂时不可用，请检查数据库连接后重试。", db, error)


@router.post("/logout-all")
def logout_all(
    response: Response,
    db: Session = Depends(get_db),
    ncwg_user_access: str | None = Cookie(default=None),
):
    # 退出所有会话：revoke sessions + refresh tokens，再清 cookie
    pid = None
    if ncwg_user_access:
        try:
            payload = decode_token(ncwg_user_access)
            if payload.get("typ") == "access" and payload.get("role") == "user":
                pid = payload.get("pid")
        except Exception:
            pid = None

    if pid is not None:
        try:
            pid_int = int(pid)
        except (TypeError, ValueError):
            pid_int = None
    else:
        pid_int = None

    if pid_int is not None:
        now = _utcnow()
        sessions = db.scalars(
            select(AuthSessionORM).where(AuthSessionORM.principal_role == "user", AuthSessionORM.principal_id == pid_int)
        ).all()
        session_ids = [s.session_id for s in sessions]
        for s in sessions:
            if s.revoked_at is None:
                s.revoked_at = now
        if session_ids:
            rts = db.scalars(select(AuthRefreshTokenORM).where(AuthRefreshTokenORM.session_id.in_(session_ids))).all()
            for rt in rts:
                if rt.revoked_at is None:
                    rt.revoked_at = now
        db.commit()

    _clear_user_cookies(response)
    return {"ok": True}


@router.get("/sessions", response_model=list[SessionInfo])
def list_sessions(db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    sessions = db.scalars(
        select(AuthSessionORM).where(AuthSessionORM.principal_role == "user", AuthSessionORM.principal_id == user.id)
    ).all()
    return [
        SessionInfo(
            session_id=s.session_id,
            principal_role=s.principal_role,
            principal_id=s.principal_id,
            created_at=s.created_at.isoformat(),
            expires_at=s.expires_at.isoformat(),
            revoked_at=s.revoked_at.isoformat() if s.revoked_at else None,
            user_agent=s.user_agent,
            ip=s.ip,
        )
        for s in sessions
    ]


@router.post("/sessions/{session_id}/revoke")
def revoke_session(session_id: str, db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    session = db.get(AuthSessionORM, session_id)
    if not session or session.principal_role != "user" or session.principal_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    now = _utcnow()
    if session.revoked_at is None:
        session.revoked_at = now
    rts = db.scalars(select(AuthRefreshTokenORM).where(AuthRefreshTokenORM.session_id == session.session_id)).all()
    for rt in rts:
        if rt.revoked_at is None:
            rt.revoked_at = now
    db.commit()
    return {"ok": True}

