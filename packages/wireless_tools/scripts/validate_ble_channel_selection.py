"""Validate BLE Channel Selection Algorithm #1/#2 against R2026a."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_channel_selection import _initial_dynamic, _settings, select

samples = json.loads(
    (ROOT / "matlab_oracle" / "samples" / "bluetooth_core_samples.json").read_text(encoding="utf-8")
)["channel_selection"]
for sample in samples:
    request = {
        name: sample[name]
        for name in ("algorithm", "hop_increment", "access_address", "used_channels", "subevent_channel_selection")
    }
    settings = _settings(request)
    state = _initial_dynamic()
    if sample["subevent_channel_selection"]:
        got = []
        for number in sample["subevent_numbers"]:
            current, state = select(
                settings, state, isochronous_event_counter=sample["isochronous_event_counter"],
                subevent_number=number,
            )
            got.extend(current)
    else:
        got, state = select(settings, state, count=len(sample["channel_indices"]))
    assert got == sample["channel_indices"], (sample["algorithm"], got, sample["channel_indices"])
print(f"PASS {len(samples)} BLE channel-selection golden samples")
