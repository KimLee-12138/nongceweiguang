from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass
from typing import Any

from app.services.condition_tree_service import extract_condition_tree_metadata, normalize_condition_tree


@dataclass(frozen=True)
class NodeResult:
    node_id: str | None
    ok: bool
    must: bool
    reason: str
    node_type: str
    description: str = ''
    field: str | None = None
    operator: str | None = None
    expected: Any | None = None
    actual: Any | None = None
    path: str | None = None
    depth: int = 0


def _get_profile_value(profile: dict[str, Any], field: str) -> Any:
    if not field:
        return None
    cursor: Any = profile
    for key in field.split('.'):
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
    return cursor


def _coerce_scalar(value: Any) -> Any:
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {'true', 'yes', '1', '是'}:
            return True
        if text in {'false', 'no', '0', '否'}:
            return False
        try:
            if '.' in text:
                return float(text)
            return int(text)
        except ValueError:
            return value.strip()
    return value


def _coerce_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _to_date(value: Any) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        text = value.strip()
        for parser in (dt.date.fromisoformat,):
            try:
                return parser(text)
            except ValueError:
                continue
    return None


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    op = (operator or '').lower()

    if op == 'exists':
        return actual is not None and actual != '' and actual != []
    if op == 'not_exists':
        return actual is None or actual == '' or actual == []
    if actual is None:
        return False

    actual_scalar = _coerce_scalar(actual)
    expected_scalar = _coerce_scalar(expected)

    if op in ('=', '=='):
        return actual_scalar == expected_scalar
    if op == '!=':
        return actual_scalar != expected_scalar
    if op in ('>', '>=', '<', '<='):
        try:
            left = float(actual_scalar)
            right = float(expected_scalar)
        except (TypeError, ValueError):
            return False
        if op == '>':
            return left > right
        if op == '>=':
            return left >= right
        if op == '<':
            return left < right
        return left <= right
    if op == 'in':
        expected_list = [_coerce_scalar(item) for item in _coerce_list(expected)]
        if isinstance(actual_scalar, list):
            return any(_coerce_scalar(item) in expected_list for item in actual_scalar)
        return actual_scalar in expected_list
    if op == 'not_in':
        expected_list = [_coerce_scalar(item) for item in _coerce_list(expected)]
        if isinstance(actual_scalar, list):
            return all(_coerce_scalar(item) not in expected_list for item in actual_scalar)
        return actual_scalar not in expected_list
    if op == 'contains':
        if isinstance(actual, list):
            return expected in actual
        return str(expected) in str(actual)
    if op == 'contains_any':
        expected_list = [str(item) for item in _coerce_list(expected)]
        if isinstance(actual, list):
            actual_values = {str(item) for item in actual}
            return any(item in actual_values for item in expected_list)
        actual_text = str(actual)
        return any(item in actual_text for item in expected_list)
    if op == 'contains_all':
        expected_list = [str(item) for item in _coerce_list(expected)]
        if isinstance(actual, list):
            actual_values = {str(item) for item in actual}
            return all(item in actual_values for item in expected_list)
        actual_text = str(actual)
        return all(item in actual_text for item in expected_list)
    if op == 'between':
        bounds = _coerce_list(expected)
        if len(bounds) != 2:
            return False
        try:
            left = float(_coerce_scalar(actual))
            lower = float(_coerce_scalar(bounds[0]))
            upper = float(_coerce_scalar(bounds[1]))
        except (TypeError, ValueError):
            return False
        return lower <= left <= upper
    if op in {'date_gte', 'date_lte'}:
        actual_date = _to_date(actual)
        expected_date = _to_date(expected)
        if not actual_date or not expected_date:
            return False
        return actual_date >= expected_date if op == 'date_gte' else actual_date <= expected_date
    if op == 'date_between':
        actual_date = _to_date(actual)
        bounds = _coerce_list(expected)
        if not actual_date or len(bounds) != 2:
            return False
        lower = _to_date(bounds[0])
        upper = _to_date(bounds[1])
        if not lower or not upper:
            return False
        return lower <= actual_date <= upper
    return False


