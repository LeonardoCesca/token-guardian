from __future__ import annotations

from app.services.optimizer_service import optimize_prompt


def test_optimize_prompt_removes_duplicate_lines() -> None:
    prompt = "Objetivo: resumir\nObjetivo: resumir\n\n\nSaida em bullets.   "
    response = optimize_prompt(prompt)

    assert "Objetivo: resumir" in response.optimized_prompt
    assert response.optimized_prompt.count("Objetivo: resumir") == 1
    assert response.estimated_reduction_percent > 0
    assert "Linhas duplicadas" in response.removed_patterns

