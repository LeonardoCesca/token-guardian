from __future__ import annotations

from app.providers.base import ModelConfig


MODEL_CATALOG: dict[tuple[str, str], ModelConfig] = {
    ("openai", "gpt-4.1"): ModelConfig(
        provider="openai",
        model="gpt-4.1",
        display_name="GPT-4.1",
        context_limit=1_000_000,
        input_cost_per_1k=0.002,
        output_cost_per_1k=0.008,
        speed_estimate="medium",
    ),
    ("anthropic", "claude-sonnet-4"): ModelConfig(
        provider="anthropic",
        model="claude-sonnet-4",
        display_name="Claude Sonnet 4",
        context_limit=200_000,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        speed_estimate="fast",
    ),
    ("anthropic", "claude-opus-4"): ModelConfig(
        provider="anthropic",
        model="claude-opus-4",
        display_name="Claude Opus 4",
        context_limit=200_000,
        input_cost_per_1k=0.015,
        output_cost_per_1k=0.075,
        speed_estimate="slow",
    ),
    ("google", "gemini-2.5-pro"): ModelConfig(
        provider="google",
        model="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        context_limit=1_000_000,
        input_cost_per_1k=0.00125,
        output_cost_per_1k=0.01,
        speed_estimate="medium",
    ),
    ("google", "gemini-2.5-flash"): ModelConfig(
        provider="google",
        model="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        context_limit=1_000_000,
        input_cost_per_1k=0.0003,
        output_cost_per_1k=0.0025,
        speed_estimate="very fast",
    ),
    ("openrouter", "openai/gpt-4.1"): ModelConfig(
        provider="openrouter",
        model="openai/gpt-4.1",
        display_name="OpenRouter GPT-4.1",
        context_limit=1_000_000,
        input_cost_per_1k=0.0022,
        output_cost_per_1k=0.0088,
        speed_estimate="medium",
    ),
}


DEFAULT_COMPARISON_MODELS: list[tuple[str, str]] = [
    ("openai", "gpt-4.1"),
    ("anthropic", "claude-sonnet-4"),
    ("anthropic", "claude-opus-4"),
    ("google", "gemini-2.5-pro"),
]

