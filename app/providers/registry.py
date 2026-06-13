from __future__ import annotations

from app.providers.base import CatalogSnapshot, ModelConfig
from app.providers.catalog_loader import load_catalog_snapshot


class UnsupportedModelError(ValueError):
    """Raised when a provider/model pair is not configured."""


def get_catalog_snapshot() -> CatalogSnapshot:
    return load_catalog_snapshot()


def get_model_config(provider: str, model: str) -> ModelConfig:
    key = (provider.strip().lower(), model.strip().lower())
    models = {(item.provider, item.model): item for item in get_catalog_snapshot().models}
    try:
        return models[key]
    except KeyError as exc:
        raise UnsupportedModelError(
            f"Unsupported provider/model combination: {provider}/{model}"
        ) from exc


def list_models() -> list[ModelConfig]:
    return list(get_catalog_snapshot().models)

