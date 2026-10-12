"""Estimate BLE AoA/AoD with the BLE MUSIC angle estimator."""
from __future__ import annotations
import numpy as np
from _bluetooth_common import InputError, complex_from_json, run_cli


ANGLE_DEFAULTS = {"array_size": 4, "element_spacing": 0.5,
                  "enable_custom_array": False, "element_position": None,
                  "slot_duration": 2, "switching_pattern": None}


def angle_configuration(properties: dict | None = None) -> dict:
    """Construct the JSON equivalent of ``bleAngleEstimateConfig``.

    Element positions use the MATLAB convention: three coordinate rows, one
    column per antenna.  With ``enable_custom_array=false`` the derived ULA
    positions are returned and callers need only supply ArraySize/spacing.
    """
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be a JSON object")
    unknown = set(properties) - set(ANGLE_DEFAULTS)
    if unknown:
        raise InputError("unsupported angle configuration fields: " + ", ".join(sorted(unknown)))
    cfg = {**ANGLE_DEFAULTS, **properties}
    if not isinstance(cfg["array_size"], int) or isinstance(cfg["array_size"], bool) or not 2 <= cfg["array_size"] <= 128:
        raise InputError("array_size must be an integer in 2..128")
    if isinstance(cfg["element_spacing"], bool) or not isinstance(cfg["element_spacing"], (int, float)) or not np.isfinite(cfg["element_spacing"]) or cfg["element_spacing"] <= 0:
        raise InputError("element_spacing must be a positive finite number")
    cfg["element_spacing"] = float(cfg["element_spacing"])
    if not isinstance(cfg["enable_custom_array"], bool):
        raise InputError("enable_custom_array must be boolean")
    if not isinstance(cfg["slot_duration"], int) or isinstance(cfg["slot_duration"], bool) or cfg["slot_duration"] not in (1, 2):
        raise InputError("slot_duration must be 1 or 2")
    position = cfg["element_position"]
    if cfg["enable_custom_array"]:
        try:
            position = np.asarray(position, dtype=float)
        except (TypeError, ValueError) as exc:
            raise InputError("element_position must be a 3-by-N numeric matrix") from exc
        if position.ndim != 2 or position.shape[0] != 3 or position.shape[1] < 2 or position.shape[1] > 128 or not np.isfinite(position).all():
            raise InputError("element_position must be a finite 3-by-N matrix with 2..128 elements")
        cfg["element_position"] = position.tolist()
        cfg["array_size"] = int(position.shape[1])
    else:
        cfg["element_position"] = [[0.0] * cfg["array_size"],
                                   [cfg["element_spacing"] * index for index in range(cfg["array_size"])],
                                   [0.0] * cfg["array_size"]]
    pattern = list(range(1, cfg["array_size"] + 1)) if cfg["switching_pattern"] is None else cfg["switching_pattern"]
    if not isinstance(pattern, list) or not pattern or pattern[0] != 1 or any(not isinstance(item, int) or isinstance(item, bool) or not 1 <= item <= cfg["array_size"] for item in pattern):
        raise InputError("switching_pattern must begin with 1 and contain valid antenna indices")
    cfg["switching_pattern"] = pattern
    return cfg

def estimate(iq, *, array_size=4, element_spacing=0.5, slot_duration=2, switching_pattern=None):
    iq=np.asarray(iq,complex).reshape(-1)
    if not isinstance(array_size,int) or array_size<2: raise InputError("array_size must be an integer >= 2")
    if not isinstance(slot_duration,int) or slot_duration not in (1,2): raise InputError("slot_duration must be 1 or 2")
    if not isinstance(element_spacing,(int,float)) or element_spacing<=0: raise InputError("element_spacing must be positive")
    pattern=list(range(1,array_size+1)) if switching_pattern is None else switching_pattern
    if not isinstance(pattern,list) or not pattern or pattern[0]!=1 or any(not isinstance(x,int) or x<1 or x>array_size for x in pattern): raise InputError("switching_pattern must begin with 1 and contain valid antenna indices")
    if iq.size<8+array_size-1: raise InputError("iq_samples is too short for array_size")
    expected=iq.size-7; switches=(pattern*((expected+len(pattern)-1)//len(pattern)))[:expected]
    phase=np.unwrap(np.angle(iq[:8])); ph_diff=1 if np.mean(np.abs(np.diff(phase))/(2*np.pi))*1e6<375e3 else 2
    reference=np.mean(iq[:8]*np.exp(-1j*np.arange(8)*ph_diff*np.pi/2))*np.exp(1j*(phase[7]-phase[0]))
    data=np.concatenate(([reference],iq[8:]))*np.exp(-1j*np.arange(expected)*slot_duration*np.pi*ph_diff)
    ordered=np.zeros(array_size,complex)
    for antenna in range(1,array_size+1): ordered[antenna-1]=np.mean(data[np.asarray(switches)==antenna])
    u=np.linalg.svd(ordered.reshape(-1,1),full_matrices=True)[0]; noise=u[:,1:]
    scan=np.arange(-90,90.0001,.1); positions=np.arange(array_size)*float(element_spacing)
    steering=np.exp(-1j*2*np.pi*np.outer(np.sin(np.deg2rad(scan)),positions))
    power=1/(np.sum(np.abs(steering @ noise)**2,axis=1)+np.finfo(float).eps)
    return float(scan[np.argmax(power)])

def _handler(_args,request):
    if request.get("operation", "estimate") == "config":
        return {"result": {"configuration": angle_configuration(request.get("properties"))}}
    if request.get("operation", "estimate") != "estimate":
        raise InputError("operation must be estimate or config")
    config = angle_configuration({key: request[key] for key in ANGLE_DEFAULTS if key in request})
    iq=complex_from_json(request.get('iq_samples'),'iq_samples')
    if config["enable_custom_array"]:
        raise InputError("custom-array MUSIC estimation is not yet implemented; use the session object to inspect its configuration")
    return {'result':{'angle_degrees':estimate(iq,array_size=config['array_size'],element_spacing=config['element_spacing'],slot_duration=config['slot_duration'],switching_pattern=config['switching_pattern'])}}
if __name__=='__main__': run_cli('ble_angle_estimate',_handler,description=__doc__)
