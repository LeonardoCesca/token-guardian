from __future__ import annotations

from pathlib import Path

import pytest

from app.providers import catalog_loader
from app.services import database


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database.DB_PATH = tmp_path / "test_token_guardian.db"
    database.init_db()
    monkeypatch.setattr(
        catalog_loader,
        "USER_CATALOG_PATH",
        tmp_path / "user_model_catalog.json",
    )

