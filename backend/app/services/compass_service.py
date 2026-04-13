from __future__ import annotations

import datetime as dt
from collections import Counter
from typing import Any

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.business_models import CompassGlossaryORM, CompassReportORM, HubeiPolicyRawORM, PolicyORM
from app.services.model_provider import generate_compass_report_payload


FILE_TYPE_LABELS = {
    'gfxwj': '规范性文件',
    'qtzd': '其他主动公开文件',
    'zcjd': '政策解读',
}


def build_compass_signals(db: Session, *, months: int = 6) -> dict[str, Any]:
    policy_rows = db.scalars(select(PolicyORM).order_by(desc(PolicyORM.created_at)).limit(200)).all()
    raw_rows = db.scalars(select(HubeiPolicyRawORM).order_by(desc(HubeiPolicyRawORM.publish_date), desc(HubeiPolicyRawORM.id)).limit(400)).all()
    glossary_rows = db.scalars(
        select(CompassGlossaryORM).where(CompassGlossaryORM.enabled.is_(True)).order_by(desc(CompassGlossaryORM.weight), CompassGlossaryORM.term)
    ).all()

    policy_count = int(db.scalar(select(func.count()).select_from(PolicyORM)) or 0)
    raw_count = int(db.scalar(select(func.count()).select_from(HubeiPolicyRawORM)) or 0)
    report_count = int(db.scalar(select(func.count()).select_from(CompassReportORM)) or 0)
    glossary_count = int(db.scalar(select(func.count()).select_from(CompassGlossaryORM).where(CompassGlossaryORM.enabled.is_(True))) or 0)

    topic_counter = Counter()
    issuer_counter = Counter()
    file_type_counter = Counter()
    validity_counter = Counter()
    audience_counter = Counter()
    region_counter = Counter()
    month_counter = Counter()

    glossary_index = _build_glossary_index(glossary_rows)

    for row in raw_rows:
        if row.topic_category:
            topic_counter[str(row.topic_category).strip()] += 1
        if row.file_category:
            topic_counter[str(row.file_category).strip()] += 1
        if row.issuer:
            issuer_counter[str(row.issuer).strip()] += 1
        label = FILE_TYPE_LABELS.get((row.file_type or '').strip(), (row.file_type or '未分类').strip() or '未分类')
        file_type_counter[label] += 1
        validity_counter[(row.validity_status or '未知').strip() or '未知'] += 1
        if row.publish_date:
            month_counter[row.publish_date.strftime('%Y-%m')] += 1
        matched_topics = _match_glossary_terms(_text_for_raw(row), glossary_index)
        topic_counter.update(matched_topics)

    for row in policy_rows:
        issuer_counter[(row.source or '未标注来源').strip() or '未标注来源'] += 1
        label = FILE_TYPE_LABELS.get((row.file_type or '').strip(), (row.file_type or '未分类').strip() or '未分类')
        file_type_counter[label] += 1
        validity_counter[(row.validity_status or '未知').strip() or '未知'] += 1
        if row.created_at:
            month_counter[row.created_at.strftime('%Y-%m')] += 1
        topic_counter.update(_match_glossary_terms(_text_for_policy(row), glossary_index))
        _accumulate_condition_tree_signals(row.condition_tree or {}, audience_counter, region_counter)

    recent_policy_cards = [
        {
            'id': row.id,
            'title': row.title,
            'source': row.source,
            'summary': (row.summary or '')[:110],
            'file_type': FILE_TYPE_LABELS.get((row.file_type or '').strip(), row.file_type or '未分类'),
            'validity_status': row.validity_status or '未知',
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
        }
        for row in policy_rows[:8]
    ]

    monthly_items = _build_monthly_items(month_counter, months=months)
    stats = {
        'policy_count': policy_count,
        'raw_policy_count': raw_count,
        'report_count': report_count,
        'glossary_count': glossary_count,
    }

    return {
        'generated_at': dt.datetime.utcnow().isoformat(),
        'stats': stats,
        'policy_count': policy_count,
        'raw_policy_count': raw_count,
        'report_count': report_count,
        'glossary_count': glossary_count,
        'theme_distribution': _counter_to_items(topic_counter, key='name', limit=10),
        'top_topics': _counter_to_items(topic_counter, key='name', limit=8),
        'issuer_distribution': _counter_to_items(issuer_counter, key='name', limit=10),
        'top_issuers': _counter_to_items(issuer_counter, key='name', limit=8),
        'file_type_distribution': _counter_to_items(file_type_counter, key='name', limit=6),
        'validity_distribution': _counter_to_items(validity_counter, key='name', limit=6),
        'audience_distribution': _counter_to_items(audience_counter, key='name', limit=8),
        'region_distribution': _counter_to_items(region_counter, key='name', limit=8),
        'monthly_trend': monthly_items,
        'recent_policy_titles': [row['title'] for row in recent_policy_cards],
        'recent_policy_cards': recent_policy_cards,
    }


