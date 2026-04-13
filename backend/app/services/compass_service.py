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

PREDICTION_RULES = [
    {
        'keywords': ('高标准农田', '农田建设', '耕地', '土地整治'),
        'title': '高标准农田与耕地质量提升仍会持续加码',
        'signal': '耕地建设',
        'detail': '近期样本中持续出现农田建设、耕地质量提升与基础设施补短板信号，说明财政与项目资金仍会围绕稳产保供持续布局。',
    },
    {
        'keywords': ('绿色', '生态', '低碳', '循环', '绿色认证'),
        'title': '绿色低碳和认证导向会继续升温',
        'signal': '绿色转型',
        'detail': '绿色生产、生态治理与质量认证相关术语出现频率较高，意味着未来政策更可能强调绿色标准、品牌认证和绿色生产方式。',
    },
    {
        'keywords': ('设施农业', '智慧农业', '数字', '智能', '农机'),
        'title': '设施化、数字化与农业装备升级是重点窗口',
        'signal': '设施升级',
        'detail': '从设施农业、智慧农业和装备升级相关表述看，政策支持将继续倾向提升生产效率、抗风险能力与数字化管理水平。',
    },
    {
        'keywords': ('合作社', '家庭农场', '龙头企业', '主体'),
        'title': '规模经营主体和带动能力强的主体更容易成为扶持重点',
        'signal': '主体扶持',
        'detail': '样本中对家庭农场、合作社与龙头企业等主体的指向较为集中，后续政策大概率继续围绕主体培育、示范与联农带农展开。',
    },
]


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
        topic_counter.update(_match_glossary_terms(_text_for_raw(row), glossary_index))

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


