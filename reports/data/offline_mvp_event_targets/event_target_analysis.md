# Offline MVP Event Target Analysis

## Summary
- This report analyzes the current heuristic frame-level event targets used by the offline MVP scaffold.
- The goal is to detect imbalance, redundancy, and target/source mismatch before making the next e_evt plan decision.

## Event Dimensions
- `0`: `energy_gate`
- `1`: `abs_delta_gate`
- `2`: `high_zero_cross`
- `3`: `low_zero_cross_voiced_like`
- `4`: `high_zero_cross_voiced_like`
- `5`: `delta_energy_rise`
- `6`: `delta_energy_fall`
- `7`: `energy_norm`

## Group Stats
### `target_train`
- record_count: `554`
- frame_count: `294606`
- event_mean:
  - `energy_gate`: `0.632818`
  - `abs_delta_gate`: `0.246791`
  - `high_zero_cross`: `0.153225`
  - `low_zero_cross_voiced_like`: `0.458412`
  - `high_zero_cross_voiced_like`: `0.193547`
  - `delta_energy_rise`: `0.494936`
  - `delta_energy_fall`: `0.505064`
  - `energy_norm`: `0.650162`
- acoustic_mean:
  - `energy`: `-3.61353`
  - `abs_mean`: `0.07717`
  - `zero_cross`: `0.089423`
  - `delta_energy`: `0.00639`
- event_vs_acoustic_corr:
  - `energy_gate`: energy=0.914112, abs_mean=0.735308, zero_cross=0.181996, delta_energy=0.02294
  - `abs_delta_gate`: energy=-0.067952, abs_mean=-0.263124, zero_cross=0.074145, delta_energy=0.08156
  - `high_zero_cross`: energy=0.137954, abs_mean=-0.089013, zero_cross=0.881998, delta_energy=0.095409
  - `low_zero_cross_voiced_like`: energy=0.690287, abs_mean=0.740485, zero_cross=-0.433907, delta_energy=-0.038062
  - `high_zero_cross_voiced_like`: energy=0.244084, abs_mean=-0.077208, zero_cross=0.782969, delta_energy=0.077699
  - `delta_energy_rise`: energy=0.052608, abs_mean=0.065096, zero_cross=0.124215, delta_energy=0.844666
  - `delta_energy_fall`: energy=-0.052608, abs_mean=-0.065096, zero_cross=-0.124215, delta_energy=-0.844666
  - `energy_norm`: energy=0.972414, abs_mean=0.749802, zero_cross=0.190854, delta_energy=0.02649

### `source_train`
- record_count: `483`
- frame_count: `166764`
- event_mean:
  - `energy_gate`: `0.40429`
  - `abs_delta_gate`: `0.265327`
  - `high_zero_cross`: `0.006914`
  - `low_zero_cross_voiced_like`: `0.480325`
  - `high_zero_cross_voiced_like`: `0.000216`
  - `delta_energy_rise`: `0.494735`
  - `delta_energy_fall`: `0.505266`
  - `energy_norm`: `0.465009`
- acoustic_mean:
  - `energy`: `-4.788274`
  - `abs_mean`: `0.01448`
  - `zero_cross`: `0.02532`
  - `delta_energy`: `0.002079`
- event_vs_acoustic_corr:
  - `energy_gate`: energy=0.743154, abs_mean=0.787737, zero_cross=-0.219796, delta_energy=0.028401
  - `abs_delta_gate`: energy=0.095947, abs_mean=-0.058392, zero_cross=0.241683, delta_energy=0.055375
  - `high_zero_cross`: energy=-0.06585, abs_mean=-0.06793, zero_cross=0.390989, delta_energy=0.006869
  - `low_zero_cross_voiced_like`: energy=0.81505, abs_mean=0.758181, zero_cross=-0.27006, delta_energy=0.030054
  - `high_zero_cross_voiced_like`: energy=0.009071, abs_mean=-0.000335, zero_cross=0.045261, delta_energy=-0.001527
  - `delta_energy_rise`: energy=0.040448, abs_mean=0.065304, zero_cross=-0.01258, delta_energy=0.930422
  - `delta_energy_fall`: energy=-0.040448, abs_mean=-0.065304, zero_cross=0.01258, delta_energy=-0.930422
  - `energy_norm`: energy=0.935493, abs_mean=0.829947, zero_cross=-0.283568, delta_energy=0.037089

## Target/Source Gaps
- `energy_gate`: target `0.632818` vs source `0.40429` (gap `0.228528`)
- `high_zero_cross_voiced_like`: target `0.193547` vs source `0.000216` (gap `0.193331`)
- `energy_norm`: target `0.650162` vs source `0.465009` (gap `0.185153`)
- `high_zero_cross`: target `0.153225` vs source `0.006914` (gap `0.146311`)
- `low_zero_cross_voiced_like`: target `0.458412` vs source `0.480325` (gap `-0.021913`)
- `abs_delta_gate`: target `0.246791` vs source `0.265327` (gap `-0.018536`)
- `delta_energy_fall`: target `0.505064` vs source `0.505266` (gap `-0.000202`)
- `delta_energy_rise`: target `0.494936` vs source `0.494735` (gap `0.000201`)

## Notes
- Event targets are derived from the current heuristic build_frame_targets implementation.
- Correlations are computed across masked frame-level targets only.
- This analysis is intended to detect imbalance, redundancy, and target/source mismatch.
