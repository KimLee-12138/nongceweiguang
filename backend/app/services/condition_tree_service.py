from __future__ import annotations

from copy import deepcopy
from typing import Any


CONDITION_TREE_SCHEMA_VERSION = '2.0'
GROUP_KEYS = {'id', 'type', 'logic', 'must', 'description', 'children', 'schema_version', 'compile_metadata'}
PREDICATE_KEYS = {
    'id',
    'type',
    'field',
    'operator',
    'value',
    'must',
    'description',
    'source_quotes',
    'source_locators',
    'notes',
    'confidence',
}
ALLOWED_OPERATORS = {
    '=',
    '==',
    '!=',
    '>',
    '>=',
    '<',
    '<=',
    'in',
    'not_in',
    'contains',
    'contains_any',
    'contains_all',
    'exists',
    'not_exists',
    'between',
    'date_gte',
    'date_lte',
    'date_between',
}


def build_empty_condition_tree(
    *,
    description: str = '未提取到可稳定执行的政策准入条件',
    compile_quality: str = 'empty',
    missing_information: list[str] | None = None,
    uncertain_points: list[str] | None = None,
    generated_by: str = 'system',
    reason: str | None = None,
    applicable_subjects: list[str] | None = None,
) -> dict[str, Any]:
    compile_metadata = {
        'compile_quality': compile_quality,
        'missing_information': list(missing_information or []),
        'uncertain_points': list(uncertain_points or []),
        'generated_by': generated_by,
        'reason': reason or description,
    }
    return {
        'schema_version': CONDITION_TREE_SCHEMA_VERSION,
        'id': 'root',
        'type': 'group',
        'logic': 'and',
        'must': True,
        'description': description,
        'applicable_subjects': list(applicable_subjects or []),
        'compile_metadata': compile_metadata,
        'children': [],
    }


def build_stub_condition_tree(raw_text: str, title: str | None = None) -> dict[str, Any]:
    _ = raw_text
    description = '待 DeepSeek 编译政策条件树'
    if title:
        description = f'待为《{title}》生成详细条件树'
    return build_empty_condition_tree(
        description=description,
        compile_quality='draft',
        generated_by='system_stub',
        reason='尚未执行 DeepSeek 条件树编译',
    )


