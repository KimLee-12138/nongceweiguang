from __future__ import annotations

import time
from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.business_models import HubeiPolicyRawORM, MatchRecordORM, PolicyORM, UserProfileORM

_CACHE_TTL = 300

_cache_kpi: dict = {"ts": 0.0, "value": None}
_cache_trend: dict = {"ts": 0.0, "value": None}
_cache_source: dict = {"ts": 0.0, "value": None}
_cache_audience: dict = {"ts": 0.0, "value": None}


def _fresh(cache: dict) -> bool:
    return cache["value"] is not None and (time.time() - cache["ts"]) < _CACHE_TTL


def build_kpi_snapshot(db: Session) -> dict:
    if _fresh(_cache_kpi):
        return _cache_kpi["value"]

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
    _cache_kpi["ts"] = time.time()
    _cache_kpi["value"] = snapshot
    return snapshot


def build_trend_analysis(db: Session) -> dict:
    if _fresh(_cache_trend):
        return _cache_trend["value"]

    period_col = func.date_format(HubeiPolicyRawORM.publish_date, '%Y-%m').label('period')
    stmt = (
        select(period_col, func.count().label('cnt'))
        .where(HubeiPolicyRawORM.publish_date.isnot(None))
        .group_by(period_col)
        .order_by(period_col.desc())
        .limit(12)
    )
    rows = db.execute(stmt).all()
    items = [{"period": row.period, "count": int(row.cnt)} for row in reversed(rows)]
    result = {"items": items}
    _cache_trend["ts"] = time.time()
    _cache_trend["value"] = result
    return result


def build_source_distribution(db: Session) -> dict:
    if _fresh(_cache_source):
        return _cache_source["value"]

    issuer_col = func.coalesce(HubeiPolicyRawORM.issuer, '未知来源').label('source_name')
    stmt = (
        select(issuer_col, func.count().label('cnt'))
        .group_by(issuer_col)
        .order_by(func.count().desc())
        .limit(12)
    )
    rows = db.execute(stmt).all()
    items = [{"source": row.source_name, "count": int(row.cnt)} for row in rows]
    result = {"items": items}
    _cache_source["ts"] = time.time()
    _cache_source["value"] = result
    return result


def build_audience_distribution(db: Session) -> dict:
    if _fresh(_cache_audience):
        return _cache_audience["value"]

    rows = db.scalars(
        select(PolicyORM.condition_tree).where(PolicyORM.condition_tree.isnot(None))
    ).all()
    counter: Counter = Counter()
    for tree in rows:
        if isinstance(tree, dict):
            _accumulate_audience_tags(tree, counter)
    items = [{"audience": key, "count": value} for key, value in counter.most_common(12)]
    result = {"items": items}
    _cache_audience["ts"] = time.time()
    _cache_audience["value"] = result
    return result


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

