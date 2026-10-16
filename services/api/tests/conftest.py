import os
import pathlib
import sys
import tempfile

# Make `app` (services/api) and repo root (for `services.worker`) importable.
API_DIR = pathlib.Path(__file__).resolve().parents[1]
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in (str(API_DIR), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

_tmp = tempfile.mkdtemp(prefix="wag_test_")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{pathlib.Path(_tmp) / 'test.db'}"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient

from wag.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c