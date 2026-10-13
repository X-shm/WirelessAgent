"""M-PSK modulation and hard-decision demodulation."""
from __future__ import annotations
import argparse, json, math, sys
import numpy as np
from qam_modulation import _gray_decode, _labels


def psk_modulate(values, order, input_type="bits", symbol_order="gray", phase_offset=0.0):
    order = int(order); width = int(math.log2(order))
    if order < 2 or 2**width != order: raise ValueError("order must be a power of two")
    if input_type == "bits":
        bits = np.asarray(values, dtype=int).reshape(-1)
        if np.any((bits != 0) & (bits != 1)) or len(bits) % width: raise ValueError("invalid bit vector length")
        labels = np.array([sum(int(b) << (width - 1 - j) for j, b in enumerate(row)) for row in bits.reshape(-1, width)])
    else: labels = np.asarray(values, dtype=int).reshape(-1)
    if np.any(labels < 0) or np.any(labels >= order): raise ValueError("symbol labels out of range")
    phase_index = np.array([_gray_decode(int(v)) for v in labels]) if symbol_order == "gray" else labels
    return np.exp(1j * (float(phase_offset) + 2 * np.pi * phase_index / order)), labels


def psk_demodulate(symbols, order, output_type="bits", symbol_order="gray", phase_offset=0.0):
    table, labels = psk_modulate(range(order), order, "symbols", symbol_order, phase_offset)
    found = labels[np.argmin(np.abs(np.asarray(symbols)[:, None] - table[None, :]) ** 2, axis=1)]
    return _labels(found, int(math.log2(order))).reshape(-1) if output_type == "bits" else found


def main():
    p=argparse.ArgumentParser(); p.add_argument("--mode",required=True,choices=("modulate","demodulate")); p.add_argument("--order",required=True,type=int)
    p.add_argument("--values",required=True); p.add_argument("--input_type",choices=("bits","symbols"),default="bits"); p.add_argument("--output_type",choices=("bits","symbols"),default="bits")
    p.add_argument("--symbol_order",choices=("gray","binary"),default="gray"); p.add_argument("--phase_offset",type=float,default=0.0); a=p.parse_args()
    try:
        if a.mode=="modulate":
            out,labels=psk_modulate([int(v) for v in a.values.split(",")],a.order,a.input_type,a.symbol_order,a.phase_offset); result={"labels":labels.tolist(),"symbols_real":out.real.tolist(),"symbols_imag":out.imag.tolist()}
        else:
            raw=json.loads(a.values); symbols=np.asarray(raw["real"])+1j*np.asarray(raw["imag"]); out=psk_demodulate(symbols,a.order,a.output_type,a.symbol_order,a.phase_offset); result={"output_type":a.output_type,"values":out.tolist()}
        print(json.dumps(result))
    except (ValueError,KeyError,json.JSONDecodeError) as e: print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
