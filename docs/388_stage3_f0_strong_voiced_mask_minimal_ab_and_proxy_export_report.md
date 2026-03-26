# 388 Stage3 `strong voiced F0 mask` minimal A/B and proxy export report

## Summary
- This round tested a minimal `F0` supervision-mask candidate on top of the new `vuv` reference:
  - baseline:
    - `teacher_e_evt_v1_balanced_vuv_gate_v1`
    - default `f0_supervision_mask_family = hard_voiced_v1`
  - candidate:
    - same `balanced_vuv_gate`
    - `f0_supervision_mask_family = strong_voiced_gate_v1`
- Goal:
  - reduce noisy `F0` supervision on weakly voiced frames
  - without touching head structure or reopening old loss sweeps
- Result:
  - `12-step` Stage3 validation improved slightly
  - but packet cheap screen did not improve `F0`
  - therefore this specific `strong_voiced_gate_v1` branch is stopped here
- Per user request, minimal proxy-audio export was also produced after the minimal validation

## Code
- Updated:
  - `src/v5vc/streaming_student/losses.py`
- Added:
  - `configs/streaming_student_loss_weights_vuvbalancedgate_strongf0mask_v1.json`

## Rationale
- On the current best `vuv balanced gate` candidate, the remaining hard failures were still primarily `F0`.
- Additional diagnostics on the 8-sample packet showed:
  - the worst `F0` records were not mainly high-aper failures
  - they had lower strong-voiced ratios
- That suggested a simple structural candidate:
  - keep `balanced_vuv_gate` fixed
  - make `coarse_f0_state / f0_state` only supervise stronger voiced frames

## Validation
- `py_compile`
- `prepare-streaming-student-supervision`
- `12-step full-validation` A/B
- downstream packet export on `sample_count = 3`
- minimal Stage3 proxy-audio export on the same `3` records

## Dry-run confirmation
- Supervision plan:
  - `reports/plans/streaming_student_supervision_vuvbalancedgate_strongf0mask_round1_1/streaming_student_supervision_plan.json`
- Confirmed fields:
  - `named_control_proxy_target_family = teacher_e_evt_v1_balanced_vuv_gate_v1`
  - `f0_supervision_mask_family = strong_voiced_gate_v1`
  - `teacher_f0_supervision_active_ratio = 0.598218`

## 12-step A/B
- Baseline summary:
  - `reports/training/streaming_student_loop_vuvbalancedgate12_round1_1/logs/streaming_student_stage_loop_vuvbalancedgate12_round1_1.summary.json`
- Candidate summary:
  - `reports/training/streaming_student_loop_vuvbalancedgate_strongf0mask12_round1_1/logs/streaming_student_stage_loop_vuvbalancedgate_strongf0mask12_round1_1.summary.json`

### Validation metrics
- `loss_total: 1.524679 -> 1.514449`
- `loss_total_semantic_disabled_reference: 1.40554 -> 1.395311`
- `loss_teacher_coarse_f0_state: 0.352649 -> 0.19285`
- `loss_teacher_f0_state: 0.348588 -> 0.191541`
- But:
  - `loss_log_f0_correction_l1: 0.07087 -> 0.085301`

Interpretation:
- At the Stage3 loss level this candidate is not dead.
- But the gain may simply come from supervising fewer frames, so packet cheap screen remains the decisive check.

## Packet cheap screen
- Baseline packet:
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate12_round1_1/streaming_student_downstream_control_packet.json`
- Candidate packet:
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_strongf0mask12_round1_1/streaming_student_downstream_control_packet.json`

### Summary
- Both stayed:
  - `f0_ready_count = 0`
  - `vuv_ready_count = 1`
  - `aper_ready_count = 2`
  - `energy_ready_count = 3`
  - `all_records_auto_reject = true`

### Per-record `F0`
- `chapter3_3_firefly_162`
  - `f0_proxy_reference_corr: 0.393434 -> 0.388299`
  - `f0_calibrated_log2_mae: 0.193859 -> 0.194718`
- `chapter3_3_firefly_138`
  - `f0_proxy_reference_corr: 0.120738 -> 0.117504`
  - `f0_calibrated_log2_mae: 0.428793 -> 0.428634`
- `chapter3_4_firefly_106`
  - `f0_proxy_reference_corr: 0.495049 -> 0.488608`
  - `f0_calibrated_log2_mae: 0.444127 -> 0.447338`

Interpretation:
- Packet cheap screen does not confirm the Stage3 gain.
- On the actual handoff-facing metrics, this candidate is flat to slightly worse.
- Therefore it does not justify a 24-step or 48-step continuation.

## Proxy audio export
- Baseline proxy bundle:
  - `reports/audio/streaming_student_proxy_audio_vuvbalancedgate12_round1_1/proxy_audio_export.json`
- Candidate proxy bundle:
  - `reports/audio/streaming_student_proxy_audio_vuvbalancedgate_strongf0mask12_round1_1/proxy_audio_export.json`
- Exported records:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

Important note:
- These are Stage3 structural proxy-audio exports, not final vocoder audio.
- They stay intentionally de-pitched and low-frequency.
- So they are useful for quick structural audit, but not for proving final `F0` realism.

## Conclusion
- `strong_voiced_gate_v1` should not be promoted.
- It improves Stage3 loss accounting, but does not improve packet-facing `F0` readiness.
- This specific line is stopped after the minimal validation.
- The current working reference remains:
  - `teacher_e_evt_v1_balanced_vuv_gate_v1`
  - with default `hard_voiced_v1` `F0` supervision mask

## Next step
- Do not continue:
  - `strong_voiced_gate_v1` horizon extension
  - threshold sweeps around `0.5`
  - another family of “just supervise fewer F0 frames”
- The next more valuable direction should move back to:
  - `F0 handoff representation / contract`
  - not another mask-threshold micro-variant
