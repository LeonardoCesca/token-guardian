from __future__ import annotations

from app.services.metrics_service import get_metrics, record_analysis


def test_metrics_aggregate_saved_analyses() -> None:
    record_analysis("anthropic", "claude-sonnet-4", 1200, 0.021)
    record_analysis("openai", "gpt-4.1", 800, 0.008)
    record_analysis("anthropic", "claude-sonnet-4", 900, 0.016)

    metrics = get_metrics()

    assert metrics.total_requests == 3
    assert metrics.total_tokens == 2900
    assert metrics.total_cost_estimated == 0.045
    assert metrics.top_models[0] == {"claude-sonnet-4": 2}
    assert metrics.top_providers[0] == {"anthropic": 2}

