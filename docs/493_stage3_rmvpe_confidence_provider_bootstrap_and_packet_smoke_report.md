# Stage3 RMVPE confidence-provider bootstrap and packet-smoke report

## Summary
- Added a new Stage3 provider mode:
  - `rmvpe_confidence_v1`
- The new mode feeds:
  - unthresholded sampled RMVPE `F0`
  - sampled RMVPE confidence as `pitch_provider_vuv`
- Wiring and smoke completed for:
  - supervision dry run
  - one-step training scaffold
  - downstream control packet export

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/rmvpe_inference.py`
  - `src/v5vc/streaming_student/pitch_provider.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_confidence_v1.json`
- The new RMVPE inference path keeps unthresholded `F0` and sampled confidence separate instead of collapsing both into the old thresholded `f0_hz > 0` contract.

## Smoke status
- Supervision dry run completed:
  - `reports/plans/streaming_student_supervision_rmvpeconf_smoke/streaming_student_supervision_plan.json`
- One-step training scaffold completed:
  - `reports/training/streaming_student_rmvpeconf_smoke/logs/streaming_student_rmvpeconf_smoke.step1.json`
  - `reports/training/streaming_student_rmvpeconf_smoke/checkpoints/streaming_student_rmvpeconf_smoke.step1.pt`
- Downstream packet sample3 export completed:
  - `reports/runtime/streaming_student_downstream_control_packet_rmvpeconf_smoke_sample3/streaming_student_downstream_control_packet.json`

## Packet-smoke result
- Aggregate packet readiness summary:
  - `f0_ready_count = 0/3`
  - `vuv_ready_count = 2/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- So the confidence-aware route is still not handoff-ready.

## Comparison vs old thresholded RMVPE route
- The confidence-aware provider did not clear packet readiness.
- But it did change the packet-level shape:
  - `aper_ready_count` improved from `0/3` to `2/3`
  - `vuv_ready_count` stayed `2/3`
- F0 packet metrics remain weak:
  - `target::chapter3_3_firefly_162`
    - old `f0_proxy_reference_corr = -0.545358`
    - new `f0_proxy_reference_corr = -0.179244`
  - `target::chapter3_3_firefly_138`
    - old `f0_proxy_reference_corr = 0.116822`
    - new `f0_proxy_reference_corr = -0.101604`
  - `target::chapter3_4_firefly_106`
    - old `f0_proxy_reference_corr = -0.490576`
    - new `f0_proxy_reference_corr = 0.097064`
- This is mixed improvement, not a decisive rescue.

## Interpretation
- The confidence-aware provider is a meaningful structural probe, not a dead end:
  - provider-only confidence-aware audit already showed large raw F0 improvement
  - the new Stage3 plumbing accepts that provider contract cleanly
- But one-step packet smoke says the route is still not ready to promote.
- The gap now appears to be:
  - raw provider quality is better
  - but the current Stage3 consumer and one-step optimization are not enough to convert that into packet-ready F0 behavior

## Decision
- Keep `rmvpe_confidence_v1` as a valid experimental branch.
- Do not promote it to the default Stage3 provider.
- Do not claim that confidence-aware RMVPE solved the Stage3 F0 gate.

## Next actions
1. If this branch continues, use a short controlled training loop rather than one-step smoke before judging the consumer contract.
2. Keep the deterministic provider as the only validated structural reference.
3. Treat the confidence-aware RMVPE route as a plausible but still unproven escalation path.
