from __future__ import annotations

from app.providers.base import ModelConfig


SOURCE_URL = "https://openrouter.ai/models"


def list_models() -> list[ModelConfig]:
    return [
        ModelConfig(
            provider="openrouter",
            model="openai/gpt-4.1",
            display_name="OpenRouter GPT-4.1",
            context_limit=1_000_000,
            input_cost_per_1k=0.0022,
            output_cost_per_1k=0.0088,
            speed_estimate="medium",
            source_url=SOURCE_URL,
        ),
    ]
