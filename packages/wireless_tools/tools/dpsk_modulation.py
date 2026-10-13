"""Differential M-PSK modulation and hard demodulation."""
from __future__ import annotations
import argparse,json,math,sys
import numpy as np
from qam_modulation import _gray_decode

def _gray_encode(v): return int(v) ^ (int(v)>>1)
def dpsk_modulate(labels,order,phase_rotation=0.0,symbol_order="binary"):
    labels=np.asarray(labels,dtype=int).reshape(-1);order=int(order)
    if order<2 or np.any(labels<0) or np.any(labels>=order):raise ValueError("invalid order or labels")
    idx=np.array([_gray_decode(v) for v in labels]) if symbol_order=="gray" else labels
    phase=np.cumsum(float(phase_rotation)+2*np.pi*idx/order)
    return np.exp(1j*phase)
def dpsk_demodulate(symbols,order,phase_rotation=0.0,symbol_order="binary"):
    y=np.asarray(symbols,dtype=np.complex128).reshape(-1);order=int(order)
    previous=np.concatenate([[1+0j],y[:-1]]);diff=np.angle(y*np.conj(previous))-float(phase_rotation)
    idx=np.mod(np.floor(diff*order/(2*np.pi)+0.5).astype(int),order)
    return np.array([_gray_encode(v) for v in idx]) if symbol_order=="gray" else idx
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("modulate","demodulate"));p.add_argument("--order",required=True,type=int);p.add_argument("--values",required=True);p.add_argument("--phase_rotation",type=float,default=0);p.add_argument("--symbol_order",choices=("binary","gray"),default="binary");a=p.parse_args()
    try:
        if a.mode=="modulate": y=dpsk_modulate([int(v) for v in a.values.split(",")],a.order,a.phase_rotation,a.symbol_order);out={"symbols_real":y.real.tolist(),"symbols_imag":y.imag.tolist()}
        else: raw=json.loads(a.values);y=np.asarray(raw["real"])+1j*np.asarray(raw["imag"]);out={"labels":dpsk_demodulate(y,a.order,a.phase_rotation,a.symbol_order).tolist()}
        print(json.dumps(out))
    except (ValueError,KeyError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
