---
name: nr_ldpc_bcc
description: |
  NR CRC、WLAN BCC 与 NR LDPC 速率匹配的注册表驱动调用说明。
user-invocable: true
---

# Additional Wireless Tools

> 此文件由 `scripts/generate_registry_docs.py` 从 `tool_registry.json` 自动生成。
> 请先更新注册表，再执行 `python scripts/generate_registry_docs.py --write`；不要直接编辑本文件。

## 注册工具

| 工具 | 产品/领域 | 状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `nr_crc` | 5G Toolbox | `validated` | — | `tools/nr_crc.schema.json` |
| `wlan_bcc` | WLAN Toolbox | `validated` | — | `tools/wlan_bcc.schema.json` |
| `nr_ldpc_rm` | 5G Toolbox | `validated` | rate match + rate recover with de-interleaving | `tools/nr_ldpc_rm.schema.json` |

```bash
python tools/nr_crc.py --help
python tools/wlan_bcc.py --help
python tools/nr_ldpc_rm.py --help
```

参数和输出以各自 schema 及 CLI 帮助为准。
