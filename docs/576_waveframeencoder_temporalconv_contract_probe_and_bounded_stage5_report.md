# 576 Waveframeencoder TemporalConv Contract Probe And Bounded Stage5 Report

## Summary
- Date: `2026-04-02`
- Goal:
  - test whether a structural producer-side contract change can push the deployable waveform-geometry code further than the plain `waveform_frame_encoder_v1` branch
  - use a short temporal-conv predictor on top of the waveform-frame encoder instead of only tuning scalar fidelity losses
- Result:
  - the new `waveform_frame_encoder_v1 + temporal_conv_v1` producer trained cleanly from the existing fidelity checkpoint
  - fixed-slice packet fidelity improved in the same directions as the previous fidelity-loss branch:
    - higher variance
    - higher frame dynamics
    - better own-vs-other record separation margin
  - but fixed-slice source-scaffold oracle stayed effectively flat:
    - `predicted_fine_structure_code_family` waveform `0.618695 -> 0.619678`
    - waveform-MLP `0.615445 -> 0.615552`
  - the important downstream surprise is at Stage5:
    - corrected bounded `train8 + validation5` held-out loss improved strongly to `0.417480`
    - this beats both the previous deployable geometry-code routes and the old no-code baseline
  - however speech-emergence moved back toward a smoother, lower-brightness regime that looks much closer to no-code than to the earlier geometry-code structure-heavy route

## A. New Producer Configuration

### Config
- new config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_waveframeencoder_wavepcatarget_whitened_temporalconv_v1.json`
- key model change:
  - keep `fine_structure_code_source_mode = waveform_frame_encoder_v1`
  - add `fine_structure_code_predictor_mode = temporal_conv_v1`
  - use `fine_structure_code_context_layers = 2`
  - use `fine_structure_code_context_kernel_size = 9`

### Why this branch
- `575` already showed that fidelity losses can move producer-side code statistics and oracle without clearly fixing bounded Stage5.
- The next discriminative question was therefore structural:
  - does short temporal context in the compact-code predictor help the deployable contract survive Stage5 better than a framewise head does

## B. Stage3 Smoke And Short Loop

### Train-step smoke
- run:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_trainstep_smoke_r1_1/`
- command setup:
  - warm-start from:
    - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_r1_1/checkpoints/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_r1_1.step8.pt`
  - loss overrides:
    - `configs/streaming_student_loss_weights_detpitch_finestructurecode_wavepcatarget_whitened_fidelity_v1.json`
- result:
  - smoke completed successfully

### Short loop
- run:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_r1_1/`
- best checkpoint:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_r1_1/checkpoints/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_r1_1.step8.pt`
- sampled validation trajectory:
  - `step2 = 2.778425`
  - `step4 = 2.216521`
  - `step6 = 2.062070`
  - `step8 = 1.959938`

### Immediate read
- This already beats the previous fidelity-loss short loop from `575`:
  - `2.061948 -> 1.959938`
- So the temporal-conv predictor is not a dead branch at the Stage3 training level.

## C. Fixed-Slice Producer Fidelity

### Comparison artifact
- summary:
  - `reports/runtime/stage3_waveframeencoder_temporalconv_fixedslice_fidelity_compare_r1_1/summary.md`
- reference producer:
  - `575` fidelity-loss step8 producer

### Fixed validation5 aggregate
- `cosine_mean = -0.006318`
- `mae = 0.966144`
- `rmse = 1.360250`
- `pred_std = 0.773871`
- `tgt_std = 1.110186`
- `pred_frame_delta_l2_mean = 3.822427`
- `tgt_frame_delta_l2_mean = 5.431798`
- `pred_template_cosine_mean = 0.124468`
- `tgt_template_cosine_mean = 0.046185`
- `record_mean_code_cosine_to_own_target = 0.032792`
- `record_mean_code_best_other_cosine = 0.192561`
- `record_mean_code_margin_vs_best_other = -0.159769`

### Delta vs the `575` fidelity producer
- `cosine_mean = +0.013836`
- `mae = +0.058970`
- `rmse = +0.075320`
- `pred_std = +0.147150`
- `pred_frame_delta_l2_mean = +0.750982`
- `pred_template_cosine_mean = +0.027036`
- `record_mean_code_cosine_to_own_target = +0.064059`
- `record_mean_code_best_other_cosine = -0.050114`
- `record_mean_code_margin_vs_best_other = +0.114173`

### Reading
- The temporal-conv producer kept pushing several contract-shape metrics in the intended direction:
  - variance increased again
  - frame dynamics increased again
  - own-vs-other record separation improved again
  - cosine to the correct record mean even crossed from negative to positive
- But not all traits improved together:
  - pointwise `mae/rmse` got worse
  - template cosine increased again relative to the `575` fidelity producer
- So the correct interpretation is:
  - temporal context improved record separation and dynamics
  - it did not produce a uniformly cleaner mimic of the whitened target code

## D. Fixed-Slice Source-Scaffold Oracle

### Artifacts
- fixed-slice packet exports:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_tv3_pkt_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_se2_pkt_r1_1/`
- fixed-slice Stage5 package index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_geomcode_fixedslice_full5_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- fixed-slice oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_geomcode_r1_1/`

### Key oracle numbers
- previous fidelity producer from `575`:
  - `selected_dynamic_controls = 0.007272 / 0.008445`
  - `predicted_fine_structure_code_family = 0.618695 / 0.615445`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.614390 / 0.611940`
