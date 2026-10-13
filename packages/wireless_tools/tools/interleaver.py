"""Matrix, seeded-random, or explicit-permutation interleaving/deinterleaving."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def permutation(length,kind,rows=None,columns=None,seed=None,indices=None):
    length=int(length)
    if kind=="matrix":
        rows,columns=int(rows),int(columns)
        if rows*columns!=length:raise ValueError("rows*columns must equal data length")
        return np.arange(length).reshape(rows,columns).T.reshape(-1)
    if kind=="random":return np.random.default_rng(seed).permutation(length)
    p=np.asarray(indices,dtype=int)
    if len(p)!=length or sorted(p.tolist())!=list(range(length)):raise ValueError("indices must be a zero-based permutation")
    return p
def interleave(data,perm,direction="interleave"):
    x=np.asarray(data);p=np.asarray(perm,dtype=int)
    if direction=="interleave":return x[p]
    out=np.empty_like(x);out[p]=x;return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--direction",required=True,choices=("interleave","deinterleave"));p.add_argument("--kind",required=True,choices=("matrix","random","explicit"));p.add_argument("--data",required=True);p.add_argument("--rows",type=int);p.add_argument("--columns",type=int);p.add_argument("--seed",type=int);p.add_argument("--indices");a=p.parse_args()
    try:
        data=json.loads(a.data);perm=permutation(len(data),a.kind,a.rows,a.columns,a.seed,[int(v) for v in a.indices.split(",")] if a.indices else None);out=interleave(data,perm,a.direction);print(json.dumps({"data":out.tolist(),"permutation":perm.tolist()}))
    except (ValueError,TypeError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
