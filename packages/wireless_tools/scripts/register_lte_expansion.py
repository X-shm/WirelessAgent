"""Register standalone LTE family dispatchers from the reviewed public-name manifest."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "_lte_expansion_names.json"
GROUPS = json.loads(MANIFEST.read_text(encoding="utf-8"))
DESCRIPTIONS = {
    "nb": "NB-IoT resource, sequence, channel and timing operations",
    "sidelink": "LTE sidelink resource, sequence, channel and waveform operations",
    "uplink": "LTE uplink control, shared channel, reference and estimation operations",
    "downlink": "LTE downlink control, shared channel, reference and allocation operations",
    "waveform": "LTE propagation, random access, RMC and test-model operations",
    "misc": "LTE coding, configuration and headless GUI-helper operations",
}
EXAMPLES = {
    "nb": ("lteNBResourceGrid", {}),
    "sidelink": ("lteSLResourceGridSize", {}),
    "uplink": ("lteULResourceGridSize", {}),
    "downlink": ("lteDLResourceGridSize", {}),
    "waveform": ("lte3DChannel", {}),
    "misc": ("saLteNscRB", {}),
}
COVERAGE = {
    "nb": "独立 Python NB-IoT NPSS/NSSS/NRS 序列及索引、NB 资源网格、NPBCH/NPDSCH/NPDCCH 索引、FDD NPUSCH 数据/DRS 索引及 Data DRS 基线序列、基线 NPRACHInfo 已与 MATLAB 样本对照；NPRACHInfo 仅支持登记的 FDD 基线配置，其余 NB-IoT 信道编码仍为部分实现。",
    "sidelink": "独立 Python Sidelink MIB、PSSS/SSSS、PSBCH/PSCCH/PSSCH 资源索引与物理信道编解码、SCI/SL-BCH 编解码、三类 DRS 验证配置、PRBS 及 SC-FDMA 几何已与 MATLAB 样本对照；其余估计和完整多天线链仍为部分实现。",
    "uplink": "独立 Python 上行 PUCCH2/3 PRBS、PUCCH1/2/3 数据/DRS 索引及 DRS 序列、ACK/RI/CQI 短块编解码、UCI/UCI3 全合法长度编码和 1..11 位软解码、SRS 小区子帧调度、无 UCI 的 UL-SCH 交织及 61 个 PUSCH MIMO 码本已与 MATLAB 样本对照；完整 PUSCH 传输处理和多层复用仍为部分实现。",
    "downlink": "独立 Python 下行 CFI、PCFICH、FDD PHICH/PDCCH 几何及基线 RE 索引、CSI-RS/PRS 与单层 PDSCH/EPDCCH DM-RS 基线序列及索引、EPDCCH 数据索引、DCI 编解码及对称带宽 DCI 长度、BCH 编解码、单端口 PBCH、PDCCH 交织和资源网格已与 MATLAB 样本对照；非对称带宽与完整多天线调度链仍为部分实现。",
    "waveform": "独立 Python 已提供基线 FDD PRACHInfo 几何、FDD/TDD RMC 与 E-TM 预设及显式抽头 FIR、参考相关和吞吐率计算；PRACHInfo 仅支持登记的标准带宽/格式基线配置，完整 3D/HST 随机信道和图形界面仍不支持。",
    "misc": "独立 Python LTE Turbo QPP 编解码、单码块速率匹配/恢复、24 位 MIB 及固定 12 子载波资源块参数已与 MATLAB 样本对照；多码块软缓冲及 GUI 未复现。",
}
SOURCE_STATUS = {
    "nb": {name: "validated_subset" for name in
           ("lteNPSS", "lteNPSSIndices", "lteNSSS", "lteNSSSIndices",
            "lteNRS", "lteNRSIndices", "lteNBResourceGrid", "lteNPBCHIndices",
            "lteNPUSCHDRSIndices", "lteNPUSCHIndices",
            "lteNPDSCHIndices", "lteNPDCCHIndices", "lteNPRACHInfo",
            "lteNPUSCHDRS")},
    "misc": {name: "validated_subset" for name in
             ("lteTurboEncode", "lteTurboDecode",
              "lteRateMatchTurbo", "lteRateRecoverTurbo", "lteMIB",
              "saLteNscRB")},
    "downlink": {name: "validated_subset" for name in
                 ("lteDLResourceGrid", "lteDLResourceGridSize", "lteCFI", "lteCFIDecode",
                  "ltePBCHPRBS", "ltePDCCHPRBS", "ltePCFICHPRBS", "ltePHICHPRBS",
                  "lteEPDCCHPRBS", "ltePCFICHIndices", "ltePCFICHInfo",
                  "ltePCFICH", "ltePCFICHDecode", "ltePHICHInfo", "ltePDCCHInfo",
                  "lteDuplexingInfo", "ltePDCCHInterleave", "ltePDCCHDeinterleave",
                  "lteDLSCHInfo", "lteDCIEncode", "lteDCIDecode",
                  "lteBCH", "lteBCHDecode", "ltePBCH", "ltePBCHDecode",
                  "lteDCIInfo", "ltePDCCHIndices", "ltePHICHIndices",
                  "lteCSIRS", "lteCSIRSIndices", "ltePRS", "ltePRSIndices",
                  "lteDMRS", "lteDMRSIndices", "lteEPDCCHDMRS",
                  "lteEPDCCHDMRSIndices", "lteEPDCCHIndices",
                  "ltePBCHIndices")},
    "uplink": {name: "validated_subset" for name in
               ("lteULResourceGrid", "lteULResourceGridSize",
                "ltePUCCH2PRBS", "ltePUCCH3PRBS", "lteSRSInfo",
                "lteULSCHInterleave", "lteULSCHDeinterleave",
                "lteULPMIInfo", "ltePUSCHPrecode", "ltePUSCHDeprecode",
                "lteUCIEncode", "lteUCIDecode", "lteUCI3Encode", "lteUCI3Decode",
                "ltePUCCH1Indices", "ltePUCCH1DRSIndices", "ltePUCCH1DRS",
                "ltePUCCH2Indices", "ltePUCCH2DRSIndices", "ltePUCCH2DRS",
                "ltePUCCH3Indices", "ltePUCCH3DRSIndices", "ltePUCCH3DRS",
                "lteACKEncode", "lteACKDecode", "lteRIEncode", "lteRIDecode",
                "lteCQIEncode", "lteCQIDecode")},
    "sidelink": {name: "validated_subset" for name in
                 ("lteSLResourceGrid", "lteSLResourceGridSize", "lteSLMIB",
                  "ltePSSS", "ltePSSSIndices", "lteSSSS", "ltePSBCHIndices",
                  "ltePSBCHDRSIndices", "lteSSSSIndices",
                  "ltePSCCHIndices", "ltePSCCHDRSIndices",
                  "ltePSSCHIndices", "ltePSSCHDRSIndices",
                  "ltePSBCHPRBS", "ltePSCCHPRBS", "ltePSSCHPRBS",
                  "ltePSBCH", "ltePSCCH", "ltePSSCH",
                  "ltePSBCHDecode", "ltePSCCHDecode", "ltePSSCHDecode",
                  "lteSCIInfo", "lteSCIEncode", "lteSCIDecode",
                  "lteSLSCFDMAInfo", "lteSLBCH", "lteSLBCHDecode",
                  "ltePSBCHDRS", "ltePSCCHDRS", "ltePSSCHDRS")},
    "waveform": {name: "validated_subset" for name in
                 ("ltePRACHInfo", "lteRMCDL", "lteRMCUL", "lteTestModel")},
}


def main():
    registry_path = ROOT / "tool_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    known = {entry["name"] for entry in registry["tools"]}
    for family, names in GROUPS.items():
        tool = f"lte_{family}_family"
        module = ROOT / "tools" / f"{tool}.py"
        module.write_text(
            f'"""Standalone {DESCRIPTIONS[family]}."""\n'
            "from __future__ import annotations\n"
            "from functools import partial\n"
            "from _nr_remaining_common import run_cli\n"
            "from _lte_expansion_core import GROUPS, execute\n\n"
            f'DISPATCH = {{name: partial(execute, name) for name in GROUPS["{family}"]}}\n\n'
            'if __name__ == "__main__":\n'
            f'    run_cli("{DESCRIPTIONS[family]}", DISPATCH)\n',
            encoding="utf-8",
        )
        exemplar, params = EXAMPLES[family]
        schema = {
            "name": tool, "script": f"{tool}.py",
            "description": DESCRIPTIONS[family],
            "implementation": COVERAGE[family],
            "inputs": {
                "function": {"type": "enum", "enum": names, "required": True,
                             "description": "MATLAB LTE public entry"},
                "params": {"type": "string", "required": True, "max_length": 250000,
                           "mcp_stdin": True, "description": "Selected entry's JSON keyword arguments"},
            },
            "outputs": {"function": {"description": "Public entry"},
                        "result": {"description": "Computed result and explicit model scope"}},
            "example": {"cmd": f"python tools/{tool}.py --function {exemplar} --params '{{}}'",
                        "result": f"{exemplar} standalone Python result"},
        }
        (ROOT / "tools" / f"{tool}.schema.json").write_text(
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if tool not in known:
            registry["tools"].append({
                "name": tool, "source_functions": names, "product": "LTE Toolbox",
                "status": "partial", "coverage": COVERAGE[family],
                "source_status": SOURCE_STATUS.get(family, {}),
                "schema": f"tools/{tool}.schema.json",
            })
        else:
            entry = next(entry for entry in registry["tools"] if entry["name"] == tool)
            entry["coverage"] = COVERAGE[family]
            entry["source_status"] = SOURCE_STATUS.get(family, {})
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    print(f"registered {sum(map(len, GROUPS.values()))} LTE names in {len(GROUPS)} families")


if __name__ == "__main__":
    main()
