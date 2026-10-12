"""LTE layer mapping/demapping for one or two codewords."""
from __future__ import annotations
import argparse,json,sys
import numpy as np


def _complex(obj): return np.asarray(obj["real"],dtype=float)+1j*np.asarray(obj["imag"],dtype=float)
def _json(a): return {"real":np.real(a).tolist(),"imag":np.imag(a).tolist()}
def _alloc(nlayers,ncw):
    if not 1<=nlayers<=8 or ncw not in (1,2): raise ValueError("nlayers 1..8 and one/two codewords supported")
    if ncw==1:return [nlayers]
    if nlayers<2:raise ValueError("two codewords require at least two layers")
    return [nlayers//2,nlayers-nlayers//2]
def layer_map(codewords,nlayers):
    alloc=_alloc(int(nlayers),len(codewords));mapped=[]
    for cw,layers in zip(codewords,alloc):
        cw=np.asarray(cw,dtype=np.complex128).reshape(-1)
        if len(cw)%layers:raise ValueError("codeword length must be divisible by allocated layers")
        mapped.append(cw.reshape(-1,layers))
    if len({part.shape[0] for part in mapped})!=1:raise ValueError("mapped codewords must yield equal symbols per layer")
    return np.concatenate(mapped,axis=1)
def layer_demap(layers,ncodewords):
    layers=np.asarray(layers,dtype=np.complex128)
    if layers.ndim!=2:raise ValueError("layers must be a matrix")
    alloc=_alloc(layers.shape[1],int(ncodewords));out=[];offset=0
    for count in alloc:out.append(layers[:,offset:offset+count].reshape(-1));offset+=count
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("map","demap"));p.add_argument("--data",required=True,help="JSON codeword list or layer object");p.add_argument("--nlayers",type=int);p.add_argument("--ncodewords",type=int,default=1);a=p.parse_args()
    try:
        raw=json.loads(a.data)
        if a.mode=="map":
            if a.nlayers is None:raise ValueError("map mode requires --nlayers")
            codewords=[_complex(v) for v in raw];result={"layers":_json(layer_map(codewords,a.nlayers))}
        else: result={"codewords":[_json(v) for v in layer_demap(_complex(raw),a.ncodewords)]}
        print(json.dumps(result))
    except (ValueError,KeyError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
