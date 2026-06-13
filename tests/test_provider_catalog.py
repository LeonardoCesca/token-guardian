from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.providers.base import ModelConfig
from app.providers.catalog_loader import load_catalog_snapshot, write_catalog_snapshot
from app.providers.sync_service import UnsupportedProviderError, sync_model_catalog


def test_load_catalog_snapshot_reads_json(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "last_updated_at": "2026-06-13",
                "models": [
                    {
                        "provider": "openai",
                        "model": "gpt-4.1",
                        "display_name": "GPT-4.1",
                        "context_limit": 1000000,
                        "input_cost_per_1k": 0.002,
                        "output_cost_per_1k": 0.008,
                        "speed_estimate": "medium",
                        "source_url": "https://platform.openai.com/docs/models",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    snapshot = load_catalog_snapshot(catalog_path)

    assert snapshot.last_updated_at == "2026-06-13"
    assert snapshot.models[0].provider == "openai"
    assert snapshot.catalog_path == catalog_path


def test_write_catalog_snapshot_persists_models(tmp_path: Path) -> None:
    model = ModelConfig(
        provider="anthropic",
        model="claude-sonnet-4",
        display_name="Claude Sonnet 4",
        context_limit=200_000,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        speed_estimate="fast",
        source_url="https://docs.anthropic.com/en/docs/about-claude/models/overview",
    )

    snapshot = write_catalog_snapshot(
        last_updated_at="2026-06-13",
        models=[model],
        path=tmp_path / "written.json",
    )

    assert snapshot.last_updated_at == "2026-06-13"
    assert len(snapshot.models) == 1
    assert snapshot.models[0].source_url.startswith("https://")


def test_sync_model_catalog_writes_filtered_snapshot(tmp_path: Path) -> None:
    snapshot = sync_model_catalog(["openai"], destination=tmp_path / "synced.json")

    assert snapshot.catalog_path == tmp_path / "synced.json"
    assert len(snapshot.models) >= 1
    assert any(model.provider == "openai" for model in snapshot.models)
    assert any(model.provider == "anthropic" for model in snapshot.models)


def test_sync_model_catalog_rejects_unknown_provider() -> None:
    with pytest.raises(UnsupportedProviderError):
        sync_model_catalog(["unknown-provider"])
