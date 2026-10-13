"""Systematic-position binary Hamming (2^m-1, 2^m-m-1) codec."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def dimensions(m):m=int(m);return 2**m-1,2**m-m-1
def encode_block(message,m):
    n,k=dimensions(m);msg=np.asarray(message,dtype=int)
    if len(msg)!=k or np.any((msg!=0)&(msg!=1)):raise ValueError(f"message must contain {k} bits")
    code=np.zeros(n+1,dtype=int);j=0
    for pos in range(1,n+1):
        if pos&(pos-1):code[pos]=msg[j];j+=1
    for bit in range(m):
        p=1<<bit;code[p]=np.bitwise_xor.reduce([code[pos] for pos in range(1,n+1) if pos&p and pos!=p],initial=0)
    return code[1:]
def decode_block(received,m):
    n,k=dimensions(m);code=np.asarray(received,dtype=int).copy()
    if len(code)!=n or np.any((code!=0)&(code!=1)):raise ValueError(f"codeword must contain {n} bits")
    syndrome=0
    for bit in range(m):
        p=1<<bit
        if np.bitwise_xor.reduce([code[pos-1] for pos in range(1,n+1) if pos&p],initial=0):syndrome|=p
    corrected=code.copy()
    if 1<=syndrome<=n:corrected[syndrome-1]^=1
    message=np.array([corrected[pos-1] for pos in range(1,n+1) if pos&(pos-1)],dtype=int)
    return message,corrected,syndrome
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("encode","decode"));p.add_argument("--m",required=True,type=int);p.add_argument("--bits",required=True);a=p.parse_args()
    try:
        bits=[int(v) for v in a.bits.split(",")]
        if a.mode=="encode":out={"codeword":encode_block(bits,a.m).tolist()}
        else:msg,corrected,syndrome=decode_block(bits,a.m);out={"message":msg.tolist(),"corrected_codeword":corrected.tolist(),"syndrome":syndrome,"corrected":bool(syndrome)}
        print(json.dumps(out))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
