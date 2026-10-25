"""Traffic schedule property and default checks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from wnet_traffic_models import (networkTrafficFTP, networkTrafficOnOff,
                                 networkTrafficVideoConference, networkTrafficVoIP)


def main():
    ftp = networkTrafficFTP(packet_count=2, fixed_file_size_mb=.001, reading_time_ms=10)
    assert [p["size_bytes"] for p in ftp["packets"]] == [1040, 1040]
    assert ftp["packets"][1]["time_ms"] == 10
    onoff = networkTrafficOnOff(packet_count=2, on_time_s=10, off_time_s=0,
                                data_rate_kbps=1000, packet_size=100)
    assert [p["time_ms"] for p in onoff["packets"]] == [.8, 1.6]
    video = networkTrafficVideoConference(packet_count=4, frame_size_method="FixedSize",
                                          fixed_frame_size=3000, has_jitter=False)
    assert [p["size_bytes"] for p in video["packets"][:3]] == [1500, 1500, 84]
    voip = networkTrafficVoIP(packet_count=3, has_jitter=False, exponential_mean_ms=100000, seed=1)
    assert [p["time_ms"] for p in voip["packets"]] == [0, 20, 40]
    assert [p["size_bytes"] for p in voip["packets"]] == [36, 36, 36]
    assert networkTrafficVoIP(packet_count=3, seed=5) == networkTrafficVoIP(packet_count=3, seed=5)
    print("PASS 4 public Wireless Network traffic model slices")


if __name__ == "__main__":
    main()
