# 387 Stage3 `vuv balanced gate` contract positive A/B report

## Summary
- This round tested a structural `vuv` contract candidate instead of another loss-weight sweep.
- New family:
  - `teacher_e_evt_v1_balanced_vuv_gate_v1`
- Core change:
  - keep current `coarse_f0_state` baseline unchanged
  - keep `aper` proxy on existing `teacher_e_evt[..., 4]`
  - change `vuv` proxy supervision to:
    - explicit deterministic voiced gate
    - normalized unvoiced-frame balancing
- Result:
  - positive at `12-step`
  - still positive at `24-step`
  - remains positive on packet cheap screen at `48-step`
  - but downstream handoff gate is still not open

## Code
- Updated:
  - `src/v5vc/streaming_student/losses.py`
- Added:
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_v1.json`

## Rationale
- Prior calibrated audit had already relocated the main named-control bottleneck to `vuv`, then `F0`.
- Additional diagnosis showed:
  - current model tends to predict `voiced` across almost the whole utterance
  - simple loss-side `teacher_vuv_state` injection did not fix this
  - current proxy family already uses a nearly hard voicing target, so merely swapping to another soft target would not be enough
- Therefore this round tested a stronger contract-level candidate:
  - explicit hard voiced gate
  - explicit unvoiced minority balancing
  - normalized per-frame weighting so mean loss scale stays stable

## Validation
- `py_compile`
- `prepare-streaming-student-supervision`
- `12-step full-validation` A/B
- `24-step full-validation` A/B
- `48-step full-validation` follow-up
- downstream packet export on:
  - `sample_count = 3`
  - `sample_count = 8`

## Key results

### 12-step
- Baseline:
  - `reports/training/streaming_student_loop_controlfamily_coarsef012_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef012_round1_1.summary.json`
- Candidate:
  - `reports/training/streaming_student_loop_vuvbalancedgate12_round1_1/logs/streaming_student_stage_loop_vuvbalancedgate12_round1_1.summary.json`
- Validation:
  - `loss_total: 1.558948 -> 1.524679`
  - `loss_total_semantic_disabled_reference: 1.439009 -> 1.40554`
  - `loss_teacher_vuv_proxy: 0.589609 -> 0.449655`
- Packet compare:
  - baseline:
    `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef012_round1_2/streaming_student_downstream_control_packet.json`
  - candidate:
    `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate12_round1_1/streaming_student_downstream_control_packet.json`
  - `vuv_ready_count: 0 -> 1`
  - all 3 sampled records improved on `vuv_reference_mae`

### 24-step
- Baseline:
  - `reports/training/streaming_student_loop_controlfamily_coarsef024_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef024_round1_1.summary.json`
- Candidate:
  - `reports/training/streaming_student_loop_vuvbalancedgate24_round1_1/logs/streaming_student_stage_loop_vuvbalancedgate24_round1_1.summary.json`
- Validation:
  - `loss_total: 0.937981 -> 0.919927`
  - `loss_total_semantic_disabled_reference: 0.8501 -> 0.832382`
  - `loss_teacher_vuv_proxy: 0.57471 -> 0.329065`
- Packet compare:
  - baseline:
    `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef024_round1_2/streaming_student_downstream_control_packet.json`
  - candidate:
    `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate24_round1_1/streaming_student_downstream_control_packet.json`
  - `vuv_ready_count: 0 -> 1`
  - all 3 sampled records again improved on `vuv_reference_mae`
  - `F0 / aper / energy` were not materially damaged

### 48-step
- Baseline:
  - `reports/training/streaming_student_loop_controlfamily_coarsef048_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef048_round1_1.summary.json`
- Candidate:
  - `reports/training/streaming_student_loop_vuvbalancedgate48_round1_1/logs/streaming_student_stage_loop_vuvbalancedgate48_round1_1.summary.json`
- Validation:
  - `loss_total: 0.644372 -> 0.643897`
  - `loss_total_semantic_disabled_reference: 0.566819 -> 0.565316`
- 3-sample packet compare:
  - baseline:
    `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef048_round1_2/streaming_student_downstream_control_packet.json`
  - candidate:
    `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate48_round1_1/streaming_student_downstream_control_packet.json`
  - `vuv_ready_count` stayed `1`
  - but all 3 sampled records again improved on `vuv_reference_mae`
- 8-sample packet compare:
  - baseline:
    `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef048_sample8_round1_1/streaming_student_downstream_control_packet.json`
  - candidate:
    `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate48_sample8_round1_1/streaming_student_downstream_control_packet.json`
  - readiness summary stayed:
    - `vuv_ready_count = 1/8`
    - `f0_ready_count = 0/8`
  - but pairwise `vuv_reference_mae` improved on `6/8` sampled validation records
  - largest wins included:
    - `chapter3_29_firefly_130: 0.514772 -> 0.247418`
    - `chapter3_30_firefly_132: 0.415478 -> 0.217503`
    - `chapter3_3_firefly_210: 0.403411 -> 0.239801`

## Interpretation
- This is the first `vuv contract / representation` candidate that produced a clear positive signal without requiring human listening or Stage5 retraining.
- The gain is not confined to one checkpoint horizon:
  - positive at `12`
  - positive at `24`
  - still positive on packet screen at `48`
- The gain is also not confined to one or two cherry-picked records:
  - `6/8` wins on the wider sample-8 cheap screen
- However the route is still not Stage5-handoff ready:
  - `all_records_auto_reject` is still `true`
  - `f0_ready_count` is still `0`
  - `vuv_ready_count` is still only `1`

## Important caveat
- Current packet export metadata still reflects checkpoint base config for `semantic_supervision`.
- Therefore the packet json may still show:
  - `named_control_proxy_target_family = teacher_e_evt_v1`
- even when the checkpoint was trained with the balanced-gate override.
- For this round, the source of truth is:
  - training loop summary
  - supervision dry-run summary
  - packet metrics themselves
- not the packet metadata echo alone.

## Conclusion
- Promote `teacher_e_evt_v1_balanced_vuv_gate_v1` to the new working reference for the `vuv contract` line.
- Do not describe `vuv` as a dead direction anymore.
- Also do not overstate it:
  - it improved the cheap screen materially
  - but it did not open the handoff gate
- Next step should not be another `vuv loss-weight sweep`.
- The more valuable next move is:
  - keep this balanced-gate family fixed
  - use it as the new baseline while re-checking the remaining bottleneck, which is still primarily `F0`, plus residual long-tail `vuv` failures.
