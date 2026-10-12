"""Stateless bounded 2-D random-walk trajectory generator."""
from __future__ import annotations
import argparse,json,sys
import numpy as np


def random_walk(initial_position,duration,time_step,speed_range=(0.415,1.66),boundary_shape="rectangle",bounds=(0,0,10,10),walk_mode="time",walk_parameter=1,seed=None):
    p=np.asarray(initial_position,dtype=float);duration=float(duration);dt=float(time_step);lo,hi=map(float,speed_range);shape=boundary_shape.lower();bounds=list(map(float,bounds));walk_parameter=float(walk_parameter)
    if p.shape!=(3,) or duration<0 or dt<=0 or lo<=0 or hi<lo or walk_parameter<=0:raise ValueError("invalid trajectory parameters")
    rng=np.random.default_rng(seed);times=np.arange(0,duration+dt/2,dt);positions=[];velocities=[];remaining_segment=0;velocity=np.zeros(3)
    for _t in times:
        positions.append(p.copy());velocities.append(velocity.copy());remaining=dt
        while remaining>1e-12:
            if remaining_segment<=1e-12:
                speed=rng.uniform(lo,hi);angle=rng.uniform(0,2*np.pi);velocity=speed*np.array([np.cos(angle),np.sin(angle),0.]);remaining_segment=walk_parameter if walk_mode=="time" else walk_parameter/speed
            step=min(remaining,remaining_segment);candidate=p+velocity*step
            if shape=="rectangle":
                cx,cy,length,width=bounds;xmin,xmax=cx-length/2,cx+length/2;ymin,ymax=cy-width/2,cy+width/2
                if candidate[0]<xmin or candidate[0]>xmax:velocity[0]*=-1;candidate=p+velocity*step
                if candidate[1]<ymin or candidate[1]>ymax:velocity[1]*=-1;candidate=p+velocity*step
                candidate[0]=np.clip(candidate[0],xmin,xmax);candidate[1]=np.clip(candidate[1],ymin,ymax)
            else:
                cx,cy,radius=bounds;rel=candidate[:2]-[cx,cy]
                if np.linalg.norm(rel)>radius:
                    normal=rel/np.linalg.norm(rel);velocity[:2]-=2*np.dot(velocity[:2],normal)*normal;candidate=p+velocity*step
            p=candidate;remaining-=step;remaining_segment-=step
    return times,np.asarray(positions),np.asarray(velocities)
def _csv(s):return [float(v) for v in s.split(",")]
def main():
    p=argparse.ArgumentParser();p.add_argument("--initial_position",required=True);p.add_argument("--duration",required=True,type=float);p.add_argument("--time_step",type=float,default=1);p.add_argument("--speed_range",default="0.415,1.66");p.add_argument("--boundary_shape",choices=("rectangle","circle"),default="rectangle");p.add_argument("--bounds",default="0,0,10,10");p.add_argument("--walk_mode",choices=("time","distance"),default="time");p.add_argument("--walk_parameter",type=float,default=1);p.add_argument("--seed",type=int);a=p.parse_args()
    try:t,pos,vel=random_walk(_csv(a.initial_position),a.duration,a.time_step,_csv(a.speed_range),a.boundary_shape,_csv(a.bounds),a.walk_mode,a.walk_parameter,a.seed);print(json.dumps({"times":t.tolist(),"positions":pos.tolist(),"velocities":vel.tolist()}))
    except ValueError as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
