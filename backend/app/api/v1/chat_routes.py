from __future__ import annotations

import datetime as dt
import json
import time
from collections.abc import Generator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, desc, func, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.api.v1.schemas_chat import ChatStreamRequest, ConversationDetailOut, ConversationOut
from app.db.session import get_db
from app.models.auth_models import EndUserORM
from app.models.business_models import ChatConversationORM, ChatMessageORM, PolicyORM, UserProfileORM
from app.services.match_engine import to_match_summary
from app.services.model_provider import (
    ModelProviderError,
    generate_agri_policy_qa_payload,
    generate_chat_interpretation_payload,
)


router = APIRouter(prefix="/chat", tags=["chat"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _profile_snapshot(profile: UserProfileORM | None) -> dict[str, Any]:
    if not profile:
        return {}
    return {
        "id": profile.id,
        "name": profile.name,
        "type": profile.type,
        "area": profile.area,
        "green_cert": profile.green_cert,
        "irrigation": profile.irrigation,
        "extra_data": profile.extra_data or {},
    }


def _policy_context(policy: PolicyORM | None) -> dict[str, Any] | None:
    if not policy:
        return None
    return {
        "policy_id": policy.id,
        "title": policy.title,
        "source": policy.source,
        "summary": policy.summary,
        "raw_text_ref": policy.raw_text_ref,
        "condition_tree": policy.condition_tree or {},
    }


def _recent_messages(db: Session, conversation_id: int, limit: int = 6) -> list[dict[str, str]]:
    rows = db.scalars(
        select(ChatMessageORM)
        .where(ChatMessageORM.conversation_id == conversation_id, ChatMessageORM.role.in_(["user", "assistant"]))
        .order_by(desc(ChatMessageORM.id))
        .limit(limit)
    ).all()
    output: list[dict[str, str]] = []
    for row in reversed(rows):
        content = (row.content or "").strip()
        if not content:
            continue
        output.append({"role": row.role, "content": content[:1200]})
    return output


def _match_based_fallback_answer(
    *,
    question: str,
    mode: str,
    profile_snapshot: dict[str, Any],
    policy_ctx: dict[str, Any] | None,
    match_summary: dict[str, Any] | None,
) -> str:
    user_name = profile_snapshot.get("name") if profile_snapshot else None
    policy_title = (policy_ctx or {}).get("title")
    lines = [f"## 结论\n{user_name or '你'}好，我先给你一个保守但可执行的判断。"]
    if policy_title:
        lines.append(f"\n你当前关注政策：**《{policy_title}》**。")
    if mode == "match" and match_summary:
        must_failed = match_summary.get("must_failed", len(match_summary.get("failed_must_nodes") or []))
        lines.append(f"\n目前你大概率还有 **{must_failed}** 个关键条件需要补齐。")
    else:
        lines.append("\n我会先用白话讲清政策逻辑，再给你下一步方案。")

    action_steps = list((match_summary or {}).get("action_steps") or [])
    lines.append("\n## 你现在可以做什么")
    if action_steps:
        for idx, step in enumerate(action_steps[:3], start=1):
            lines.append(f"{idx}. {step}")
    else:
        lines.append("1. 先确认你所在区县、主体类型、经营面积这三个核心信息。")
        lines.append("2. 准备主体资质、土地/经营证明、近一年经营材料。")
        lines.append("3. 对照政策条款逐项核对是否满足准入条件。")
        lines.append("4. 如果你愿意，我可以继续给你“材料清单 + 办理顺序”。")

    lines.append(f"\n## 你的问题\n> {question}")
    return "\n".join(lines)


def _agri_llm_fallback_answer(
    *,
    question: str,
    profile_snapshot: dict[str, Any],
    policy_ctx: dict[str, Any] | None,
) -> str:
    user_name = profile_snapshot.get("name") if profile_snapshot else None
    lines = [f"## 结论\n{user_name or '你'}好，这个问题我可以按农业政策口径帮你分析。"]
    if policy_ctx:
        lines.append(f"\n我会结合你当前选中的 **《{policy_ctx.get('title') or '相关政策'}》** 一起回答。")
    lines.append("\n## 通用判断框架")
    lines.append("1. 先确认政策适用对象（你是否属于目标主体）。")
    lines.append("2. 再核对准入门槛（面积、资质、认证、行业方向）。")
    lines.append("3. 最后准备申报材料（主体证明、经营证明、辅助附件）。")
    lines.append(f"\n## 你的问题\n> {question}")
    lines.append("\n## 建议补充信息")
    lines.append("- 所在地区（省/市/区县）")
    lines.append("- 经营主体类型（家庭农场/合作社/企业）")
    lines.append("- 当前最关心的是“能不能报”还是“怎么报”")
    return "\n".join(lines)


def _validate_stream_mode(payload: ChatStreamRequest):
    if payload.mode not in {"match", "interpret"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="mode 仅支持 match 或 interpret；农业政策大模型请调用 /chat/agri-llm/stream",
        )
    if payload.mode == "interpret" and not payload.policy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="政策白话解读模式必须先选择政策",
        )


def _chunk_text(text: str, size: int = 8) -> Generator[str, None, None]:
    if size <= 0:
        size = 1
    for i in range(0, len(text), size):
        yield text[i : i + size]


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    rows = db.scalars(
        select(ChatConversationORM).where(ChatConversationORM.owner_user_id == user.id).order_by(desc(ChatConversationORM.updated_at))
    ).all()
    return [ConversationOut(id=r.id, title=r.title, last_mode=r.last_mode, last_profile_id=r.last_profile_id) for r in rows]


@router.post("/conversations", response_model=ConversationOut)
def create_conversation(db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    conv = ChatConversationORM(owner_user_id=user.id, title="新会话")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationOut(id=conv.id, title=conv.title, last_mode=conv.last_mode, last_profile_id=conv.last_profile_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db), user: EndUserORM = Depends(get_current_user)):
    conv = db.get(ChatConversationORM, conversation_id)
    if not conv or conv.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    msgs = db.scalars(
        select(ChatMessageORM).where(ChatMessageORM.conversation_id == conv.id).order_by(ChatMessageORM.id.asc()).limit(200)
    ).all()
    return ConversationDetailOut(
        conversation=ConversationOut(id=conv.id, title=conv.title, last_mode=conv.last_mode, last_profile_id=conv.last_profile_id),
        messages=[
            {
                "id": m.id,
                "role": m.role,
                "status": m.status,
                "content": m.content,
                "render_payload_json": m.render_payload_json,
                "created_at": m.created_at.isoformat(),
            }
            for m in msgs
        ],
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: EndUserORM = Depends(get_current_user),
):
    conv = db.get(ChatConversationORM, conversation_id)
    if not conv or conv.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    db.execute(delete(ChatMessageORM).where(ChatMessageORM.conversation_id == conversation_id))
    db.delete(conv)
    db.commit()


@router.post("/stream")
def stream_chat(
    payload: ChatStreamRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: EndUserORM = Depends(get_current_user),
):
    _ = request
    _validate_stream_mode(payload)
    # 确保会话存在
    if payload.conversation_id:
        conv = db.get(ChatConversationORM, payload.conversation_id)
        if not conv or conv.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conv = ChatConversationORM(owner_user_id=user.id, title="新会话", last_mode=payload.mode, last_profile_id=payload.profile_id)
        db.add(conv)
        db.flush()

    conv.last_mode = payload.mode
    conv.last_profile_id = payload.profile_id
    conv.last_message_at = time_to_dt()

    # 画像快照（用于回放）
    profile = None
    if payload.profile_id:
        profile = db.get(UserProfileORM, payload.profile_id)
        if not profile or profile.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile_snapshot = _profile_snapshot(profile)

    policy = None
    if payload.policy_id:
        policy = db.get(PolicyORM, payload.policy_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    policy_ctx = _policy_context(policy)
    match_summary = to_match_summary(policy.condition_tree or {}, profile_snapshot) if policy and profile else None
    recent_messages = _recent_messages(db, conv.id, limit=6)

    # 先落库用户消息与助手消息（助手消息 streaming）
    next_seq = (db.scalar(select(func.max(ChatMessageORM.sequence)).where(ChatMessageORM.conversation_id == conv.id)) or 0) + 1
    user_msg = ChatMessageORM(
        conversation_id=conv.id,
        sequence=next_seq,
        role="user",
        status="done",
        content=payload.message,
        mode=payload.mode,
        profile_id=payload.profile_id,
        profile_snapshot_json=profile_snapshot,
        citation_json={},
        render_payload_json={},
        error_message=None,
    )
    assistant_msg = ChatMessageORM(
        conversation_id=conv.id,
        sequence=next_seq + 1,
        role="assistant",
        status="streaming",
        content="",
        mode=payload.mode,
        profile_id=payload.profile_id,
        profile_snapshot_json=profile_snapshot,
        citation_json={},
        render_payload_json={},
        error_message=None,
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    conv_id = conv.id
    assistant_message_id = assistant_msg.id
    policy_id = policy.id if policy else None

    policy_report = None
    if match_summary and policy:
        policy_report = {
            "policy_id": policy.id,
            "title": policy.title,
            "summary": policy.summary,
            "match_summary": match_summary,
        }

    def event_gen() -> Generator[str, None, None]:
        # 开场 meta
        yield _sse("message_meta", {"conversation_id": conv_id, "assistant_message_id": assistant_message_id})

        if policy_ctx:
            yield _sse("policy_context", policy_ctx)
        if policy_report:
            yield _sse("policy_report", policy_report)

        interpretation_report = {
            "eligibility_level": "medium",
            "key_points": [],
            "next_steps": list((match_summary or {}).get("action_steps") or [])[:3],
            "risk_warnings": list((match_summary or {}).get("risk_warnings") or [])[:3],
            "provider": "fallback",
        }
        text = _match_based_fallback_answer(
            question=payload.message,
            mode=payload.mode,
            profile_snapshot=profile_snapshot,
            policy_ctx=policy_ctx,
            match_summary=match_summary,
        )

        try:
            result = generate_chat_interpretation_payload(
                question=payload.message,
                mode=payload.mode,
                profile=profile_snapshot,
                policy=policy_ctx,
                match_summary=match_summary,
                recent_messages=recent_messages,
            )
            text = result["answer"]
            interpretation_report = result["interpretation_report"]
        except ModelProviderError as exc:
            interpretation_report["error"] = str(exc)

        yield _sse("interpretation_report", interpretation_report)

        acc = ""
        for chunk in _chunk_text(text):
            acc += chunk
            yield _sse("content", {"delta": chunk})
            time.sleep(0.005)

        # 结束事件
        yield _sse("content_done", {"ok": True, "provider": interpretation_report.get("provider")})

        # 落库最终内容与 render_payload
        render_payload = {}
        if policy_ctx:
            render_payload["policy_context"] = policy_ctx
        if policy_report:
            render_payload["policy_report"] = policy_report
        if interpretation_report:
            render_payload["interpretation_report"] = interpretation_report

        assistant_row = db.get(ChatMessageORM, assistant_message_id)
        if assistant_row:
            assistant_row.content = acc
            assistant_row.status = "done"
            assistant_row.render_payload_json = render_payload
            assistant_row.error_message = None
            assistant_row.citation_json = {"policy_id": policy_id} if policy_id else {}

        conv_row = db.get(ChatConversationORM, conv_id)
        if conv_row:
            conv_row.last_message_at = time_to_dt()
        db.commit()

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.post("/agri-llm/stream")
def stream_agri_llm_chat(
    payload: ChatStreamRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: EndUserORM = Depends(get_current_user),
):
    _ = request
    mode = "agri_llm"

    if payload.conversation_id:
        conv = db.get(ChatConversationORM, payload.conversation_id)
        if not conv or conv.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conv = ChatConversationORM(owner_user_id=user.id, title="新会话", last_mode=mode, last_profile_id=payload.profile_id)
        db.add(conv)
        db.flush()

    conv.last_mode = mode
    conv.last_profile_id = payload.profile_id
    conv.last_message_at = time_to_dt()

    profile = None
    if payload.profile_id:
        profile = db.get(UserProfileORM, payload.profile_id)
        if not profile or profile.owner_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile_snapshot = _profile_snapshot(profile)

    policy = None
    if payload.policy_id:
        policy = db.get(PolicyORM, payload.policy_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    policy_ctx = _policy_context(policy)

    recent_messages = _recent_messages(db, conv.id, limit=6)
    next_seq = (db.scalar(select(func.max(ChatMessageORM.sequence)).where(ChatMessageORM.conversation_id == conv.id)) or 0) + 1
    user_msg = ChatMessageORM(
        conversation_id=conv.id,
        sequence=next_seq,
        role="user",
        status="done",
        content=payload.message,
        mode=mode,
        profile_id=payload.profile_id,
        profile_snapshot_json=profile_snapshot,
        citation_json={},
        render_payload_json={},
        error_message=None,
    )
    assistant_msg = ChatMessageORM(
        conversation_id=conv.id,
        sequence=next_seq + 1,
        role="assistant",
        status="streaming",
        content="",
        mode=mode,
        profile_id=payload.profile_id,
        profile_snapshot_json=profile_snapshot,
        citation_json={},
        render_payload_json={},
        error_message=None,
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    conv_id = conv.id
    assistant_message_id = assistant_msg.id
    policy_id = policy.id if policy else None

    def event_gen() -> Generator[str, None, None]:
        yield _sse("message_meta", {"conversation_id": conv_id, "assistant_message_id": assistant_message_id})
        if policy_ctx:
            yield _sse("policy_context", policy_ctx)

        qa_report = {"in_scope": True, "key_points": [], "followups": [], "provider": "fallback"}
        text = _agri_llm_fallback_answer(
            question=payload.message,
            profile_snapshot=profile_snapshot,
            policy_ctx=policy_ctx,
        )
        try:
            result = generate_agri_policy_qa_payload(
                question=payload.message,
                profile=profile_snapshot if profile_snapshot else None,
                policy=policy_ctx,
                recent_messages=recent_messages,
            )
            text = result["answer"]
            qa_report = result["qa_report"]
        except ModelProviderError as exc:
            qa_report["error"] = str(exc)

        yield _sse("agri_qa_report", qa_report)

        acc = ""
        for chunk in _chunk_text(text):
            acc += chunk
            yield _sse("content", {"delta": chunk})
            time.sleep(0.005)

        yield _sse("content_done", {"ok": True, "provider": qa_report.get("provider")})

        render_payload = {"agri_qa_report": qa_report}
        if policy_ctx:
            render_payload["policy_context"] = policy_ctx

        assistant_row = db.get(ChatMessageORM, assistant_message_id)
        if assistant_row:
            assistant_row.content = acc
            assistant_row.status = "done"
            assistant_row.render_payload_json = render_payload
            assistant_row.error_message = None
            assistant_row.citation_json = {"policy_id": policy_id} if policy_id else {}

        conv_row = db.get(ChatConversationORM, conv_id)
        if conv_row:
            conv_row.last_message_at = time_to_dt()
        db.commit()

    return StreamingResponse(event_gen(), media_type="text/event-stream")


def time_to_dt():
    return dt.datetime.utcnow()

