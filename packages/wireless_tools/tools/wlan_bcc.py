"""WLAN BCC Tool — IEEE 802.11 Binary Convolutional Code (BCC).

Replicates MATLAB wlanBCCEncode / wlanBCCDecode.
Generator polynomials: g0=133, g1=171 (octal), constraint length 7.
Rates: 1/2, 2/3, 3/4, 5/6 with standard puncturing patterns.
Verified against MATLAB golden samples.
"""
from __future__ import annotations

import json
import sys
import numpy as np

# Generator polynomials: g0=133(oct)=91, g1=171(oct)=121
# Coefficient vectors: [x^6, x^5, x^4, x^3, x^2, x, 1]
_G0 = np.array([1,0,1,1,0,1,1], dtype=np.uint8)   # 133 octal
_G1 = np.array([1,1,1,1,0,0,1], dtype=np.uint8)   # 171 octal

# Puncturing patterns (0=omit, 1=keep) for each rate
_PUNCTURE = {
    '1/2': np.array([1, 1]),                    # [P0, P1] — both kept
    '2/3': np.array([1, 1, 1, 0]),              # omit every 4th bit
    '3/4': np.array([1, 1, 1, 0, 0, 1]),       # omit 2 of every 6
    '5/6': np.array([1, 1, 1, 0, 0, 1, 1, 0, 0, 1]), # keep 6 of every 10 (rate 5/6)
}


def _build_trellis() -> tuple[np.ndarray, np.ndarray]:
    """Build the 64-state trellis for the IEEE 802.11 BCC mother code."""
    constraint_length = 7
    n_states = 1 << (constraint_length - 1)
    outputs = np.zeros((n_states, 2), dtype=np.uint8)
    next_states = np.zeros((n_states, 2), dtype=np.uint8)

    for state in range(n_states):
        for input_bit in (0, 1):
            # ``state`` holds the previous six input bits, newest first.
            register = np.zeros(constraint_length, dtype=np.uint8)
            register[0] = input_bit
            for index in range(constraint_length - 1):
                register[index + 1] = (
                    state >> (constraint_length - 2 - index)
                ) & 1
            output_0 = int((register * _G0).sum() % 2)
            output_1 = int((register * _G1).sum() % 2)
            outputs[state, input_bit] = (output_0 << 1) | output_1
            next_states[state, input_bit] = (
                input_bit << (constraint_length - 2)
            ) | (state >> 1)

    return outputs, next_states


def _data_length_from_punctured_length(
    codeword_length: int, puncture: np.ndarray
) -> int:
    """Return the input length corresponding to a punctured codeword length."""
    if codeword_length == 0:
        return 0

    kept_bits = 0
    data_length = 0
    pattern_length = len(puncture)
    while kept_bits < codeword_length:
        for output_index in range(2):
            if puncture[(2 * data_length + output_index) % pattern_length]:
                kept_bits += 1
        data_length += 1

    if kept_bits != codeword_length:
        raise ValueError(
            f"Codeword length {codeword_length} is invalid for this puncturing rate."
        )
    return data_length


def _depuncture(
    codeword: np.ndarray, data_length: int, puncture: np.ndarray
) -> np.ndarray:
    """Restore punctured output pairs, representing omitted bits with -1."""
    observations = np.full((data_length, 2), -1, dtype=np.int8)
    codeword_index = 0
    pattern_length = len(puncture)

    for data_index in range(data_length):
        for output_index in range(2):
            if puncture[(2 * data_index + output_index) % pattern_length]:
                observations[data_index, output_index] = codeword[codeword_index]
                codeword_index += 1
    return observations


def _conv_encode(bits: np.ndarray) -> np.ndarray:
    """Rate 1/2 mother convolutional encoding using MATLAB-compatible trellis."""
    outputs, next_states = _build_trellis()

    bits = np.asarray(bits, dtype=np.uint8) % 2
    out = np.zeros(2 * len(bits), dtype=np.uint8)
    state = 0
    for i, b in enumerate(bits):
        o = outputs[state, int(b)]
        out[2 * i] = (o >> 1) & 1
        out[2 * i + 1] = o & 1
        state = next_states[state, int(b)]
    return out


def bcc_encode(bits: np.ndarray, rate: str) -> np.ndarray:
    """BCC encode at specified rate."""
    bits = np.asarray(bits, dtype=np.uint8) % 2
    mother = _conv_encode(bits)
    punc = _PUNCTURE[rate]
    # Repeat puncturing pattern over mother code
    kept = []
    period = len(punc)
    for i in range(len(mother)):
        if punc[i % period]:
            kept.append(mother[i])
    return np.array(kept, dtype=np.uint8)


def _hamming_dist(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.sum(a != b))


def bcc_decode(codeword: np.ndarray, rate: str) -> np.ndarray:
    """Hard-decision Viterbi decoding of punctured BCC."""
    if rate not in _PUNCTURE:
        raise ValueError(f"Unsupported BCC coding rate: {rate}")

    received = np.asarray(codeword, dtype=np.uint8).reshape(-1) % 2
    puncture = _PUNCTURE[rate]
    data_length = _data_length_from_punctured_length(len(received), puncture)
    if data_length == 0:
        return np.zeros(0, dtype=np.uint8)

    observations = _depuncture(received, data_length, puncture)
    outputs, next_states = _build_trellis()
    n_states = len(outputs)

    # The encoder starts in state zero but is not terminated.  Select the
    # lowest-metric survivor after the final received symbol pair.
    path_metrics = np.full(n_states, np.inf)
    path_metrics[0] = 0
    predecessors = np.zeros((data_length, n_states), dtype=np.uint8)
    survivor_bits = np.zeros((data_length, n_states), dtype=np.uint8)

    for data_index, (received_0, received_1) in enumerate(observations):
        next_metrics = np.full(n_states, np.inf)
        for state, metric in enumerate(path_metrics):
            if not np.isfinite(metric):
                continue
            for input_bit in (0, 1):
                expected = outputs[state, input_bit]
                branch_metric = 0
                if received_0 >= 0:
                    branch_metric += received_0 != ((expected >> 1) & 1)
                if received_1 >= 0:
                    branch_metric += received_1 != (expected & 1)

                destination = int(next_states[state, input_bit])
                candidate_metric = metric + branch_metric
                if candidate_metric < next_metrics[destination]:
                    next_metrics[destination] = candidate_metric
                    predecessors[data_index, destination] = state
                    survivor_bits[data_index, destination] = input_bit
        path_metrics = next_metrics

    decoded = np.zeros(data_length, dtype=np.uint8)
    state = int(np.argmin(path_metrics))
    for data_index in range(data_length - 1, -1, -1):
        decoded[data_index] = survivor_bits[data_index, state]
        state = int(predecessors[data_index, state])
    return decoded


def main():
    import argparse
    parser = argparse.ArgumentParser("WLAN BCC tool")
    parser.add_argument('--bits', required=True, help="comma-separated data bits")
    parser.add_argument('--rate', required=True, choices=['1/2','2/3','3/4','5/6'])
    parser.add_argument('--decode', action='store_true')
    args = parser.parse_args()
    bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.uint8)

    if args.decode:
        dec = bcc_decode(bits, args.rate)
        print(json.dumps({"rate": args.rate, "decoded": dec.tolist()}))
    else:
        out = bcc_encode(bits, args.rate)
        print(json.dumps({"rate": args.rate, "input_bits": bits.tolist(),
                          "output_bits": out.tolist()}))


if __name__ == '__main__':
    main()
