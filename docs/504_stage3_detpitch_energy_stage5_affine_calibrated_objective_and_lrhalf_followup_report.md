# Stage3 deterministic Stage5 affine-calibrated energy objective and lr-half follow-up report

## Summary
- Continued the deterministic isolated `ENERGY` line with a more direct packet-facing objective:
  - keep the existing `dedicated_energy_branch_v1`
  - keep the rest of the scaffold frozen
  - add a differentiable Stage5 affine-calibrated MAE loss
- This is a real improvement over the previous best dynamic-range probe.
- But `ENERGY` still does not open:
  - `energy_ready_count = 0/3`
  - `all_core_controls_ready_count = 0/3`
- A follow-up `learning_rate = 2.5e-4` run did not stabilize the gain and should not become the new default.

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/losses.py`
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5calib_v1.json`
- New loss key:
  - `teacher_energy_stage5_affine_calibrated`
- The new loss mirrors the downstream packet audit more directly:
  - fit an affine map from Stage5-normalized energy proxy to target
  - clamp to `[0, 1]`
  - minimize weighted calibrated L1 error

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energycalib_smoke/logs/ss_detpitch_energycalib_smoke.step1.json`
- The smoke confirms:
  - the new calibrated loss is active
  - warm-start and freeze behavior remain valid
- Example smoke metrics:
  - `loss_teacher_energy_stage5_affine_calibrated = 0.253618`
  - validation `loss_teacher_energy_stage5_affine_calibrated = 0.138282`

## Main warm-start loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterfreeze_v1.json`
- Loss override:
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5calib_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energycalib_warm4/logs/ss_detpitch_energycalib_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_warm4/streaming_student_packet_checkpoint_selection.json`

## Packet result
- All screened checkpoints still preserve the already-open controls:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
- `ENERGY` remains closed:
  - `energy_ready_count = 0/3`
- Best `ENERGY` checkpoint inside this family is step `2`:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.547625`
- This is the best packet-facing deterministic isolated-energy result so far.

## Important selector note
- The packet-aware selector lexicographic rule still ranks step `3` above step `2`.
- That top-1 ranking is not the right conclusion for this family-specific `ENERGY` question.
- Why:
  - step `3` has slightly better `VUV` and `F0` secondary metrics
  - but its `ENERGY` regresses all the way back to `0.707125`
- So for the current deterministic energy line, the correct reading is:
  - selector top-1 is not the energy-best checkpoint
  - raw `ENERGY` metrics must be read explicitly alongside the selector ranking

## Diagnostic evidence
- Representative packet diagnostics on `target::chapter3_3_firefly_138`:
  - previous dynamic-range step `2`:
    - proxy std `0.010822`
    - calibrated std `0.039403`
    - reference std `0.352777`
    - correlation `0.111692`
    - calibrated MAE `0.280867`
  - current affine-calibrated step `2`:
    - proxy std `0.010828`
    - calibrated std `0.067272`
    - reference std `0.352777`
    - correlation `0.190693`
    - calibrated MAE `0.273546`
- So the new objective improves the right packet-facing quantity:
  - stronger post-calibration spread
  - higher correlation
  - lower calibrated MAE

## Comparison vs earlier deterministic energy probes
- Dedicated energy-adapter best:
  - `docs/499_stage3_detpitch_energy_adapter_freeze_probe_report.md`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550192`
- Stage5-scale state objective:
  - `docs/500_stage3_detpitch_energy_stage5_objective_routing_probe_report.md`
  - `0.550175`
- Widening:
  - `docs/501_stage3_detpitch_energy_adapter_widening_probe_report.md`
  - widened-family best `0.550949`
- Generic Stage5 shape objective:
  - `docs/502_stage3_detpitch_energy_stage5_shape_objective_probe_report.md`
  - regressed to `0.707125`
- Dynamic-range objective:
  - `docs/503_stage3_detpitch_energy_stage5_dynamic_range_objective_probe_report.md`
  - improved to `0.550066`
- Current affine-calibrated objective:
  - `0.547625`
- This is the clearest positive trend so far on the isolated deterministic energy line.

## LR-half follow-up
- Follow-up run:
  - same scaffold
  - same loss override
  - `learning_rate = 2.5e-4`
- Training summary:
  - `reports/training/ss_detpitch_energycalib_lrhalf_warm4/logs/ss_detpitch_energycalib_lrhalf_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_lrhalf_warm4/streaming_student_packet_checkpoint_selection.json`
- This follow-up does not help:
  - best visible `ENERGY` values are only `0.550892` at step `2` and `0.550539` at step `3`
  - both are worse than the original affine-calibrated run step `2 = 0.547625`
- So halving the learning rate is not the right default continuation for this family.

## Main conclusion
- The deterministic isolated `ENERGY` line now has a better-defined active family:
  - calibration-aware objectives are stronger than generic shape losses
  - the affine-calibrated objective is the best result so far
- But the route is still closed:
  - `energy_ready_count = 0/3`
- The correct reading is:
  - objective family improved
  - optimizer follow-up with smaller learning rate did not improve it
  - future continuation should stay inside the calibration-aware family, not move sideways to lower-learning-rate retries by inertia

## Decision
- Keep the affine-calibrated dynamic-range family as the active deterministic `ENERGY` line.
- Do not adopt the lr-half follow-up as the new default.
- When reviewing this family, read raw energy metrics explicitly instead of trusting packet-selector top-1 rank alone.

## Next actions
1. Keep the dedicated deterministic energy branch as the active scaffold.
2. Keep working inside the explicit calibration-aware objective family.
3. Do not repeat the lr-half follow-up by inertia.
