"""5G NR 无线工具接入单测：目录加载 / CLI 执行 / 目录注入 / use_tool。"""
import asyncio

from app.services.wireless_tool_runner import load_nr_catalog, run_tool
from app.agent.tools.wireless import wireless_directory_prompt, _use_tool


def test_load_nr_catalog():
    catalog = load_nr_catalog()
    assert len(catalog) >= 50  # 5G NR 应有 58 个工具
    assert "nr_modulation" in catalog
    spec = catalog["nr_modulation"]
    assert spec.input_schema["type"] == "object"
    assert "mod" in spec.input_schema["properties"]


def test_run_nr_modulation():
    spec = load_nr_catalog()["nr_modulation"]
    result = run_tool(spec, {"mod": "QPSK", "bits": "1,1,0,1"}, timeout=30)
    assert result.get("modulation") == "QPSK"
    assert "symbols_real" in result
    assert "symbols_imag" in result


def test_wireless_directory_prompt():
    directory = wireless_directory_prompt()
    assert "nr_modulation" in directory
    assert "nr_tbs" in directory


def test_use_tool_hit_and_miss():
    async def _run():
        hit = await _use_tool({"name": "nr_modulation"}, None)
        assert hit["name"] == "nr_modulation"
        assert "input_schema" in hit
        miss = await _use_tool({"name": "nope"}, None)
        assert "未知无线工具" in miss["error"]

    asyncio.run(_run())
