"""White Gaussian noise generator compatible with wgn power conventions."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def wgn(rows,columns,power,impedance=1.0,power_type="dbw",output_type="real",seed=None):
    rows,columns=int(rows),int(columns);impedance=float(impedance);p=float(power);mode=power_type.lower()
    if rows<=0 or columns<=0 or impedance<=0:raise ValueError("positive dimensions and impedance required")
    watts=10**(p/10) if mode=="dbw" else 10**((p-30)/10) if mode=="dbm" else p
    if watts<0:raise ValueError("linear power must be nonnegative")
    voltage_power=watts*impedance;rng=np.random.default_rng(seed)
    if output_type=="complex":y=np.sqrt(voltage_power/2)*(rng.standard_normal((rows,columns))+1j*rng.standard_normal((rows,columns)))
    else:y=np.sqrt(voltage_power)*rng.standard_normal((rows,columns))
    return y
def main():
    p=argparse.ArgumentParser();p.add_argument("--rows",required=True,type=int);p.add_argument("--columns",required=True,type=int);p.add_argument("--power",required=True,type=float);p.add_argument("--impedance",type=float,default=1);p.add_argument("--power_type",choices=("dbw","dbm","linear"),default="dbw");p.add_argument("--output_type",choices=("real","complex"),default="real");p.add_argument("--seed",type=int);a=p.parse_args()
    try:y=wgn(a.rows,a.columns,a.power,a.impedance,a.power_type,a.output_type,a.seed);print(json.dumps({"noise_real":y.real.tolist(),"noise_imag":y.imag.tolist()}))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