def normalize_condition_tree(
    tree: dict[str, Any] | None,
    *,
    generated_by: str | None = None,
    compile_quality: str | None = None,
    missing_information: list[str] | None = None,
    uncertain_points: list[str] | None = None,
    applicable_subjects: list[str] | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    if not isinstance(tree, dict) or not tree:
        normalized = build_empty_condition_tree(
            compile_quality=compile_quality or 'empty',
            generated_by=generated_by or 'system',
            missing_information=missing_information,
            uncertain_points=uncertain_points,
            applicable_subjects=applicable_subjects,
            reason=reason,
        )
    else:
        normalized = _normalize_node(tree, is_root=True)

    metadata = dict(normalized.get('compile_metadata') or {})
    if generated_by:
        metadata['generated_by'] = generated_by
    metadata['compile_quality'] = str(compile_quality or metadata.get('compile_quality') or 'generated').strip()
    metadata['missing_information'] = _normalize_string_list(
        missing_information if missing_information is not None else metadata.get('missing_information')
    )
    metadata['uncertain_points'] = _normalize_string_list(
        uncertain_points if uncertain_points is not None else metadata.get('uncertain_points')
    )
    if reason:
        metadata['reason'] = reason
    elif not metadata.get('reason'):
        metadata['reason'] = normalized.get('description') or '条件树已规范化'

    normalized['schema_version'] = CONDITION_TREE_SCHEMA_VERSION
    normalized['compile_metadata'] = metadata
    normalized['applicable_subjects'] = _normalize_string_list(
        applicable_subjects if applicable_subjects is not None else normalized.get('applicable_subjects')
    )
    return normalized


def extract_condition_tree_metadata(tree: dict[str, Any] | None) -> dict[str, Any]:
    normalized = normalize_condition_tree(tree or {})
    metadata = dict(normalized.get('compile_metadata') or {})
    return {
        'schema_version': normalized.get('schema_version') or CONDITION_TREE_SCHEMA_VERSION,
        'compile_quality': metadata.get('compile_quality') or 'generated',
        'missing_information': list(metadata.get('missing_information') or []),
        'uncertain_points': list(metadata.get('uncertain_points') or []),
        'generated_by': metadata.get('generated_by') or 'unknown',
        'reason': metadata.get('reason') or normalized.get('description') or '',
        'applicable_subjects': list(normalized.get('applicable_subjects') or []),
        'node_count': count_condition_tree_nodes(normalized),
        'predicate_count': count_condition_tree_predicates(normalized),
    }


def count_condition_tree_nodes(tree: dict[str, Any] | None) -> int:
    normalized = normalize_condition_tree(tree or {})

    def walk(node: dict[str, Any]) -> int:
        total = 1
        for child in list(node.get('children') or []):
            if isinstance(child, dict):
                total += walk(child)
        return total

    return walk(normalized)


def count_condition_tree_predicates(tree: dict[str, Any] | None) -> int:
    normalized = normalize_condition_tree(tree or {})

    def walk(node: dict[str, Any]) -> int:
        if node.get('type') == 'predicate':
            return 1
        return sum(walk(child) for child in list(node.get('children') or []) if isinstance(child, dict))

    return walk(normalized)


def clone_condition_tree(tree: dict[str, Any] | None) -> dict[str, Any]:
    return normalize_condition_tree(deepcopy(tree or {}))


def _normalize_node(node: dict[str, Any], *, is_root: bool = False) -> dict[str, Any]:
    if _is_legacy_predicate(node) or node.get('type') == 'predicate':
        return _normalize_predicate(node)
    return _normalize_group(node, is_root=is_root)


def _normalize_group(node: dict[str, Any], *, is_root: bool = False) -> dict[str, Any]:
    logic = str(node.get('logic') or node.get('relation') or 'and').strip().lower()
    if logic not in ('and', 'or'):
        logic = 'and'
    normalized = {
        'id': str(node.get('id') or ('root' if is_root else 'group')),
        'type': 'group',
        'logic': logic,
        'must': bool(node.get('must', True)),
        'description': str(node.get('description') or '').strip(),
        'children': [],
    }
    if is_root:
        normalized['schema_version'] = CONDITION_TREE_SCHEMA_VERSION
        normalized['applicable_subjects'] = _normalize_string_list(node.get('applicable_subjects'))
        normalized['compile_metadata'] = {
            'compile_quality': str((node.get('compile_metadata') or {}).get('compile_quality') or 'generated').strip(),
            'missing_information': _normalize_string_list((node.get('compile_metadata') or {}).get('missing_information')),
            'uncertain_points': _normalize_string_list((node.get('compile_metadata') or {}).get('uncertain_points')),
            'generated_by': str((node.get('compile_metadata') or {}).get('generated_by') or 'unknown').strip(),
            'reason': str((node.get('compile_metadata') or {}).get('reason') or node.get('description') or '').strip(),
        }
    for key in ('source_quotes', 'source_locators', 'notes'):
        values = _normalize_string_list(node.get(key))
        if values:
            normalized[key] = values
    if node.get('confidence') is not None:
        try:
            normalized['confidence'] = float(node.get('confidence'))
        except (TypeError, ValueError):
            pass
    for child in list(node.get('children') or []):
        if isinstance(child, dict):
            normalized['children'].append(_normalize_node(child))
    return normalized


def _normalize_predicate(node: dict[str, Any]) -> dict[str, Any]:
    operator = str(node.get('operator') or '').strip()
    if operator not in ALLOWED_OPERATORS:
        raise ValueError(f'不支持的条件树操作符: {operator}')
    field = str(node.get('field') or '').strip()
    if not field:
        raise ValueError('predicate 节点缺少 field')
    normalized = {
        'id': str(node.get('id') or field.replace('.', '_') or 'predicate'),
        'type': 'predicate',
        'field': field,
        'operator': operator,
        'value': node.get('value'),
        'must': bool(node.get('must', True)),
        'description': str(node.get('description') or '').strip(),
    }
    for key in ('source_quotes', 'source_locators', 'notes'):
        values = _normalize_string_list(node.get(key))
        if values:
            normalized[key] = values
    if node.get('confidence') is not None:
        try:
            normalized['confidence'] = float(node.get('confidence'))
        except (TypeError, ValueError):
            pass
    return normalized


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    output: list[str] = []
    for item in items:
        text = str(item or '').strip()
        if text:
            output.append(text)
    return output


def _is_legacy_predicate(node: dict[str, Any]) -> bool:
    return bool(node.get('field') and node.get('operator'))
