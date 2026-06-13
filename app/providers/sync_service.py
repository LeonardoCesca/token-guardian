from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

from app.providers.base import CatalogSnapshot, ModelConfig
from app.providers.catalog import PACKAGE_CATALOG_PATH, USER_CATALOG_PATH
from app.providers.catalog_loader import load_catalog_snapshot, write_catalog_snapshot
from app.providers.sources import PROVIDER_ADAPTERS


class UnsupportedProviderError(ValueError):
    """Raised when a provider adapter is not available."""


def sync_model_catalog(
    providers: Sequence[str] | None = None,
    *,
    destination: Path | None = None,
) -> CatalogSnapshot:
    selected = [provider.strip().lower() for provider in providers or PROVIDER_ADAPTERS]
    unknown = [provider for provider in selected if provider not in PROVIDER_ADAPTERS]
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise UnsupportedProviderError(f"Unsupported providers: {joined}")

    if providers:
        models = _merge_selected_providers(selected)
    else:
        models: list[ModelConfig] = []
        for provider in selected:
            models.extend(PROVIDER_ADAPTERS[provider]())

    return write_catalog_snapshot(
        last_updated_at=datetime.now(UTC).date().isoformat(),
        models=sorted(models, key=lambda item: (item.provider, item.model)),
        path=destination,
    )


def _merge_selected_providers(selected: list[str]) -> list[ModelConfig]:
    merged = {
        (item.provider, item.model): item
        for item in load_catalog_snapshot(PACKAGE_CATALOG_PATH).models
    }
    if USER_CATALOG_PATH.exists():
        for item in load_catalog_snapshot(USER_CATALOG_PATH).models:
            merged[(item.provider, item.model)] = item

    remaining = [item for item in merged.values() if item.provider not in set(selected)]
    refreshed: list[ModelConfig] = []
    for provider in selected:
        refreshed.extend(PROVIDER_ADAPTERS[provider]())
    return remaining + refreshed
