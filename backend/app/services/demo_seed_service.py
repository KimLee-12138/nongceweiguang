from __future__ import annotations

import base64
import datetime as dt
from pathlib import Path
from typing import Any

from docx import Document
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin_models import AutoCrawlerRunORM, SystemConfigORM
from app.models.auth_models import AdminUserORM, AuthRefreshTokenORM, AuthSessionORM, EndUserORM, RequestRateLimitORM
from app.models.business_models import (
    ChatConversationORM,
    ChatMessageORM,
    CompassGlossaryORM,
    CompassReportORM,
    HubeiPolicyRawORM,
    MatchRecordORM,
    PolicyORM,
    UserProfileORM,
)
from app.models.policy_review_models import PolicyReviewEventORM, PolicyReviewTaskORM
from app.services.match_engine import to_match_summary
from app.services.passwords import hash_password


DEMO_ADMIN = {"username": "demo_admin", "password": "DemoAdmin123"}

DEMO_USERS = [
    {"username": "demo_farmer_a", "password": "DemoUser123"},
    {"username": "demo_farmer_b", "password": "DemoUser123"},
    {"username": "demo_farmer_c", "password": "DemoUser123"},
]

DEMO_PROFILES = [
    {"username": "demo_farmer_a", "name": "洪湖稻田基地", "type": "种植户", "area": 120, "green_cert": True, "irrigation": "高标准农田", "extra_data": {"coop_level": "省级", "county": "洪湖市"}},
    {"username": "demo_farmer_a", "name": "荆州蔬菜合作社", "type": "合作社", "area": 85, "green_cert": False, "irrigation": "滴灌", "extra_data": {"coop_level": "市级", "county": "荆州市"}},
    {"username": "demo_farmer_b", "name": "襄阳粮油家庭农场", "type": "家庭农场", "area": 60, "green_cert": True, "irrigation": "喷灌", "extra_data": {"grain_focus": True, "county": "襄阳市"}},
    {"username": "demo_farmer_b", "name": "随州香菇基地", "type": "企业", "area": 35, "green_cert": False, "irrigation": "山泉", "extra_data": {"industry": "食用菌", "county": "随州市"}},
    {"username": "demo_farmer_c", "name": "宜昌柑橘园", "type": "种植户", "area": 48, "green_cert": True, "irrigation": "滴灌", "extra_data": {"fruit": "柑橘", "county": "宜昌市"}},
    {"username": "demo_farmer_c", "name": "黄冈水产养殖场", "type": "企业", "area": 90, "green_cert": False, "irrigation": "循环水", "extra_data": {"industry": "水产", "county": "黄冈市"}},
]

