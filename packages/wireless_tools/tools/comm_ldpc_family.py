"""MATLAB-free generic and DVB-S2 binary LDPC matrix and codec slices."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix

from _nr_remaining_common import run_cli


_TABLE_PATH = Path(__file__).resolve().parents[1] / "matlab_oracle" / "samples" / "comm_dvbs2_tables.json"


def _binary(value, name):
    result = np.asarray(value, int).reshape(-1)
    if not len(result) or np.any((result != 0) & (result != 1)):
        raise ValueError(f"{name} must contain binary bits")
    return result.astype(np.uint8)


def _coo(h):
    if isinstance(h, dict):
        shape = tuple(map(int, h["shape"]))
        rows = np.asarray(h["row_indices"], int)
        cols = np.asarray(h["col_indices"], int)
        if len(shape) != 2 or shape[0] < 1 or shape[1] <= shape[0] or len(rows) != len(cols):
            raise ValueError("invalid sparse parity-check shape or indices")
        if np.any(rows < 0) or np.any(rows >= shape[0]) or np.any(cols < 0) or np.any(cols >= shape[1]):
            raise ValueError("sparse parity-check index out of bounds")
        matrix = coo_matrix((np.ones(len(rows), np.uint8), (rows, cols)), shape=shape).tocsr()
        matrix.data &= 1
        matrix.eliminate_zeros()
        return matrix
    dense = np.asarray(h, int)
    if dense.ndim != 2 or dense.shape[0] < 1 or dense.shape[1] <= dense.shape[0] or np.any((dense != 0) & (dense != 1)):
        raise ValueError("h must be a binary matrix with more columns than rows")
    return csr_matrix(dense.astype(np.uint8))


def _encode_sparse(h):
    matrix = _coo(h).tocoo()
    return {"shape": list(matrix.shape), "row_indices": matrix.row.astype(int),
            "col_indices": matrix.col.astype(int)}


def ldpcQuasiCyclicMatrix(block_size: int, p):
    prototype = np.asarray(p, int)
    if block_size < 1 or int(block_size) != block_size or prototype.ndim != 2 or prototype.shape[0] >= prototype.shape[1]:
        raise ValueError("positive block_size and wide 2-D prototype required")
    if np.any(prototype < -1) or np.any(prototype >= block_size):
        raise ValueError("prototype entries must be -1 or [0,block_size)")
    rows, cols = [], []
    for block_row, block_col in zip(*np.nonzero(prototype >= 0)):
        shift = prototype[block_row, block_col]
        for col in range(block_size):
            rows.append(int(block_row*block_size + (col-shift) % block_size))
            cols.append(int(block_col*block_size + col))
    return {"shape": [prototype.shape[0]*block_size, prototype.shape[1]*block_size],
            "row_indices": rows, "col_indices": cols}


def dvbs2ldpc(rate: str, row_start: int = 0, row_stop=None):
    tables = json.loads(_TABLE_PATH.read_text(encoding="utf-8"))
    if rate not in tables:
        raise ValueError(f"rate must be one of {sorted(tables)}")
    numerator, denominator = map(int, rate.split("/"))
    n, k = 64800, 64800*numerator//denominator
    m, q = n-k, (n-k)//360
    if row_stop is None:
        row_stop = m
    if not 0 <= row_start < row_stop <= m:
        raise ValueError("row window must lie inside parity-check matrix")
    rows, cols = [], []
    group = 0
    for part in ("ct1", "ct2"):
        for table_row in tables[rate][part]:
            base = np.asarray(table_row, int)
            for within in range(360):
                indices = (base + within*q) % m
                for row in indices:
                    if row_start <= row < row_stop:
                        rows.append(int(row-row_start))
                        cols.append(int(group*360+within))
            group += 1
    if group*360 != k:
        raise ValueError("DVB-S2 static table has inconsistent information dimension")
    for parity_col in range(m):
        for row in (parity_col, parity_col+1):
            if row < m and row_start <= row < row_stop:
                rows.append(row-row_start)
                cols.append(k+parity_col)
    return {"shape": [row_stop-row_start, n], "full_shape": [m, n],
            "row_offset": row_start, "row_indices": rows, "col_indices": cols,
            "standard": "DVB-S2", "rate": rate}


def ldpcPCM(h=None, standard="wlan", rate="5/6", block_length=648, block_size=None, prototype=None):
    if h is not None:
        return _encode_sparse(h)
    if prototype is not None:
        return ldpcQuasiCyclicMatrix(block_size, prototype)
    if standard.lower() == "dvbs2":
        return dvbs2ldpc(rate)
    if standard.lower() == "wlan":
        from wlan_ldpc import _load_H
        return _encode_sparse(_load_H(rate, block_length))
    raise ValueError("standard must be wlan or dvbs2")


def ldpcEncoderConfig(h=None, standard="wlan", rate="5/6", block_length=648):
    if h is None:
        descriptor = {"standard": standard, "rate": rate, "block_length": block_length}
        matrix = ldpcPCM(standard=standard, rate=rate, block_length=block_length)
    else:
        descriptor = {"h": _encode_sparse(h)}
        matrix = descriptor["h"]
    m, n = matrix["shape"]
    if n <= 4096 and h is not None:
        parity = _coo(matrix)[:, n-m:].toarray().astype(np.uint8)
        if _gf2_rank(parity) != m:
            raise ValueError("last parity-check columns must be invertible over GF(2)")
    return {**descriptor, "block_length": n, "num_information_bits": n-m,
            "num_parity_bits": m}


def ldpcDecoderConfig(h=None, standard="wlan", rate="5/6", block_length=648,
                      algorithm="minsum"):
    if algorithm not in ("minsum", "normalized_minsum"):
        raise ValueError("algorithm must be minsum or normalized_minsum")
    config = ldpcEncoderConfig(h, standard, rate, block_length)
    config["algorithm"] = algorithm
    return config


def _gf2_rank(matrix):
    a = matrix.copy()
    row = 0
    for col in range(a.shape[1]):
        pivots = np.flatnonzero(a[row:, col])
        if len(pivots):
            pivot = row+pivots[0]
            a[[row, pivot]] = a[[pivot, row]]
            for r in range(row+1, len(a)):
                if a[r, col]:
                    a[r] ^= a[row]
            row += 1
            if row == len(a):
                break
    return row


def _gf2_solve(a, b):
    a = a.astype(np.uint8).copy()
    b = b.astype(np.uint8).copy()
    n = len(b)
    for col in range(n):
        pivots = np.flatnonzero(a[col:, col])
        if not len(pivots):
            raise ValueError("parity block is singular")
        pivot = col+pivots[0]
        a[[col, pivot]] = a[[pivot, col]]
        b[[col, pivot]] = b[[pivot, col]]
        for row in range(n):
            if row != col and a[row, col]:
                a[row] ^= a[col]
                b[row] ^= b[col]
    return b


def _matrix_for_config(cfg):
    if "h" in cfg:
        return _coo(cfg["h"])
    return _coo(ldpcPCM(standard=cfg.get("standard", "wlan"),
                        rate=cfg.get("rate", "5/6"), block_length=cfg.get("block_length", 648)))


def ldpcEncode(information_bits, cfg):
    info = _binary(information_bits, "information_bits")
    matrix = _matrix_for_config(cfg)
    m, n = matrix.shape
    if len(info) != n-m:
        raise ValueError(f"expected {n-m} information bits")
    syndrome = np.asarray((matrix[:, :n-m] @ info) & 1, np.uint8).reshape(-1)
    if cfg.get("standard", "").lower() == "dvbs2" and "h" not in cfg:
        parity = np.bitwise_xor.accumulate(syndrome)
    else:
        if m > 2048:
            raise ValueError("generic parity solve limited to 2048 checks")
        parity = _gf2_solve(matrix[:, n-m:].toarray(), syndrome)
    codeword = np.r_[info, parity]
    if np.any((matrix @ codeword) & 1):
        raise ValueError("LDPC parity verification failed")
    return {"codeword": codeword}


def ldpcDecode(llr, cfg, max_iterations: int = 20, normalization: float = .8):
    likelihood = np.asarray(llr, float).reshape(-1)
    h = _matrix_for_config(cfg)
    m, n = h.shape
    if len(likelihood) != n or np.any(~np.isfinite(likelihood)) or max_iterations < 1:
        raise ValueError("finite block-length LLR and positive max_iterations required")
    if not 0 < normalization <= 1:
        raise ValueError("normalization must be in (0,1]")
    h = h.tocsr()
    edge_cols = h.indices
    variable_to_check = likelihood[edge_cols].copy()
    check_to_variable = np.zeros_like(variable_to_check)
    for iteration in range(max_iterations+1):
        total = likelihood.copy()
        np.add.at(total, edge_cols, check_to_variable)
        decoded = (total < 0).astype(np.uint8)
        checks = np.asarray((h @ decoded) & 1).reshape(-1)
        if not np.any(checks) or iteration == max_iterations:
            return {"information_bits": decoded[:n-m], "codeword": decoded,
                    "actual_iterations": iteration, "final_parity_checks": checks}
        variable_to_check = total[edge_cols] - check_to_variable
        for row in range(m):
            lo, hi = h.indptr[row:row+2]
            if hi <= lo:
                continue
            msg = variable_to_check[lo:hi]
            absval = abs(msg)
            sign = np.where(msg < 0, -1.0, 1.0)
            parity_sign = np.prod(sign)
            smallest = np.min(absval)
            second = np.partition(absval, 1)[1] if len(absval) > 1 else smallest
            check_to_variable[lo:hi] = normalization * parity_sign * sign * np.where(absval == smallest, second, smallest)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    run_cli("Generic and DVB-S2 LDPC matrix/codec slices", {
        "dvbs2ldpc": dvbs2ldpc, "ldpcPCM": ldpcPCM,
        "ldpcQuasiCyclicMatrix": ldpcQuasiCyclicMatrix,
        "ldpcEncoderConfig": ldpcEncoderConfig,
        "ldpcDecoderConfig": ldpcDecoderConfig,
        "ldpcEncode": ldpcEncode, "ldpcDecode": ldpcDecode,
    })
