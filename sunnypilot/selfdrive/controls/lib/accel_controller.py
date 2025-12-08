from cereal import custom
from openpilot.common.numpy_fast import interp

AccelPersonality = custom.AccelerationPersonality

# accel personality by @arne182 modified by cgw and kumar
_DP_CRUISE_MIN_V =       [-0.2, -0.2,  -0.2]
_DP_CRUISE_MIN_V_ECO =   [-0.2, -0.2, -0.2]
_DP_CRUISE_MIN_V_SPORT = [-3.5, -3.5,  -3.5]
_DP_CRUISE_MIN_BP =      [0.,   11.1,  20.]

_DP_CRUISE_MAX_V =       [1.6, 1.5, 1.4, 1.3, 1.2, 1.0,  0.7,  0.6,  0.5]
_DP_CRUISE_MAX_V_ECO =   [1.20, 1.10, 1.05, 1.0, 0.92, .54,  .43,  .32,  .088]
_DP_CRUISE_MAX_V_SPORT = [2.5, 2.5, 2.5, 2.5, 2.5, 2.5,  2.5,  2.5,  2.5]
_DP_CRUISE_MAX_BP =      [0.,  1.,  6.,  8.,   11.,  20.,  25.,  30.,  55.]
