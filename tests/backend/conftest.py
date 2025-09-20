import os
from pathlib import Path

import pytest

from backend.app import config


@pytest.fixture(autouse=True)
def reset_settings(tmp_path: Path):
    config.get_settings.cache_clear()  # type: ignore[attr-defined]
    os.environ["STORAGE_ROOT"] = str(tmp_path / "storage")
    yield
    config.get_settings.cache_clear()  # type: ignore[attr-defined]
    os.environ.pop("STORAGE_ROOT", None)