def evaluate_condition_tree(condition_tree: dict[str, Any], profile: dict[str, Any]) -> tuple[bool, list[NodeResult]]:
    normalized = normalize_condition_tree(condition_tree or {})
    results: list[NodeResult] = []

    def walk(node: dict[str, Any], *, depth: int = 0, parent_path: str = '') -> bool:
        node_id = str(node.get('id') or f'node_{len(results) + 1}')
        path = f'{parent_path}.{node_id}' if parent_path else node_id
        must = bool(node.get('must', True))
        description = str(node.get('description') or '').strip()
        if node.get('type') == 'predicate':
            field = str(node.get('field') or '').strip()
            operator = str(node.get('operator') or '').strip()
            expected = node.get('value')
            actual = _get_profile_value(profile, field)
            ok = _compare(actual, operator, expected)
            if ok:
                reason = description or '条件命中'
            elif actual in (None, '', []):
                reason = f'缺少字段 {field}'
            else:
                reason = description or f'不满足 {field} {operator} {expected}'
            results.append(
                NodeResult(
                    node_id=node_id,
                    ok=ok,
                    must=must,
                    reason=reason,
                    node_type='predicate',
                    description=description,
                    field=field,
                    operator=operator,
                    expected=expected,
                    actual=actual,
                    path=path,
                    depth=depth,
                )
            )
            return ok

        children = [child for child in list(node.get('children') or []) if isinstance(child, dict)]
        logic = str(node.get('logic') or 'and').lower()
        child_results = [walk(child, depth=depth + 1, parent_path=path) for child in children]
        ok = any(child_results) if logic == 'or' else all(child_results)
        if not children:
            ok = True
        results.append(
            NodeResult(
                node_id=node_id,
                ok=ok,
                must=must,
                reason=description or ('空分组' if not children else f'{logic} 分组'),
                node_type='group',
                description=description,
                path=path,
                depth=depth,
            )
        )
        return ok

    overall_ok = walk(normalized)
    return overall_ok, results


def to_match_summary(condition_tree: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_condition_tree(condition_tree or {})
    metadata = extract_condition_tree_metadata(normalized)
    overall_ok, node_results = evaluate_condition_tree(normalized, profile or {})
    predicate_results = [item for item in node_results if item.node_type == 'predicate']
    group_results = [item for item in node_results if item.node_type == 'group']

    failed_must_leaf = [item for item in predicate_results if item.must and not item.ok]
    failed_should_leaf = [item for item in predicate_results if (not item.must) and not item.ok]
    matched_leaf = [item for item in predicate_results if item.ok]

    must_total = len([item for item in predicate_results if item.must])
    should_total = len([item for item in predicate_results if not item.must])
    must_failed = len(failed_must_leaf)
    should_failed = len(failed_should_leaf)

    must_ratio = 1.0 if must_total == 0 else (must_total - must_failed) / must_total
    should_ratio = 1.0 if should_total == 0 else (should_total - should_failed) / should_total
    match_score = max(0.0, min(1.0, must_ratio * 0.85 + should_ratio * 0.15))

    missing_fields = sorted({item.field for item in failed_must_leaf if item.field and item.actual in (None, '', [])})
    action_steps: list[str] = []
    for item in failed_must_leaf[:10]:
        if item.field and item.actual in (None, '', []):
            action_steps.append(f'补充画像字段：{item.field}')
        elif item.description:
            action_steps.append(f'核对条件：{item.description}')
        elif item.field:
            action_steps.append(f'调整 {item.field} 以满足 {item.operator} {item.expected}')
    risk_warnings = [
        item.description or f'建议关注条件：{item.field or item.node_id}'
        for item in failed_should_leaf[:5]
    ]
    explanation = [
        f'已命中 {len(matched_leaf)} 个条件节点',
        f'未满足 {must_failed} 个必要条件',
        f'未满足 {should_failed} 个建议条件',
    ]

    return {
        'fully_matched': bool(overall_ok) and must_failed == 0,
        'match_score': round(match_score, 4),
        'must_total': must_total,
        'must_failed': must_failed,
        'should_total': should_total,
        'should_failed': should_failed,
        'failed_must_nodes': [asdict(item) for item in failed_must_leaf],
        'failed_should_nodes': [asdict(item) for item in failed_should_leaf],
        'matched_nodes': [asdict(item) for item in matched_leaf],
        'group_results': [asdict(item) for item in group_results],
        'action_steps': action_steps,
        'risk_warnings': risk_warnings,
        'missing_fields': missing_fields,
        'uncertain_points': list(metadata.get('uncertain_points') or []),
        'policy_applicable_subjects': list(metadata.get('applicable_subjects') or []),
        'match_explanation': explanation,
        'condition_tree_meta': metadata,
        'node_results': [asdict(item) for item in node_results],
    }
