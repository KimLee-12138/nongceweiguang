from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.api.v1.schemas_profiles import OnboardingRefineIn, ProfileRefineOut, UserProfileIn, UserProfileOut, UserProfileWithHistoryOut
from app.db.session import get_db
from app.models.auth_models import EndUserORM
from app.models.business_models import MatchRecordORM, PolicyORM, UserProfileORM
from app.services.match_engine import to_match_summary
from app.services.profile_onboarding_service import refine_onboarding


router = APIRouter(prefix="/profiles", tags=["profiles"])


def _to_profile_out(profile: UserProfileORM) -> UserProfileOut:
    return UserProfileOut(
        id=profile.id,
        name=profile.name,
        type=profile.type,
        area=profile.area,
        green_cert=profile.green_cert,
        irrigation=profile.irrigation,
        extra_data=profile.extra_data or {},
    )


def _get_effective_profile(db: Session, user_id: int) -> UserProfileORM | None:
    return db.scalars(
        select(UserProfileORM)
        .where(UserProfileORM.owner_user_id == user_id)
        .order_by(desc(UserProfileORM.updated_at), desc(UserProfileORM.id))
        .limit(1)
    ).first()


def _get_effective_profile_or_404(db: Session, user: EndUserORM, profile_id: int) -> UserProfileORM:
    profile = _get_effective_profile(db, user.id)
    if not profile or profile.id != profile_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


def _recommendation_score(summary: dict) -> tuple[float, str]:
    must_total = int(summary.get("must_total") or 0)
    should_total = int(summary.get("should_total") or 0)
    must_failed = int(summary.get("must_failed") or len(summary.get("failed_must_nodes") or []))
    should_failed = int(summary.get("should_failed") or len(summary.get("failed_should_nodes") or []))

    must_ratio = 1.0 if must_total == 0 else max(0.0, (must_total - must_failed) / max(1, must_total))
    should_ratio = 1.0 if should_total == 0 else max(0.0, (should_total - should_failed) / max(1, should_total))
    score = max(0.0, min(1.0, must_ratio * 0.88 + should_ratio * 0.12))

    if bool(summary.get("fully_matched")):
        fit = "high"
    elif must_ratio >= 0.6:
        fit = "medium"
    else:
        fit = "low"
    return round(score, 4), fit


@router.post("", response_model=UserProfileOut)
def create_profile(
    payload: UserProfileIn,
    db: Session = Depends(get_db),
    _user: EndUserORM = Depends(get_current_user),
):
    existing = _get_effective_profile(db, _user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="每个用户只能创建一个画像，请在“管理画像”中修改当前画像。",
        )
    profile = UserProfileORM(
        owner_user_id=_user.id,
        name=payload.name,
        type=payload.type,
        area=payload.area,
        green_cert=payload.green_cert,
        irrigation=payload.irrigation,
        extra_data=payload.extra_data or {},
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_profile_out(profile)

@router.post("/onboarding/refine", response_model=ProfileRefineOut)
def refine_onboarding_profile(
    payload: OnboardingRefineIn,
    _user: EndUserORM = Depends(get_current_user),
):
    profile_dict, source = refine_onboarding(payload.answers or {}, use_model=True)
    return ProfileRefineOut(profile=UserProfileIn(**profile_dict), source=source)


@router.get("", response_model=list[UserProfileOut])
def list_profiles(db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    profile = _get_effective_profile(db, user.id)
    if not profile:
        return []
    return [_to_profile_out(profile)]


@router.get("/{profile_id}", response_model=UserProfileWithHistoryOut)
def get_profile(profile_id: int, db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    profile = _get_effective_profile_or_404(db, user, profile_id)
    records = db.scalars(
        select(MatchRecordORM)
        .where(MatchRecordORM.user_profile_id == profile.id)
        .order_by(desc(MatchRecordORM.id))
        .limit(20)
    ).all()
    return UserProfileWithHistoryOut(
        id=profile.id,
        name=profile.name,
        type=profile.type,
        area=profile.area,
        green_cert=profile.green_cert,
        irrigation=profile.irrigation,
        extra_data=profile.extra_data or {},
        match_records=[
            {
                "id": r.id,
                "policy_id": r.policy_id,
                "fully_matched": r.fully_matched,
                "match_detail": r.match_detail,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ],
    )


@router.put("/{profile_id}", response_model=UserProfileOut)
def update_profile(
    profile_id: int,
    payload: UserProfileIn,
    db: Session = Depends(get_db),
    user: EndUserORM = Depends(get_current_user),
):
    profile = _get_effective_profile_or_404(db, user, profile_id)
    profile.name = payload.name
    profile.type = payload.type
    profile.area = payload.area
    profile.green_cert = payload.green_cert
    profile.irrigation = payload.irrigation
    profile.extra_data = payload.extra_data or {}
    db.commit()
    db.refresh(profile)
    return _to_profile_out(profile)


@router.get("/{profile_id}/suggested-policies")
def suggested_policies(
    profile_id: int,
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: EndUserORM = Depends(get_current_user),
):
    profile = _get_effective_profile_or_404(db, user, profile_id)

    profile_dict = {
        "name": profile.name,
        "type": profile.type,
        "area": profile.area,
        "green_cert": profile.green_cert,
        "irrigation": profile.irrigation,
        "extra_data": profile.extra_data or {},
    }

    policies = db.scalars(select(PolicyORM).order_by(desc(PolicyORM.id)).offset(offset).limit(200)).all()
    scored = []
    for p in policies:
        summary = to_match_summary(p.condition_tree or {}, profile_dict)
        score, fit_label = _recommendation_score(summary)
        scored.append(
            {
                "policy_id": p.id,
                "title": p.title,
                "source": p.source,
                "summary": p.summary,
                "raw_text_ref": p.raw_text_ref,
                "fully_matched": summary["fully_matched"],
                "fit_label": fit_label,
                "score": round(score, 3),
                "match_score": summary.get("match_score", round(score, 3)),
                "must_failed": summary.get("must_failed", len(summary.get("failed_must_nodes") or [])),
                "should_failed": summary.get("should_failed", len(summary.get("failed_should_nodes") or [])),
                "risk_warnings": summary.get("risk_warnings") or [],
                "action_steps": summary.get("action_steps") or [],
                "match_summary": summary,
            }
        )

    scored.sort(
        key=lambda x: (
            x["fully_matched"],
            x["score"],
            -(x["must_failed"] + x["should_failed"]),
            -x["policy_id"],
        ),
        reverse=True,
    )
    return {"items": scored[: max(1, min(limit, 50))]}

