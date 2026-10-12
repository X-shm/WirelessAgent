"""Binary symmetric channel."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def bsc(data,probability,seed=None):
    x=np.asarray(data,dtype=int);p=float(probability)
    if np.any((x!=0)&(x!=1)) or not 0<=p<=1:raise ValueError("binary data and probability 0..1 required")
    err=(np.random.default_rng(seed).random(x.shape)<p).astype(int);return x^err,err
def main():
    p=argparse.ArgumentParser();p.add_argument("--data",required=True);p.add_argument("--probability",required=True,type=float);p.add_argument("--seed",type=int);a=p.parse_args()
    try:y,e=bsc(json.loads(a.data),a.probability,a.seed);print(json.dumps({"output":y.tolist(),"errors":e.tolist(),"observed_probability":float(e.mean())}))
    except (ValueError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
