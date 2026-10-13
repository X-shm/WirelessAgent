"""Group bits into integers or expand integers into fixed-width bits."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def bit_to_int(bits,width,bit_order="msbfirst"):
    bits=np.asarray(bits,dtype=int).reshape(-1);width=int(width)
    if width<=0 or len(bits)%width or np.any((bits!=0)&(bits!=1)): raise ValueError("invalid bits or width")
    groups=bits.reshape(-1,width); shifts=np.arange(width-1,-1,-1) if bit_order=="msbfirst" else np.arange(width)
    return np.sum(groups*(1<<shifts),axis=1).astype(int)
def int_to_bit(values,width,bit_order="msbfirst"):
    values=np.asarray(values,dtype=int).reshape(-1);width=int(width)
    if width<=0 or np.any(values<0) or np.any(values>=2**width): raise ValueError("integer outside selected width")
    shifts=np.arange(width-1,-1,-1) if bit_order=="msbfirst" else np.arange(width)
    return ((values[:,None]>>shifts)&1).reshape(-1)
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("bit_to_int","int_to_bit"));p.add_argument("--values",required=True);p.add_argument("--width",required=True,type=int);p.add_argument("--bit_order",choices=("msbfirst","lsbfirst"),default="msbfirst");a=p.parse_args()
    try:
        vals=[int(v) for v in a.values.split(",")];out=bit_to_int(vals,a.width,a.bit_order) if a.mode=="bit_to_int" else int_to_bit(vals,a.width,a.bit_order);print(json.dumps({"mode":a.mode,"values":out.tolist()}))
    except ValueError as e: print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