def build_policy_briefing(db: Session, *, months: int = 6, policy_id: int | None = None) -> dict[str, Any]:
    signals = build_compass_signals(db, months=months)
    glossary_rows = db.scalars(
        select(CompassGlossaryORM).where(CompassGlossaryORM.enabled.is_(True)).order_by(desc(CompassGlossaryORM.weight), CompassGlossaryORM.term)
    ).all()
    policy = db.get(PolicyORM, policy_id) if policy_id else None

    forecast_cards = _build_forecast_cards(signals)
    focus_terms = _select_focus_terms(signals, glossary_rows, limit=6)
    selected_policy_terms = _explain_selected_policy_terms(policy, glossary_rows)

    return {
        'generated_at': signals['generated_at'],
        'province': '湖北省',
        'months': months,
        'overview': {
            'summary': _build_forecast_summary(signals, forecast_cards),
            'policy_count': signals['policy_count'],
            'raw_policy_count': signals['raw_policy_count'],
            'report_count': signals['report_count'],
        },
        'forecast_cards': forecast_cards,
        'signal_highlights': {
            'top_topics': list(signals.get('top_topics') or [])[:5],
            'top_issuers': list(signals.get('top_issuers') or [])[:5],
            'monthly_trend': list(signals.get('monthly_trend') or []),
            'audience_distribution': list(signals.get('audience_distribution') or [])[:5],
        },
        'focus_terms': focus_terms,
        'selected_policy': _serialize_selected_policy(policy, selected_policy_terms),
        'recent_policy_cards': list(signals.get('recent_policy_cards') or [])[:6],
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


def _build_forecast_cards(signals: dict[str, Any]) -> list[dict[str, Any]]:
    topic_names = [str(item.get('name') or '') for item in list(signals.get('top_topics') or [])]
    audience_names = [str(item.get('name') or '') for item in list(signals.get('audience_distribution') or [])]
    issuer_names = [str(item.get('name') or '') for item in list(signals.get('top_issuers') or [])]
    monthly_trend = list(signals.get('monthly_trend') or [])
    current_count = int((monthly_trend[-1] or {}).get('count') or 0) if monthly_trend else 0
    previous_count = int((monthly_trend[-2] or {}).get('count') or 0) if len(monthly_trend) > 1 else current_count
    delta = current_count - previous_count

    cards: list[dict[str, Any]] = []
    for rule in PREDICTION_RULES:
        matched_terms = [name for name in topic_names + audience_names if any(keyword in name for keyword in rule['keywords'])]
        if not matched_terms:
            continue
        confidence = '高' if len(matched_terms) >= 2 else '中'
        cards.append(
            {
                'title': rule['title'],
                'signal': rule['signal'],
                'confidence': confidence,
                'detail': rule['detail'],
                'basis': matched_terms[:3],
            }
        )

    if not cards:
        default_basis = [name for name in topic_names[:2] if name] or ['近期政策样本']
        cards.append(
            {
                'title': '财政扶持与重点项目导向仍将保持连续性',
                'signal': '连续扶持',
                'confidence': '中',
                'detail': '从近期政策更新节奏和主题集中度看，湖北农业政策仍会围绕稳产保供、重点项目建设和主体能力提升持续释放信号。',
                'basis': default_basis,
            }
        )

    if not any(card['signal'] == '发文节奏' for card in cards):
        trend_label = '发文节奏上扬' if delta > 0 else '发文节奏平稳'
        trend_detail = (
            '最近一个月政策新增数量较上月有所提升，短期内更可能继续围绕重点专项密集发文。'
            if delta > 0
            else '最近两个月政策新增强度整体平稳，后续更可能延续已有主线并对重点领域做细化补充。'
        )
        cards.append(
            {
                'title': '近期发文节奏显示政策将继续围绕重点方向做细化延展',
                'signal': '发文节奏',
                'confidence': '中',
                'detail': trend_detail,
                'basis': [trend_label, *(issuer_names[:2] or ['近期样本'])][:3],
            }
        )

    return cards[:4]


def _build_forecast_summary(signals: dict[str, Any], cards: list[dict[str, Any]]) -> str:
    top_topic = ((signals.get('top_topics') or [{}])[0] or {}).get('name') or '重点建设'
    top_issuer = ((signals.get('top_issuers') or [{}])[0] or {}).get('name') or '省级主管部门'
    top_card = (cards or [{}])[0]
    return (
        f'基于近 {len(list(signals.get("monthly_trend") or [])) or 0} 个月已入库湖北农业政策样本，'
        f'当前风向主要集中在“{top_topic}”等方向，且 {top_issuer} 发文活跃。'
        f'综合主题热度、主体分布与近期发文节奏判断，后续政策大概率继续沿着“{top_card.get("signal") or "重点扶持"}”主线加密落地。'
    )


def _select_focus_terms(
    signals: dict[str, Any],
    glossary_rows: list[CompassGlossaryORM],
    *,
    limit: int = 6,
) -> list[dict[str, Any]]:
    theme_names = {str(item.get('name') or '').strip() for item in list(signals.get('top_topics') or [])}
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in glossary_rows:
        term = str(row.term or '').strip()
        if not term or term in seen:
            continue
        aliases = [str(alias).strip() for alias in list(row.aliases_json or []) if str(alias).strip()]
        if term in theme_names or any(alias in theme_names for alias in aliases) or len(selected) < 3:
            selected.append(
                {
                    'term': term,
                    'category': row.category,
                    'description': row.description,
                    'aliases': aliases,
                }
            )
            seen.add(term)
        if len(selected) >= limit:
            break

    if selected:
        return selected

    return [
        {
            'term': str(item.get('name') or '重点方向'),
            'category': '政策主题',
            'description': '该术语在近期湖北农业政策样本中高频出现，通常代表当前扶持或监管重点方向。',
            'aliases': [],
        }
        for item in list(signals.get('top_topics') or [])[:limit]
        if str(item.get('name') or '').strip()
    ]


def _explain_selected_policy_terms(
    policy: PolicyORM | None,
    glossary_rows: list[CompassGlossaryORM],
) -> list[dict[str, Any]]:
    if not policy:
        return []
    text = _text_for_policy(policy)
    if not text:
        return []

    matched: list[dict[str, Any]] = []
    seen: set[str] = set()
    lowered = text.lower()
    for row in glossary_rows:
        term = str(row.term or '').strip()
        aliases = [str(alias).strip() for alias in list(row.aliases_json or []) if str(alias).strip()]
        tokens = [term, *aliases]
        if not term or term in seen:
            continue
        if any(token and token.lower() in lowered for token in tokens):
            matched.append(
                {
                    'term': term,
                    'category': row.category,
                    'description': row.description,
                    'aliases': aliases,
                }
            )
            seen.add(term)
        if len(matched) >= 5:
            break

    if matched:
        return matched

    subjects = list((policy.condition_tree or {}).get('applicable_subjects') or [])
    explanations: list[dict[str, Any]] = []
    if subjects:
        explanations.append(
            {
                'term': '适用主体',
                'category': '主体类型',
                'description': f'这条政策当前主要面向：{"、".join(str(item).strip() for item in subjects if str(item).strip())}。',
                'aliases': [],
            }
        )
    if policy.validity_status:
        explanations.append(
            {
                'term': '效力状态',
                'category': '政策状态',
                'description': f'当前政策状态为“{policy.validity_status}”，使用前仍建议核对最新公告与是否存在补充通知。',
                'aliases': [],
            }
        )
    return explanations


def _serialize_selected_policy(policy: PolicyORM | None, terms: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not policy:
        return None
    return {
        'id': policy.id,
        'title': policy.title,
        'summary': policy.summary,
        'source': policy.source,
        'validity_status': policy.validity_status,
        'terms': terms,
    }


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
