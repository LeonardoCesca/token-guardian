from __future__ import annotations

from pathlib import Path


PACKAGE_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "model_catalog.json"
USER_CATALOG_PATH = Path.home() / ".token-guardian" / "model_catalog.json"

DEFAULT_COMPARISON_MODELS: list[tuple[str, str]] = [
    ("openai", "gpt-4.1"),
    ("anthropic", "claude-sonnet-4"),
    ("anthropic", "claude-opus-4"),
    ("google", "gemini-2.5-pro"),
]
