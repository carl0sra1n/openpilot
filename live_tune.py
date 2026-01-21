#!/usr/bin/env python3
import sys
import time
from openpilot.common.params import Params


def main():
  params = Params()

  # Default values (Current stable tuning)
  DEFAULTS = {"LiveTuningKp": "0.10", "LiveTuningKi": "0.05", "LiveTuningFriction": "0.05", "LiveTuningLatAccelFactor": "1.7", "LiveTuningEnabled": "1"}

  print("\n🚗 NIDEC LIVE TUNING TOOL 🚗")
  print("==============================")

  # Initialize if not present
  if not params.get_bool("LiveTuningEnabled"):
    print("Initializing Live Tuning parameters...")
    for k, v in DEFAULTS.items():
      params.put(k, v)
  else:
    print("Live Tuning is ALREADY ACTIVE.")

  while True:
    try:
      # Read current values
      kp = float(params.get("LiveTuningKp", encoding='utf-8') or DEFAULTS["LiveTuningKp"])
      ki = float(params.get("LiveTuningKi", encoding='utf-8') or DEFAULTS["LiveTuningKi"])
      friction = float(params.get("LiveTuningFriction", encoding='utf-8') or DEFAULTS["LiveTuningFriction"])
      lat_accel = float(params.get("LiveTuningLatAccelFactor", encoding='utf-8') or DEFAULTS["LiveTuningLatAccelFactor"])
      enabled = params.get_bool("LiveTuningEnabled")

      print("\nCURRENT VALUES (Applied every ~1s):")
      print(f"1. kP (Proportional)    : {kp:.4f}")
      print(f"2. kI (Integral)        : {ki:.4f}")
      print(f"3. Friction             : {friction:.4f}")
      print(f"4. LatAccelFactor       : {lat_accel:.4f}")
      print(f"5. Master Switch        : {'ON' if enabled else 'OFF'}")
      print("6. Reset to Defaults")
      print("0. Exit")

      choice = input("\nSelect parameter to change (0-6): ").strip()

      if choice == '0':
        break
      elif choice == '1':
        val = input(f"New kP value [{kp}]: ").strip()
        if val:
          params.put("LiveTuningKp", val)
      elif choice == '2':
        val = input(f"New kI value [{ki}]: ").strip()
        if val:
          params.put("LiveTuningKi", val)
      elif choice == '3':
        val = input(f"New Friction value [{friction}]: ").strip()
        if val:
          params.put("LiveTuningFriction", val)
      elif choice == '4':
        val = input(f"New LatAccelFactor value [{lat_accel}]: ").strip()
        if val:
          params.put("LiveTuningLatAccelFactor", val)
      elif choice == '5':
        new_state = "0" if enabled else "1"
        params.put("LiveTuningEnabled", new_state)
        print(f"Toggling Master Switch -> {new_state}")
      elif choice == '6':
        print("Restoring defaults...")
        for k, v in DEFAULTS.items():
          params.put(k, v)

      print("Parameter updated!")
      time.sleep(0.5)

    except KeyboardInterrupt:
      break
    except Exception as e:
      print(f"Error: {e}")
      time.sleep(1)


if __name__ == "__main__":
  main()
