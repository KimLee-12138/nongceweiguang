from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_admin
from app.db.session import get_db
from app.models.admin_models import AdminOperationRunItemORM, AdminOperationRunORM, TelemetryEventORM
from app.models.auth_models import AdminUserORM
from app.models.business_models import CompassReportORM, PolicyORM
from app.models.policy_review_models import PolicyReviewTaskORM
from app.services.admin_operation_service import consume_one_pending_run


router = APIRouter(prefix="/admin-ops", tags=["admin-ops"])


@router.get("/dashboard-summary")
def dashboard_summary(db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    policy_count = db.scalar(select(func.count()).select_from(PolicyORM)) or 0
    pending_review = (
        db.scalar(
            select(func.count())
            .select_from(PolicyReviewTaskORM)
            .where(PolicyReviewTaskORM.review_status == "pending")
        )
        or 0
    )

    latest_ac = db.scalar(
        select(AdminOperationRunORM)
        .where(AdminOperationRunORM.operation_type == "auto_crawler_run")
        .order_by(desc(AdminOperationRunORM.id))
        .limit(1)
    )
    last_auto = None
    last_queued = 0
    if latest_ac:
        prog = (latest_ac.result_json or {}).get("progress") or {}
        last_queued = int(prog.get("review_task_count") or 0)
        ts = latest_ac.updated_at or latest_ac.created_at
        last_auto = {
            "run_at": ts.isoformat() if ts else None,
            "status": latest_ac.status,
            "crawled_count": int(prog.get("candidates_count") or 0),
            "filtered_count": int(prog.get("stored_count") or 0),
            "queued_count": last_queued,
            "summary_message": latest_ac.summary_message or "",
        }

    latest_report = db.scalar(
        select(CompassReportORM).order_by(desc(CompassReportORM.published_at), desc(CompassReportORM.id)).limit(1)
    )
    compass_block = None
    if latest_report:
        pub = latest_report.published_at
        compass_block = {
            "id": latest_report.id,
            "title": latest_report.title,
            "published_at": pub.isoformat() if pub else None,
        }

    return {
        "policy_count": int(policy_count),
        "pending_review_count": int(pending_review),
        "last_queued_count": last_queued,
        "last_auto_crawler_run": last_auto,
        "latest_compass_report": compass_block,
    }


@router.get("/runs")
def list_runs(db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    runs = db.scalars(select(AdminOperationRunORM).order_by(desc(AdminOperationRunORM.id)).limit(200)).all()
    return [
        {
            "id": r.id,
            "operation_type": r.operation_type,
            "status": r.status,
            "trigger_source": r.trigger_source,
            "summary_message": r.summary_message,
            "progress_completed": r.progress_completed,
            "progress_total": r.progress_total,
            "progress_failed": r.progress_failed,
            "progress": (r.result_json or {}).get("progress") or {},
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat() if getattr(r, "updated_at", None) else None,
        }
        for r in runs
    ]


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    run = db.get(AdminOperationRunORM, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    items = db.scalars(select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id).order_by(AdminOperationRunItemORM.item_index)).all()
    return {
        "run": {
            "id": run.id,
            "operation_type": run.operation_type,
            "status": run.status,
            "payload_json": run.payload_json,
            "result_json": run.result_json,
            "summary_message": run.summary_message,
            "progress_completed": run.progress_completed,
            "progress_total": run.progress_total,
            "progress_failed": run.progress_failed,
            "progress": (run.result_json or {}).get("progress") or {},
            "created_at": run.created_at.isoformat(),
            "updated_at": run.updated_at.isoformat() if getattr(run, "updated_at", None) else None,
        },
        "items": [
            {
                "id": it.id,
                "item_index": it.item_index,
                "status": it.status,
                "input_json": it.input_json,
                "result_json": it.result_json,
                "error_message": it.error_message,
                "updated_at": it.updated_at.isoformat() if getattr(it, "updated_at", None) else None,
            }
            for it in items
        ],
    }


@router.get("/telemetry")
def list_telemetry(db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    rows = db.scalars(select(TelemetryEventORM).order_by(desc(TelemetryEventORM.id)).limit(200)).all()
    return [
        {
            "id": e.id,
            "domain": e.domain,
            "event_name": e.event_name,
            "status": e.status,
            "duration_ms": e.duration_ms,
            "reason_code": e.reason_code,
            "metadata_json": e.metadata_json,
            "created_at": e.created_at.isoformat(),
        }
        for e in rows
    ]


@router.post("/consume-once")
def consume_once(db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    run = consume_one_pending_run(db)
    return {"ran": bool(run), "run_id": run.id if run else None, "status": run.status if run else None}


@router.post("/runs/{run_id}/retry")
def retry_run(run_id: int, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    run = db.get(AdminOperationRunORM, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    if run.status not in ("failed", "partial"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅失败或部分成功的任务可重试")
    run.status = "pending"
    run.summary_message = ""
    run.result_json = {}
    run.updated_at = dt.datetime.utcnow()
    items = db.scalars(select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id)).all()
    for it in items:
        it.status = "pending"
        it.error_message = ""
        it.result_json = {}
    db.commit()
    return {"ok": True, "run_id": run.id}

