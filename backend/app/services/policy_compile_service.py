from __future__ import annotations

import json
import re

from app.services.condition_tree_service import build_stub_condition_tree as build_stub_condition_tree_v2, normalize_condition_tree
from app.services.model_provider import ModelProviderError, compile_policy_text as compile_policy_text_via_model


def build_stub_condition_tree(raw_text: str, title: str | None = None) -> dict:
    return build_stub_condition_tree_v2(raw_text, title)


def suggest_summary_from_text(raw_text: str, max_len: int = 300) -> str:
    text = (raw_text or '').strip()
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return text[:max_len] + ('...' if len(text) > max_len else '')


def compile_policy_text(raw_text: str, title: str | None = None, source: str | None = None) -> dict:
    if not (raw_text or '').strip():
        raise ModelProviderError('缺少政策原文，无法调用 DeepSeek 生成条件树')

    result = compile_policy_text_via_model(raw_text=raw_text, title=title, source=source)
    condition_tree = normalize_condition_tree(
        result.get('condition_tree') or {},
        generated_by='deepseek',
        compile_quality=result.get('compile_quality') or 'generated',
        missing_information=list(result.get('missing_information') or []),
        uncertain_points=list(result.get('uncertain_points') or []),
        applicable_subjects=list(result.get('applicable_subjects') or []),
        reason=result.get('compile_reason'),
    )
    metadata = condition_tree.get('compile_metadata') or {}
    return {
        'summary': str(result.get('summary') or '').strip(),
        'condition_tree': condition_tree,
        'category': str(result.get('category') or '其他').strip() or '其他',
        'mode': str(result.get('mode') or 'model').strip() or 'model',
        'compile_quality': metadata.get('compile_quality') or 'generated',
        'missing_information': list(metadata.get('missing_information') or []),
        'uncertain_points': list(metadata.get('uncertain_points') or []),
        'applicable_subjects': list(condition_tree.get('applicable_subjects') or []),
    }


def parse_condition_tree_json(text: str) -> dict:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError('condition_tree 必须是 JSON 对象')
    return normalize_condition_tree(data)
