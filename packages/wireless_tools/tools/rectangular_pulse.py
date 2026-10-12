"""Rectangular pulse shaping by sample repetition, corresponding to rectpulse."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def rectangular_pulse(values,samples_per_symbol):
    n=int(samples_per_symbol)
    if n<=0:raise ValueError("samples_per_symbol must be positive")
    return np.repeat(np.asarray(values),n,axis=0)
def main():
    p=argparse.ArgumentParser();p.add_argument("--values",required=True,help="JSON array");p.add_argument("--samples_per_symbol",required=True,type=int);a=p.parse_args()
    try:print(json.dumps({"samples":rectangular_pulse(json.loads(a.values),a.samples_per_symbol).tolist()}))
    except (ValueError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
