"""Stateless random-waypoint trajectory generator."""
from __future__ import annotations
import argparse,json,sys
import numpy as np


def _point(rng,shape,bounds,z):
    if shape=="rectangle":
        cx,cy,length,width=bounds;return np.array([cx+(rng.random()-.5)*length,cy+(rng.random()-.5)*width,z])
    cx,cy,radius=bounds;r=radius*np.sqrt(rng.random());theta=2*np.pi*rng.random();return np.array([cx+r*np.cos(theta),cy+r*np.sin(theta),z])
def random_waypoint(initial_position,duration,time_step,speed_range=(0.415,1.66),pause_duration=0,boundary_shape="rectangle",bounds=(0,0,10,10),seed=None):
    p=np.asarray(initial_position,dtype=float);duration=float(duration);dt=float(time_step);lo,hi=map(float,speed_range);shape=boundary_shape.lower();bounds=list(map(float,bounds))
    if p.shape!=(3,) or duration<0 or dt<=0 or lo<=0 or hi<lo or pause_duration<0:raise ValueError("invalid trajectory parameters")
    if (shape=="rectangle" and (len(bounds)!=4 or min(bounds[2:])<=0)) or (shape=="circle" and (len(bounds)!=3 or bounds[2]<=0)):raise ValueError("invalid bounds")
    rng=np.random.default_rng(seed);times=np.arange(0,duration+dt/2,dt);positions=[];velocities=[];target=None;pause=0.0;velocity=np.zeros(3)
    for _t in times:
        positions.append(p.copy());velocities.append(velocity.copy())
        remaining=dt
        while remaining>1e-12:
            if pause>0:step=min(remaining,pause);pause-=step;remaining-=step;velocity=np.zeros(3);continue
            if target is None:
                target=_point(rng,shape,bounds,p[2]);delta=target-p;dist=np.linalg.norm(delta[:2]);speed=rng.uniform(lo,hi);velocity=delta/dist*speed if dist>1e-12 else np.zeros(3)
            dist=np.linalg.norm((target-p)[:2]);travel=np.linalg.norm(velocity[:2])*remaining
            if travel+1e-12>=dist:
                used=dist/max(np.linalg.norm(velocity[:2]),1e-12);p=target;remaining-=used;target=None;pause=float(pause_duration);velocity=np.zeros(3)
            else:p=p+velocity*remaining;remaining=0
    return times,np.asarray(positions),np.asarray(velocities)
def _csv(s):return [float(v) for v in s.split(",")]
def main():
    p=argparse.ArgumentParser();p.add_argument("--initial_position",required=True);p.add_argument("--duration",required=True,type=float);p.add_argument("--time_step",type=float,default=1);p.add_argument("--speed_range",default="0.415,1.66");p.add_argument("--pause_duration",type=float,default=0);p.add_argument("--boundary_shape",choices=("rectangle","circle"),default="rectangle");p.add_argument("--bounds",default="0,0,10,10");p.add_argument("--seed",type=int);a=p.parse_args()
    try:t,pos,vel=random_waypoint(_csv(a.initial_position),a.duration,a.time_step,_csv(a.speed_range),a.pause_duration,a.boundary_shape,_csv(a.bounds),a.seed);print(json.dumps({"times":t.tolist(),"positions":pos.tolist(),"velocities":vel.tolist()}))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
