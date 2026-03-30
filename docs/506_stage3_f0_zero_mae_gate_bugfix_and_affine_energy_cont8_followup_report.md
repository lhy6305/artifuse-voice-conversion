# Stage3 F0 zero-mae gate bugfix and affine-calibrated energy cont8 follow-up report

## Summary
- Found a second downstream packet audit bug in the Stage3 readiness gate.
- Root cause:
  - `assess_named_control_readiness()` used `float(f0_calibration_summary.get("calibrated_log2_mae") or 999.0)`
  - so an exact `0.0` MAE was treated as falsy and replaced by `999.0`
- This bug created a false `F0` regression story in the first affine-calibrated continuation report.
- After fixing the gate and re-running the continuation selector:
  - `ss_detpitch_energycalib_cont4` keeps `F0 = 3/3` on all four checkpoints
  - `ENERGY` still improves monotonically from `0.239505` to `0.232511`
- A further continuation to `ss_detpitch_energycalib_cont8` keeps:
  - `F0 = 3/3`
  - `VUV = 3/3`
  - `APER = 2/3`
  - on all four checkpoints
- The new deterministic isolated-energy best is now:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.224320`
  - at `ss_detpitch_energycalib_cont8.step4`

## Root cause
- File:
  - `src/v5vc/streaming_student/downstream_control_packet.py`
- Old gate logic treated `0.0` as failure only for the `F0` calibrated MAE path.
- This affected `F0` readiness but not the underlying packet tensors themselves.
- The issue was easy to miss because:
  - `proxy_reference_corr = 1.0`
  - `reference_voiced_frame_count` stayed valid
  - only the exact-zero `calibrated_log2_mae` case flipped the gate result

## Fix
- Replaced the falsy-based fallback with explicit `None` handling:
  - `None -> 999.0`
  - real numeric `0.0 -> 0.0`
- This keeps the gate semantics unchanged for missing values while fixing the exact-zero success case.

## Re-evaluation of cont4
- Re-ran:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont4/streaming_student_packet_checkpoint_selection.json`
- Corrected continuation result:

| step | f0 ready | vuv ready | aper ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 3 | 3 | 2 | 0 | 0.239505 |
| 2 | 3 | 3 | 2 | 0 | 0.236783 |
| 3 | 3 | 3 | 2 | 0 | 0.234545 |
| 4 | 3 | 3 | 2 | 0 | 0.232511 |

- So the earlier apparent `F0` degradation in the continuation was an audit artifact, not a real control tradeoff.

## New continuation: cont8
- Started from:
  - `reports/training/ss_detpitch_energycalib_cont4/checkpoints/ss_detpitch_energycalib_cont4.step4.pt`
- Ran:
  - `reports/training/ss_detpitch_energycalib_cont8`
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont8/streaming_student_packet_checkpoint_selection.json`

## cont8 packet result

| step | f0 ready | vuv ready | aper ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 3 | 3 | 2 | 0 | 0.230522 |
| 2 | 3 | 3 | 2 | 0 | 0.228461 |
| 3 | 3 | 3 | 2 | 0 | 0.226366 |
| 4 | 3 | 3 | 2 | 0 | 0.224320 |

- This extends the monotonic affine-calibrated deterministic energy improvement:
  - warm4 energy-best: `0.243179`
  - cont4 energy-best: `0.232511`
  - cont8 energy-best: `0.224320`

## Selector interpretation
- The packet-aware selector top-1 still stays at step `1` inside both `cont4` and `cont8`.
- This is not because later steps are worse on `ENERGY`.
- It is because the lexicographic selector still prioritizes:
  - `VUV`
  - then `F0`
  - then `APER`
  - then `ENERGY`
- In `cont8`, all checkpoints tie on readiness counts, so slightly better early-step `VUV` MAE keeps step `1` ranked first.
- Therefore the active deterministic `ENERGY` conclusion must still cite:
  - selector top-1
  - raw energy-best step

## Main conclusion
- The affine-calibrated deterministic isolated-energy line is stronger than the previous mainline believed twice over:
  - the old `~0.55` story was broken by the clipped-scale stale-bias bug
  - the later `F0` tradeoff story was broken by the zero-mae gate bug
- After both fixes, the current true mainline is:
  - deterministic nof0corr scaffold remains stable on `F0 / VUV / APER`
  - affine-calibrated energy continuation keeps improving `ENERGY`
  - current best packet-facing deterministic energy is `0.224320`
- The route is still not open because `energy_ready_count` remains `0/3`.
- But the right next move is now simple again:
  - continue the affine-calibrated deterministic family
  - do not escalate into joint-control redesign based on the now-invalid earlier tradeoff reading

## Decision
- Keep the affine-calibrated deterministic isolated-energy family as the active mainline.
- Treat the earlier `cont4` F0-tradeoff interpretation as numerically superseded by this gate bugfix.
- Keep reading energy-best checkpoints separately from selector top-1.

## Next actions
1. Continue the affine-calibrated deterministic family from `cont8.step4`.
2. Keep packet-aware screening on the same sample3 slice for continuity.
3. Do not open a redesign branch unless the corrected continuation trend actually plateaus.
