from __future__ import annotations

from app.models.schemas import AnalyzePromptRequest, CompareModelsRequest
from app.services.analyzer_service import analyze_prompt, compare_models


def test_analyze_prompt_returns_expected_payload() -> None:
    response = analyze_prompt(
        AnalyzePromptRequest(
            provider="anthropic",
            model="claude-sonnet-4",
            prompt="Explique a arquitetura do sistema.\nExplique a arquitetura do sistema.",
            estimated_output_tokens=800,
        )
    )

    assert response.input_tokens > 0
    assert response.estimated_output_tokens == 800
    assert response.estimated_total_tokens == response.input_tokens + 800
    assert response.context_limit == 200_000
    assert response.estimated_cost_usd > 0
    assert response.risk_level in {"low", "medium", "high", "critical"}
    assert response.context_health_score <= 100
    assert response.suggestions


def test_compare_models_orders_by_cost() -> None:
    response = compare_models(
        CompareModelsRequest(
            prompt="Crie um plano de migracao para microservicos com riscos e fases.",
            estimated_output_tokens=600,
        )
    )

    assert len(response.comparisons) == 4
    costs = [item.estimated_cost_usd for item in response.comparisons]
    assert costs == sorted(costs)

