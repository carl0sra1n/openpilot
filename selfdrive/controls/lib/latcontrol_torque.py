import math
import numpy as np

from cereal import log
from opendbc.car.lateral import FRICTION_THRESHOLD, get_friction
from openpilot.common.constants import ACCELERATION_DUE_TO_GRAVITY
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController
from openpilot.common.params import Params

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt

# At higher speeds (25+mph) we can assume:
# Lateral acceleration achieved by a specific car correlates to
# torque applied to the steering rack. It does not correlate to
# wheel slip, or to speed.

# This controller applies torque to achieve desired lateral
# accelerations. To compensate for the low speed effects we
# use a LOW_SPEED_FACTOR in the error. Additionally, there is
# friction in the steering wheel that needs to be overcome to
# move it at all, this is compensated for too.

LOW_SPEED_X = [0, 10, 20, 30]
LOW_SPEED_Y = [15, 13, 10, 5]


class LatControlTorque(LatControl):
  def __init__(self, CP, CP_SP, CI):
    super().__init__(CP, CP_SP, CI)
    self.torque_params = CP.lateralTuning.torque.as_builder()
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.lateral_accel_from_torque = CI.lateral_accel_from_torque()
    self.pid = PIDController(self.torque_params.kp, self.torque_params.ki, k_f=self.torque_params.kf)
    self.update_limits()
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg

    self.params_storage = Params()
    self.step = 0

    self.extension = LatControlTorqueExt(self, CP, CP_SP, CI)

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction
    self.update_limits()

  def update_limits(self):
    self.pid.set_limits(self.lateral_accel_from_torque(self.steer_max, self.torque_params), self.lateral_accel_from_torque(-self.steer_max, self.torque_params))

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, calibrated_pose, curvature_limited):
    # Override torque params from extension
    if self.extension.update_override_torque_params(self.torque_params):
      self.update_limits()

    self.check_live_tuning()

    pid_log = log.ControlsState.LateralTorqueState.new_message()
    if not active:
      output_torque = 0.0
      pid_log.active = False
    else:
      actual_curvature = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
      roll_compensation = params.roll * ACCELERATION_DUE_TO_GRAVITY
      curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))

      desired_lateral_accel = desired_curvature * CS.vEgo**2
      actual_lateral_accel = actual_curvature * CS.vEgo**2
      lateral_accel_deadzone = curvature_deadzone * CS.vEgo**2

      low_speed_factor = np.interp(CS.vEgo, LOW_SPEED_X, LOW_SPEED_Y) ** 2
      setpoint = desired_lateral_accel + low_speed_factor * desired_curvature
      measurement = actual_lateral_accel + low_speed_factor * actual_curvature
      gravity_adjusted_lateral_accel = desired_lateral_accel - roll_compensation

      # do error correction in lateral acceleration space, convert at end to handle non-linear torque responses correctly
      pid_log.error = float(setpoint - measurement)
      ff = gravity_adjusted_lateral_accel
      # latAccelOffset corrects roll compensation bias from device roll misalignment relative to car roll
      ff -= self.torque_params.latAccelOffset
      ff += get_friction(desired_lateral_accel - actual_lateral_accel, lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)

      freeze_integrator = steer_limited_by_safety or CS.steeringPressed or CS.vEgo < 5
      output_lataccel = self.pid.update(pid_log.error, feedforward=ff, speed=CS.vEgo, freeze_integrator=freeze_integrator)
      output_torque = self.torque_from_lateral_accel(output_lataccel, self.torque_params)

      # Lateral acceleration torque controller extension updates
      # Overrides pid_log.error and output_torque
      pid_log, output_torque = self.extension.update(
        CS,
        VM,
        self.pid,
        params,
        ff,
        pid_log,
        setpoint,
        measurement,
        calibrated_pose,
        roll_compensation,
        desired_lateral_accel,
        actual_lateral_accel,
        lateral_accel_deadzone,
        gravity_adjusted_lateral_accel,
        desired_curvature,
        actual_curvature,
        steer_limited_by_safety,
        output_torque,
      )

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.d = float(self.pid.d)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(-output_torque)  # TODO: log lat accel?
      pid_log.actualLateralAccel = float(actual_lateral_accel)
      pid_log.desiredLateralAccel = float(desired_lateral_accel)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited_by_safety, curvature_limited))

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log

  def check_live_tuning(self):
    self.step += 1
    if self.step % 100 != 0:
      return

    try:
      # Check if live tuning is enabled
      if self.params_storage.get_bool("LiveTuningEnabled"):
        kp = float(self.params_storage.get("LiveTuningKp"))
        ki = float(self.params_storage.get("LiveTuningKi"))
        friction = float(self.params_storage.get("LiveTuningFriction"))
        lat_accel_factor = float(self.params_storage.get("LiveTuningLatAccelFactor"))
        kf = float(self.params_storage.get("LiveTuningKf"))
        deadzone = float(self.params_storage.get("LiveTuningDeadzone"))

        # Update PID params
        self.pid._k_p = [[0], [kp]]
        self.pid._k_i = [[0], [ki]]
        self.pid.k_f = kf

        # Update Torque params
        self.torque_params.friction = friction
        self.torque_params.latAccelFactor = lat_accel_factor
        self.steering_angle_deadzone_deg = deadzone

        # Update limits with new params
        self.update_limits()
    except:
      pass