def list_glossary_items(
    db: Session,
    *,
    keyword: str | None = None,
    category: str | None = None,
    enabled: bool | None = None,
    limit: int = 100,
) -> list[CompassGlossaryORM]:
    stmt = select(CompassGlossaryORM)
    if keyword:
        pattern = f'%{keyword.strip()}%'
        stmt = stmt.where(
            or_(
                CompassGlossaryORM.term.ilike(pattern),
                CompassGlossaryORM.description.ilike(pattern),
            )
        )
    if category:
        stmt = stmt.where(CompassGlossaryORM.category == category)
    if enabled is not None:
        stmt = stmt.where(CompassGlossaryORM.enabled.is_(enabled))
    stmt = stmt.order_by(desc(CompassGlossaryORM.enabled), desc(CompassGlossaryORM.weight), CompassGlossaryORM.term).limit(limit)
    return db.scalars(stmt).all()


def create_glossary_item(
    db: Session,
    *,
    term: str,
    description: str,
    category: str = '政策主题',
    aliases: list[str] | None = None,
    weight: int = 1,
    enabled: bool = True,
) -> CompassGlossaryORM:
    row = CompassGlossaryORM(
        term=term.strip(),
        description=description.strip(),
        category=category.strip() or '政策主题',
        aliases_json=_normalize_aliases(aliases),
        weight=max(int(weight), 1),
        enabled=bool(enabled),
        published_at=dt.datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_glossary_item(
    db: Session,
    *,
    glossary_id: int,
    term: str | None = None,
    description: str | None = None,
    category: str | None = None,
    aliases: list[str] | None = None,
    weight: int | None = None,
    enabled: bool | None = None,
) -> CompassGlossaryORM | None:
    row = db.get(CompassGlossaryORM, glossary_id)
    if not row:
        return None
    if term is not None:
        row.term = term.strip()
    if description is not None:
        row.description = description.strip()
    if category is not None:
        row.category = category.strip() or row.category
    if aliases is not None:
        row.aliases_json = _normalize_aliases(aliases)
    if weight is not None:
        row.weight = max(int(weight), 1)
    if enabled is not None:
        row.enabled = bool(enabled)
    row.updated_at = dt.datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


def delete_glossary_item(db: Session, *, glossary_id: int) -> bool:
    row = db.get(CompassGlossaryORM, glossary_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def generate_and_store_compass_report(db: Session) -> dict[str, Any]:
    signals = build_compass_signals(db)
    glossary_rows = list_glossary_items(db, enabled=True, limit=100)
    payload = generate_compass_report_payload(
        signals=signals,
        glossary_items=[
            {
                'term': row.term,
                'category': row.category,
                'aliases': list(row.aliases_json or []),
                'description': row.description,
                'weight': row.weight,
            }
            for row in glossary_rows
        ],
    )
    now = dt.datetime.utcnow()
    report = CompassReportORM(
        title=payload['title'],
        category=payload['category'] or 'weekly',
        summary=payload['summary'],
        content=payload['content'],
        published_at=now,
    )
    db.add(report)
    _upsert_generated_glossary(db, payload.get('glossary') or [], published_at=now)
    db.commit()
    db.refresh(report)
    return {'report_id': report.id, 'signals': signals}


def _counter_to_items(counter: Counter, *, key: str, limit: int) -> list[dict[str, Any]]:
    return [{key: name, 'count': count} for name, count in counter.most_common(limit)]


def _build_monthly_items(counter: Counter, *, months: int) -> list[dict[str, Any]]:
    current = dt.date.today().replace(day=1)
    items: list[dict[str, Any]] = []
    cursor = current
    for _ in range(max(months, 1)):
        label = cursor.strftime('%Y-%m')
        items.append({'period': label, 'count': int(counter.get(label, 0))})
        if cursor.month == 1:
            cursor = cursor.replace(year=cursor.year - 1, month=12)
        else:
            cursor = cursor.replace(month=cursor.month - 1)
    items.reverse()
    return items


def _build_glossary_index(rows: list[CompassGlossaryORM]) -> list[tuple[str, str, int]]:
    items: list[tuple[str, str, int]] = []
    for row in rows:
        if not row.enabled:
            continue
        terms = [row.term, *(row.aliases_json or [])]
        for token in terms:
            normalized = str(token or '').strip()
            if normalized:
                items.append((normalized.lower(), row.term, max(int(row.weight or 1), 1)))
    items.sort(key=lambda item: len(item[0]), reverse=True)
    return items


def _match_glossary_terms(text: str, glossary_index: list[tuple[str, str, int]]) -> Counter:
    lowered = (text or '').lower()
    matched = Counter()
    for token, canonical_term, weight in glossary_index:
        if token and token in lowered:
            matched[canonical_term] += weight
    return matched


def _accumulate_condition_tree_signals(node: dict[str, Any], audience_counter: Counter, region_counter: Counter) -> None:
    if not isinstance(node, dict):
        return
    for subject in list(node.get('applicable_subjects') or []):
        normalized = str(subject).strip()
        if normalized:
            audience_counter[normalized] += 1

    node_type = node.get('type')
    if node_type == 'predicate':
        field = str(node.get('field') or '').strip()
        value = node.get('value')
        if field in {'type', 'subject_type', 'qualification'}:
            for item in _as_list(value):
                normalized = str(item).strip()
                if normalized:
                    audience_counter[normalized] += 1
        if field in {'region', 'extra_data.region', 'area_region'}:
            for item in _as_list(value):
                normalized = str(item).strip()
                if normalized:
                    region_counter[normalized] += 1

    for child in list(node.get('children') or []):
        if isinstance(child, dict):
            _accumulate_condition_tree_signals(child, audience_counter, region_counter)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_aliases(aliases: list[str] | None) -> list[str]:
    normalized: list[str] = []
    for item in aliases or []:
        text = str(item or '').strip()
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def _upsert_generated_glossary(db: Session, items: list[dict[str, Any]], *, published_at: dt.datetime) -> None:
    for item in items:
        term = str(item.get('term') or '').strip()
        description = str(item.get('description') or '').strip()
        if not term or not description:
            continue
        existing = db.scalar(select(CompassGlossaryORM).where(CompassGlossaryORM.term == term))
        aliases = _normalize_aliases(item.get('aliases') or [])
        category = str(item.get('category') or '政策主题').strip() or '政策主题'
        weight = max(int(item.get('weight') or 1), 1)
        if existing:
            existing.description = description
            existing.category = category
            existing.aliases_json = aliases or list(existing.aliases_json or [])
            existing.weight = weight
            existing.enabled = True
            existing.updated_at = published_at
        else:
            db.add(
                CompassGlossaryORM(
                    term=term,
                    description=description,
                    category=category,
                    aliases_json=aliases,
                    weight=weight,
                    enabled=True,
                    published_at=published_at,
                )
            )


def _text_for_policy(row: PolicyORM) -> str:
    pieces = [row.title or '', row.summary or '', row.source or '']
    return '\n'.join(piece for piece in pieces if piece)


def _text_for_raw(row: HubeiPolicyRawORM) -> str:
    pieces = [
        row.title or '',
        row.issuer or '',
        row.topic_category or '',
        row.file_category or '',
        row.column_name or '',
        row.full_text or '',
    ]
    return '\n'.join(piece for piece in pieces if piece)
