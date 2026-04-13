from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import ValidationError

from app.api.v1.schemas_profiles import UserProfileIn
from app.core.config import get_settings
from app.services.model_provider import ModelProviderError, _chat_json


def _str_or_empty(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def build_profile_from_answers(answers: dict[str, Any]) -> dict[str, Any]:
    """Deterministic mapping from onboarding answers (q1..q20) to UserProfileIn-shaped dict."""
    a = answers or {}

    type_map = {
        "household": "种植户",
        "family_farm": "家庭农场",
        "coop": "合作社",
        "enterprise": "企业",
    }
    raw_type = _str_or_empty(a.get("q1")) or "household"
    p_type = type_map.get(raw_type, "种植户")

    area_map = {
        "lt50": 25.0,
        "50_200": 125.0,
        "200_500": 350.0,
        "gt500": 600.0,
    }
    raw_area = a.get("q2")
    try:
        area = float(area_map.get(str(raw_area), 25.0))
    except (TypeError, ValueError):
        area = 25.0

    gcs = _str_or_empty(a.get("q4")) or "none"
    green_cert = gcs == "certified"
    green_cert_status: Literal["certified", "pending", "none"] = (
        "certified" if gcs == "certified" else ("pending" if gcs == "pending" else "none")
    )

    irr_map = {
        "flood": "漫灌",
        "drip": "滴灌",
        "sprinkler": "喷灌",
        "rainfed": "靠天",
    }
    raw_irr = _str_or_empty(a.get("q5")) or "flood"
    irrigation = irr_map.get(raw_irr, "漫灌")

    name = _str_or_empty(a.get("q6"))
    if not name:
        name = f"{p_type}经营画像"

    county_map = {
        "honghu": "洪湖市",
        "jingzhou": "荆州市",
        "xiangyang": "襄阳市",
        "yichang": "宜昌市",
        "huanggang": "黄冈市",
        "suizhou": "随州市",
        "wuhan": "武汉市",
        "hubei_other": "省内其他",
        "outside": "省外",
    }
    county = county_map.get(_str_or_empty(a.get("q7")), "省内其他")

    industry_map = {
        "grain_oil": "粮食油料",
        "veg_fruit": "蔬菜瓜果",
        "forestry_fruit": "林果",
        "livestock": "畜禽",
        "aquaculture": "水产",
        "edible_fungus": "食用菌",
        "tcm": "中药材",
        "mixed": "混合",
    }
    ind_key = _str_or_empty(a.get("q8")) or "mixed"
    industry = industry_map.get(ind_key, "混合")

    gf_raw = a.get("q9")
    if isinstance(gf_raw, bool):
        grain_focus = gf_raw
    else:
        s = _str_or_empty(gf_raw)
        grain_focus = s in ("yes", "true", "1") or s == "是"

    if industry == "粮食油料":
        grain_focus = True

    fruit_map = {
        "citrus": "柑橘",
        "pome": "苹果梨桃",
        "na": "不涉及",
        "other": "其他",
    }
    fruit = fruit_map.get(_str_or_empty(a.get("q10")), "不涉及")

    coop_map = {
        "provincial": "省级",
        "municipal": "市级",
        "county": "县级",
        "none": "未获评",
        "na": "不适用",
    }
    coop_level = coop_map.get(_str_or_empty(a.get("q11")), "不适用")

    years_map = {
        "lt1": "lt1",
        "y1_3": "y1_3",
        "y3_10": "y3_10",
        "gt10": "gt10",
    }
    operating_years = years_map.get(_str_or_empty(a.get("q12")), "y1_3")

    ins_map = {
        "full": "full",
        "partial": "partial",
        "none": "none",
        "unknown": "unknown",
    }
    agri_insurance = ins_map.get(_str_or_empty(a.get("q13")), "unknown")

    mech_map = {
        "low": "low",
        "medium": "medium",
        "facility_heavy": "facility_heavy",
        "minimal": "minimal",
    }
    mechanization = mech_map.get(_str_or_empty(a.get("q14")), "medium")

    land_map = {
        "own_contract": "own_contract",
        "leased": "leased",
        "mixed": "mixed",
        "park": "park",
    }
    land_tenure = land_map.get(_str_or_empty(a.get("q15")), "mixed")

    q16 = a.get("q16")
    if isinstance(q16, list):
        sales_channels = [str(x) for x in q16]
    elif q16 is None or q16 == "":
        sales_channels = []
    else:
        sales_channels = [str(q16)]

    emp_map = {
        "0": "0",
        "1_5": "1_5",
        "6_20": "6_20",
        "gt20": "gt20",
    }
    employees = emp_map.get(_str_or_empty(a.get("q17")), "0")

    loan_map = {
        "active": "active",
        "once": "once",
        "none": "none",
        "unknown": "unknown",
    }
    loan_history = loan_map.get(_str_or_empty(a.get("q18")), "unknown")

    q19 = a.get("q19")
    if isinstance(q19, list):
        support_focus = [str(x) for x in q19]
    elif q19 is None or q19 == "":
        support_focus = []
    else:
        support_focus = [str(q19)]

    user_notes = _str_or_empty(a.get("q20"))

    q3 = a.get("q3")
    if isinstance(q3, list):
        crops = [str(x) for x in q3]
    elif q3 is None or q3 == "":
        crops = []
    else:
        crops = [str(q3)]

    extra_data: dict[str, Any] = {
        "crops": crops,
        "green_cert_status": green_cert_status,
        "county": county,
        "industry": industry,
        "grain_focus": grain_focus,
        "fruit": fruit,
        "coop_level": coop_level,
        "operating_years": operating_years,
        "agri_insurance": agri_insurance,
        "mechanization": mechanization,
        "land_tenure": land_tenure,
        "sales_channels": sales_channels,
        "employees": employees,
        "loan_history": loan_history,
        "support_focus": support_focus,
    }
    if user_notes:
        extra_data["user_notes"] = user_notes

    return {
        "name": name[:128],
        "type": p_type,
        "area": max(0.0, area),
        "green_cert": green_cert,
        "irrigation": irrigation,
        "extra_data": extra_data,
    }


def validate_profile_dict(data: dict[str, Any]) -> UserProfileIn:
    return UserProfileIn.model_validate(data)


def refine_profile_with_model(*, answers: dict[str, Any], local_profile: dict[str, Any]) -> dict[str, Any]:
    """Call DeepSeek to reconcile conflicts; must return UserProfileIn-shaped dict."""
    system_prompt = """你是农业经营主体画像归一助手。你只输出一个 JSON 对象，不要 Markdown。
必须严格符合用户给定的 schema：name(string), type(string), area(number>=0), green_cert(boolean), irrigation(string), extra_data(object)。
type 只能是：种植户、家庭农场、合作社、企业 之一。
irrigation 只能是：漫灌、滴灌、喷灌、靠天 之一。
extra_data 保留本地草稿中的键，可微调值以消除矛盾（例如 Q3 与 Q8 主导产业不一致时以 Q8 为准并同步 crops 语义说明可在 extra_data.ai_notes 简短中文一句）。
不要新增与政策匹配无关的长篇文字。若无法改进，返回与 local_profile 等价的 JSON。"""
    user_prompt = f"""
本地规则生成的画像（优先作为基准，仅在有明确理由时微调）：
{json.dumps(local_profile, ensure_ascii=False)}

原始问卷答案（键 q1..q20）：
{json.dumps(answers, ensure_ascii=False)}

请输出最终画像 JSON，字段仅限：name, type, area, green_cert, irrigation, extra_data。
"""
    result = _chat_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.15,
        max_tokens=2000,
    )
    if not isinstance(result, dict):
        raise ModelProviderError("模型返回格式错误")
    merged = {**local_profile, **result}
    merged["extra_data"] = {**(local_profile.get("extra_data") or {}), **(result.get("extra_data") or {})}
    try:
        validated = validate_profile_dict(merged)
        return validated.model_dump()
    except ValidationError as exc:
        raise ModelProviderError(f"模型输出未通过校验：{exc}") from exc


def refine_onboarding(
    answers: dict[str, Any], *, use_model: bool = True
) -> tuple[dict[str, Any], Literal["local", "deepseek"]]:
    """Build local profile; optionally refine with DeepSeek."""
    local = build_profile_from_answers(answers)
    if not use_model or not get_settings().DEEPSEEK_API_KEY:
        return local, "local"
    try:
        refined = refine_profile_with_model(answers=answers, local_profile=local)
        return refined, "deepseek"
    except ModelProviderError:
        return local, "local"