DEMO_POLICIES = [
    {
        "title": "湖北省粮油绿色高产补贴",
        "source": "湖北省农业农村厅",
        "summary": "面向粮油生产主体的绿色高产补贴。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "type", "field": "type", "operator": "in", "value": ["种植户", "合作社", "家庭农场"], "must": True}, {"id": "area", "field": "area", "operator": ">=", "value": 50, "must": True}, {"id": "green", "field": "green_cert", "operator": "==", "value": True, "must": False}]},
    },
    {
        "title": "高标准农田提质改造支持政策",
        "source": "湖北省农业农村厅",
        "summary": "支持高标准农田和灌溉改造。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "irrigation", "field": "irrigation", "operator": "exists", "value": None, "must": True}, {"id": "area", "field": "area", "operator": ">=", "value": 30, "must": True}]},
    },
    {
        "title": "合作社数字农业示范奖励",
        "source": "湖北省农业农村厅",
        "summary": "面向规范合作社的数字农业奖励。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "type", "field": "type", "operator": "==", "value": "合作社", "must": True}, {"id": "coop", "field": "coop_level", "operator": "exists", "value": None, "must": True}]},
    },
    {
        "title": "食用菌产业升级扶持",
        "source": "湖北省农业农村厅",
        "summary": "支持食用菌产业设备升级。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "industry", "field": "industry", "operator": "==", "value": "食用菌", "must": True}]},
    },
    {
        "title": "柑橘品质提升专项",
        "source": "湖北省农业农村厅",
        "summary": "支持柑橘产业品质提升与绿色认证。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "fruit", "field": "fruit", "operator": "==", "value": "柑橘", "must": True}, {"id": "green", "field": "green_cert", "operator": "==", "value": True, "must": True}]},
    },
    {
        "title": "水产养殖尾水治理支持",
        "source": "湖北省农业农村厅",
        "summary": "支持水产养殖尾水治理和升级。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "industry", "field": "industry", "operator": "==", "value": "水产", "must": True}, {"id": "area", "field": "area", "operator": ">=", "value": 50, "must": False}]},
    },
    {
        "title": "家庭农场粮食烘干补助",
        "source": "湖北省农业农村厅",
        "summary": "支持家庭农场粮食烘干设备。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "type", "field": "type", "operator": "==", "value": "家庭农场", "must": True}, {"id": "grain", "field": "grain_focus", "operator": "==", "value": True, "must": False}]},
    },
    {
        "title": "绿色认证农产品品牌扶持",
        "source": "湖北省农业农村厅",
        "summary": "支持绿色认证主体品牌建设。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "green", "field": "green_cert", "operator": "==", "value": True, "must": True}]},
    },
    {
        "title": "县域农业社会化服务试点",
        "source": "湖北省农业农村厅",
        "summary": "支持县域农业社会化服务。",
        "condition_tree": {"id": "root", "logic": "or", "must": True, "children": [{"id": "county", "field": "county", "operator": "in", "value": ["洪湖市", "荆州市", "襄阳市"], "must": True}, {"id": "type", "field": "type", "operator": "==", "value": "合作社", "must": False}]},
    },
    {
        "title": "蔬菜保供基地稳产政策",
        "source": "湖北省农业农村厅",
        "summary": "支持蔬菜保供基地稳产增效。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "type", "field": "type", "operator": "in", "value": ["合作社", "企业"], "must": True}, {"id": "area", "field": "area", "operator": ">=", "value": 20, "must": True}]},
    },
    {
        "title": "设施农业节水改造项目",
        "source": "湖北省农业农村厅",
        "summary": "支持设施农业节水改造。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "irrigation", "field": "irrigation", "operator": "in", "value": ["滴灌", "喷灌"], "must": True}]},
    },
    {
        "title": "农业经营主体金融贴息支持",
        "source": "湖北省农业农村厅",
        "summary": "支持农业经营主体融资贴息。",
        "condition_tree": {"id": "root", "logic": "and", "must": True, "children": [{"id": "type", "field": "type", "operator": "in", "value": ["种植户", "合作社", "企业", "家庭农场"], "must": True}, {"id": "area", "field": "area", "operator": ">=", "value": 30, "must": False}]},
    },
]

DEMO_GLOSSARY = [
    ("结构化信号", "先计算可验证数据，再生成文字结论。"),
    ("政策画像", "面向政策的适用对象和条件抽象。"),
    ("匹配结论", "画像与条件树对比后的可执行结果。"),
    ("申报准备", "为满足政策条件需要补齐的材料与动作。"),
    ("绿色认证", "农业绿色认证相关资格。"),
    ("高标准农田", "具备较高基础设施标准的农田。"),
    ("节水灌溉", "通过滴灌、喷灌等方式降低水耗。"),
    ("社会化服务", "由专业组织提供农机、仓储等服务。"),
]


def seed_demo_data(db: Session, *, workspace_root: Path | None = None) -> dict[str, Any]:
    admin = _ensure_admin(db)
    users = _ensure_users(db)
    profiles = _ensure_profiles(db, users)
    policies = _ensure_policies(db)
    _ensure_match_records(db, profiles, policies)
    _ensure_conversations(db, users, profiles, policies)
    _ensure_compass(db)
    _ensure_raw_policies(db)
    _ensure_review_tasks(db, policies)
    _ensure_system_rows(db)
    _ensure_rate_limit_rows(db)
    _ensure_demo_sessions(db, admin, list(users.values()))
    sample_files = []
    if workspace_root is not None:
        sample_files = _write_demo_files(workspace_root)
    db.commit()
    return {
        "admin": DEMO_ADMIN["username"],
        "users": list(users.keys()),
        "profiles": len(profiles),
        "policies": len(policies),
        "sample_files": [str(path) for path in sample_files],
    }


def _ensure_admin(db: Session) -> AdminUserORM:
    admin = db.scalar(select(AdminUserORM).where(AdminUserORM.username == DEMO_ADMIN["username"]))
    if admin:
        return admin
    admin = AdminUserORM(username=DEMO_ADMIN["username"], password_hash=hash_password(DEMO_ADMIN["password"]))
    db.add(admin)
    db.flush()
    return admin


