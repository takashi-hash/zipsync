import os
import sys
import importlib
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """Prepare isolated working directory and helper to reload modules."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "resources").mkdir()
    monkeypatch.syspath_prepend(str(REPO_ROOT))

    def reload_module(name: str):
        module = importlib.import_module(name)
        return importlib.reload(module)

    env = {
        "tmp_path": tmp_path,
        "resources": tmp_path / "resources",
        "reload": reload_module,
    }
    return env
