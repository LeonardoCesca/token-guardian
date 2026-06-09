from __future__ import annotations

from app.models.schemas import (
    AnalyzePromptRequest,
    AnalyzePromptResponse,
    CompareModelsRequest,
    CompareModelsResponse,
    ModelComparisonItem,
)
from app.providers.catalog import DEFAULT_COMPARISON_MODELS
from app.providers.registry import get_model_config
from app.services.metrics_service import record_analysis
from app.utils.prompt_analysis import (
    calculate_context_usage_percent,
    classify_complexity,
    classify_risk,
    context_health_score,
    prompt_suggestions,
    score_cost,
)
from app.utils.token_estimator import estimate_input_tokens, estimate_output_tokens


def analyze_prompt(request: AnalyzePromptRequest) -> AnalyzePromptResponse:
    config = get_model_config(request.provider, request.model)
    input_tokens = estimate_input_tokens(request.prompt)
    output_tokens = request.estimated_output_tokens or estimate_output_tokens(request.prompt)
    total_tokens = input_tokens + output_tokens
    usage_percent = calculate_context_usage_percent(total_tokens, config.context_limit)
    estimated_cost = round(
        ((input_tokens / 1000) * config.input_cost_per_1k)
        + ((output_tokens / 1000) * config.output_cost_per_1k),
        6,
    )
    risk_level = classify_risk(usage_percent)
    health_score = context_health_score(request.prompt, input_tokens)
    complexity = classify_complexity(request.prompt, input_tokens)
    suggestions = prompt_suggestions(request.prompt, input_tokens)

    record_analysis(config.provider, config.model, total_tokens, estimated_cost)

    return AnalyzePromptResponse(
        provider=config.provider,
        model=config.model,
        input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        estimated_total_tokens=total_tokens,
        context_limit=config.context_limit,
        context_usage_percent=usage_percent,
        estimated_cost_usd=estimated_cost,
        risk_level=risk_level,
        context_health_score=health_score,
        cost_score=score_cost(estimated_cost),
        complexity_score=complexity,
        suggestions=suggestions,
    )


def compare_models(request: CompareModelsRequest) -> CompareModelsResponse:
    input_tokens = estimate_input_tokens(request.prompt)
    output_tokens = request.estimated_output_tokens or estimate_output_tokens(request.prompt)
    comparisons: list[ModelComparisonItem] = []

    for provider, model in DEFAULT_COMPARISON_MODELS:
        config = get_model_config(provider, model)
        total_tokens = input_tokens + output_tokens
        estimated_cost = round(
            ((input_tokens / 1000) * config.input_cost_per_1k)
            + ((output_tokens / 1000) * config.output_cost_per_1k),
            6,
        )
        usage_percent = calculate_context_usage_percent(total_tokens, config.context_limit)
        comparisons.append(
            ModelComparisonItem(
                provider=config.provider,
                model=config.model,
                input_tokens=input_tokens,
                estimated_output_tokens=output_tokens,
                estimated_total_tokens=total_tokens,
                context_limit=config.context_limit,
                estimated_cost_usd=estimated_cost,
                speed_estimate=config.speed_estimate,
                risk_level=classify_risk(usage_percent),
            )
        )

    comparisons.sort(key=lambda item: (item.estimated_cost_usd, item.estimated_total_tokens))
    return CompareModelsResponse(
        prompt_length=len(request.prompt),
        comparisons=comparisons,
    )

