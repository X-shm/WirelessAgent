"""The website API remains importable without the separately deployed digest."""
import asyncio
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.config import settings
from app.main import app as site_app
from app.routes.papers import refresh


def test_site_imports_without_digest():
    paths = {getattr(route, "path", "") for route in site_app.routes}
    assert "/api/health" in paths
    if not (Path(settings.arxiv_digest_dir) / "scripts" / "digest_routes.py").is_file():
        assert not any(path.startswith("/api/digest") for path in paths)


def test_paper_refresh_requires_external_digest():
    if (Path(settings.arxiv_digest_dir) / "scripts" / "arxiv_fetcher.py").is_file():
        pytest.skip("External digest is installed in this environment")
    with pytest.raises(HTTPException) as error:
        asyncio.run(refresh(None, days=7, max_papers=20, db=None))
    assert error.value.status_code == 503
