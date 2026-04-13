from pathlib import Path
p = Path("backend/app/api/v1/profile_routes.py")
t = p.read_text(encoding="utf-8")
if "onboarding/refine" in t:
    raise SystemExit(0)
insert = '''
from app.api.v1.schemas_profiles import UserProfileIn, UserProfileOut, UserProfileWithHistoryOut
'''
old = "from app.api.v1.schemas_profiles import UserProfileIn, UserProfileOut, UserProfileWithHistoryOut"
new = "from app.api.v1.schemas_profiles import OnboardingRefineIn, ProfileRefineOut, UserProfileIn, UserProfileOut, UserProfileWithHistoryOut"
if old not in t:
    raise SystemExit(f"replace failed: {old!r}")
t = t.replace(old, new, 1)
t = t.replace(
    "from app.services.match_engine import to_match_summary",
    "from app.services.match_engine import to_match_summary\nfrom app.services.profile_onboarding_service import refine_onboarding",
)
block = '''

@router.post("/onboarding/refine", response_model=ProfileRefineOut)
def refine_onboarding_profile(
    payload: OnboardingRefineIn,
    user: EndUserORM = Depends(get_current_user),
):
    profile_dict, source = refine_onboarding(payload.answers or {}, use_model=True)
    return ProfileRefineOut(profile=UserProfileIn(**profile_dict), source=source)
'''
# insert after create_profile function (after first return of create_profile)
marker = "    return UserProfileOut(**payload.model_dump(), id=profile.id)\n\n\n@router.get"
if marker not in t:
    raise SystemExit("marker not found")
t = t.replace(marker, "    return UserProfileOut(**payload.model_dump(), id=profile.id)" + block + "\n\n@router.get", 1)
p.write_text(t, encoding="utf-8")
print("ok")
