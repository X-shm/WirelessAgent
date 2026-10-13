"""Apply one or more frequency offsets to signal columns."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def apply_frequency_offset(signal,sample_rate,offset):
    x=np.asarray(signal,dtype=complex);x=x[:,None] if x.ndim==1 else x;fs=float(sample_rate);off=np.asarray(offset,dtype=float).reshape(-1)
    if fs<=0 or (len(off) not in (1,x.shape[1])):raise ValueError("positive sample_rate and scalar/per-column offset required")
    t=np.arange(x.shape[0])[:,None]/fs;return x*np.exp(2j*np.pi*t*off[None,:])
def main():
    p=argparse.ArgumentParser();p.add_argument("--signal",required=True);p.add_argument("--sample_rate",required=True,type=float);p.add_argument("--offset",required=True);a=p.parse_args()
    try:r=json.loads(a.signal);x=np.asarray(r["real"])+1j*np.asarray(r["imag"]);y=apply_frequency_offset(x,a.sample_rate,[float(v) for v in a.offset.split(",")]);print(json.dumps({"signal_real":y.real.tolist(),"signal_imag":y.imag.tolist()}))
    except (ValueError,KeyError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
