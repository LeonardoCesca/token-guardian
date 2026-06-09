from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high", "critical"]
ComplexityLevel = Literal["Simple", "Medium", "Complex", "Very Complex"]
CostScore = Literal["$", "$$", "$$$", "$$$$"]


class AnalyzePromptRequest(BaseModel):
    provider: str = Field(..., examples=["anthropic"])
    model: str = Field(..., examples=["claude-sonnet-4"])
    prompt: str = Field(..., min_length=1)
    estimated_output_tokens: int | None = Field(default=None, ge=1)


class AnalyzePromptResponse(BaseModel):
    provider: str
    model: str
    input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    context_limit: int
    context_usage_percent: float
    estimated_cost_usd: float
    risk_level: RiskLevel
    context_health_score: int
    cost_score: CostScore
    complexity_score: ComplexityLevel
    suggestions: list[str]


class CompareModelsRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    estimated_output_tokens: int | None = Field(default=None, ge=1)


class ModelComparisonItem(BaseModel):
    provider: str
    model: str
    input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    context_limit: int
    estimated_cost_usd: float
    speed_estimate: str
    risk_level: RiskLevel


class CompareModelsResponse(BaseModel):
    prompt_length: int
    comparisons: list[ModelComparisonItem]


class OptimizePromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class OptimizePromptResponse(BaseModel):
    optimized_prompt: str
    estimated_reduction_percent: int
    removed_patterns: list[str]


class MetricsResponse(BaseModel):
    total_requests: int
    total_tokens: int
    total_cost_estimated: float
    top_models: list[dict[str, int]]
    top_providers: list[dict[str, int]]

