"""LTE secondary synchronization signal, TS 36.211 section 6.11.2."""
from __future__ import annotations
import argparse,json,sys
import numpy as np


def _mseq(kind):
    x=np.zeros(31,dtype=int);x[4]=1
    for n in range(26):
        if kind=="s": x[n+5]=x[n+2]^x[n]
        elif kind=="c": x[n+5]=x[n+3]^x[n]
        else: x[n+5]=x[n+4]^x[n+2]^x[n+1]^x[n]
    return 1-2*x


def lte_sss(ncellid,nsubframe=0):
    ncellid=int(ncellid);nsubframe=int(nsubframe)
    if not 0<=ncellid<=503: raise ValueError("ncellid must be in 0..503")
    if nsubframe not in (0,5):
        if 0<=nsubframe<=9:return np.zeros(0,dtype=int)
        raise ValueError("nsubframe must be in 0..9")
    nid1=ncellid//3;nid2=ncellid%3
    qprime=nid1//30;q=(nid1+qprime*(qprime+1)//2)//30;mprime=nid1+q*(q+1)//2
    m0=mprime%31;m1=(m0+mprime//31+1)%31;n=np.arange(31)
    s,c,z=_mseq("s"),_mseq("c"),_mseq("z")
    s0=s[(n+m0)%31];s1=s[(n+m1)%31];c0=c[(n+nid2)%31];c1=c[(n+nid2+3)%31]
    z0=z[(n+(m0%8))%31];z1=z[(n+(m1%8))%31]
    out=np.empty(62,dtype=int)
    if nsubframe==0: out[0::2]=s0*c0;out[1::2]=s1*c1*z0
    else: out[0::2]=s1*c0;out[1::2]=s0*c1*z1
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument("--ncellid",required=True,type=int);p.add_argument("--nsubframe",type=int,default=0);a=p.parse_args()
    try: print(json.dumps({"ncellid":a.ncellid,"nid1":a.ncellid//3,"nid2":a.ncellid%3,"nsubframe":a.nsubframe,"sequence":lte_sss(a.ncellid,a.nsubframe).tolist()}))
    except ValueError as e: print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
