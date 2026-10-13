---
name: nr_modulation
description: |
  nr_modulation 的注册表驱动调用说明。调用前读取 schema 并确认注册状态和覆盖范围。
user-invocable: true
---

# NR Modulation

> 此文件由 `scripts/generate_registry_docs.py` 从 `tool_registry.json` 自动生成。
> 请先更新注册表，再执行 `python scripts/generate_registry_docs.py --write`；不要直接编辑本文件。

## 注册记录

- 工具：`nr_modulation`
- 产品/领域：5G Toolbox
- 状态：`validated`
- 注册源函数：`nrSymbolModulate`, `nrSymbolDemodulate`
- 覆盖范围：BPSK, pi/2-BPSK, QPSK and square QAM through 1024QAM, includes soft demodulation (LLR)
- Schema：`tools/nr_modulation.schema.json`

## 调用

```bash
python tools/nr_modulation.py --help
```

参数、子命令和 JSON 输出以对应 schema 及 CLI 帮助为准。
