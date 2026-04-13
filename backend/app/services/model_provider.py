from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings


class ModelProviderError(RuntimeError):
    pass


@dataclass
class ModelReadiness:
    ok: bool
    status: str
    message: str
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            'ok': self.ok,
            'status': self.status,
            'message': self.message,
            'detail': self.detail,
        }


MIN_DETAILED_ANSWER_CHARS = 420


def _settings():
    return get_settings()


def _chat_endpoint() -> str:
    base = _settings().DEEPSEEK_BASE_URL.rstrip('/')
    return f'{base}/chat/completions'


def _headers() -> dict[str, str]:
    settings = _settings()
    if not settings.DEEPSEEK_API_KEY:
        raise ModelProviderError('DEEPSEEK_API_KEY 未配置，无法执行模型调用')
    return {
        'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }


def _parse_json_payload(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise ModelProviderError('模型返回的内容不是有效 JSON')


def _chat_json(*, system_prompt: str, user_prompt: str, temperature: float = 0.2, max_tokens: int = 1800) -> dict[str, Any]:
    settings = _settings()
    payload = {
        'model': settings.DEEPSEEK_MODEL,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'response_format': {'type': 'json_object'},
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
    }
    try:
        with httpx.Client(timeout=settings.HTTP_TIMEOUT_SECONDS, trust_env=False) as client:
            response = client.post(_chat_endpoint(), headers=_headers(), json=payload)
            response.raise_for_status()
    except httpx.ReadTimeout as exc:
        raise ModelProviderError(
            f'模型接口请求超时：DeepSeek 在 {settings.HTTP_TIMEOUT_SECONDS:g} 秒内未返回结果，请稍后重试或检查网络连接'
        ) from exc
    except httpx.ConnectTimeout as exc:
        raise ModelProviderError(
            f'模型接口连接超时：无法在 {settings.HTTP_TIMEOUT_SECONDS:g} 秒内连接到 DeepSeek，请检查网络环境'
        ) from exc
    except httpx.ConnectError as exc:
        raise ModelProviderError('模型接口网络连接失败：无法连接到 DeepSeek，请检查网络或代理设置') from exc
    except httpx.HTTPStatusError as exc:
        raise ModelProviderError(f'模型接口返回错误：HTTP {exc.response.status_code}') from exc
    except httpx.HTTPError as exc:
        raise ModelProviderError(f'模型接口请求失败：{exc}') from exc

    data = response.json()
    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
    if not isinstance(content, str) or not content.strip():
        raise ModelProviderError('模型返回内容为空')
    return _parse_json_payload(content.strip())


def _answer_too_short(answer: str) -> bool:
    text = (answer or '').strip()
    if len(text) < MIN_DETAILED_ANSWER_CHARS:
        return True
    if text.count('\n') < 6:
        return True
    lowered = text.lower()
    if '##' not in lowered and '###' not in lowered and '- ' not in text:
        return True
    return False


def _normalize_review_recommendation(value: Any) -> str:
    text = str(value or '').strip().lower()
    if not text:
        return 'review'
    approve_tokens = ('approve', 'approved', 'pass', 'accept', '通过', '建议通过', '可通过')
    reject_tokens = ('reject', 'rejected', 'deny', 'fail', '驳回', '拒绝', '不通过', '建议驳回')
    if any(token in text for token in approve_tokens):
        return 'approve'
    if any(token in text for token in reject_tokens):
        return 'reject'
    return 'review'


def _normalize_risk_points(value: Any) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for item in list(value or []):
        if isinstance(item, dict):
            title = str(item.get('title') or item.get('name') or item.get('risk') or '风险提示').strip()
            detail = str(item.get('detail') or item.get('reason') or item.get('description') or '').strip()
            if title or detail:
                normalized.append({'title': title or '风险提示', 'detail': detail})
        elif item:
            normalized.append({'title': '风险提示', 'detail': str(item).strip()})
    return normalized


def _normalize_evidence(value: Any) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for idx, item in enumerate(list(value or []), start=1):
        if isinstance(item, dict):
            locator = str(item.get('locator') or item.get('position') or f'证据 {idx}').strip()
            excerpt = str(item.get('excerpt') or item.get('quote') or item.get('content') or '').strip()
            relevance = str(item.get('relevance') or item.get('reason') or item.get('detail') or '').strip()
            source_type = str(item.get('source_type') or 'raw_text').strip() or 'raw_text'
        elif item:
            locator = f'证据 {idx}'
            excerpt = str(item).strip()
            relevance = ''
            source_type = 'raw_text'
        else:
            continue
        normalized.append(
            {
                'source_type': source_type,
                'locator': locator or f'证据 {idx}',
                'excerpt': excerpt,
                'relevance': relevance,
            }
        )
    return normalized


def _expand_answer_to_detailed_markdown(
    *,
    answer: str,
    question: str,
    context: dict[str, Any],
    system_prompt: str,
) -> str:
    if not _answer_too_short(answer):
        return answer

    expand_prompt = f"""
请把下面这段回答扩写为更详细、更结构化、更可执行的版本，保留原意，不要编造事实。
要求：
1. 使用 Markdown 输出。
2. 至少包含以下小节：`## 结论`、`## 详细说明`、`## 你现在可以做什么`、`## 风险与注意事项`、`## 还需要补充的信息`。
3. “你现在可以做什么”至少列出 4 条具体步骤。
4. 内容明显比原回答更完整。

用户问题：{question}
上下文：{json.dumps(context, ensure_ascii=False)}
当前回答：{answer}

只返回 JSON，例如：{{"answer": "...markdown..."}}。
"""
    try:
        expanded = _chat_json(
            system_prompt=system_prompt,
            user_prompt=expand_prompt,
            temperature=0.3,
            max_tokens=2600,
        )
    except ModelProviderError:
        return answer

    candidate = str(expanded.get('answer') or '').strip()
    return candidate or answer


def check_model_readiness(*, live: bool = False) -> ModelReadiness:
    settings = _settings()
    if not settings.DEEPSEEK_API_KEY:
        return ModelReadiness(False, 'missing_config', '未配置 DEEPSEEK_API_KEY', {'configured': False})
    if not live:
        return ModelReadiness(True, 'configured', '模型配置已存在，未执行在线校验', {'configured': True})
    try:
        result = _chat_json(
            system_prompt='你是健康检查助手，只返回 JSON。',
            user_prompt='请返回 JSON：{"ok": true, "provider": "deepseek"}',
            temperature=0,
            max_tokens=32,
        )
    except ModelProviderError as exc:
        return ModelReadiness(False, 'error', str(exc), {'configured': True})
    if result.get('ok') is True:
        return ModelReadiness(True, 'ready', '模型在线校验成功', {'configured': True, 'provider': result.get('provider', 'deepseek')})
    return ModelReadiness(False, 'invalid_response', '模型在线校验未返回预期结构', {'configured': True, 'response': result})


def compile_policy_text(*, raw_text: str, title: str | None = None, source: str | None = None) -> dict[str, Any]:
    prompt = f"""
你要把一段中文涉农政策原文编译成可供规则匹配引擎直接执行的详细 JSON。
输出字段：
- summary: 不超过 180 字的中文摘要
- condition_tree: 详细条件树，根节点固定为 group，必须包含 schema_version、compile_metadata、applicable_subjects
- category: 政策分类短词
- compile_quality: generated | partial | empty | failed
- missing_information: 数组，列出原文缺失的关键信息
- uncertain_points: 数组，列出无法确定但会影响匹配的点
- applicable_subjects: 数组，列出明确适用主体

condition_tree 规则：
- 根节点固定结构：
  {{
    "schema_version": "2.0",
    "id": "root",
    "type": "group",
    "logic": "and",
    "must": true,
    "description": "...",
    "applicable_subjects": ["..."],
    "compile_metadata": {{
      "compile_quality": "generated",
      "missing_information": [],
      "uncertain_points": [],
      "generated_by": "deepseek",
      "reason": "..."
    }},
    "children": [...]
  }}
- group 节点字段：id/type=group/logic/must/description/children，可选 source_quotes/source_locators/notes/confidence
- predicate 节点字段：id/type=predicate/field/operator/value/must/description，可选 source_quotes/source_locators/notes/confidence
- operator 仅允许 =、==、!=、>、>=、<、<=、in、not_in、contains、contains_any、contains_all、exists、not_exists、between、date_gte、date_lte、date_between
- 常用 field 优先使用：type、area、green_cert、irrigation、extra_data.*、effective_date、expiry_date、region、subject_type、qualification、scale
- 必须尽量结构化抽取：适用主体、区域限制、时间窗口、规模门槛、资质/证照、限制性条款、排除条件
- 要明确区分必要条件 must=true 和建议条件 must=false
- 无法确定的条件不得编造，写入 uncertain_points，并在节点 description 里说明依据不足
- 如果原文没有稳定可结构化的准入条件，也要返回空 children，但 compile_quality 不能伪装成 generated
- 只返回 JSON，不要加解释文字

政策标题：{title or '未提供'}
政策来源：{source or '未提供'}
政策原文：{raw_text[:12000]}
"""
    result = _chat_json(
        system_prompt='你是农业政策结构化编译助手，只返回 JSON。',
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=2200,
    )
    tree = result.get('condition_tree')
    if not isinstance(tree, dict) or tree.get('id') != 'root':
        raise ModelProviderError('模型未返回合法的 condition_tree')
    return {
        'summary': str(result.get('summary') or '').strip(),
        'condition_tree': tree,
        'category': str(result.get('category') or '').strip(),
        'compile_quality': str(result.get('compile_quality') or '').strip() or 'generated',
        'missing_information': [str(item).strip() for item in list(result.get('missing_information') or []) if str(item).strip()],
        'uncertain_points': [str(item).strip() for item in list(result.get('uncertain_points') or []) if str(item).strip()],
        'applicable_subjects': [str(item).strip() for item in list(result.get('applicable_subjects') or []) if str(item).strip()],
        'compile_reason': str(result.get('compile_reason') or result.get('reason') or '').strip(),
        'mode': 'model',
    }


def generate_review_payload(
    *,
    raw_text: str,
    draft_summary: str | None,
    draft_condition_tree: dict[str, Any],
    title: str | None,
    source: str | None,
    draft_file_type: str | None,
    draft_validity_status: str | None,
    draft_effective_date: Any,
    draft_expiry_date: Any,
) -> dict[str, Any]:
    prompt = f"""
你是政策审核助手。请根据原文与草稿结构输出 JSON，对人工审核提供辅助信息。
JSON 字段：
- summary
- category
- suggestion
- recommendation
- risk_points: 数组，元素含 title/detail
- evidence: 数组，元素含 quote/reason

政策标题：{title or '未提供'}
政策来源：{source or '未提供'}
文件类型：{draft_file_type or '未提供'}
效力状态：{draft_validity_status or '未提供'}
生效日期：{draft_effective_date.isoformat() if getattr(draft_effective_date, 'isoformat', None) else ''}
失效日期：{draft_expiry_date.isoformat() if getattr(draft_expiry_date, 'isoformat', None) else ''}
草稿摘要：{draft_summary or ''}
草稿条件树：{json.dumps(draft_condition_tree or {}, ensure_ascii=False)}
政策原文：{raw_text[:12000]}
"""
    result = _chat_json(
        system_prompt='你是农业政策审核助手，只返回 JSON。',
        user_prompt=prompt,
        temperature=0.2,
        max_tokens=1800,
    )
    return {
        'summary': result.get('summary') or draft_summary or '',
        'category': result.get('category') or '其他',
        'suggestion': result.get('suggestion') or '',
        'risk_points': _normalize_risk_points(result.get('risk_points') or []),
        'evidence': _normalize_evidence(result.get('evidence') or []),
        'recommendation': _normalize_review_recommendation(result.get('recommendation')),
    }


def generate_compass_report_payload(*, signals: dict[str, Any], glossary_items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    prompt = f"""
你是农业政策风向标撰稿助手。请根据结构化信号生成周报 JSON。
JSON 字段：
- title
- category: 固定 weekly
- summary: 120 字内摘要
- content: Markdown 正文，包含趋势、机会、准备事项三个小节，尽量引用结构化统计结果
- glossary: 数组，元素含 term/description/category/aliases/weight

结构化信号：
{json.dumps(signals, ensure_ascii=False)}

现有词典（可复用、补充、纠偏，但不要无依据编造）：
{json.dumps(glossary_items or [], ensure_ascii=False)}
"""
    result = _chat_json(
        system_prompt='你是农业政策风向标撰稿助手，只返回 JSON。',
        user_prompt=prompt,
        temperature=0.3,
        max_tokens=2200,
    )
    glossary = []
    for item in list(result.get('glossary') or []):
        if isinstance(item, dict) and item.get('term') and item.get('description'):
            aliases = [str(alias).strip() for alias in list(item.get('aliases') or []) if str(alias).strip()]
            glossary.append(
                {
                    'term': str(item['term']).strip(),
                    'description': str(item['description']).strip(),
                    'category': str(item.get('category') or '政策主题').strip() or '政策主题',
                    'aliases': aliases,
                    'weight': max(int(item.get('weight') or 1), 1),
                }
            )
    return {
        'title': str(result.get('title') or '本期政策风向标').strip(),
        'category': str(result.get('category') or 'weekly').strip(),
        'summary': str(result.get('summary') or '').strip(),
        'content': str(result.get('content') or '').strip(),
        'glossary': glossary,
    }


def generate_chat_interpretation_payload(
    *,
    question: str,
    mode: str,
    profile: dict[str, Any] | None,
    policy: dict[str, Any] | None,
    match_summary: dict[str, Any] | None,
    recent_messages: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    system_prompt = '你是高质量农业政策解读助手，回答要自然、清晰、可执行，只返回 JSON。'
    context = {
        'mode': mode,
        'question': question,
        'profile': profile or {},
        'policy': policy or {},
        'match_summary': match_summary or {},
        'recent_messages': list(recent_messages or []),
    }
    prompt = f"""
请根据用户画像、政策摘要和匹配结果，输出一份详细的政策解读。
要求：
1. 回答正文使用 Markdown，并至少包含：`## 结论`、`## 依据与分析`、`## 可执行步骤`、`## 注意事项`、`## 你可以继续追问我`。
2. 不得编造政策条款或审批结论；信息不足时明确说明。
3. “可执行步骤”至少给 4 条。

返回 JSON，字段：
- answer: Markdown 文本
- interpretation_report: 对象，包含 eligibility_level、key_points、next_steps、risk_warnings

上下文：
{json.dumps(context, ensure_ascii=False)}
"""
    result = _chat_json(
        system_prompt=system_prompt,
        user_prompt=prompt,
        temperature=0.35,
        max_tokens=2800,
    )

    answer = str(result.get('answer') or '').strip()
    report = result.get('interpretation_report') or {}
    if not answer:
        raise ModelProviderError('模型返回了空回答')
    if not isinstance(report, dict):
        report = {}

    level = str(report.get('eligibility_level') or '').strip().lower()
    if level not in {'high', 'medium', 'low'}:
        level = 'medium'
    answer = _expand_answer_to_detailed_markdown(
        answer=answer,
        question=question,
        context=context,
        system_prompt=system_prompt,
    )

    return {
        'answer': answer,
        'interpretation_report': {
            'eligibility_level': level,
            'key_points': [str(item).strip() for item in list(report.get('key_points') or []) if str(item).strip()][:6],
            'next_steps': [str(item).strip() for item in list(report.get('next_steps') or []) if str(item).strip()][:6],
            'risk_warnings': [str(item).strip() for item in list(report.get('risk_warnings') or []) if str(item).strip()][:4],
            'provider': 'deepseek',
        },
    }


def generate_agri_policy_qa_payload(
    *,
    question: str,
    profile: dict[str, Any] | None,
    policy: dict[str, Any] | None,
    recent_messages: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    system_prompt = '你是高质量农业政策问答助手，回答要自然、清晰、可执行，只返回 JSON。'
    context = {
        'question': question,
        'profile': profile or {},
        'policy': policy or {},
        'recent_messages': list(recent_messages or []),
    }
    prompt = f"""
请回答农业、农村、涉农政策相关问题。
要求：
1. 超出农业政策范围时，明确说明并给出可继续提问的涉农方向。
2. 不编造政策条款、办理时限或审批结果；不确定时直接说明。
3. 正文使用 Markdown，并至少包含：`## 结论`、`## 详细说明`、`## 你可以马上做的事`、`## 风险或误区`、`## 我建议你继续补充的信息`。
4. “你可以马上做的事”至少列出 4 条。

返回 JSON，字段：
- answer: Markdown 文本
- qa_report: 对象，包含 in_scope、key_points、followups、provider

上下文：
{json.dumps(context, ensure_ascii=False)}
"""
    result = _chat_json(
        system_prompt=system_prompt,
        user_prompt=prompt,
        temperature=0.4,
        max_tokens=2800,
    )

    answer = str(result.get('answer') or '').strip()
    report = result.get('qa_report') or {}
    if not answer:
        raise ModelProviderError('模型返回了空回答')
    if not isinstance(report, dict):
        report = {}

    in_scope = bool(report.get('in_scope', True))
    answer = _expand_answer_to_detailed_markdown(
        answer=answer,
        question=question,
        context=context,
        system_prompt=system_prompt,
    )
    return {
        'answer': answer,
        'qa_report': {
            'in_scope': in_scope,
            'key_points': [str(item).strip() for item in list(report.get('key_points') or []) if str(item).strip()][:6],
            'followups': [str(item).strip() for item in list(report.get('followups') or []) if str(item).strip()][:4],
            'provider': 'deepseek',
        },
    }
