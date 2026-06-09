from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import MetricsResponse
from app.services.metrics_service import get_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
def metrics() -> MetricsResponse:
    return get_metrics()
