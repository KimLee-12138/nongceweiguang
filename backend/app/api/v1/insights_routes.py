from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.insights_service import (
    build_audience_distribution,
    build_kpi_snapshot,
    build_source_distribution,
    build_trend_analysis,
)


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/kpi-summary")
def kpi_summary(db: Session = Depends(get_db)):
    return build_kpi_snapshot(db)


@router.get("/trend-analysis")
def trend_analysis(db: Session = Depends(get_db)):
    return build_trend_analysis(db)


@router.get("/source-distribution")
def source_distribution(db: Session = Depends(get_db)):
    return build_source_distribution(db)


@router.get("/audience-distribution")
def audience_distribution(db: Session = Depends(get_db)):
    return build_audience_distribution(db)

