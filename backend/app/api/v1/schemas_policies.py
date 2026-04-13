from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field


class PolicyIn(BaseModel):
    title: str
    source: str = ""
    version: str | None = None
    summary: str = ""
    raw_text_ref: str | None = None
    file_type: str | None = None
    validity_status: str = "有效"
    effective_date: dt.date | None = None
    expiry_date: dt.date | None = None
    condition_tree: dict = Field(default_factory=dict)


class PolicyOut(PolicyIn):
    id: int
    condition_tree_meta: dict = Field(default_factory=dict)


class MatchEvaluateRequest(BaseModel):
    condition_tree: dict
    profile: dict


class MatchEvaluateResponse(BaseModel):
    summary: dict


class CompileTextRequest(BaseModel):
    raw_text: str = ""
    title: str | None = None
    source: str | None = None


class CompileTextResponse(BaseModel):
    condition_tree: dict
    detailed_condition_tree: dict = Field(default_factory=dict)
    summary: str
    category: str = ""
    mode: str = "stub"
    compile_quality: str = "stub"
    missing_information: list[str] = Field(default_factory=list)
    uncertain_points: list[str] = Field(default_factory=list)
    applicable_subjects: list[str] = Field(default_factory=list)

