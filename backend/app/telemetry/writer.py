from __future__ import annotations

import time
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.models.admin_models import TelemetryEventORM


def emit_event(
    db: Session,
    *,
    domain: str,
    event_name: str,
    status: str = "info",
    duration_ms: int | None = None,
    reason_code: str = "",
    metadata: dict | None = None,
) -> None:
    ev = TelemetryEventORM(
        domain=domain,
        event_name=event_name,
        status=status,
        duration_ms=duration_ms,
        reason_code=reason_code,
        metadata_json=metadata or {},
    )
    db.add(ev)


@contextmanager
def telemetry_span(db: Session, *, domain: str, event_name: str, metadata: dict | None = None):
    start = time.time()
    try:
        yield
        emit_event(
            db,
            domain=domain,
            event_name=event_name,
            status="success",
            duration_ms=int((time.time() - start) * 1000),
            metadata=metadata,
        )
    except Exception as e:
        emit_event(
            db,
            domain=domain,
            event_name=event_name,
            status="error",
            duration_ms=int((time.time() - start) * 1000),
            reason_code=type(e).__name__,
            metadata={**(metadata or {}), "error": str(e)},
        )
        raise

