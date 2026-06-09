from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AnalyzePromptRequest,
    AnalyzePromptResponse,
    CompareModelsRequest,
    CompareModelsResponse,
    OptimizePromptRequest,
    OptimizePromptResponse,
)
from app.providers.registry import UnsupportedModelError
from app.services.analyzer_service import analyze_prompt, compare_models
from app.services.optimizer_service import optimize_prompt


router = APIRouter(prefix="/api", tags=["api"])


@router.post("/analyze", response_model=AnalyzePromptResponse)
def analyze(request: AnalyzePromptRequest) -> AnalyzePromptResponse:
    try:
        return analyze_prompt(request)
    except UnsupportedModelError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/compare", response_model=CompareModelsResponse)
def compare(request: CompareModelsRequest) -> CompareModelsResponse:
    return compare_models(request)


@router.post("/optimize", response_model=OptimizePromptResponse)
def optimize(request: OptimizePromptRequest) -> OptimizePromptResponse:
    return optimize_prompt(request.prompt)

