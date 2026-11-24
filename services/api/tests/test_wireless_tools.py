"""无线工具接入单测：目录加载 / CLI 执行 / 目录注入 / use_tool。"""
import asyncio

from app.services.wireless_tool_runner import load_wireless_catalog, run_tool
from app.agent.tools.wireless import wireless_directory_prompt, _use_tool


def test_load_wireless_catalog():
    catalog = load_wireless_catalog()
    assert len(catalog) >= 58  # 58 nr_* + 8 workflow
    assert "nr_modulation" in catalog
    assert "link_capacity" in catalog
    assert "radio_link_diagnosis" in catalog
    spec = catalog["nr_modulation"]
    assert spec.input_schema["type"] == "object"
    assert "mod" in spec.input_schema["properties"]


def test_run_nr_modulation():
    spec = load_wireless_catalog()["nr_modulation"]
    result = run_tool(spec, {"mod": "QPSK", "bits": "1,1,0,1"}, timeout=30)
    assert result.get("modulation") == "QPSK"
    assert "symbols_real" in result
    assert "symbols_imag" in result


def test_run_link_capacity():
    spec = load_wireless_catalog()["link_capacity"]
    result = run_tool(spec, {"snr_db": 10, "bandwidth_hz": 1000000}, timeout=30)
    assert "capacity_bps" in result
    assert result["capacity_bps"] > 0


def test_run_radio_link_diagnosis():
    spec = load_wireless_catalog()["radio_link_diagnosis"]
    result = run_tool(
        spec,
        {"snr_db": 0, "frequency_offset_hz": 3000, "cp_samples": 9, "timing_offset_samples": 12},
        timeout=30,
    )
    assert "findings" in result


def test_wireless_directory_prompt():
    directory = wireless_directory_prompt()
    assert "nr_modulation" in directory
    assert "nr_tbs" in directory
    assert "link_capacity" in directory


def test_use_tool_hit_and_miss():
    async def _run():
        hit = await _use_tool({"name": "nr_modulation"}, None)
        assert hit["name"] == "nr_modulation"
        assert "input_schema" in hit
        miss = await _use_tool({"name": "nope"}, None)
        assert "未知无线工具" in miss["error"]

    asyncio.run(_run())
