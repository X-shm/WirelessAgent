"""LTE convolutional sub-block interleaving, rate matching, and soft recovery."""
from __future__ import annotations
import argparse,json,math,sys
import numpy as np
P=np.array([1,17,9,25,5,21,13,29,3,19,11,27,7,23,15,31,0,16,8,24,4,20,12,28,2,18,10,26,6,22,14,30])
def _interleave(stream,third=False):
    d=np.asarray(stream,dtype=int);r=math.ceil(len(d)/32);k=r*32;padded=np.concatenate([np.full(k-len(d),-1,dtype=int),d])
    if third:return np.array([padded[(P[j//r]+32*(j%r)+1)%k] for j in range(k)],dtype=int)
    matrix=padded.reshape(r,32);return np.concatenate([matrix[:,col] for col in P])
def rate_match_indices(input_length,output_length):
    n=int(input_length)
    if n%3:raise ValueError("input_length must contain three equal streams")
    d=n//3;streams=[]
    for i in range(3):streams.append(_interleave(np.arange(i*d,(i+1)*d)))
    w=np.concatenate(streams)
    valid=w[w>=0]
    if len(valid)==0:return np.zeros(0,dtype=int)
    return np.resize(valid,int(output_length))
def rate_match(values,output_length):
    x=np.asarray(values);return x[rate_match_indices(len(x),output_length)]
def rate_recover(values,output_length):
    y=np.asarray(values);idx=rate_match_indices(int(output_length),len(y));out=np.zeros(int(output_length),dtype=y.dtype)
    np.add.at(out,idx,y);return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("match","recover"));p.add_argument("--values",required=True);p.add_argument("--output_length",required=True,type=int);a=p.parse_args()
    try:
        values=np.asarray(json.loads(a.values));out=rate_match(values,a.output_length) if a.mode=="match" else rate_recover(values,a.output_length);print(json.dumps({"values":out.tolist()}))
    except (ValueError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
