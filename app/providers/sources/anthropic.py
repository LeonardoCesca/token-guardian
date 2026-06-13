from __future__ import annotations

from app.providers.base import ModelConfig


SOURCE_URL = "https://docs.anthropic.com/en/docs/about-claude/models/overview"


def list_models() -> list[ModelConfig]:
    return [
        ModelConfig(
            provider="anthropic",
            model="claude-opus-4",
            display_name="Claude Opus 4",
            context_limit=200_000,
            input_cost_per_1k=0.015,
            output_cost_per_1k=0.075,
            speed_estimate="slow",
            source_url=SOURCE_URL,
        ),
        ModelConfig(
            provider="anthropic",
            model="claude-sonnet-4",
            display_name="Claude Sonnet 4",
            context_limit=200_000,
            input_cost_per_1k=0.003,
            output_cost_per_1k=0.015,
            speed_estimate="fast",
            source_url=SOURCE_URL,
        ),
    ]
