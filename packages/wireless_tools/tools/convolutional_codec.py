"""Configurable rate-1/N convolutional encoder and hard Viterbi decoder."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def _generators(text):return [int(v,8) for v in text.split(",")]
def _transition(state,bit,k,gens):
    reg=(int(bit)<<(k-1))|state;out=[(reg&g).bit_count()&1 for g in gens];return ((int(bit)<<(k-2))|(state>>1))&((1<<(k-1))-1),out
def encode(bits,constraint_length,generators,initial_state=0,puncture=None):
    bits=np.asarray(bits,dtype=int);k=int(constraint_length);gens=list(generators);state=int(initial_state);coded=[]
    if np.any((bits!=0)&(bits!=1)) or k<2 or any(g>=1<<k for g in gens):raise ValueError("invalid code parameters")
    for bit in bits:state,out=_transition(state,bit,k,gens);coded.extend(out)
    if puncture:
        pattern=np.asarray(puncture,dtype=int);coded=np.asarray(coded);coded=coded[np.resize(pattern,len(coded)).astype(bool)]
    return np.asarray(coded,dtype=int),state
def decode_hard(coded,constraint_length,generators,final_state=None):
    c=np.asarray(coded,dtype=int);k=int(constraint_length);gens=list(generators);n=len(gens)
    if len(c)%n:raise ValueError("coded length must be divisible by number of generators")
    rx=c.reshape(-1,n);states=1<<(k-1);metric=np.full(states,10**9,dtype=int);metric[0]=0;prev=np.zeros((len(rx),states),int);choice=np.zeros((len(rx),states),int)
    for t,row in enumerate(rx):
        nxt=np.full(states,10**9,dtype=int)
        for s in range(states):
            if metric[s]>=10**9:continue
            for bit in (0,1):
                ns,out=_transition(s,bit,k,gens);m=metric[s]+sum(int(a)!=int(b) for a,b in zip(out,row))
                if m<nxt[ns]:nxt[ns]=m;prev[t,ns]=s;choice[t,ns]=bit
        metric=nxt
    state=int(np.argmin(metric)) if final_state is None else int(final_state);bits=np.zeros(len(rx),int);best=int(metric[state])
    for t in range(len(rx)-1,-1,-1):bits[t]=choice[t,state];state=prev[t,state]
    return bits,best
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("encode","decode"));p.add_argument("--bits",required=True);p.add_argument("--constraint_length",required=True,type=int);p.add_argument("--generators",required=True,help="octal comma list");p.add_argument("--initial_state",type=int,default=0);p.add_argument("--final_state",type=int);p.add_argument("--puncture");a=p.parse_args()
    try:
        bits=[int(v) for v in a.bits.split(",")];gens=_generators(a.generators)
        if a.mode=="encode":out,state=encode(bits,a.constraint_length,gens,a.initial_state,[int(v) for v in a.puncture.split(",")] if a.puncture else None);result={"coded_bits":out.tolist(),"final_state":state}
        else:out,metric=decode_hard(bits,a.constraint_length,gens,a.final_state);result={"decoded_bits":out.tolist(),"path_metric":metric}
        print(json.dumps(result))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
