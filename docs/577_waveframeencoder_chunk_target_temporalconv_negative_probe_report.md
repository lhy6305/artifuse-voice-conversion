# 577 Waveframeencoder Chunk Target TemporalConv Negative Probe Report

## Summary
- Date: `2026-04-02`
- Goal:
  - test the next most direct upstream-contract variant after `576`
  - keep the successful `waveform_frame_encoder_v1 + temporal_conv_v1` producer path
  - but replace the framewise whitened PCA supervision target with a chunk-aware whitened target
- Result:
  - the branch trains cleanly, but it regresses on the metrics that matter
  - sampled Stage3 validation is slightly worse than the framewise temporal-conv branch
  - fixed-slice deployable oracle drops materially:
    - `predicted_fine_structure_code_family` waveform `0.619678 -> 0.507787`
    - waveform-MLP `0.615552 -> 0.510964`
  - because the deployable contract itself got weaker on the fixed-slice oracle, this branch was not promoted to a bounded Stage5 run

## A. Config
- new config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_v1.json`
- key change relative to `576`:
  - keep:
    - `fine_structure_code_source_mode = waveform_frame_encoder_v1`
    - `fine_structure_code_predictor_mode = temporal_conv_v1`
    - `fine_structure_code_context_layers = 2`
    - `fine_structure_code_context_kernel_size = 9`
  - change supervision to:
    - `fine_structure_supervision.mode = waveform_chunk_pca_code_v1`
    - `normalize_code = true`
    - `chunk_radius = 2`
- intended meaning:
  - each `16D` deployable code is now trained against a local `5`-frame waveform chunk PCA code rather than a strictly frame-local code

## B. Stage3 Smoke And Short Loop

### Smoke
- run:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_trainstep_smoke_r1_1/`
- result:
  - training-step smoke completed successfully

### Short loop
- run:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_loop8_r1_1/`
- best checkpoint:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_loop8_r1_1/checkpoints/ss_detpitch_finestructcode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_loop8_r1_1.step8.pt`
- sampled validation trajectory:
  - `step2 = 2.611279`
  - `step4 = 2.350833`
  - `step6 = 2.142643`
  - `step8 = 2.027666`

### Comparison against the framewise temporal-conv branch from `576`
- `576` sampled validation:
  - `step2 = 2.778425`
  - `step4 = 2.216521`
  - `step6 = 2.062070`
  - `step8 = 1.959938`
- reading:
  - the chunk-target branch is not catastrophic
  - but it is already slightly worse by the end of the short loop:
    - `1.959938 -> 2.027666`

## C. Fixed-Slice Source-Scaffold Oracle

### Artifacts
- fixed-slice packet exports:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_tv3_pkt_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_se2_pkt_r1_1/`
- fixed-slice Stage5 package index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_step8_geomcode_fixedslice_full5_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- fixed-slice oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_waveframeencoder_wavepcachunktarget_whitened_temporalconv_fidelity_step8_geomcode_r1_1/`

### Comparison against the framewise temporal-conv branch from `576`
- `576` framewise temporal-conv:
  - `selected_dynamic_controls = 0.006078 / 0.001394`
  - `predicted_fine_structure_code_family = 0.619678 / 0.615552`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.611393 / 0.612625`
- chunk-target temporal-conv:
  - `selected_dynamic_controls = 0.003389 / -0.002534`
  - `predicted_fine_structure_code_family = 0.507787 / 0.510964`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.499542 / 0.503362`

### Reading
- This is a clear regression, not noise.
- The deployable predicted code got weaker on the same fixed slice:
  - waveform `0.619678 -> 0.507787`
  - waveform-MLP `0.615552 -> 0.510964`
- Even the surrounding selected-dynamic baseline drifted down:
  - waveform `0.006078 -> 0.003389`
  - waveform-MLP `0.001394 -> -0.002534`
- So the chunk-target branch did not preserve the producer-side contract strength opened by `576`.

## D. Decision
- This branch was not promoted to a bounded `train8 + validation5` Stage5 run.
- Reason:
  - the fixed-slice deployable oracle regressed materially before downstream integration
  - that is already enough to reject it as the next main line

## Main Conclusion
- The negative result is useful:
  - not every "more temporal / more chunk-aware" supervision target helps
  - replacing the framewise whitened target with a chunk-level PCA target weakened the deployable contract on the actual oracle we care about
- So the next upstream move should not be:
  - more chunk-target variants for the same framewise exported code
- The more plausible next move is:
  - change the deployable contract output shape itself
  - for example a short-temporal code or chunk-aware exported code
  - instead of asking the same framewise `16D` export head to imitate a chunk-level target distribution

## Next Recommended Direction
- Keep `576` as the current best bounded Stage5 branch.
- Treat this report as a negative gate on:
  - `framewise exported code + chunk-level PCA target`
- The next contract experiment should change the exported contract, not only the supervision target:
  - short-temporal-code export
  - chunk-aware deployable code family
  - or an explicit two-timescale code where Stage5 can distinguish local geometry from slower envelope state
