"""模型路由层单测：模型池解析 / 标签匹配 / 手动覆盖 / 降级顺序。"""
import pytest

from app.config import settings
from app.services.model_router import ModelRouter


POOL = [
    {"name": "kimi", "base_url": "http://a/v1", "api_key": "", "model": "m-kimi",
     "tags": ["default", "talk"], "priority": 0},
    {"name": "workhorse", "base_url": "http://b/v1", "api_key": "k2", "model": "m-work",
     "tags": ["work"], "priority": 1},
    {"name": "searcher", "base_url": "http://c/v1", "api_key": "k3", "model": "m-search",
     "tags": ["search"], "priority": 2},
]


def test_empty_pool_falls_back_to_default(monkeypatch):
    monkeypatch.setattr(settings, "model_pool", [])
    cands = ModelRouter().resolve(mode="talk", tool=None)
    assert len(cands) == 1
    assert cands[0].name == "default"


def test_tag_match_search(monkeypatch):
    monkeypatch.setattr(settings, "model_pool", POOL)
    cands = ModelRouter().resolve(mode="talk", tool="search")
    assert cands[0].name == "searcher"


def test_tag_match_work(monkeypatch):
    monkeypatch.setattr(settings, "model_pool", POOL)
    cands = ModelRouter().resolve(mode="work", tool=None)
    assert cands[0].name == "workhorse"


def test_manual_override_priority_no_fallback(monkeypatch):
    monkeypatch.setattr(settings, "model_pool", POOL)
    cands = ModelRouter().resolve(mode="work", tool=None, manual_model="m-manual")
    assert len(cands) == 1
    assert cands[0].model == "m-manual"


def test_fallback_order_by_priority(monkeypatch):
    monkeypatch.setattr(settings, "model_pool", POOL)
    cands = ModelRouter().resolve(mode="talk", tool=None)
    # talk 标签 → kimi；降级序列按 priority：workhorse、searcher
    assert [c.name for c in cands] == ["kimi", "workhorse", "searcher"]