- temporal-conv producer:
  - `selected_dynamic_controls = 0.006078 / 0.001394`
  - `predicted_fine_structure_code_family = 0.619678 / 0.615552`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.611393 / 0.612625`

### Reading
- The deployable fixed-slice oracle did not move materially.
- The gain is effectively flat:
  - waveform `0.618695 -> 0.619678`
  - waveform-MLP `0.615445 -> 0.615552`
- So the temporal-conv branch did not open a clearly stronger producer-side oracle than the `575` fidelity branch.

## E. Corrected Bounded Stage5 Integration

### Corrected matched dataset
- train8 packet export:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_train8_pkt_r1_1/`
- corrected train8 package index:
  - `reports/runtime/stage5_train8_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_geomcode_train8explicit_r1_1/streaming_student_stage5_dataset_index.json`
- corrected merged `train8 + validation5` index:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_geomcode_train8explicit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`

### Bounded Stage5 run
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_geomcode_train8explicit_warmstart20_r1_1/`
- warm-start:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- shared settings:
  - `num_steps = 20`
  - `packages_per_step = 2`
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`

### Held-out validation result
- old deployable geometry-code route from `574`:
  - `loss_total = 0.535322`
- `575` fidelity-loss route:
  - `loss_total = 0.542880`
- temporal-conv fidelity route:
  - `loss_total = 0.417480`
- no-code baseline from `574`:
  - `loss_total = 0.433231`

### Reading
- This is the first deployable geometry-code branch that beats the old no-code baseline on the matched held-out Stage5 objective.
- The result is not marginal:
  - vs old geometry code:
    - `0.535322 -> 0.417480`
  - vs `575` fidelity producer:
    - `0.542880 -> 0.417480`
  - vs no-code baseline:
    - `0.433231 -> 0.417480`
- So the temporal-conv contract change materially improved bounded Stage5 trainability and held-out optimization.

## F. Speech-Emergence Tradeoff

### Artifact
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_geomcode_train8explicit_warmstart20_speechemergence_r1_1/`

### Baseline comparison
- old deployable geometry-code route from `574`:
  - `decoded_zero_crossing_rate = 0.457168`
  - `decoded_spectral_centroid_hz = 10061.893555`
  - `decoded_spectral_high_band_energy_ratio = 0.757599`
  - `decoded_to_aligned_rms_ratio = 1.958084`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.788139`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.659590`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.758089`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.817157`
- `575` fidelity-loss route:
  - `decoded_zero_crossing_rate = 0.463930`
  - `decoded_spectral_centroid_hz = 10188.966797`
  - `decoded_spectral_high_band_energy_ratio = 0.763876`
  - `decoded_to_aligned_rms_ratio = 2.533511`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.676518`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.487106`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.780808`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.855660`
- temporal-conv fidelity route:
  - `decoded_zero_crossing_rate = 0.250777`
  - `decoded_spectral_centroid_hz = 4457.849121`
  - `decoded_spectral_high_band_energy_ratio = 0.305093`
  - `decoded_to_aligned_rms_ratio = 1.537689`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.885131`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.871404`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.981473`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.938219`

### Reading
- The temporal-conv route became much calmer and less bright:
  - centroid collapsed from `~10.1k` to `4.46k`
  - high-band ratio collapsed from `~0.76` to `0.305`
  - RMS ratio improved from `2.533511` to `1.537689`
- But it also lost the earlier geometry-heavy structure readout:
  - `decoded_frame_template_cosine_gap_vs_aligned` regressed from `0.676518` to `0.885131`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned` regressed from `0.487106` to `0.871404`
- This puts the route much closer to the smoother no-code basin than to the earlier geometry-code structure-heavy basin.
- So the current best interpretation is:
  - temporal-conv makes the deployable contract easier for Stage5 to optimize
  - but the resulting route may be smoothing away the very frame-geometry variation that made the earlier geometry-code checkpoints structurally different

## Main Conclusion
- `waveform_frame_encoder_v1 + temporal_conv_v1` is a real upstream contract result, not noise:
  - it improves Stage3 sampled validation
  - it improves several fixed-slice producer fidelity traits
  - and it produces the current best bounded held-out Stage5 loss
- But the route does not win by preserving more of the earlier structure-heavy geometry signal at inference.
- Instead, it appears to trade some of that geometry-heavy behavior for a calmer, more no-code-like decode regime.
- The project state is therefore more specific now:
  - temporal context in the producer contract matters
  - but lower bounded Stage5 loss still does not guarantee that the fine-structure signal survived in the intended way

## Next Recommended Direction
- Keep the temporal-conv producer branch as the current bounded-Stage5 best checkpoint line.
- Do not jump to listening review yet.
- The next upstream-contract question should be:
  - can the contract keep the calmer distribution that Stage5 likes
  - without collapsing back toward no-code-like frame-template and adjacent-frame behavior
- The most targeted next branch is:
  - extend the deployable contract from a framewise `16D` code toward a short temporal code or chunk-aware code
  - keep the waveform-frame encoder input route
  - keep the fixed-slice fidelity/oracle protocol
  - then rerun the same matched bounded Stage5 comparison
