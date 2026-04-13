from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class UserProfileIn(BaseModel):
    name: str
    type: str
    area: float = Field(ge=0)
    green_cert: bool = False
    irrigation: str = ""
    extra_data: dict = Field(default_factory=dict)


class UserProfileOut(UserProfileIn):
    id: int


class UserProfileWithHistoryOut(UserProfileOut):
    match_records: list[dict] = Field(default_factory=list)

class OnboardingRefineIn(BaseModel):
    answers: dict = Field(default_factory=dict)


class ProfileRefineOut(BaseModel):
    profile: UserProfileIn
    source: Literal["local", "deepseek"]

