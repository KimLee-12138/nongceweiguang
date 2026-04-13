from __future__ import annotations

from pydantic import BaseModel, Field


class ConversationOut(BaseModel):
    id: int
    title: str
    last_mode: str
    last_profile_id: int | None = None


class ConversationDetailOut(BaseModel):
    conversation: ConversationOut
    messages: list[dict] = Field(default_factory=list)


class ChatStreamRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(min_length=1, max_length=8000)
    mode: str = "interpret"  # match | agri_llm | interpret
    profile_id: int | None = None
    policy_id: int | None = None

