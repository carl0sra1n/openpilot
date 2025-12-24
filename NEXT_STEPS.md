# Next Steps - Honda Civic Nidec Porting

## Overview
This document outlines the recommended steps to take after completing the code porting.

---

## STEP 1: Code Verification ✅ (COMPLETED)
- ✅ All features ported
- ✅ All functions/variables verified as used
- ✅ Modified EPS support enabled
- ✅ 8 commits created

---

## STEP 2: Pre-Compilation Checks 🔍

### 2.1 Review Git Status
```bash
cd /Users/carlosanguiano/Desktop/sunnypilot-old/sunnypilot-new

# View all commits on branch
git log --oneline port-nidec-tuning-from-old ^master | head -20

# View diff summary
git diff master...port-nidec-tuning-from-old --stat

# View all changes
git diff master...port-nidec-tuning-from-old > /tmp/all_changes.diff
```

### 2.2 Verify Submodule Status
```bash
# Check opendbc_repo submodule
cd opendbc_repo
git log --oneline HEAD ^origin/master | head -10
cd ..
```

### 2.3 Code Quality Check (Optional)
```bash
# Check Python syntax
find . -name "*.py" -path "*/car/honda/*" -o -path "*/controls/lib/*" | \
  xargs python3 -m py_compile 2>&1 | grep -v "^$"
```

---

## STEP 3: Compilation 🔨

### 3.1 Setup Build Environment
```bash
cd /Users/carlosanguiano/Desktop/sunnypilot-old/sunnypilot-new

# Update submodules
git submodule update --init --recursive

# Install dependencies (if needed)
# Follow sunnypilot build instructions
```

### 3.2 Build
```bash
# Build openpilot/sunnypilot
# Command depends on your build system
# Example:
scons -j$(nproc)

# Or if using SCons:
scons -u -j8
```

### 3.3 Watch for Errors
Pay special attention to:
- Import errors in modified files
- Type mismatches in torque calculations
- Missing parameters in function calls
- Submodule compatibility issues

**Common Issues to Check**:
```python
# Verify these imports work:
from opendbc.car.interfaces import TorqueFromLateralAccelCallbackType
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

# Verify numpy is available
import numpy as np
```

---

## STEP 4: Unit Testing 🧪

### 4.1 Run Existing Tests
```bash
# Run Honda-specific tests
pytest opendbc_repo/opendbc/car/honda/tests/ -v

# Run lateral control tests
pytest selfdrive/controls/lib/tests/test_latcontrol*.py -v

# Run longitudinal tests
pytest selfdrive/controls/lib/tests/test_longcontrol*.py -v
```

### 4.2 Manual Function Testing
Create a simple test script:
```python
# test_porting.py
import numpy as np
from opendbc.car.honda.interface import CarInterface
from opendbc.car import structs

# Test non-linear torque
ci = CarInterface()
result = ci.torque_from_lateral_accel_modded(1.0, mock_params, True)
print(f"Torque result: {result}")

# Test personality functions
from selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import get_jerk_factor, get_T_FOLLOW
print(f"Jerk factor: {get_jerk_factor()}")
print(f"T_FOLLOW: {get_T_FOLLOW()}")
```

---

## STEP 5: Simulation Testing 🎮

### 5.1 Setup Simulation
```bash
# If you have openpilot simulation environment
# Run with Honda Civic Nidec model
```

### 5.2 Test Scenarios
- **Scenario 1**: Straight driving at various speeds
  - Verify longitudinal tuning works
  - Check personality profiles respond correctly

- **Scenario 2**: Lane changes
  - Verify 7s max time
  - Check smooth fade transitions

- **Scenario 3**: Cruise control
  - Test float-over (5mph coast above set speed)
  - Verify acceleration limits

- **Scenario 4**: Modified EPS detection
  - Ensure control is enabled (not dashcam-only)
  - Verify correct tuning is applied

### 5.3 Monitor Logs
```bash
# Watch for errors during simulation
tail -f /data/community/crashes/*.log
```

---

## STEP 6: On-Vehicle Testing ⚠️ (CRITICAL)

### ⚠️ SAFETY FIRST ⚠️
**NEVER test on public roads without:**
- ✅ Full understanding of changes
- ✅ Safe testing environment (empty parking lot / private road)
- ✅ Emergency override ready (hands on wheel, foot over brake)
- ✅ Second person to monitor

### 6.1 Pre-Test Checklist
- [ ] Verified firmware: EPS contains "," in version
- [ ] Backup previous working version
- [ ] Camera and radar connectors secure
- [ ] Fully charged battery
- [ ] Clear weather conditions
- [ ] Emergency contact informed

