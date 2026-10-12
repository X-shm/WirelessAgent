"""LTE turbo-code block segmentation/desegmentation, TS 36.212 5.1.2."""
from __future__ import annotations
import argparse,json,math,sys
import numpy as np
from lte_crc import crc_encode,crc_verify

LEGAL_SIZES=list(range(40,513,8))+list(range(528,1025,16))+list(range(1056,2049,32))+list(range(2112,6145,64))
def _parameters(length):
    b=int(length);l=0 if b<=6144 else 24;c=1 if l==0 else math.ceil(b/(6144-l));bp=b+c*l
    kplus=next(k for k in LEGAL_SIZES if k>=math.ceil(bp/c))
    if c==1:kminus=0;cminus=0
    else:
        kminus=LEGAL_SIZES[LEGAL_SIZES.index(kplus)-1];cminus=(c*kplus-bp)//(kplus-kminus)
    cplus=c-cminus;f=cplus*kplus+cminus*kminus-bp
    return {"C":c,"L":l,"Kplus":kplus,"Kminus":kminus,"Cplus":cplus,"Cminus":cminus,"F":f}
def segment(bits):
    bits=np.asarray(bits,dtype=int).reshape(-1)
    if np.any((bits!=0)&(bits!=1)) or len(bits)==0:raise ValueError("nonempty binary block required")
    p=_parameters(len(bits));blocks=[];pos=0
    for r in range(p["C"]):
        k=p["Kminus"] if r<p["Cminus"] else p["Kplus"];payload=k-p["L"];fill=p["F"] if r==0 else 0;take=payload-fill
        data=np.concatenate([np.full(fill,-1,dtype=int),bits[pos:pos+take]]);pos+=take
        blocks.append(crc_encode(data,"24B") if p["L"] else data)
    if pos!=len(bits):raise RuntimeError("segmentation length mismatch")
    return blocks,p
def desegment(blocks,block_length=None):
    arrays=[np.asarray(v,dtype=int).reshape(-1) for v in blocks]
    if not arrays:raise ValueError("at least one code block required")
    errors=[];payload=[]
    if len(arrays)>1:
        for block in arrays:
            valid,data=crc_verify(block,"24B");errors.append(not valid);payload.append(data)
    else:payload=arrays
    joined=np.concatenate(payload);filler=0
    if block_length is not None:
        length=int(block_length);filler=len(joined)-length
        if filler<0:raise ValueError("block_length exceeds recovered payload")
        joined=joined[filler:]
    return joined,errors,filler
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("segment","desegment"));p.add_argument("--data",required=True,help="comma bits or JSON block list");p.add_argument("--block_length",type=int);a=p.parse_args()
    try:
        if a.mode=="segment":blocks,params=segment([int(v) for v in a.data.split(",")]);out={"blocks":[v.tolist() for v in blocks],"parameters":params}
        else:bits,errors,filler=desegment(json.loads(a.data),a.block_length);out={"bits":bits.tolist(),"crc_errors":errors,"filler_removed":filler}
        print(json.dumps(out))
    except (ValueError,StopIteration,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
