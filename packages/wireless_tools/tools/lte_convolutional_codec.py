"""LTE rate-1/3 tail-biting convolutional encoder and hard Viterbi decoder."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
POLYS=(0o133,0o171,0o165)
def _parity(v):return int(v).bit_count()&1
def _transition(state,bit):
    reg=(int(bit)<<6)|state;out=tuple(_parity(reg&p) for p in POLYS);new=((int(bit)<<5)|(state>>1))&0x3F;return new,out
def convolutional_encode(bits):
    b=np.asarray(bits,dtype=int).reshape(-1)
    if len(b)<6 or np.any((b!=0)&(b!=1)):raise ValueError("at least 6 binary input bits required")
    # State bit 5 is the most recent previous input and bit 0 the oldest.
    # Initializing it from the final six information bits makes the trellis
    # terminate in the same state (tail biting).
    state=sum(int(b[-1-i])<<(5-i) for i in range(6));streams=[[],[],[]]
    for bit in b:
        state,out=_transition(state,bit)
        for j,v in enumerate(out):streams[j].append(v)
    return np.concatenate([np.asarray(v,dtype=int) for v in streams])
def convolutional_decode(coded):
    c=np.asarray(coded,dtype=int).reshape(-1)
    if len(c)%3 or np.any((c!=0)&(c!=1)):raise ValueError("coded input must contain three binary streams")
    n=len(c)//3;rx=np.stack([c[:n],c[n:2*n],c[2*n:]],axis=1);best_metric=10**18;best=None
    for initial in range(64):
        metrics=np.full(64,10**9,dtype=int);metrics[initial]=0;paths=np.zeros((n,64),dtype=np.int8);prevs=np.zeros((n,64),dtype=np.int8)
        for i in range(n):
            nxt=np.full(64,10**9,dtype=int)
            for state in range(64):
                if metrics[state]>=10**9:continue
                for bit in (0,1):
                    ns,out=_transition(state,bit);metric=metrics[state]+sum(int(out[j])!=int(rx[i,j]) for j in range(3))
                    if metric<nxt[ns]:nxt[ns]=metric;paths[i,ns]=bit;prevs[i,ns]=state
            metrics=nxt
        metric=metrics[initial]
        if metric<best_metric:
            bits=np.zeros(n,dtype=int);state=initial
            for i in range(n-1,-1,-1):bits[i]=paths[i,state];state=int(prevs[i,state])
            best_metric=metric;best=bits
    return best,int(best_metric)
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("encode","decode"));p.add_argument("--bits",required=True);a=p.parse_args()
    try:
        b=[int(v) for v in a.bits.split(",")]
        if a.mode=="encode":out={"coded_bits":convolutional_encode(b).tolist()}
        else:d,m=convolutional_decode(b);out={"decoded_bits":d.tolist(),"path_metric":m}
        print(json.dumps(out))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