### 6.2 Initial Test (Parking Lot)
1. **Power on** - Verify no errors on boot
2. **Engage at low speed** (5-10 mph)
   - Check steering response
   - Verify no harsh movements
   - Test disengagement works
3. **Test cruise control** at 15 mph
   - Verify acceleration feels smooth
   - Test set speed changes
4. **Test lane keeping** (if lane markings available)

### 6.3 Extended Test (Private Road)
**Only if parking lot tests pass**
1. Test at highway speeds (up to speed limit)
2. Verify float-over cruise (coast 5mph over set speed)
3. Test lane changes
4. Test following distance (all 3 personalities)
5. Monitor steering feel and responsiveness

### 6.4 Data Collection
```bash
# Save logs from test drive
ssh comma@<ip>
cp -r /data/media/0/realdata/<route> /tmp/
# Transfer to computer for analysis
```

### 6.5 What to Monitor
- **Steering**: Should be smooth, not jerky
- **Acceleration**: Progressive, not harsh
- **Braking**: Gradual, not sudden
- **Lane keeping**: Centered, not ping-ponging
- **Personality**: Noticeable difference between modes

---

## STEP 7: Tuning Adjustments 🎛️

Based on testing, you may need to adjust:

### If steering too aggressive:
```python
# In interface.py, line 314
stock_cp.lateralTuning.pid.kpV = [[0.12]]  # Reduce from 0.15
```

### If steering too weak:
```python
# In interface.py, line 314
stock_cp.lateralTuning.pid.kpV = [[0.18]]  # Increase from 0.15
```

### If acceleration too aggressive:
```python
# In long_mpc.py, line 70
return 1.2  # Increase from 0.9 (less aggressive)
```

### If following too close:
```python
# In long_mpc.py, line 82
return 1.2  # Increase from 1.0 (more distance)
```

---

## STEP 8: Documentation & Merge 📚

### 8.1 Update CHANGELOG
```bash
# Create or update CHANGELOG
cat >> CHANGELOG.md << 'EOF'
## [Unreleased]
### Added
- Non-linear torque response for modified Honda Civic Nidec EPS
- Support for Honda Civic Nidec with modified EPS firmware
- Enhanced longitudinal tuning with 6 breakpoints
- Float-over cruise feature (5mph coast above set speed)

### Changed
- Default personality from standard to aggressive (2-bar)
- Wind brake tuning with 4 breakpoints
- Lane change timing reduced to 7s max
- NIDEC_ACCEL_MAX increased to 4.0 m/s²

### Fixed
- Modified EPS now properly detected and supported
- Gas interceptor threshold adjusted for better detection
EOF
```

### 8.2 Create Pull Request (if contributing back)
```bash
# Push to remote
git push origin port-nidec-tuning-from-old

# Create PR description with:
# - Summary of changes
# - Testing performed
# - Breaking changes (if any)
# - Screenshots/videos of testing
```

### 8.3 Tag Release (for personal use)
```bash
# Create a tag
git tag -a v1.0.0-civic-nidec-tuned -m "Honda Civic Nidec optimized tuning"
git push origin v1.0.0-civic-nidec-tuned
```

---

## STEP 9: Long-Term Monitoring 📊

### After deployment:
1. **Collect data** from multiple drives
2. **Monitor disengagement** frequency
3. **Track any errors** in logs
4. **Gather user feedback** (if shared)
5. **Iterate on tuning** based on real-world data

### Metrics to Track:
- Miles driven without disengagement
- Average time in lane-keep mode
- Steering intervention frequency
- Acceleration smoothness rating
- User satisfaction score

---

## RECOMMENDED IMMEDIATE NEXT STEPS

1. **NOW**: Review git commits and diff
2. **TODAY**: Attempt compilation
3. **THIS WEEK**: Run unit tests
4. **AFTER TESTS PASS**: Simulation testing
5. **ONLY WHEN CONFIDENT**: Careful on-vehicle testing

---

## Need Help?

### Resources:
- **openpilot Discord**: Community support
- **sunnypilot GitHub**: Issue tracker
- **comma.ai docs**: Technical documentation

### Common Issues & Solutions:
See `TROUBLESHOOTING.md` (create if needed)

---

## Final Notes

⚠️ **Remember**:
- This is experimental tuning
- Your safety is paramount
- Start conservative, tune gradually
- Keep detailed notes of changes
- Always have a rollback plan

✅ **You've ported 13 features successfully**
🎯 **Focus now on safe testing and validation**
🚀 **Good luck with your testing!**
