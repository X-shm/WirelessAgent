"""Create and validate a JSON-safe wirelessPacket structure."""
from __future__ import annotations
import argparse,json,sys


def wireless_packet(**values):
    packet={"TechnologyType":0,"TransmitterID":None,"TransmitterPosition":None,"TransmitterVelocity":[0,0,0],"NumTransmitAntennas":None,"StartTime":None,"Duration":None,"Power":None,"CenterFrequency":None,"Bandwidth":None,"Abstraction":False,"SampleRate":None,"DirectToDestination":0,"Data":[],"Metadata":{"Channel":{"PathGains":[],"PathDelays":[],"PathFilters":[],"SampleTimes":[]}},"Tags":[]}
    packet.update({k:v for k,v in values.items() if v is not None})
    if packet["TransmitterID"] is not None and int(packet["TransmitterID"])<=0:raise ValueError("TransmitterID must be positive")
    for key in ("TransmitterPosition","TransmitterVelocity"):
        if packet[key] is not None and len(packet[key])!=3:raise ValueError(f"{key} must have 3 values")
    for key in ("Duration","Bandwidth","CenterFrequency","SampleRate"):
        if packet[key] is not None and float(packet[key])<0:raise ValueError(f"{key} must be nonnegative")
    return packet
def main():
    p=argparse.ArgumentParser();p.add_argument("--technology_type",type=int,default=0);p.add_argument("--transmitter_id",type=int);p.add_argument("--transmitter_position");p.add_argument("--transmitter_velocity",default="0,0,0");p.add_argument("--num_transmit_antennas",type=int);p.add_argument("--start_time",type=float);p.add_argument("--duration",type=float);p.add_argument("--power",type=float);p.add_argument("--center_frequency",type=float);p.add_argument("--bandwidth",type=float);p.add_argument("--abstraction",action="store_true");p.add_argument("--sample_rate",type=float);p.add_argument("--direct_to_destination",type=int,default=0);p.add_argument("--data",default="[]");p.add_argument("--metadata");p.add_argument("--tags",default="[]");a=p.parse_args()
    cv=lambda s:None if s is None else [float(v) for v in s.split(",")]
    try:
        packet=wireless_packet(TechnologyType=a.technology_type,TransmitterID=a.transmitter_id,TransmitterPosition=cv(a.transmitter_position),TransmitterVelocity=cv(a.transmitter_velocity),NumTransmitAntennas=a.num_transmit_antennas,StartTime=a.start_time,Duration=a.duration,Power=a.power,CenterFrequency=a.center_frequency,Bandwidth=a.bandwidth,Abstraction=a.abstraction,SampleRate=a.sample_rate,DirectToDestination=a.direct_to_destination,Data=json.loads(a.data),Metadata=json.loads(a.metadata) if a.metadata else None,Tags=json.loads(a.tags));print(json.dumps(packet,ensure_ascii=False))
    except (ValueError,json.JSONDecodeError) as e:print(json.dumps({"error":str(e)},ensure_ascii=False));sys.exit(1)
if __name__=="__main__":main()
