#!/usr/bin/env python3
import sys
import time
from openpilot.common.params import Params


def main():
  params = Params()

  # Keys matching C++ UI (TorqueParamsOverride)
  KEYS = {
    "kP": "TorqueParamsOverrideKp",
    "kI": "TorqueParamsOverrideKi",
    "kF": "TorqueParamsOverrideKf",
    "Deadzone": "TorqueParamsOverrideDeadzone",
    "Friction": "TorqueParamsOverrideFriction",
    "LatAccel": "TorqueParamsOverrideLatAccelFactor",
    "Master": "TorqueParamsOverrideEnabled",  # Toggles "Manual Real-Time Tuning" in UI
  }

  # Scaling factors (UI stores Ints, we want Floats)
  SCALES = {
    "kP": 100.0,
    "kI": 100.0,
    "kF": 100000.0,
    "Deadzone": 10.0,
    "Friction": 100.0,
    "LatAccel": 100.0,
  }

  print("\n🚗 NIDEC LIVE TUNING TOOL (v3 - UI Sync) 🚗")
  print("==========================================")
  print("NOTE: This script now syncs perfectly with the Car Settings UI.")
  print("Values entered here will appear correctly on screen and vice-versa.\n")

  # Helper to read scaled param
  def get_val(name):
    # Fix: Remove user encoding arg, decode bytes manually
    raw = params.get(KEYS[name])
    if raw is None:
      return 0.0
    try:
      val_str = raw.decode('utf-8') if isinstance(raw, bytes) else raw
      return float(val_str) / SCALES[name]
    except:
      return 0.0

  # Helper to write scaled param
  def put_val(name, val_float):
    scaled_int = int(val_float * SCALES[name])
    params.put(KEYS[name], str(scaled_int))

  while True:
    try:
      kp = get_val("kP")
      ki = get_val("kI")
      kf = get_val("kF")
      dz = get_val("Deadzone")
      fric = get_val("Friction")
      lat = get_val("LatAccel")
      enabled = params.get_bool(KEYS["Master"])

      print("\nCURRENT VALUES:")
      print(f"1. kP (Proportional)    : {kp:.4f}")
      print(f"2. kI (Integral)        : {ki:.4f}")
      print(f"3. kF (Feed-Forward)    : {kf:.5f}")
      print(f"4. Deadzone (deg)       : {dz:.2f}")
      print(f"5. Friction             : {fric:.4f}")
      print(f"6. LatAccelFactor       : {lat:.4f}")
      print("---------------------------------")
      print(f"7. Tuning Enabled       : {'ON' if enabled else 'OFF'}")
      print("0. Exit")

      choice = input("\nSelect parameter to change (0-7): ").strip()

      if choice == '0':
        break

      elif choice in ['1', '2', '3', '4', '5', '6']:
        # Mapping choice to key name
        name_map = {'1': 'kP', '2': 'kI', '3': 'kF', '4': 'Deadzone', '5': 'Friction', '6': 'LatAccel'}
        key_name = name_map[choice]

        current = get_val(key_name)
        val_str = input(f"New {key_name} value [{current}]: ").strip()
        if val_str:
          try:
            val = float(val_str)
            put_val(key_name, val)
            print(f"Saved {key_name} -> {val} (Internal: {int(val * SCALES[key_name])})")
          except ValueError:
            print("Invalid number.")

      elif choice == '7':
        new_state = not enabled
        params.put_bool(KEYS["Master"], new_state)
        print(f"Toggling Master Switch -> {'ON' if new_state else 'OFF'}")

      time.sleep(0.5)

    except KeyboardInterrupt:
      break
    except Exception as e:
      print(f"Error: {e}")
      time.sleep(1)


if __name__ == "__main__":
  main()
