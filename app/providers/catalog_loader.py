from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.providers.base import CatalogSnapshot, ModelConfig
from app.providers.catalog import PACKAGE_CATALOG_PATH, USER_CATALOG_PATH


def get_catalog_path() -> Path:
    if USER_CATALOG_PATH.exists():
        return USER_CATALOG_PATH
    return PACKAGE_CATALOG_PATH


def load_catalog_snapshot(path: Path | None = None) -> CatalogSnapshot:
    catalog_path = path or get_catalog_path()
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    models = tuple(
        ModelConfig.from_dict(item)
        for item in sorted(
            payload["models"],
            key=lambda item: (
                str(item["provider"]).lower(),
                str(item["model"]).lower(),
            ),
        )
    )
    return CatalogSnapshot(
        last_updated_at=str(payload["last_updated_at"]),
        models=models,
        catalog_path=catalog_path,
    )


def write_catalog_snapshot(
    *,
    last_updated_at: str,
    models: list[ModelConfig],
    path: Path | None = None,
) -> CatalogSnapshot:
    catalog_path = path or USER_CATALOG_PATH
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "last_updated_at": last_updated_at,
        "models": [model.to_dict() for model in models],
    }
    catalog_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return load_catalog_snapshot(catalog_path)
