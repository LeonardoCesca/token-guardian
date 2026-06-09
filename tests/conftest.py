from __future__ import annotations

from pathlib import Path

import pytest

from app.services import database


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path) -> None:
    database.DB_PATH = tmp_path / "test_token_guardian.db"
    database.init_db()

