from __future__ import annotations

from app.providers.base import ModelConfig


SOURCE_URL = "https://platform.openai.com/docs/models"


def list_models() -> list[ModelConfig]:
    return [
        ModelConfig(
            provider="openai",
            model="gpt-4.1",
            display_name="GPT-4.1",
            context_limit=1_000_000,
            input_cost_per_1k=0.002,
            output_cost_per_1k=0.008,
            speed_estimate="medium",
            source_url=SOURCE_URL,
        ),
    ]
