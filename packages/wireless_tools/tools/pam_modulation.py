"""M-PAM modulation and hard-decision demodulation."""
from __future__ import annotations
import argparse,json,math,sys
import numpy as np
from qam_modulation import _gray_decode,_labels


def pam_table(order,symbol_order="gray",unit_average_power=False):
    order=int(order); width=int(math.log2(order))
    if order<2 or 2**width!=order: raise ValueError("order must be a power of two")
    idx=np.array([_gray_decode(v) for v in range(order)]) if symbol_order=="gray" else np.arange(order)
    table=2*idx-order+1
    return table/math.sqrt((order**2-1)/3) if unit_average_power else table.astype(float)
def pam_modulate(values,order,input_type="bits",symbol_order="gray",unit_average_power=False):
    width=int(math.log2(order)); table=pam_table(order,symbol_order,unit_average_power)
    if input_type=="bits":
        bits=np.asarray(values,dtype=int).reshape(-1)
        if np.any((bits!=0)&(bits!=1)) or len(bits)%width: raise ValueError("invalid bit vector length")
        labels=np.array([sum(int(b)<<(width-1-j) for j,b in enumerate(r)) for r in bits.reshape(-1,width)])
    else: labels=np.asarray(values,dtype=int).reshape(-1)
    if np.any(labels<0) or np.any(labels>=order): raise ValueError("symbol labels out of range")
    return table[labels],labels
def pam_demodulate(values,order,output_type="bits",symbol_order="gray",unit_average_power=False):
    table=pam_table(order,symbol_order,unit_average_power); labels=np.argmin(abs(np.asarray(values)[:,None]-table[None,:]),axis=1)
    return _labels(labels,int(math.log2(order))).reshape(-1) if output_type=="bits" else labels
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("modulate","demodulate"));p.add_argument("--order",required=True,type=int);p.add_argument("--values",required=True)
    p.add_argument("--input_type",choices=("bits","symbols"),default="bits");p.add_argument("--output_type",choices=("bits","symbols"),default="bits");p.add_argument("--symbol_order",choices=("gray","binary"),default="gray");p.add_argument("--unit_average_power",action="store_true");a=p.parse_args()
    try:
        vals=[float(v) if a.mode=="demodulate" else int(v) for v in a.values.split(",")]
        if a.mode=="modulate": out,labels=pam_modulate(vals,a.order,a.input_type,a.symbol_order,a.unit_average_power);result={"labels":labels.tolist(),"symbols":out.tolist()}
        else: out=pam_demodulate(vals,a.order,a.output_type,a.symbol_order,a.unit_average_power);result={"output_type":a.output_type,"values":out.tolist()}
        print(json.dumps(result))
    except ValueError as e: print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
