from __future__ import annotations

import argparse
import json
from pathlib import Path

import bcrypt
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.main import create_app
from app.db.init_db import create_all_tables
from app.db.session import get_engine
from app.models.auth_models import AdminUserORM
from app.services.demo_seed_service import DEMO_ADMIN, DEMO_USERS, seed_demo_data
from app.services.dependency_service import collect_dependency_status


def init_admin(username: str, password: str) -> None:
    create_all_tables()
    engine = get_engine()
    with Session(engine) as db:
        exists = db.scalar(select(AdminUserORM).where(AdminUserORM.username == username))
        if exists:
            print("管理员已存在")
            return
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        db.add(AdminUserORM(username=username, password_hash=pw_hash))
        db.commit()
        print("管理员已创建")


def seed_demo(workspace_root: str | None = None) -> None:
    create_all_tables()
    engine = get_engine()
    root = Path(workspace_root).resolve() if workspace_root else None
    with Session(engine) as db:
        result = seed_demo_data(db, workspace_root=root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def verify_baseline(live: bool = False) -> None:
    create_all_tables()
    app = create_app()
    engine = get_engine()
    required_tables = [
        "admin_users",
        "end_users",
        "auth_sessions",
        "auth_refresh_tokens",
        "request_rate_limits",
        "user_profiles",
        "policies",
        "match_records",
        "chat_conversations",
        "chat_messages",
        "policy_review_tasks",
        "policy_review_events",
        "hubei_policies_raw",
        "compass_reports",
        "compass_glossary",
        "system_config",
        "admin_operation_runs",
        "admin_operation_run_items",
        "auto_crawler_runs",
        "telemetry_events",
    ]
    with Session(engine) as db:
        dep_status = collect_dependency_status(db, live=live)
        table_names = sorted(inspect(engine).get_table_names())
        route_paths = sorted({route.path for route in app.routes if getattr(route, "path", "").startswith("/api/v1")})
    missing = [table for table in required_tables if table not in table_names]
    output = {
        "ok": dep_status["ok"] and not missing,
        "dependencies": dep_status,
        "tables": {"required": required_tables, "missing": missing, "all": table_names},
        "routes": route_paths,
        "demo_credentials": {
            "admin": DEMO_ADMIN,
            "users": DEMO_USERS,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="ncwg-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init-admin", help="初始化管理员账号")
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)

    p = sub.add_parser("seed-demo", help="写入 MySQL 联调/演示数据")
    p.add_argument("--workspace-root", default=None, help="工作区根目录，用于生成演示文件")

    p = sub.add_parser("verify-baseline", help="校验 P0 基线环境、表、接口与依赖")
    p.add_argument("--live", action="store_true", help="执行在线依赖验证")

    args = parser.parse_args()
    if args.cmd == "init-admin":
        init_admin(args.username, args.password)
    elif args.cmd == "seed-demo":
        seed_demo(args.workspace_root)
    elif args.cmd == "verify-baseline":
        verify_baseline(live=args.live)


if __name__ == "__main__":
    main()

