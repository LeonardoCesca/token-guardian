from __future__ import annotations

from app.providers.base import ModelConfig
from app.providers.catalog import MODEL_CATALOG


class UnsupportedModelError(ValueError):
    """Raised when a provider/model pair is not configured."""


def get_model_config(provider: str, model: str) -> ModelConfig:
    key = (provider.strip().lower(), model.strip().lower())
    try:
        return MODEL_CATALOG[key]
    except KeyError as exc:
        raise UnsupportedModelError(
            f"Unsupported provider/model combination: {provider}/{model}"
        ) from exc


def list_models() -> list[ModelConfig]:
    return list(MODEL_CATALOG.values())