def _ensure_users(db: Session) -> dict[str, EndUserORM]:
    users: dict[str, EndUserORM] = {}
    for item in DEMO_USERS:
        user = db.scalar(select(EndUserORM).where(EndUserORM.username == item["username"]))
        if not user:
            user = EndUserORM(username=item["username"], password_hash=hash_password(item["password"]))
            db.add(user)
            db.flush()
        users[item["username"]] = user
    return users


def _ensure_profiles(db: Session, users: dict[str, EndUserORM]) -> list[UserProfileORM]:
    profiles: list[UserProfileORM] = []
    for item in DEMO_PROFILES:
        owner = users[item["username"]]
        row = db.scalar(
            select(UserProfileORM).where(
                UserProfileORM.owner_user_id == owner.id,
                UserProfileORM.name == item["name"],
            )
        )
        if not row:
            row = UserProfileORM(
                owner_user_id=owner.id,
                name=item["name"],
                type=item["type"],
                area=item["area"],
                green_cert=item["green_cert"],
                irrigation=item["irrigation"],
                extra_data=item["extra_data"],
            )
            db.add(row)
            db.flush()
        profiles.append(row)
    return profiles


def _ensure_policies(db: Session) -> list[PolicyORM]:
    policies: list[PolicyORM] = []
    for item in DEMO_POLICIES:
        row = db.scalar(select(PolicyORM).where(PolicyORM.title == item["title"]))
        if not row:
            row = PolicyORM(
                title=item["title"],
                source=item["source"],
                version="2026Q2",
                summary=item["summary"],
                raw_text_ref=f"demo://policy/{base64.urlsafe_b64encode(item['title'].encode('utf-8')).decode('ascii').rstrip('=')}",
                condition_tree=item["condition_tree"],
            )
            db.add(row)
            db.flush()
        policies.append(row)
    return policies


def _ensure_match_records(db: Session, profiles: list[UserProfileORM], policies: list[PolicyORM]) -> None:
    for profile, policy in zip(profiles, policies[:6]):
        exists = db.scalar(
            select(MatchRecordORM).where(
                MatchRecordORM.user_profile_id == profile.id,
                MatchRecordORM.policy_id == policy.id,
            )
        )
        if exists:
            continue
        profile_dict = {
            "name": profile.name,
            "type": profile.type,
            "area": profile.area,
            "green_cert": profile.green_cert,
            "irrigation": profile.irrigation,
            "extra_data": profile.extra_data or {},
        }
        summary = to_match_summary(policy.condition_tree or {}, profile_dict)
        db.add(
            MatchRecordORM(
                user_profile_id=profile.id,
                policy_id=policy.id,
                fully_matched=summary["fully_matched"],
                match_detail=summary,
                expected_subsidy=0.0,
                total_cost_to_comply=0.0,
                roi=None,
            )
        )


def _ensure_conversations(db: Session, users: dict[str, EndUserORM], profiles: list[UserProfileORM], policies: list[PolicyORM]) -> None:
    examples = [
        (users["demo_farmer_a"], profiles[0], policies[0], "我能申请哪项粮食补贴？"),
        (users["demo_farmer_b"], profiles[2], policies[6], "家庭农场的烘干补助怎么准备？"),
        (users["demo_farmer_c"], profiles[4], policies[4], "柑橘园适合哪些提升政策？"),
    ]
    for user, profile, policy, question in examples:
        conv = db.scalar(
            select(ChatConversationORM).where(
                ChatConversationORM.owner_user_id == user.id,
                ChatConversationORM.title == question[:20],
            )
        )
        if not conv:
            conv = ChatConversationORM(
                owner_user_id=user.id,
                title=question[:20],
                last_message_at=dt.datetime.utcnow(),
                last_mode="match",
                last_profile_id=profile.id,
            )
            db.add(conv)
            db.flush()
            summary = to_match_summary(
                policy.condition_tree or {},
                {
                    "name": profile.name,
                    "type": profile.type,
                    "area": profile.area,
                    "green_cert": profile.green_cert,
                    "irrigation": profile.irrigation,
                    "extra_data": profile.extra_data or {},
                },
            )
            db.add(
                ChatMessageORM(
                    conversation_id=conv.id,
                    sequence=1,
                    role="user",
                    status="done",
                    content=question,
                    mode="match",
                    profile_id=profile.id,
                    profile_snapshot_json={"profile_id": profile.id},
                    citation_json={},
                    render_payload_json={},
                    error_message=None,
                )
            )
            db.add(
                ChatMessageORM(
                    conversation_id=conv.id,
                    sequence=2,
                    role="assistant",
                    status="done",
                    content=f"已根据画像 {profile.name} 生成政策体检。",
                    mode="match",
                    profile_id=profile.id,
                    profile_snapshot_json={"profile_id": profile.id},
                    citation_json={},
                    render_payload_json={"policy_report": {"policy_id": policy.id, "title": policy.title, "match_summary": summary}},
                    error_message=None,
                )
            )


