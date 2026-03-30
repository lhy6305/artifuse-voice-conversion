# Stage3 deterministic Stage5 dynamic-range energy objective probe report

## Summary
- Tested the next packet-facing `ENERGY` objective on the deterministic isolated energy branch:
  - keep the existing `dedicated_energy_branch_v1`
  - keep the rest of the scaffold frozen
  - add Stage5-normalized centered-shape and per-sample std losses
- This probe is the first direct packet-facing objective that slightly beats the earlier dedicated energy-branch best.
- But the route still does not open:
  - `energy_ready_count = 0/3`
  - `all_core_controls_ready_count = 0/3`

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/losses.py`
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5dynrange_v1.json`
- New loss keys:
  - `teacher_energy_stage5_centered_state`
  - `teacher_energy_stage5_std`
- The new losses operate on Stage5-normalized energy and target the observed failure mode more directly than generic temporal or correlation shaping:
  - centered sequence mismatch
  - per-sample dynamic-range mismatch

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energydynrange_smoke/logs/ss_detpitch_energydynrange_smoke.step1.json`
- The smoke confirms:
  - new loss keys propagate correctly
  - partial warm-start remains valid
  - the isolated trainable subset is unchanged
- Example smoke metrics:
  - `loss_teacher_energy_stage5_centered_state = 0.12512`
  - `loss_teacher_energy_stage5_std = 0.124326`

## Warm-start short loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterfreeze_v1.json`
- Loss override:
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5dynrange_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energydynrange_warm4/logs/ss_detpitch_energydynrange_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energydynrange_warm4/streaming_student_packet_checkpoint_selection.json`

## Training behavior
- The new dynamic-range losses are active and the short loop is healthy.
- Training loss falls across the four warm-start steps:
  - step `1`: `3.415882`
  - step `2`: `3.295566`
  - step `3`: `3.15736`
  - step `4`: `3.084196`
- Sampled validation again picks an early checkpoint:
  - step `1`
  - `loss_total = 2.420882`

## Packet result
- Packet-aware screening still preserves the already-open controls on every screened checkpoint:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
- `ENERGY` is still not ready:
  - `energy_ready_count = 0/3`
- Packet-best checkpoint:
  - step `2`
- Packet-best `ENERGY` metric:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550066`
- This is a real but very small improvement over the earlier best isolated result.

## Comparison vs recent deterministic energy probes
- Earlier dedicated energy-adapter best:
  - `docs/499_stage3_detpitch_energy_adapter_freeze_probe_report.md`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550192`
- Stage5-scale state-loss routing:
  - `docs/500_stage3_detpitch_energy_stage5_objective_routing_probe_report.md`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550175`
- Naive widening:
  - `docs/501_stage3_detpitch_energy_adapter_widening_probe_report.md`
  - widened-family best `avg_energy_stage5_norm_calibrated_reference_mae = 0.550949`
- Generic Stage5-shape routing:
  - `docs/502_stage3_detpitch_energy_stage5_shape_objective_probe_report.md`
  - packet-facing result regressed to `0.707125`
- Current dynamic-range objective:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550066`
- So direct dynamic-range pressure is slightly better than the earlier branch best, while generic Stage5 shape pressure was not.

## Diagnostic note
- The improvement is still very small.
- Representative packet diagnostics on `target::chapter3_3_firefly_138` show why the route is not open yet:
  - previous dedicated branch step `2`:
    - proxy std `0.010751`
    - calibrated std `0.037628`
    - reference std `0.352777`
    - calibrated MAE `0.281245`
  - current dynamic-range step `2`:
    - proxy std `0.010822`
    - calibrated std `0.039403`
    - reference std `0.352777`
    - calibrated MAE `0.280867`
- So the new objective is moving the right quantity, but only slightly. The dominant issue remains severe dynamic-range compression.

## Main conclusion
- The deterministic isolated `ENERGY` line now has a clearer direction:
  - generic Stage5 trajectory shaping was a dead end
  - explicit dynamic-range pressure is at least directionally correct
- But the current centered-plus-std objective is still far below packet-gate readiness.
- This is not a route-opening result. It is only the first small positive signal inside the more direct packet-facing objective family.

## Decision
- Keep the dedicated deterministic energy branch as the active isolated scaffold.
- Do not go back to generic Stage5 temporal or correlation shaping.
- Continue only if the next objective stays explicitly dynamic-range or calibration aware.

## Next actions
1. Keep the deterministic dedicated energy branch as the active reference scaffold.
2. Continue direct dynamic-range or calibration-aware `ENERGY` objectives rather than generic shape losses.
3. Do not treat the new `0.550066` best value as readiness; the gate is still fully closed on `ENERGY`.
