from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class SessionResponse(BaseModel):
    token_type: str = "cookie"
    id: int
    username: str
    role: str


class SessionMeResponse(BaseModel):
    authenticated: bool
    role: str | None = None
    id: int | None = None
    username: str | None = None


class SessionInfo(BaseModel):
    session_id: str
    principal_role: str
    principal_id: int
    created_at: str
    expires_at: str
    revoked_at: str | None = None
    user_agent: str | None = None
    ip: str | None = None

