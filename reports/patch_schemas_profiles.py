from pathlib import Path

p = Path("backend/app/api/v1/schemas_profiles.py")
t = p.read_text(encoding="utf-8")
if "OnboardingRefineIn" in t:
    raise SystemExit(0)
t = t.replace(
    "from pydantic import BaseModel, Field",
    "from typing import Literal\n\nfrom pydantic import BaseModel, Field",
)
extra = """

class OnboardingRefineIn(BaseModel):
    answers: dict = Field(default_factory=dict)


class ProfileRefineOut(BaseModel):
    profile: UserProfileIn
    source: Literal["local", "deepseek"]
"""
p.write_text(t.rstrip() + extra + "\n", encoding="utf-8")
