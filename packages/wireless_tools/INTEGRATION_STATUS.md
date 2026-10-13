# Wireless Toolbox 集成状态

更新日期：2026-10-12。此目录是无线工具箱在团队仓库中的独立模块。下列结论只描述本地代码和样本验证，不代表团队网站或服务器已经接入。

## 已提供

- `tool_registry.json` 登记 144 个 Python CLI 工具；输入契约位于 `tools/*.schema.json`，具体支持范围以注册表和 `bluetooth_capabilities.json` 为准。
- `matlab_oracle/` 包含样本生成器、63 份 JSON 参考样本和完整性清单；`scripts/` 提供契约、回归和端到端检查。
- `mcp_server/` 从注册表提供工具发现和调用，启动及数据目录约束见 [MCP 接入说明](docs/MCP_接入说明.md)。
- `skillopt_wireless/`、`skillopt_data/` 和 [待审题集](docs/README.md)用于本地实验。专家设计题仍为 `draft`，当前技能不作为发布版本。

## 在此目录验证

```bash
python -m pip install -r requirements-mcp.txt
python scripts/check_json.py
python scripts/generate_sample_manifest.py --check
python scripts/generate_registry_docs.py --check
python scripts/check_contracts.py
python scripts/validate_all.py
python scripts/test_nr_pdsch_e2e.py --perfect-only
python -m unittest scripts.test_mcp_server -v
```

如需运行 SkillOpt 离线测试，另安装 `requirements-skillopt.txt`，并按 [本地训练说明](docs/SkillOpt_本地训练说明.md)操作。付费训练须显式配置 API 密钥；密钥和本地运行目录不进入仓库。

## 待团队联调

网站 Agent 与后端需决定 MCP 的启动方式、可见工具子集和受控文件取回流程，然后在目标环境验证 `tools/list`、代表性 `tools/call`、错误参数及文件型工具。服务器和网站的实际端到端结果应由集成负责人记录。
