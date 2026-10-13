"""Smoke-verify wireless_numeric skill against original tools + closed-form goldens."""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
DIS = ROOT / "skills" / "wireless_numeric" / "dispatcher.py"
PY = sys.executable


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run([PY, str(DIS), *args], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT))
    return p.returncode, (p.stdout or "").strip()


def run_raw(tool: str, *flags: str) -> tuple[int, str]:
    p = subprocess.run([PY, str(ROOT / "tools" / f"{tool}.py"), *flags], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT))
    return p.returncode, (p.stdout or "").strip()


fails: list[str] = []
oks = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global oks
    if cond:
        oks += 1
        print(f"PASS {name} {detail}")
    else:
        fails.append(name)
        print(f"FAIL {name} {detail}")


# --- goldens ---
rc, out = run("run", "q_function", "--mode", "qfunc", "--values", "1,2")
d = json.loads(out)
check("Q(1)", abs(d["output"][0] - 0.15865525393145707) < 1e-12, f"got {d['output'][0]}")
check("Q(2)", abs(d["output"][1] - 0.022750131948179216) < 1e-12, f"got {d['output'][1]}")

rc, out = run("run", "ber_awgn", "--ebno_db", "0", "--modulation", "bpsk")
d = json.loads(out)
gold = 0.5 * math.erfc(math.sqrt(1.0))  # Q(sqrt(2)) at Eb/N0=0dB for BPSK
check("BPSK BER EbN0=0", abs(d["ber"][0] - gold) < 1e-9, f"got {d['ber'][0]} gold {gold}")

rc, out = run("run", "convert_snr", "--x", "0", "--input_mode", "ebno", "--output_mode", "esno", "--bits_per_symbol", "2")
d = json.loads(out)
check("EbN0=0dB,k=2 → EsN0=3.01dB", abs(d["values_db"] - 10 * math.log10(2)) < 1e-9, f"got {d['values_db']}")

rc, out = run("run", "link_capacity", "--snr_db", "0", "--bandwidth_hz", "1")
d = json.loads(out)
# C = B log2(1+SNR) = 1 bit/s at SNR=0dB,B=1
cap = d.get("capacity_bps") or d.get("capacity") or d.get("shannon_capacity_bps")
check("Shannon SNR=0dB B=1", cap is not None and abs(float(cap) - 1.0) < 1e-6, f"got {d}")

# --- every PACK tool at least --help / one example-ish run ---
rc, out = run("list")
pack = json.loads(out)["tools"]
print(f"PACK size {len(pack)}")
for item in pack:
    tool = item["tool"]
    rc, _ = run("help", tool)
    check(f"help {tool}", rc == 0)

# dispatcher == direct tool
rc1, o1 = run("run", "lte_mcs", "--imcs", "17", "--table", "PDSCH")
rc2, o2 = run_raw("lte_mcs", "--imcs", "17", "--table", "PDSCH")
check("dispatcher==tools", rc1 == rc2 and o1 == o2)

# pack boundary
rc, out = run("run", "ble_att", "--input", "{}")
check("reject out-of-pack", rc != 0 and "not in numeric pack" in out)

print(f"\n=== {oks} passed, {len(fails)} failed ===")
if fails:
    print("failed:", fails)
raise SystemExit(1 if fails else 0)
