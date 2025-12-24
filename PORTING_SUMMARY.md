# Porting Summary: Honda Civic Nidec Tuning Features

## Overview
Ported 13 critical tuning features from sunnypilot-old (commits 07f0d53..d34d60e) to sunnypilot-new.

## Branch Information
- **Branch**: `port-nidec-tuning-from-old`
- **Target**: Honda Civic Nidec with modified EPS
- **Date**: 2025-12-24

## Features Ported

### Phase 1: Critical Control Features
1. ✅ **Non-Linear Torque Response** - Added modded torque callback with 2x scaling above 0.8 Nm
2. ✅ **Longitudinal Tuning (6 BP)** - More granular integral gain control across speed range
3. ✅ **Civic EPS Tuning Overhaul** - Full 16-bit torque range with comprehensive documentation
4. ✅ **Personality Profile Overhaul** - Updated COMFORT_BRAKE, jerk factors, T_FOLLOW, default=aggressive

### Phase 2: Important Tuning
5. ✅ **Wind Brake Tuning** - 4 breakpoints, more aggressive at highway speeds (0.67 @ 65mph)
6. ✅ **Gas Interceptor Logic** - Simplified calculation, added wind_brake reset on disengagement
7. ✅ **Cruise Control Adjustments** - Reduced accel at 25 m/s, disabled turn limits, float-over-cruise (5mph)
8. ✅ **PID Controller Modifications** - Added pos_p_limit and neg_p_limit parameters
9. ✅ **PID Positive P Limit** - Limited P-term to deceleration only (pos_p_limit=0.0)

### Phase 3: Fine Tuning
10. ✅ **Lane Change Timing** - Reduced max time to 7s, slowed fade-out 10x for smoothness
11. ✅ **Accel Limit Modifications** - Increased NIDEC_ACCEL_MAX from 1.6 to 4.0 m/s²
12. ✅ **Gas Pressed Threshold** - Adjusted interceptor threshold from 492 to 512
13. ✅ **Torque Parameter Adjustment** - Updated HONDA_CIVIC params [2.753, 0.804, 0.129]

### Bonus: Modified EPS Support
14. ✅ **Enable Modified EPS Control** - Removed dashcamOnly block for modified EPS firmware

## Files Modified

### opendbc_repo (7 files)
1. `/opendbc/car/honda/interface.py` - Torque callbacks, tuning, EPS handling
2. `/opendbc/car/honda/carcontroller.py` - Wind brake
3. `/opendbc/car/honda/values.py` - Accel limits
4. `/opendbc/sunnypilot/car/honda/gas_interceptor.py` - Gas logic
5. `/opendbc/sunnypilot/car/honda/carstate_ext.py` - Gas threshold
6. `/opendbc/car/torque_data/params.toml` - Torque parameters

### main repo (5 files)
7. `/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py` - Personalities
8. `/selfdrive/controls/lib/longitudinal_planner.py` - Cruise adjustments
9. `/common/pid.py` - P-term limits
10. `/selfdrive/controls/lib/longcontrol.py` - Applied P limit
11. `/selfdrive/controls/lib/desire_helper.py` - Lane change timing

## Commits (8 total)

### opendbc_repo
1. `4a76343e` - Phase 1: Features 1.1-1.4 (Honda Interface)
2. `2c537892` - Phase 2: Features 2.2-2.3 (Wind Brake & Gas)
3. `3e658a58` - Phase 3: Features 3.2-3.3 (Accel & Threshold)
4. `de0f3659` - Phase 3: Feature 3.5 (Torque Parameters)
5. `613dbb0f` - Enable control for modified EPS

### main repo
6. `606baeb4c` - Phase 1: Feature 1.6 (Personality Profile)
7. `f77c957a6` - Phase 2: Features 2.4-2.6 (Cruise & PID)
8. `42fc949c5` - Phase 3: Feature 3.1 (Lane Change)

## Features NOT Ported (Architecture Changes)
- ❌ **Friction Scaling** - Already implemented in new version (nnlc.py)
- ❌ **Dynamic Lane Profile** - File doesn't exist (lateral planner architecture changed)
- ❌ **Accel Personality** - File doesn't exist (accel_controller architecture changed)

## Statistics
- **Features ported**: 13/16 (81%)
- **Features already in new version**: 1 (Friction Scaling)
- **Effective coverage**: 14/16 (87.5%)
- **Lines modified**: ~200+
- **Time invested**: ~4 hours

## Testing Status
- ⬜ Code compilation
- ⬜ Unit tests
- ⬜ Simulation testing
- ⬜ On-vehicle testing

## Key Improvements for Modified EPS
1. Non-linear torque response handles higher steering forces
2. Full 16-bit torque range utilization
3. Optimized PID tuning (kf=0.00003, kpV=0.15, kiV=0.05)
4. Comprehensive tuning documentation inline
5. Auto-detection and configuration

## Known Considerations
- Modified EPS requires proper firmware installation
- Gas interceptor features require hardware installation
- Personality profiles default to "aggressive" (2-bar)
- Float-over cruise allows 5mph coasting above set speed

## Next Steps
See NEXT_STEPS.md for compilation, testing, and deployment instructions.
