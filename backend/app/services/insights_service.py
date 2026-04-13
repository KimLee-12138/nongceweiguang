from __future__ import annotations

import time
from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.business_models import HubeiPolicyRawORM, MatchRecordORM, PolicyORM, UserProfileORM


_cache = {"ts": 0.0, "value": None}


def build_kpi_snapshot(db: Session) -> dict:
    # 300s 缓存（概要设计）
    now = time.time()
    if _cache["value"] is not None and (now - _cache["ts"]) < 300:
        return _cache["value"]

    policy_count = db.scalar(select(func.count()).select_from(PolicyORM)) or 0
    profile_count = db.scalar(select(func.count()).select_from(UserProfileORM)) or 0
    match_count = db.scalar(select(func.count()).select_from(MatchRecordORM)) or 0
    raw_policy_count = db.scalar(select(func.count()).select_from(HubeiPolicyRawORM)) or 0
    snapshot = {
        "policy_count": int(policy_count),
        "profile_count": int(profile_count),
        "match_record_count": int(match_count),
        "raw_policy_count": int(raw_policy_count),
    }
    _cache["ts"] = now
    _cache["value"] = snapshot
    return snapshot


def build_trend_analysis(db: Session) -> dict:
    rows = db.scalars(select(HubeiPolicyRawORM).order_by(HubeiPolicyRawORM.publish_date.desc())).all()
    bucket = Counter()
    for row in rows:
        if row.publish_date:
            bucket[row.publish_date.strftime("%Y-%m")] += 1
    items = [{"period": period, "count": bucket[period]} for period in sorted(bucket.keys())[-12:]]
    return {"items": items}


def build_source_distribution(db: Session) -> dict:
    rows = db.scalars(select(HubeiPolicyRawORM)).all()
    counter = Counter((row.issuer or "未知来源") for row in rows)
    items = [{"source": name, "count": count} for name, count in counter.most_common(12)]
    return {"items": items}


def build_audience_distribution(db: Session) -> dict:
    rows = db.scalars(select(PolicyORM)).all()
    counter = Counter()
    for row in rows:
        tree = row.condition_tree or {}
        _accumulate_audience_tags(tree, counter)
    items = [{"audience": key, "count": value} for key, value in counter.most_common(12)]
    return {"items": items}


def _accumulate_audience_tags(node: dict, counter: Counter) -> None:
    if not isinstance(node, dict):
        return
    field = node.get("field")
    value = node.get("value")
    if field == "type":
        if isinstance(value, list):
            for item in value:
                counter[str(item)] += 1
        elif value is not None:
            counter[str(value)] += 1
    for child in node.get("children") or []:
        _accumulate_audience_tags(child, counter)

