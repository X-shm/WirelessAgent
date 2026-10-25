"""GSM frame structure and configuration properties."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_gsm_family import (gsmCheckTimeMask, gsmDownlinkBurstType, gsmDownlinkConfig,
                             gsmFrame, gsmInfo, gsmUplinkBurstType, gsmUplinkConfig)


def main():
    assert gsmDownlinkBurstType("FB")["code"] == 1
    assert gsmUplinkBurstType("AB")["code"] == 4
    up = gsmUplinkConfig(burst_type=["Off"]+ ["NB"]*7)
    down = gsmDownlinkConfig()
    assert gsmInfo(down)["frame_length_samples"] == 20000
    assert gsmInfo(up)["num_bursts_per_frame"] == 8
    frame = gsmFrame(up, seed=5)["waveform"]
    assert len(frame) == 20000 and np.max(abs(frame[:2500])) == 0
    assert gsmCheckTimeMask(up, frame)["pass"]
    print("PASS 7 Communications GSM entry slices")


if __name__ == "__main__":
    main()
