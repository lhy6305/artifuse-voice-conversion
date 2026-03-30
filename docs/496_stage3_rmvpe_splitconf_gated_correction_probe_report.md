# Stage3 RMVPE split-confidence gated-correction probe report

## Summary
- Added a consumer-side redesign probe on top of `rmvpe_split_confidence_v1`:
  - `provider_confidence_gate_mode = hard_vuv_times_confidence_v1`
- The goal was to test whether the main remaining RMVPE failure came from the student correction branch damaging a partially useful provider signal.
- Wiring and smoke completed for:
  - supervision dry run
  - one-step training
  - sample3 downstream control packet export

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_splitconf_gate_v1.json`
- The new gate mode scales:
  - `f0_delta`
  - `vuv_logit_delta`
- Gate definition:
  - sampled provider confidence
  - multiplied by hard provider `VUV`
- This is a real consumer-side change, not another provider-only tweak.

## Smoke artifacts
- Supervision dry run:
  - `reports/plans/streaming_student_supervision_rmvpesplitgate_smoke/streaming_student_supervision_plan.json`
- One-step training:
  - `reports/training/streaming_student_rmvpesplitgate_smoke/logs/streaming_student_rmvpesplitgate_smoke.step1.json`
  - `reports/training/streaming_student_rmvpesplitgate_smoke/checkpoints/streaming_student_rmvpesplitgate_smoke.step1.pt`
- Sample3 packet export:
  - `reports/runtime/streaming_student_downstream_control_packet_rmvpesplitgate_smoke_sample3/streaming_student_downstream_control_packet.json`

## Immediate training effect
- The gate did reduce correction activity:
  - ungated split-confidence `loss_log_f0_correction_l1 = 0.099057`
  - gated split-confidence `loss_log_f0_correction_l1 = 0.047207`
- Sample packet diagnostics also show smaller correction magnitude:
  - `target::chapter3_3_firefly_162`
    - ungated `delta_abs_mean = 0.152761`
    - gated `delta_abs_mean = 0.087587`
  - `target::chapter3_3_firefly_138`
    - ungated `delta_abs_mean = 0.14909`
    - gated `delta_abs_mean = 0.071396`
  - `target::chapter3_4_firefly_106`
    - ungated `delta_abs_mean = 0.145602`
    - gated `delta_abs_mean = 0.040274`

## Packet result
- Packet readiness still did not improve:
  - `f0_ready_count = 0/3`
  - `vuv_ready_count = 2/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- So protecting the provider from large low-confidence corrections was still not enough to open the route.

## Comparison vs ungated split-confidence probe
- Packet-level summary stayed identical at the gate level.
- Per-record `F0` tradeoff was mixed:
  - `target::chapter3_3_firefly_162`
    - `f0_corr` worsened from `-0.183369` to `-0.233722`
    - `f0_mae` improved slightly from `0.498518` to `0.496758`
  - `target::chapter3_3_firefly_138`
    - `f0_corr` improved from `-0.102261` to `-0.095093`
    - `f0_mae` was effectively unchanged
  - `target::chapter3_4_firefly_106`
    - `f0_corr` worsened from `0.09486` to `0.070376`
    - `f0_mae` worsened slightly from `1.693055` to `1.695876`
- `VUV` metrics stayed effectively unchanged.

## Additional interpretation
- This probe confirmed a real sub-problem:
  - the correction head was too active relative to the current RMVPE sidecar contract
- But it also confirmed a stronger conclusion:
  - simply shrinking or confidence-gating those corrections does not rescue packet-facing `F0`
- So the RMVPE branch is now blocked at a deeper level than:
  - threshold choice
  - confidence-vs-VUV conflation
  - ungated correction magnitude

## Decision
- Stop this current RMVPE Stage3 family as an active route-opening line.
- Keep the completed RMVPE probes as documented diagnostics, not as the current handoff candidate.
- Keep `deterministic_extractor_v1` as the only validated Stage3 pitch-provider reference.

## Next actions
1. Do not continue more same-family RMVPE packet smokes by inertia.
2. If RMVPE is revisited later, require a larger redesign than the current scaffold:
   - explicit voiced-support latent or state modeling
   - revised packet-side `F0` objective
   - or a different consumer that does not reuse the current correction contract
3. Return mainline effort to:
   - generation-side completion
   - deterministic-provider-backed structural reference work
   - non-RMVPE packet-gated Stage3 decisions
