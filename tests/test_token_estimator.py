from __future__ import annotations

from app.utils.token_estimator import estimate_input_tokens, estimate_output_tokens


def test_token_estimators_return_positive_values() -> None:
    prompt = "Analise este prompt e produza um resumo objetivo com acoes."

    assert estimate_input_tokens(prompt) > 0
    assert estimate_output_tokens(prompt) >= 128
