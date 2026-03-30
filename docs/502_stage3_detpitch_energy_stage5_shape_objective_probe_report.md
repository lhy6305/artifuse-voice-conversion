# Stage3 deterministic Stage5-shape energy objective probe report

## Summary
- Tested a more direct packet-facing `ENERGY` objective on the deterministic isolated energy branch:
  - keep the existing `dedicated_energy_branch_v1`
  - keep the rest of the scaffold frozen
  - add Stage5-normalized energy temporal and correlation losses
- The new losses are wired correctly and actively optimize during smoke and short-loop training.
- But packet-facing `ENERGY` does not improve at all.
- In fact, the whole screened family falls back to the old plateau:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
  - `energy_ready_count = 0/3`

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/losses.py`
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5shape_v1.json`
- New loss keys:
  - `teacher_energy_stage5_temporal`
  - `teacher_energy_stage5_correlation`
- The new losses operate on:
  - `normalize_energy_log_rms_for_stage5(predicted_energy)`
  - `normalize_energy_log_rms_for_stage5(teacher_target_energy)`

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energyshape_smoke/logs/ss_detpitch_energyshape_smoke.step1.json`
- The smoke confirms:
  - the new loss keys propagate through the training step
  - partial warm-start still works from the deterministic nof0corr packet-best checkpoint
  - the isolated trainable subset is unchanged from the dedicated energy-adapter freeze scaffold
- Example smoke metrics:
  - `loss_teacher_energy_stage5_temporal = 0.000589`
  - `loss_teacher_energy_stage5_correlation = 0.095575`

## Warm-start short loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterfreeze_v1.json`
- Loss override:
  - `configs/streaming_student_loss_weights_detpitch_energy_stage5shape_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energyshape_warm4/logs/ss_detpitch_energyshape_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energyshape_warm4/streaming_student_packet_checkpoint_selection.json`

## Training behavior
- The new objective is not inert.
- Training loss falls across the four warm-start steps:
  - step `1`: `3.40362`
  - step `2`: `3.302515`
  - step `3`: `3.167717`
  - step `4`: `3.096658`
- Sampled validation also records a legitimate best checkpoint:
  - step `1`
  - `loss_total = 2.442519`
- So this is not a broken-loss or broken-plumbing run.

## Packet result
- Packet-aware screening still gives the same control-readiness pattern on every screened checkpoint:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
- Packet-best checkpoint:
  - step `4`
- Packet-best `ENERGY` metric:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
- This value is identical across all four screened checkpoints.

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
- Current Stage5-shape objective:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
- So generic Stage5 temporal and correlation shaping is not just insufficient; on the screened packet metric it fully regresses to the old energy plateau.

## Main conclusion
- The deterministic isolated `ENERGY` line has now ruled out another natural next guess:
  - generic Stage5-normalized trajectory shaping
- Even when the shape losses are active and teacher-loss training moves in the expected direction, the packet-facing energy metric stays pinned at the pre-adapter plateau.
- That strongly suggests the remaining blocker is not "missing generic trajectory pressure".
- The more likely issue is still packet-facing amplitude and calibration behavior, especially dynamic-range collapse.

## Decision
- Do not continue same-family `teacher_energy_stage5_temporal` or `teacher_energy_stage5_correlation` tuning by inertia.
- Keep the dedicated deterministic energy branch as the reference scaffold.
- The next valid move should target the actual observed failure mode more directly:
  - centered energy shape
  - dynamic-range or variance matching
  - or a more explicit calibration-aware packet-facing objective

## Next actions
1. Stop generic Stage5 temporal or correlation loss tuning on this family.
2. Keep the deterministic dedicated energy branch as the packet-facing reference scaffold.
3. If this line continues, probe a more explicit dynamic-range objective instead of another generic per-frame shape loss.
