# Stage3 deterministic dedicated energy-adapter freeze probe report

## Summary
- Added a new isolated `ENERGY` structural probe on top of the current deterministic nof0corr Stage3 reference.
- The new probe keeps `F0 / VUV / APER` protected with prefix freeze, but replaces the old "energy delta from shared f0 branch only" path with a dedicated `ENERGY` branch.
- This is the first isolated deterministic probe that improves packet-facing `ENERGY` error without collapsing `F0 / VUV / APER`.
- But it still does not open the `ENERGY` gate:
  - `energy_ready_count` stays `0/3`
  - `all_core_controls_ready_count` stays `0/3`

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `src/v5vc/streaming_student/checkpoint_init.py`
  - `src/v5vc/streaming_student/train_step_entry.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterfreeze_v1.json`
- New model contract:
  - `energy_control_branch_mode = dedicated_energy_branch_v1`
  - `energy_control_branch_layers = 2`
- New dedicated branch input uses:
  - `control_hidden`
  - `conditioning`
  - frontend `coarse_log_f0 / vuv / aper / energy`
  - frontend `event_prior`
- The branch only affects `energy_correction`.
- Default behavior remains unchanged when `energy_control_branch_mode = shared_f0_branch_v1`.

## Partial warm-start support
- Added a training-only init helper so structural probes can warm-start from old checkpoints while leaving new parameters randomly initialized.
- New config switch:
  - `training.allow_partial_init_checkpoint = true`
- Current warm-start correctly reports `10` missing new branch keys and `0` unexpected keys.

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energyadapterfreeze_smoke/logs/ss_detpitch_energyadapterfreeze_smoke.step1.json`
- The smoke confirms:
  - partial init worked
  - freeze wiring worked
  - the new trainable set is exactly the intended energy-only subset
- Trainable parameter count:
  - `14`
- Trainable prefixes:
  - `frontend.energy_head`
  - `student.energy_branch_input_proj`
  - `student.energy_branch_norm`
  - `student.energy_branch_encoder`
  - `student.energy_branch_delta_head`

## Warm-start short loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterfreeze_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energyadapterfreeze_warm4/logs/ss_detpitch_energyadapterfreeze_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energyadapterfreeze_warm4/streaming_student_packet_checkpoint_selection.json`

## Packet result
- All four screened checkpoints preserved the already-open controls:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
- `ENERGY` still did not cross the packet gate:
  - `energy_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- Packet-best checkpoint is now step `2`.
- Packet-best averages:
  - `avg_f0_proxy_reference_corr = 1.0`
  - `avg_f0_calibrated_log2_mae = 0.016837`
  - `avg_vuv_reference_mae = 0.006118`
  - `avg_aper_calibrated_reference_mae = 0.282301`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550192`

## Comparison vs strict energy-freeze
- Previous strict freeze report:
  - `docs/498_stage3_detpitch_energyfreeze_isolation_probe_report.md`
- Previous strict freeze packet-best:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
  - `energy_ready_count = 0/3`
- New dedicated adapter freeze packet-best:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550192`
  - `energy_ready_count = 0/3`
- So the new branch does add real isolated energy capacity.
- But that gain is still sub-threshold and not enough to open the route.

## Comparison vs unrestricted energy-focus warm-start
- Unrestricted warm-start could reach `energy_ready_count = 2/3`.
- But it did so by damaging already-open `F0 / APER`.
- The dedicated adapter freeze result is the opposite tradeoff:
  - preserves `F0 / VUV / APER`
  - improves packet-facing `ENERGY` error
  - still fails the actual `ENERGY` readiness gate

## Main conclusion
- The active deterministic line is now localized more precisely:
  - strict two-head freeze was too weak to move `ENERGY`
  - dedicated isolated energy-branch capacity does move packet-facing `ENERGY`
  - but the current branch is still not strong enough to open the packet gate
- This is a real positive structural result, but not a route-opening result.

## Decision
- Keep the dedicated energy-branch idea as the current best isolated `ENERGY` direction on the deterministic line.
- Do not treat this as a solved Stage3 named-control opening.
- Do not go back to shared scalar energy tuning as the default next move.

## Next actions
1. Keep `deterministic_extractor_v1 + f0_correction_enabled = false` as the packet-facing base reference.
2. Keep the dedicated energy-branch scaffold as the new energy-specific isolated probe family.
3. If this line continues, the next valid escalation should target stronger isolated `ENERGY` capacity or energy-specific objective routing, not more copies of the old two-head freeze.
