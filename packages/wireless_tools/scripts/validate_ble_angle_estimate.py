"""Validate the R2026a bleAngleEstimate documented ULA example."""
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from ble_angle_estimate import estimate
iq=np.array([.8507+.5257j,-.5257+.8507j,-.8507-.5257j,.5257-.8507j,.8507+.5257j,-.5257+.8507j,-.8507-.5257j,.5257-.8507j,-.3561+.9345j])
got=estimate(iq,array_size=2,slot_duration=2,switching_pattern=[1,2])
assert abs(got-70)<.051,got
print('PASS BLE angle-estimate R2026a ULA example')
