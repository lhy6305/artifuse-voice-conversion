# Stage3 deterministic energy-freeze isolation probe report

## Summary
- Implemented a minimal Stage3 training-freeze mechanism so short loops can train only selected parameter prefixes.
- Used that mechanism to test the strictest realistic energy-isolation probe on top of the current deterministic nof0corr packet reference.
- The probe trained only:
  - `frontend.energy_head`
  - `student.energy_branch_delta_head`
- The result is decisive:
  - the freeze worked as intended and preserved packet-facing `F0 / VUV / APER`
  - but `ENERGY` stayed completely unchanged at the packet gate
- This means the previous energy tradeoff was not only "catastrophic forgetting from shared updates".
- It also means the currently exposed energy-only heads do not have enough isolated capacity to move packet-facing `ENERGY` on their own.

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/training_freeze.py`
  - `src/v5vc/streaming_student/train_step_entry.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyfreeze_v1.json`
- The new freeze mode is config-driven:
  - `training.freeze.trainable_parameter_prefixes`
- Current probe allowlist:
  - `frontend.energy_head`
  - `student.energy_branch_delta_head`

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energyfreeze_smoke/logs/ss_detpitch_energyfreeze_smoke.step1.json`
- The freeze summary confirms the intended isolation:
  - `trainable_parameter_count = 4`
  - `frozen_parameter_count = 62`
  - trainable names are exactly:
    - `frontend.energy_head.weight`
    - `frontend.energy_head.bias`
    - `student.energy_branch_delta_head.weight`
    - `student.energy_branch_delta_head.bias`

## Warm-start short loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyfreeze_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energyfreeze_warm4/logs/ss_detpitch_energyfreeze_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energyfreeze_warm4/streaming_student_packet_checkpoint_selection.json`

## Packet result
- All four screened checkpoints preserved the same packet readiness pattern:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
- Packet-facing metrics barely moved across steps `1` to `4`.
- Best packet checkpoint was step `3`, but only by tiny metric noise:
  - `avg_f0_calibrated_log2_mae = 0.016534`
  - `avg_vuv_reference_mae = 0.006111`
  - `avg_aper_calibrated_reference_mae = 0.282344`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
- The key point is not the ranking.
- The key point is that `avg_energy_stage5_norm_calibrated_reference_mae` stayed pinned at `0.707125` for every screened checkpoint.

## Comparison vs earlier probes

### Comparison vs deterministic nof0corr packet reference
- Previous best packet reference:
  - `reports/runtime/ss_pktsel_detpitch_nof0corr6/streaming_student_packet_checkpoint_selection.json`
- That reference already had:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
- The energy-freeze probe preserves that exact state instead of degrading it.
- But it also does not improve `ENERGY` at all.

### Comparison vs unrestricted energy-focus warm-start
- Previous unrestricted warm-start:
  - `reports/runtime/ss_pktsel_detpitch_nof0corr_energyfocus_warm4/streaming_student_packet_checkpoint_selection.json`
- That run showed the old failure mode:
  - packet-best step `1` already dropped to `f0_ready_count = 0/3`
  - late step `4` reached `energy_ready_count = 2/3`
  - but only by collapsing `F0` and `APER`
- The new energy-freeze probe removes that forgetting failure:
  - `F0 / VUV / APER` stay open or nearly open throughout the loop
  - but `ENERGY` never moves

## Main conclusion
- The current deterministic nof0corr line is now localized more precisely:
  - shared-parameter energy optimization can move `ENERGY`, but damages already-open controls
  - strict isolated energy-head optimization preserves already-open controls, but cannot move `ENERGY`
- Therefore the remaining blocker is not just optimization interference.
- The remaining blocker is also missing isolated energy-specific capacity in the current scaffold.

## Decision
- Do not continue more loops of this exact energy-freeze setup by inertia.
- The current isolated trainable set is too weak.
- The next valid move must add new isolated energy capacity while still protecting `F0 / VUV / APER`.

## Next actions
1. Keep the training-freeze mechanism because it is now a useful Stage3 diagnostic tool.
2. Do not keep running more head-only energy-freeze loops with the same two trainable modules.
3. If this line continues, the next valid structural probe should introduce a dedicated energy-specific branch or adapter with isolated trainable capacity.
