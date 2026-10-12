"""Generic OFDM modulation/demodulation with null and pilot carriers."""
from __future__ import annotations
import argparse,json,sys
import numpy as np
def _complex(v):return np.asarray(v["real"],dtype=float)+1j*np.asarray(v["imag"],dtype=float)
def _out(v):return {"real":np.real(v).tolist(),"imag":np.imag(v).tolist()}
def _cp(cp,n):
    vals=[int(v) for v in (cp if isinstance(cp,(list,tuple)) else [cp])];return vals*n if len(vals)==1 else vals
def ofdm_modulate(data,nfft,cp_length,null_indices=(),pilot_indices=(),pilots=None):
    data=np.asarray(data,dtype=np.complex128);data=data[:,None] if data.ndim==1 else data;nfft=int(nfft);nsym=data.shape[1];cp=_cp(cp_length,nsym)
    if len(cp)!=nsym or any(v<0 or v>nfft for v in cp):raise ValueError("invalid cyclic prefix lengths")
    null={int(v)-1 for v in null_indices};pilot={int(v)-1 for v in pilot_indices};active=[i for i in range(nfft) if i not in null and i not in pilot]
    if data.shape[0]!=len(active):raise ValueError(f"data rows must equal {len(active)} active carriers")
    grid=np.zeros((nfft,nsym),complex);grid[active,:]=data
    if pilot:
        p=np.asarray(pilots,dtype=complex);p=p[:,None] if p.ndim==1 else p
        if p.shape!=(len(pilot),nsym):raise ValueError("pilot shape mismatch")
        grid[sorted(pilot),:]=p
    parts=[]
    for s in range(nsym):
        time=np.fft.ifft(np.fft.ifftshift(grid[:,s]));parts.append(np.concatenate([time[-cp[s]:] if cp[s] else [],time]))
    return np.concatenate(parts)
def ofdm_demodulate(waveform,nfft,cp_length,symbol_offset=None,null_indices=(),pilot_indices=()):
    y=np.asarray(waveform,dtype=complex).reshape(-1);nfft=int(nfft);cp0=[int(v) for v in (cp_length if isinstance(cp_length,(list,tuple)) else [cp_length])]
    if len(cp0)==1:
        size=nfft+cp0[0]
        if len(y)%size:raise ValueError("waveform length mismatch")
        cp=cp0*(len(y)//size)
    else:cp=cp0
    offsets=_cp(cp if symbol_offset is None else symbol_offset,len(cp));grids=[];pos=0
    for c,o in zip(cp,offsets):
        if not 0<=o<=c:raise ValueError("symbol_offset must lie in cyclic prefix")
        segment=y[pos+o:pos+o+nfft];grids.append(np.fft.fftshift(np.fft.fft(segment))*np.exp(-2j*np.pi*np.arange(-nfft//2,nfft-nfft//2)*(c-o)/nfft));pos+=nfft+c
    grid=np.stack(grids,axis=1);null={int(v)-1 for v in null_indices};pilot={int(v)-1 for v in pilot_indices};data=[i for i in range(nfft) if i not in null and i not in pilot]
    return grid[data,:],grid[sorted(pilot),:] if pilot else np.zeros((0,len(cp)),complex)
def _ints(s):return [] if not s else [int(v) for v in s.split(",")]
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=("modulate","demodulate"));p.add_argument("--data",required=True);p.add_argument("--nfft",required=True,type=int);p.add_argument("--cp_length",required=True);p.add_argument("--symbol_offset");p.add_argument("--null_indices",default="");p.add_argument("--pilot_indices",default="");p.add_argument("--pilots");a=p.parse_args()
    try:
        cp=_ints(a.cp_length);cp=cp[0] if len(cp)==1 else cp;null=_ints(a.null_indices);pilot=_ints(a.pilot_indices)
        if a.mode=="modulate":y=ofdm_modulate(_complex(json.loads(a.data)),a.nfft,cp,null,pilot,_complex(json.loads(a.pilots)) if a.pilots else None);out={"waveform":_out(y)}
        else:data,pil=ofdm_demodulate(_complex(json.loads(a.data)),a.nfft,cp,_ints(a.symbol_offset) if a.symbol_offset else None,null,pilot);out={"data":_out(data),"pilots":_out(pil)}
        print(json.dumps(out))
    except (ValueError,KeyError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