def _ensure_compass(db: Session) -> None:
    reports = db.scalars(select(CompassReportORM).where(CompassReportORM.title.in_(["本周湖北涉农风向标", "县域产业机会观察"]))).all()
    if len(reports) < 2:
        for title, summary in [
            ("本周湖北涉农风向标", "聚焦粮食生产、节水灌溉和绿色认证三条主线。"),
            ("县域产业机会观察", "合作社数字化、食用菌和柑橘提质仍是高频主题。"),
        ]:
            exists = db.scalar(select(CompassReportORM).where(CompassReportORM.title == title))
            if exists:
                continue
            db.add(
                CompassReportORM(
                    title=title,
                    category="weekly",
                    summary=summary,
                    content=f"## 趋势\n{summary}\n\n## 机会\n建议优先关注样板项目。\n\n## 准备事项\n完善画像、材料与历史匹配记录。",
                    published_at=dt.datetime.utcnow(),
                )
            )
    for term, description in DEMO_GLOSSARY:
        exists = db.scalar(select(CompassGlossaryORM).where(CompassGlossaryORM.term == term))
        if exists:
            continue
        db.add(CompassGlossaryORM(term=term, description=description, published_at=dt.datetime.utcnow()))


def _ensure_raw_policies(db: Session) -> None:
    rows = [
        {
            "title": "关于推进粮食绿色高产高效行动的通知",
            "issuer": "湖北省农业农村厅",
            "page_url": "https://demo.local/hubei/raw/1",
            "topic_category": "粮食生产",
        },
        {
            "title": "关于开展节水灌溉设施改造的通知",
            "issuer": "湖北省农业农村厅",
            "page_url": "https://demo.local/hubei/raw/2",
            "topic_category": "节水改造",
        },
    ]
    for item in rows:
        exists = db.scalar(select(HubeiPolicyRawORM).where(HubeiPolicyRawORM.page_url == item["page_url"]))
        if exists:
            continue
        db.add(
            HubeiPolicyRawORM(
                title=item["title"],
                issuer=item["issuer"],
                doc_no=None,
                publish_date=dt.date.today(),
                column_name="演示数据",
                file_category="policy",
                topic_category=item["topic_category"],
                page_url=item["page_url"],
                attachment_urls=[],
                html_text=item["title"],
                attachment_text="",
                full_text=f"{item['title']}。该条目用于联调和风向标演示。",
            )
        )


def _ensure_review_tasks(db: Session, policies: list[PolicyORM]) -> None:
    titles = ["文件导入待审核示例", "爬虫待审核示例"]
    for idx, title in enumerate(titles):
        exists = db.scalar(select(PolicyReviewTaskORM).where(PolicyReviewTaskORM.title == title))
        if exists:
            continue
        task = PolicyReviewTaskORM(
            source_type="manual" if idx == 0 else "crawler",
            source_ref=f"demo://review/{idx + 1}",
            raw_policy_id=None,
            title=title,
            source="demo",
            raw_text="这是一条用于审核台联调的演示政策原文。",
            raw_text_ref=f"demo://review-raw/{idx + 1}",
            review_status="pending",
            draft_status="success",
            ai_status="success",
            ai_risk_points_json=[],
            ai_evidence_json=[],
            created_by=DEMO_ADMIN["username"],
            draft_title=policies[idx].title,
            draft_source=policies[idx].source,
            draft_summary=policies[idx].summary,
            draft_category="其他",
            draft_condition_tree=policies[idx].condition_tree,
            ai_summary=policies[idx].summary,
            ai_category="其他",
            ai_suggestion="请核对条件树字段命名与原文一致。",
            ai_recommendation="适合用于审核台演示。",
        )
        db.add(task)
        db.flush()
        db.add(
            PolicyReviewEventORM(
                task_id=task.id,
                event_type="created",
                operator=DEMO_ADMIN["username"],
                before_snapshot_json=None,
                after_snapshot_json={"review_status": "pending"},
                comment="demo seed",
            )
        )


