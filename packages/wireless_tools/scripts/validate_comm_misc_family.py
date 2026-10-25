"""Legacy metadata and VITA header checks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_misc_family import (checkinp, comm_links, commlib, commprivate,
                              comms, intdump, vita49Reader)


def main():
    assert checkinp([[], 2], [3, 4])["values"] == [3, 2]
    assert intdump([1, 3, 2, 4], 2)["samples"].tolist() == [2, 3]
    assert commprivate("intdump", {"x": [1, 3], "nsamp": 2})["samples"].tolist() == [2]
    assert commlib()["library"] == "commlibv2"
    assert len(comms()["tools"]) > 30
    links = comm_links([{"path": "a", "library": "commlibv1"},
                        {"path": "b", "library": "commlibv2"}])
    assert links["obsolete"] == ["a"] and links["current"] == ["b"]
    packet = vita49Reader(data_hex="1000000200000001")["packets"][0]
    assert packet["stream_id"] == 1 and packet["size_words"] == 2
    print("PASS 7 Communications legacy/metadata entry slices")


if __name__ == "__main__":
    main()
