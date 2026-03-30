# Stage3 deterministic energy stage5-objective routing probe report

## Summary
- Added a new Stage3 loss term that supervises `ENERGY` on the same `stage5_norm` scale used by the packet readiness gate.
- The probe reused the current isolated dedicated energy-branch scaffold unchanged.
- The result is negative:
  - the new objective wiring works
  - but packet-facing `ENERGY` does not improve beyond the previous dedicated energy-adapter freeze result in any meaningful way
- Therefore the next bottleneck is not simple target-scale mismatch alone.

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/losses.py`
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5_focus_v1.json`
- New loss key:
  - `teacher_energy_stage5_state`
- The new loss compares:
  - `normalize_energy_log_rms_for_stage5(predicted_energy)`
  - `normalize_energy_log_rms_for_stage5(teacher_target_energy)`
- Default weight remains `0.0` unless explicitly enabled.

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energyadapter_stage5_smoke/logs/ss_detpitch_energyadapter_stage5_smoke.step1.json`
- The smoke confirms:
  - override loading works
  - the new metric is present
  - `loss_teacher_energy_stage5_state` is non-zero and trainable

## Warm-start short loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterfreeze_v1.json`
- Loss override:
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5_focus_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energyadapter_stage5_warm4/logs/ss_detpitch_energyadapter_stage5_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energyadapter_stage5_warm4/streaming_student_packet_checkpoint_selection.json`

## Packet result
- Packet-best checkpoint is again step `2`.
- Packet-best readiness remains unchanged:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
  - `all_core_controls_ready_count = 0/3`
- Packet-best metrics:
  - `avg_f0_proxy_reference_corr = 1.0`
  - `avg_f0_calibrated_log2_mae = 0.016837`
  - `avg_vuv_reference_mae = 0.006119`
  - `avg_aper_calibrated_reference_mae = 0.2823`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550175`

## Comparison vs previous dedicated energy-adapter freeze
- Previous dedicated adapter report:
  - `docs/499_stage3_detpitch_energy_adapter_freeze_probe_report.md`
- Previous packet-best:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550192`
- New packet-best:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550175`
- The difference is effectively noise-level and does not change readiness.
- So "align the supervised scale to the packet gate" is not enough on its own.

## Main conclusion
- The deterministic energy line is now narrowed again:
  - adding isolated energy capacity helped materially
  - adding a gate-scale-aligned Stage5 energy loss on top of that does not materially change the packet result
- The current blocker is therefore not just objective scale mismatch.
- The next valid move should target either:
  - stronger isolated energy capacity
  - or a more direct packet-facing / calibration-aware energy objective than the current per-frame MSE family

## Decision
- Keep the new loss term available because it is a clean and low-risk supervision option.
- Do not keep rerunning the same dedicated energy-branch family with only small weight changes on this new loss.
- Treat this probe as a no-go for "scale alignment alone will rescue ENERGY".

## Next actions
1. Keep `deterministic_extractor_v1 + f0_correction_enabled = false` as the current deterministic reference line.
2. Keep the dedicated energy-branch family as the active isolated `ENERGY` line.
3. If this line continues, prioritize stronger isolated branch capacity or more direct packet-facing energy objectives over more same-family scale-alignment tuning.