def _ensure_system_rows(db: Session) -> None:
    auto_config = db.get(SystemConfigORM, "auto_crawler")
    value = {"enabled": True, "sources": ["hubei_agri_policy"], "interval_hours": 24, "max_pages_per_source": 3}
    if auto_config:
        auto_config.set_json_value(value)
    else:
        row = SystemConfigORM(key="auto_crawler")
        row.set_json_value(value)
        db.add(row)

    if not db.scalar(select(AutoCrawlerRunORM).limit(1)):
        db.add(
            AutoCrawlerRunORM(
                status="success",
                source_ids_json=["hubei_agri_policy"],
                max_pages=3,
                created_by=DEMO_ADMIN["username"],
                summary_message="演示自动爬虫运行记录",
                started_at=dt.datetime.utcnow(),
                finished_at=dt.datetime.utcnow(),
            )
        )


def _ensure_rate_limit_rows(db: Session) -> None:
    if db.scalar(select(RequestRateLimitORM).limit(1)):
        return
    db.add(
        RequestRateLimitORM(
            scope="demo",
            subject_type="user",
            subject_key="demo_farmer_a",
            window_started_at=dt.datetime.utcnow(),
            count=1,
            blocked_until=None,
            last_seen_at=dt.datetime.utcnow(),
        )
    )


def _ensure_demo_sessions(db: Session, admin: AdminUserORM, users: list[EndUserORM]) -> None:
    if db.scalar(select(AuthSessionORM).where(AuthSessionORM.principal_role == "admin", AuthSessionORM.principal_id == admin.id)):
        return
    now = dt.datetime.utcnow()
    admin_session = AuthSessionORM(
        session_id="demo-admin-session",
        principal_role="admin",
        principal_id=admin.id,
        expires_at=now + dt.timedelta(days=7),
        user_agent="demo-seed",
        ip="127.0.0.1",
        last_seen_at=now,
    )
    db.add(admin_session)
    db.flush()
    db.add(
        AuthRefreshTokenORM(
            jti="demo-admin-refresh",
            session_id=admin_session.session_id,
            token_hash="demo-admin-refresh-token",
            expires_at=now + dt.timedelta(days=7),
        )
    )
    for user in users[:2]:
        session_id = f"demo-user-session-{user.id}"
        session = AuthSessionORM(
            session_id=session_id,
            principal_role="user",
            principal_id=user.id,
            expires_at=now + dt.timedelta(days=7),
            user_agent="demo-seed",
            ip="127.0.0.1",
            last_seen_at=now,
        )
        db.add(session)
        db.flush()


def _write_demo_files(workspace_root: Path) -> list[Path]:
    base_dir = workspace_root / "reports" / "demo-files"
    base_dir.mkdir(parents=True, exist_ok=True)
    files = [
        (base_dir / "policy_sample_1.docx", "湖北粮油绿色高产补贴示例\n适用对象：种植户、合作社、家庭农场。\n面积要求：50亩及以上。"),
        (base_dir / "policy_sample_2.docx", "设施农业节水改造示例\n适用对象：节水灌溉主体。\n建议材料：基地证明、设备清单。"),
    ]
    for path, text in files:
        if not path.exists():
            doc = Document()
            for line in text.splitlines():
                doc.add_paragraph(line)
            doc.save(path)

    pdf_files = [
        (base_dir / "policy_sample_3.pdf", "Demo policy PDF A\nEligible type: cooperative\nArea >= 20"),
        (base_dir / "policy_sample_4.pdf", "Demo policy PDF B\nEligible type: family farm\nNeed irrigation proof"),
    ]
    for path, text in pdf_files:
        if not path.exists():
            path.write_bytes(_build_simple_pdf(text))
    return [path for path, _ in files + pdf_files]


def _build_simple_pdf(text: str) -> bytes:
    lines = text.splitlines() or [text]
    stream_lines = ["BT", "/F1 12 Tf", "50 780 Td"]
    for idx, line in enumerate(lines):
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if idx:
            stream_lines.append("0 -18 Td")
        stream_lines.append(f"({safe}) Tj")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream",
    ]

    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(content))
        content.extend(f"{index} 0 obj\n".encode("ascii"))
        content.extend(obj)
        content.extend(b"\nendobj\n")

    xref_start = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    content.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii")
    )
    return bytes(content)
