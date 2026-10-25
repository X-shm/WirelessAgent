"""Reversible WLAN BCC interleaver, stream and two-segment routing slices."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import run_cli


def _bits(values):
    data = np.asarray(values)
    if data.ndim not in (1, 2) or data.size == 0 or not np.all((data == 0) | (data == 1)):
        raise ValueError("bits must be a nonempty 1-D or 2-D binary array")
    return data.astype(np.uint8)


def _matrix(values):
    data = _bits(values)
    return data[:, None] if data.ndim == 1 else data


def _interleave_indices(ncbps, nbpscs, type):
    ncol = 13 if type == "VHT" and ncbps % 13 == 0 else 16
    if not isinstance(ncbps, int) or ncbps < ncol or ncbps % ncol or nbpscs not in (1, 2, 4, 6, 8, 10, 12):
        raise ValueError("ncbps must divide into WLAN interleaver columns and nbpscs be a modulation order")
    k = np.arange(ncbps)
    first = (ncbps // ncol) * (k % ncol) + k // ncol
    s = max(nbpscs // 2, 1)
    second = s * (first // s) + (first + ncbps - (ncol * first) // ncbps) % s
    if len(np.unique(second)) != ncbps:
        raise ValueError("interleaver parameters do not produce a permutation")
    return second


def wlan_bcc_interleave(bits, ncbps, nbpscs=1, type="Non-HT"):
    if type not in ("Non-HT", "VHT"):
        raise ValueError("type must be Non-HT or VHT")
    data = _matrix(bits)
    if data.shape[0] % ncbps:
        raise ValueError("bit count per stream must be a multiple of ncbps")
    perm = _interleave_indices(ncbps, nbpscs, type)
    out = np.empty_like(data)
    for start in range(0, data.shape[0], ncbps):
        out[start + perm, :] = data[start:start+ncbps, :]
    return {"bits": out[:, 0].tolist() if np.asarray(bits).ndim == 1 else out.tolist(),
            "ncbps": ncbps, "nbpscs": nbpscs}


def wlan_bcc_deinterleave(bits, ncbps, nbpscs=1, type="Non-HT"):
    if type not in ("Non-HT", "VHT"):
        raise ValueError("type must be Non-HT or VHT")
    data = _matrix(bits)
    if data.shape[0] % ncbps:
        raise ValueError("bit count per stream must be a multiple of ncbps")
    perm = _interleave_indices(ncbps, nbpscs, type)
    out = np.empty_like(data)
    for start in range(0, data.shape[0], ncbps):
        out[start:start+ncbps, :] = data[start + perm, :]
    return {"bits": out[:, 0].tolist() if np.asarray(bits).ndim == 1 else out.tolist(),
            "ncbps": ncbps, "nbpscs": nbpscs}


def wlan_stream_parse(bits, num_space_time_streams, num_cbps, num_bpscs=1):
    data = _bits(bits).reshape(-1)
    nss = num_space_time_streams
    if not isinstance(nss, int) or not 1 <= nss <= 8 or num_cbps < 1 or num_cbps % nss:
        raise ValueError("num_space_time_streams must be 1..8 and divide num_cbps")
    if len(data) % num_cbps:
        raise ValueError("input length must be a multiple of num_cbps")
    s = max(1, num_bpscs // 2)
    if num_cbps % (nss*s):
        raise ValueError("num_cbps must be divisible by streams times routing block")
    groups = data.reshape(-1, s)
    streams = [groups[i::nss].reshape(-1).tolist() for i in range(nss)]
    return {"streams": streams, "num_space_time_streams": nss, "routing_block": s}


def wlan_stream_deparse(streams, num_encoded_streams=1, num_cbps=None, num_bpscs=1):
    if not isinstance(streams, list) or not 1 <= len(streams) <= 8:
        raise ValueError("streams must be a list of 1..8 bit vectors")
    arrays = [_bits(stream).reshape(-1) for stream in streams]
    lengths = {len(a) for a in arrays}
    s = max(1, num_bpscs // 2)
    if len(lengths) != 1 or next(iter(lengths)) % s:
        raise ValueError("stream lengths must match and divide into routing blocks")
    groups = [a.reshape(-1, s) for a in arrays]
    merged = np.stack(groups, axis=1).reshape(-1)
    if num_cbps is not None and merged.size % num_cbps:
        raise ValueError("merged length must be a multiple of num_cbps")
    if not isinstance(num_encoded_streams, int) or num_encoded_streams < 1 or merged.size % num_encoded_streams:
        raise ValueError("invalid num_encoded_streams")
    return {"encoded_streams": merged.reshape(num_encoded_streams, -1).tolist(),
            "bits": merged.tolist()}


def _segment_count(channel_bandwidth):
    if channel_bandwidth not in ("CBW1", "CBW2", "CBW4", "CBW8", "CBW16",
                                 "CBW20", "CBW40", "CBW80", "CBW160"):
        raise ValueError("invalid VHT/S1G channel bandwidth")
    return 2 if channel_bandwidth in ("CBW16", "CBW160") else 1


def wlan_segment_parse_bits(bits, channel_bandwidth="CBW80", num_bpscs=1,
                            num_encoded_streams=1):
    data = _matrix(bits)
    nseg = _segment_count(channel_bandwidth)
    if nseg == 1:
        return {"segments": [data.tolist()], "num_segments": 1}
    s = max(1, num_bpscs // 2)
    if data.shape[0] % (2*s):
        raise ValueError("bits per stream must be divisible by two routing blocks")
    groups = data.reshape(-1, s, data.shape[1])
    return {"segments": [groups[i::2].reshape(-1, data.shape[1]).tolist() for i in range(2)],
            "num_segments": 2, "num_encoded_streams": num_encoded_streams}


def wlan_segment_deparse_bits(segments, channel_bandwidth="CBW80", num_bpscs=1,
                              num_encoded_streams=1):
    nseg = _segment_count(channel_bandwidth)
    if not isinstance(segments, list) or len(segments) != nseg:
        raise ValueError("segment count does not match channel bandwidth")
    arrays = [_matrix(segment) for segment in segments]
    if nseg == 1:
        out = arrays[0]
    else:
        if arrays[0].shape != arrays[1].shape:
            raise ValueError("segment shapes differ")
        s = max(1, num_bpscs // 2)
        if arrays[0].shape[0] % s:
            raise ValueError("segment length must divide routing block")
        out = np.stack([array.reshape(-1, s, array.shape[1]) for array in arrays], axis=1)
        out = out.reshape(-1, arrays[0].shape[1])
    return {"bits": out[:, 0].tolist() if out.shape[1] == 1 else out.tolist(),
            "num_segments": nseg, "num_encoded_streams": num_encoded_streams}


def wlan_segment_parse_symbols(symbols, channel_bandwidth="CBW80"):
    data = np.asarray(symbols)
    if data.ndim < 1 or data.shape[0] == 0:
        raise ValueError("symbols require a nonempty leading subcarrier dimension")
    nseg = _segment_count(channel_bandwidth)
    if data.shape[0] % nseg:
        raise ValueError("subcarrier count not divisible by segment count")
    return {"segments": [part.tolist() for part in np.split(data, nseg, axis=0)],
            "num_segments": nseg}


def wlan_segment_deparse_symbols(segments, channel_bandwidth="CBW80"):
    nseg = _segment_count(channel_bandwidth)
    if not isinstance(segments, list) or len(segments) != nseg:
        raise ValueError("segment count does not match channel bandwidth")
    arrays = [np.asarray(part) for part in segments]
    if any(part.shape[1:] != arrays[0].shape[1:] for part in arrays):
        raise ValueError("segment trailing dimensions differ")
    return {"symbols": np.concatenate(arrays, axis=0).tolist(), "num_segments": nseg}


DISPATCH = {
    "wlanBCCInterleave": wlan_bcc_interleave,
    "wlanBCCDeinterleave": wlan_bcc_deinterleave,
    "wlanStreamParse": wlan_stream_parse,
    "wlanStreamDeparse": wlan_stream_deparse,
    "wlanSegmentParseBits": wlan_segment_parse_bits,
    "wlanSegmentDeparseBits": wlan_segment_deparse_bits,
    "wlanSegmentParseSymbols": wlan_segment_parse_symbols,
    "wlanSegmentDeparseSymbols": wlan_segment_deparse_symbols,
}


if __name__ == "__main__":
    run_cli("WLAN BCC interleaver and stream/segment routing", DISPATCH)
