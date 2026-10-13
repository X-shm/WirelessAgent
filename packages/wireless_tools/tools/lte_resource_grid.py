"""LTE downlink/uplink resource-grid sizing and zero-grid creation."""
from __future__ import annotations
import argparse,json,sys
def resource_grid_size(link,nrb,cyclic_prefix="Normal",ports=1):
    link=link.lower();nrb=int(nrb);ports=int(ports);cp=cyclic_prefix.lower()
    if link not in ("downlink","uplink") or not 1<=nrb<=110 or ports<=0 or cp not in ("normal","extended"):raise ValueError("invalid grid parameters")
    return [12*nrb,14 if cp=="normal" else 12,ports]
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("size","create"));p.add_argument("--link",required=True,choices=("downlink","uplink"));p.add_argument("--nrb",required=True,type=int);p.add_argument("--cyclic_prefix",choices=("Normal","Extended"),default="Normal");p.add_argument("--ports",type=int,default=1);a=p.parse_args()
    try:
        size=resource_grid_size(a.link,a.nrb,a.cyclic_prefix,a.ports);out={"size":size}
        if a.mode=="create":out["grid"]={"shape":size,"fill_real":0.0,"fill_imag":0.0}
        print(json.dumps(out))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
