from __future__ import annotations

from app.utils.prompt_analysis import (
    calculate_context_usage_percent,
    classify_complexity,
    classify_risk,
    context_health_score,
    score_cost,
)


def test_context_usage_percent_and_risk() -> None:
    usage = calculate_context_usage_percent(190_000, 200_000)

    assert usage == 95.0
    assert classify_risk(usage) == "critical"


def test_health_score_penalizes_repetition() -> None:
    repetitive_prompt = "\n".join(["repita isto"] * 20)
    concise_prompt = "Explique o erro e sugira uma correcao."

    assert context_health_score(concise_prompt, 20) > context_health_score(
        repetitive_prompt, 200
    )


def test_cost_and_complexity_scores() -> None:
    assert score_cost(0.005) == "$"
    assert score_cost(0.02) == "$$"
    assert score_cost(0.05) == "$$$"
    assert score_cost(0.2) == "$$$$"
    assert classify_complexity("linha\n" * 40, 1300) == "Complex"

