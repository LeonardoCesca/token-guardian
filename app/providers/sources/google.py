from __future__ import annotations

from app.providers.base import ModelConfig


SOURCE_URL = "https://ai.google.dev/gemini-api/docs/models"


def list_models() -> list[ModelConfig]:
    return [
        ModelConfig(
            provider="google",
            model="gemini-2.5-flash",
            display_name="Gemini 2.5 Flash",
            context_limit=1_000_000,
            input_cost_per_1k=0.0003,
            output_cost_per_1k=0.0025,
            speed_estimate="very fast",
            source_url=SOURCE_URL,
        ),
        ModelConfig(
            provider="google",
            model="gemini-2.5-pro",
            display_name="Gemini 2.5 Pro",
            context_limit=1_000_000,
            input_cost_per_1k=0.00125,
            output_cost_per_1k=0.01,
            speed_estimate="medium",
            source_url=SOURCE_URL,
        ),
    ]
