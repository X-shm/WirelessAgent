"""Noncoherent M-FSK waveform modulation and demodulation."""
from __future__ import annotations
import argparse,json,math,sys
import numpy as np
from qam_modulation import _gray_decode
def _gray(v):return int(v)^(int(v)>>1)
def _freqs(order,separation):return (np.arange(order)-(order-1)/2)*float(separation)
def fsk_modulate(labels,order,frequency_separation,samples_per_symbol,sample_rate=1.0,phase_continuity="continuous",symbol_order="binary"):
    labels=np.asarray(labels,dtype=int).reshape(-1);order=int(order);n=int(samples_per_symbol);fs=float(sample_rate)
    if order<2 or order&(order-1) or n<=1 or frequency_separation<=0 or fs<=0 or (order-1)*frequency_separation/2>fs/2:raise ValueError("invalid FSK parameters")
    if np.any(labels<0)|np.any(labels>=order):raise ValueError("labels out of range")
    idx=np.array([_gray_decode(v) for v in labels]) if symbol_order=="gray" else labels;freq=_freqs(order,frequency_separation);out=[];phase=0.0
    for value in idx:
        t=np.arange(n)/fs;segment=np.exp(1j*(phase+2*np.pi*freq[value]*t));out.append(segment)
        phase=(phase+2*np.pi*freq[value]*n/fs)%(2*np.pi) if phase_continuity=="continuous" else 0.0
    return np.concatenate(out)
def fsk_demodulate(waveform,order,frequency_separation,samples_per_symbol,sample_rate=1.0,symbol_order="binary"):
    y=np.asarray(waveform,dtype=np.complex128).reshape(-1);n=int(samples_per_symbol);fs=float(sample_rate)
    if len(y)%n:raise ValueError("waveform length must be divisible by samples_per_symbol")
    tones=np.exp(-1j*2*np.pi*np.arange(n)[:,None]*_freqs(order,frequency_separation)[None,:]/fs);blocks=y.reshape(-1,n);idx=np.argmax(np.abs(blocks@tones),axis=1)
    return np.array([_gray(v) for v in idx]) if symbol_order=="gray" else idx
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("modulate","demodulate"));p.add_argument("--order",required=True,type=int);p.add_argument("--values",required=True);p.add_argument("--frequency_separation",required=True,type=float);p.add_argument("--samples_per_symbol",required=True,type=int);p.add_argument("--sample_rate",type=float,default=1);p.add_argument("--phase_continuity",choices=("continuous","discontinuous"),default="continuous");p.add_argument("--symbol_order",choices=("binary","gray"),default="binary");a=p.parse_args()
    try:
        if a.mode=="modulate":y=fsk_modulate([int(v) for v in a.values.split(",")],a.order,a.frequency_separation,a.samples_per_symbol,a.sample_rate,a.phase_continuity,a.symbol_order);out={"waveform_real":y.real.tolist(),"waveform_imag":y.imag.tolist()}
        else:r=json.loads(a.values);y=np.asarray(r["real"])+1j*np.asarray(r["imag"]);out={"labels":fsk_demodulate(y,a.order,a.frequency_separation,a.samples_per_symbol,a.sample_rate,a.symbol_order).tolist()}
        print(json.dumps(out))
    except (ValueError,KeyError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
