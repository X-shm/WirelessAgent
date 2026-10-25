"""Standalone single-RB PUCCH format 0-4 processing subsets."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import bits, complex_array, run_cli
from nr_low_papr import low_papr_type1
from nr_modulation import modulate, soft_demodulate
from nr_prbs import prbs


def _base_sequence(nid: int, initial_cs: int, mcs: int = 0):
    if not 0 <= nid <= 1023 or not 0 <= initial_cs <= 11:
        raise ValueError("nid must be 0..1023 and initial_cs 0..11")
    alpha = 2 * np.pi * ((initial_cs + mcs) % 12) / 12
    return low_papr_type1(nid % 30, 0, alpha, 12).reshape(12)


def _format0_mcs(ack, sr: int):
    a = [] if ack is None else np.asarray(ack, dtype=int).reshape(-1).tolist()
    if len(a) > 2 or any(bit not in (0, 1) for bit in a) or sr not in (0, 1):
        raise ValueError("format 0 permits up to two ACK bits and one SR bit")
    if len(a) == 0:
        return 0 if sr else None
    if len(a) == 1:
        return (6 if a[0] else 0) + (3 if sr else 0)
    if sr:
        raise ValueError("this format-0 subset does not combine two ACK bits with SR")
    return {(0, 0): 0, (0, 1): 3, (1, 1): 6, (1, 0): 9}[tuple(a)]


def pucch0(ack=None, sr: int = 0, nid: int = 0, initial_cs: int = 0,
           num_symbols: int = 1):
    if num_symbols not in (1, 2):
        raise ValueError("format 0 num_symbols must be 1 or 2")
    mcs = _format0_mcs(ack, sr)
    if mcs is None:
        return {"symbols": np.zeros(0, dtype=complex), "mcs": None}
    sequence = _base_sequence(nid, initial_cs, mcs)
    return {"symbols": np.tile(sequence, num_symbols), "mcs": mcs}


def pucch1(uci_bits, nid: int = 0, initial_cs: int = 0,
           num_symbols: int = 4, slot: int = 0):
    data = bits(uci_bits, "uci_bits")
    if len(data) not in (1, 2) or not 4 <= num_symbols <= 14:
        raise ValueError("format 1 needs one/two UCI bits and 4..14 symbols")
    modulation = "BPSK" if len(data) == 1 else "QPSK"
    symbol = modulate(data, modulation)[0]
    shifts = pucch_hopping_info(nid, slot, initial_cs)["cyclic_shifts"]
    data_locations = range(1, num_symbols, 2)
    symbols = np.concatenate([_base_sequence(nid, int(shifts[l])) * symbol
                              for l in data_locations])
    return {"symbols": symbols,
            "dmrs_symbols": list(range(0, num_symbols, 2))}


def _coded(uci_bits, format_number: int, nid: int = 0, nrb: int = 1,
           num_symbols: int = 2):
    data = bits(uci_bits, "uci_bits")
    if format_number == 2:
        if not 1 <= nrb <= 16 or num_symbols not in (1, 2):
            raise ValueError("format 2 needs 1..16 RBs and 1..2 symbols")
    elif format_number in (3, 4):
        if not 4 <= num_symbols <= 14 or (format_number == 4 and nrb != 1):
            raise ValueError("format 3/4 needs 4..14 symbols; format 4 one RB")
    else:
        raise ValueError("format_number must be 2, 3 or 4")
    capacity = 12 * nrb * num_symbols
    if format_number == 2:
        capacity = 8 * nrb * num_symbols
    if len(data) % 2 or len(data) // 2 > capacity:
        raise ValueError("even-length coded UCI must fit the resource capacity")
    scrambled = data ^ prbs(nid, len(data)).astype(np.uint8)
    # The supplied bits are already UCI encoded and rate matched.
    symbols = modulate(scrambled, "QPSK")
    if format_number == 3:
        chunks = [np.fft.fft(symbols[i:i + 12], norm="ortho")
                  for i in range(0, len(symbols), 12)]
        symbols = np.concatenate(chunks) if chunks else symbols
    if format_number == 4:
        symbols = np.repeat(symbols, 2)
    return {"symbols": symbols, "format": format_number}


def pucch2(uci_bits, nid: int = 0, nrb: int = 1, num_symbols: int = 2):
    return _coded(uci_bits, 2, nid, nrb, num_symbols)


def pucch3(uci_bits, nid: int = 0, nrb: int = 1, num_symbols: int = 4):
    return _coded(uci_bits, 3, nid, nrb, num_symbols)


def pucch4(uci_bits, nid: int = 0, nrb: int = 1, num_symbols: int = 4):
    return _coded(uci_bits, 4, nid, nrb, num_symbols)


def pucch(format_number: int, uci_bits=None, ack=None, sr: int = 0,
          nid: int = 0, initial_cs: int = 0, nrb: int = 1,
          num_symbols: int | None = None, slot: int = 0):
    if format_number == 0:
        if slot:
            raise ValueError("nonzero slot is supported only for format 1")
        return pucch0(ack, sr, nid, initial_cs, num_symbols or 1)
    if format_number == 1:
        return pucch1(uci_bits, nid, initial_cs, num_symbols or 4, slot)
    if slot:
        raise ValueError("nonzero slot is supported only for format 1")
    return _coded(uci_bits, format_number, nid, nrb,
                  num_symbols or (2 if format_number == 2 else 4))


def pucch_indices(nrb: int, rb: int = 0, symbol_start: int = 0,
                  num_symbols: int = 1, format_number: int = 0,
                  index_base: int = 1):
    if not 1 <= nrb <= 275 or not 0 <= rb < nrb or not 0 <= symbol_start < 14:
        raise ValueError("invalid carrier, RB or start symbol")
    if num_symbols < 1 or symbol_start + num_symbols > 14 or format_number not in range(5):
        raise ValueError("invalid symbol allocation or PUCCH format")
    if index_base not in (0, 1):
        raise ValueError("index_base must be 0/1")
    dmrs_subcarriers = {1, 4, 7, 10}
    data, dmrs = [], []
    for l in range(symbol_start, symbol_start + num_symbols):
        for k in range(12):
            index = index_base + l * 12 * nrb + rb * 12 + k
            if format_number == 2 and k in dmrs_subcarriers:
                dmrs.append(index)
            elif format_number == 1 and (l - symbol_start) % 2 == 0:
                dmrs.append(index)
            elif format_number in (3, 4) and (l - symbol_start) % 2:
                dmrs.append(index)
            else:
                data.append(index)
    return {"indices": data, "dmrs_indices": dmrs}


def pucch_dmrs_indices(nrb: int, rb: int = 0, symbol_start: int = 0,
                       num_symbols: int = 4, format_number: int = 1,
                       index_base: int = 1):
    return {"indices": pucch_indices(nrb, rb, symbol_start, num_symbols,
                                     format_number, index_base)["dmrs_indices"]}


def pucch_dmrs(nid: int, nrb: int = 1, num_symbols: int = 4,
               format_number: int = 1, initial_cs: int = 0, slot: int = 0):
    if format_number not in (1, 2, 3, 4):
        raise ValueError("DM-RS supports formats 1..4")
    idx = pucch_dmrs_indices(nrb, 0, 0, num_symbols, format_number, 0)["indices"]
    if format_number == 2:
        sequence = prbs(nid, 2 * len(idx)).reshape(-1, 2).astype(int)
        symbols = ((1 - 2 * sequence[:, 0]) + 1j * (1 - 2 * sequence[:, 1])) / np.sqrt(2)
    elif format_number == 1:
        shifts = pucch_hopping_info(nid, slot, initial_cs)["cyclic_shifts"]
        symbols = np.concatenate([_base_sequence(nid, int(shifts[l]))
                                  for l in range(0, num_symbols, 2)])
    else:
        if slot:
            raise ValueError("nonzero slot is supported only for format 1")
        base = _base_sequence(nid, initial_cs)
        symbols = np.tile(base, max(1, len(idx) // 12))[:len(idx)]
    return {"symbols": symbols, "indices": idx}


def pucch_hopping_info(nid: int, slot: int = 0, initial_cs: int = 0):
    if not 0 <= nid <= 1023 or slot < 0 or not 0 <= initial_cs <= 11:
        raise ValueError("invalid nid, slot or initial_cs")
    sequence = prbs(nid, 8 * (14 * slot + 14)).reshape(-1, 8)
    values = sequence[14 * slot:14 * slot + 14] @ (1 << np.arange(8))
    return {"group": nid % 30, "sequence_hopping": 0,
            "cyclic_shifts": ((initial_cs + values) % 12).astype(int)}


def pucch_decode(symbols, format_number: int, nid: int = 0,
                 initial_cs: int = 0, num_symbols: int = 1, noise_variance: float = 1.0,
                 ack_bits: int = 1, allow_sr: bool = False,
                 uci_bits_length: int = 2, slot: int = 0):
    received = complex_array(symbols).reshape(-1)
    if noise_variance <= 0:
        raise ValueError("noise_variance must be positive")
    if format_number == 0:
        if ack_bits not in (0, 1, 2):
            raise ValueError("ack_bits must be 0, 1 or 2")
        if ack_bits == 2 and allow_sr:
            raise ValueError("two ACK bits plus SR are unsupported")
        candidates = [([(value >> shift) & 1 for shift in range(ack_bits - 1, -1, -1)], sr)
                      for value in range(1 << ack_bits)
                      for sr in (range(2) if allow_sr else (0,))
                      if ack_bits or sr]
        if not candidates:
            raise ValueError("no format-0 transmission candidates")
        scores = []
        for ack, sr in candidates:
            reference = pucch0(ack, sr, nid, initial_cs, num_symbols)["symbols"]
            scores.append(abs(np.vdot(reference, received)) if len(reference) == len(received) else -1)
        index = int(np.argmax(scores))
        return {"ack": candidates[index][0], "sr": candidates[index][1],
                "correlation": float(scores[index])}
    if format_number == 1:
        if uci_bits_length not in (1, 2):
            raise ValueError("format 1 uci_bits_length must be 1 or 2")
        if not 4 <= num_symbols <= 14:
            raise ValueError("format 1 num_symbols must be 4..14")
        shifts = pucch_hopping_info(nid, slot, initial_cs)["cyclic_shifts"]
        base = np.concatenate([_base_sequence(nid, int(shifts[l]))
                               for l in range(1, num_symbols, 2)])
        if len(received) != len(base):
            raise ValueError("format 1 received symbol length mismatch")
        estimate = np.vdot(base, received) / len(base)
        modulation = "BPSK" if uci_bits_length == 1 else "QPSK"
        llr = soft_demodulate(np.asarray([estimate]), modulation, noise_variance)
        return {"bits": (llr < 0).astype(int), "llr": llr}
    if format_number in (2, 3, 4):
        if format_number == 4:
            if len(received) % 2:
                raise ValueError("format 4 needs an even number of symbols")
            received = received.reshape(-1, 2).mean(axis=1)
        if format_number == 3:
            received = np.concatenate([np.fft.ifft(received[i:i + 12], norm="ortho")
                                       for i in range(0, len(received), 12)])
        llr = soft_demodulate(received, "QPSK", noise_variance)
        llr *= 1 - 2 * prbs(nid, len(llr)).astype(int)
        return {"bits": (llr < 0).astype(int), "llr": llr}
    raise ValueError("format_number must be 0..4")


if __name__ == "__main__":
    run_cli("Standalone single-RB NR PUCCH subsets", {
        "nrPUCCH": pucch,
        "nrPUCCH0": pucch0,
        "nrPUCCH1": pucch1,
        "nrPUCCH2": pucch2,
        "nrPUCCH3": pucch3,
        "nrPUCCH4": pucch4,
        "nrPUCCHDecode": pucch_decode,
        "nrPUCCHDMRS": pucch_dmrs,
        "nrPUCCHDMRSIndices": pucch_dmrs_indices,
        "nrPUCCHHoppingInfo": pucch_hopping_info,
        "nrPUCCHIndices": pucch_indices,
    })
