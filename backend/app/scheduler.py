from __future__ import annotations

import datetime as dt
import time

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.services.admin_operation_service import consume_one_pending_run, create_run
from app.services.crawler_service import create_auto_crawler_run_record, get_auto_crawler_config
from app.models.admin_models import AutoCrawlerRunORM


def _consume_once():
    engine = get_engine()
    with Session(engine) as db:
        _enqueue_due_auto_crawler(db)
        consume_one_pending_run(db)


def _enqueue_due_auto_crawler(db: Session) -> None:
    config = get_auto_crawler_config(db)
    if not config.get("enabled"):
        return

    interval_hours = max(1, int(config.get("interval_hours") or 24))
    latest = db.scalar(select(AutoCrawlerRunORM).order_by(desc(AutoCrawlerRunORM.id)).limit(1))
    now = dt.datetime.utcnow()
    if latest and latest.created_at and latest.created_at > now - dt.timedelta(hours=interval_hours):
        return

    source_ids = list(config.get("sources") or [])
    max_pages = int(config.get("max_pages_per_source") or 5)
    record = create_auto_crawler_run_record(
        db,
        source_ids=source_ids,
        max_pages=max_pages,
        created_by="scheduler",
        status="pending",
        summary_message="调度器自动触发",
    )
    create_run(
        db,
        operation_type="auto_crawler_run",
        payload={
            "source_ids": source_ids,
            "max_pages_per_source": max_pages,
            "max_candidates": 8,
            "operator": "scheduler",
            "auto_crawler_record_id": record.id,
        },
        trigger_source="scheduler",
        items=[{"source_ids": source_ids, "max_pages_per_source": max_pages, "max_candidates": 8}],
    )


def main():
    scheduler = BackgroundScheduler()
    # 概要设计：后台作业消费者每 10 秒轮询一次
    scheduler.add_job(_consume_once, "interval", seconds=10, id="admin_ops_consumer")
    scheduler.start()

    try:
        while True:
            time.sleep(60)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()

