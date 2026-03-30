# Stage3 RMVPE split-confidence provider probe report

## Summary
- Added a new Stage3 pitch-provider mode:
  - `rmvpe_split_confidence_v1`
- This probe keeps:
  - unthresholded RMVPE `F0`
  - thresholded hard `VUV`
  - separate sampled RMVPE confidence
- The goal was to stop overloading confidence as `VUV` and test whether the current Stage3 consumer behaves better when voicing and confidence are split.
- Wiring and smoke completed for:
  - supervision dry run
  - one-step training
  - sample3 downstream control packet export

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/rmvpe_inference.py`
  - `src/v5vc/streaming_student/pitch_provider.py`
  - `src/v5vc/streaming_student/data.py`
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_split_confidence_v1.json`
- The new mode introduces an extra explicit provider tensor:
  - `pitch_provider_confidence`
- The current probe uses that extra feature only inside the Stage3 `F0` branch input.
- It does not change:
  - loss formulas
  - readiness-gate thresholds
  - downstream packet calibration logic

## Smoke artifacts
- Supervision dry run:
  - `reports/plans/streaming_student_supervision_rmvpesplitconf_smoke/streaming_student_supervision_plan.json`
- One-step training:
  - `reports/training/streaming_student_rmvpesplitconf_smoke/logs/streaming_student_rmvpesplitconf_smoke.step1.json`
  - `reports/training/streaming_student_rmvpesplitconf_smoke/checkpoints/streaming_student_rmvpesplitconf_smoke.step1.pt`
- Sample3 packet export:
  - `reports/runtime/streaming_student_downstream_control_packet_rmvpesplitconf_smoke_sample3/streaming_student_downstream_control_packet.json`

## Packet result
- Packet readiness summary stayed unchanged versus `rmvpe_confidence_v1`:
  - `f0_ready_count = 0/3`
  - `vuv_ready_count = 2/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- So splitting confidence away from `VUV` did not open the packet gate.

## Comparison vs `rmvpe_confidence_v1`
- Aggregate sample3 comparison:
  - `avg_f0_proxy_reference_corr`
    - old confidence route: `-0.061261`
    - split-confidence route: `-0.06359`
  - `avg_f0_calibrated_log2_mae`
    - old confidence route: `1.075175`
    - split-confidence route: `0.992191`
  - `avg_vuv_reference_mae`
    - old confidence route: `0.18547`
    - split-confidence route: `0.208616`
- Per-record shape:
  - `target::chapter3_3_firefly_162`
    - `f0_mae` improved from `0.651267` to `0.498518`
    - `f0_corr` changed from `-0.179244` to `-0.183369`
    - `vuv_mae` worsened from `0.144676` to `0.162023`
  - `target::chapter3_3_firefly_138`
    - `f0_mae` improved from `0.830426` to `0.785001`
    - `f0_corr` changed from `-0.101604` to `-0.102261`
    - `vuv_mae` worsened from `0.120748` to `0.157749`
  - `target::chapter3_4_firefly_106`
    - `f0_mae` improved from `1.743831` to `1.693055`
    - `f0_corr` changed from `0.097064` to `0.09486`
    - `vuv_mae` worsened from `0.290986` to `0.306077`

## Interpretation
- The split-confidence probe produced a clean tradeoff:
  - slightly better affine-calibrated `F0` magnitude fit
  - slightly worse `VUV` agreement
  - no real improvement in `F0` correlation
  - no change in packet readiness
- This means the earlier failure was not explained simply by "confidence was being misused as VUV."
- The current Stage3 consumer still does not know how to turn the richer RMVPE sidecar contract into packet-ready `F0`.

## Decision
- Keep `rmvpe_split_confidence_v1` only as a completed diagnostic branch.
- Do not promote it to an active handoff candidate.
- Do not continue more consumer-preserving RMVPE probes by inertia.

## Next actions
1. Keep `deterministic_extractor_v1` as the only validated Stage3 pitch-provider reference.
2. If RMVPE work continues at all, require a deeper redesign:
   - explicit voiced-support modeling in the consumer
   - confidence-aware or salience-aware correction logic
   - or revised `F0` supervision and packet calibration objectives
3. Otherwise shift effort back to:
   - generation-side completion
   - non-RMVPE handoff-gated Stage3 work
