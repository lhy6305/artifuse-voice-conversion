# 575 Stage3 Waveframeencoder Fidelity Losses And Bounded Stage5 Tradeoff Report

## Summary
- Date: `2026-04-02`
- Goal:
  - improve the deployable `waveform_frame_encoder_v1 -> waveform_geometry_code` producer by targeting the specific whitened-code weaknesses identified in `574`
  - check whether better producer-side fidelity moves both the fixed-slice oracle and the bounded Stage5 integration result
- Result:
  - new producer-side fidelity losses materially improved several packet-level code traits:
    - higher code variance
    - stronger frame-to-frame dynamics
    - lower template collapse
    - better own-record vs wrong-record margin
  - the fixed-slice source-scaffold oracle improved:
    - `predicted_fine_structure_code_family` waveform cosine `0.545295 -> 0.618695`
    - waveform-MLP cosine `0.547317 -> 0.615445`
  - but the corrected bounded `train8 + validation5` Stage5 run still did not beat the previous deployable geometry-code route on held-out loss:
    - `0.535322 -> 0.542880`
  - speech-emergence metrics became more mixed:
    - several structure-facing correlations improved
    - brightness and RMS drift worsened

## A. New Producer-Side Fidelity Losses

### Code changes
- Main file:
  - `src/v5vc/streaming_student/losses.py`
- New teacher-supervision terms added for the predicted compact fine-structure code:
  - `teacher_fine_structure_code_std`
  - `teacher_fine_structure_code_temporal`
  - `teacher_fine_structure_code_template_excess`
  - `teacher_fine_structure_code_record_margin`
- Support config:
  - `configs/streaming_student_loss_weights_detpitch_finestructurecode_wavepcatarget_whitened_fidelity_v1.json`

### Intended effect
- `teacher_fine_structure_code_std`:
  - reduce the old "too-flat code" failure mode
- `teacher_fine_structure_code_temporal`:
  - increase frame-to-frame movement toward the whitened target dynamics
- `teacher_fine_structure_code_template_excess`:
  - penalize the predicted code if it collapses harder toward its own per-record template than the target code does
- `teacher_fine_structure_code_record_margin`:
  - push the mean predicted code closer to its true record target than to the best wrong-record target

### Smoke
- run:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_trainstep_smoke_r1_1/`
- key validation terms at step1:
  - `loss_total = 2.549500`
  - `loss_teacher_fine_structure_code_target = 0.604241`
  - `loss_teacher_fine_structure_code_std = 0.313219`
  - `loss_teacher_fine_structure_code_temporal = 1.057823`
  - `loss_teacher_fine_structure_code_template_excess = 0.006515`
  - `loss_teacher_fine_structure_code_record_margin = 0.156816`

### Short training loop
- run:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_r1_1/`
- best checkpoint:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_r1_1/checkpoints/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_r1_1.step8.pt`
- validation trajectory:
  - `step2 = 2.932604`
  - `step4 = 2.305410`
  - `step6 = 2.283335`
  - `step8 = 2.061948`

## B. Fixed-Slice Producer Fidelity Comparison

### Protocol
- fixed validation5 slice:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`
  - `target::no_text_voice/chapter3_17_firefly_106`
  - `target::no_text_voice/chapter3_3_firefly_110`
- train8 slice:
  - `target::archive_firefly_1`
  - `target::chapter3_20_firefly_114`
  - `target::chapter3_22_firefly_108`
  - `target::chapter3_2_firefly_133`
  - `target::chapter3_2_firefly_236`
  - `target::chapter3_3_firefly_143`
  - `target::chapter3_3_firefly_243`
  - `target::chapter4_7_firefly_124`
- comparison artifact:
  - `reports/runtime/stage3_waveframeencoder_fixedslice_fidelity_compare_r1_1/summary.md`

### Fixed validation5 aggregate
- old step8 producer:
  - `cosine_mean = -0.016703`
  - `mae = 0.858329`
  - `rmse = 1.191049`
  - `pred_std = 0.419583`
  - `tgt_std = 1.110186`
  - `pred_frame_delta_l2_mean = 1.916465`
  - `tgt_frame_delta_l2_mean = 5.431798`
  - `pred_template_cosine_mean = 0.137658`
  - `tgt_template_cosine_mean = 0.046185`
  - `record_mean_code_margin_vs_best_other = -0.363781`
- new fidelity-loss step8 producer:
  - `cosine_mean = -0.020154`
  - `mae = 0.907174`
  - `rmse = 1.284929`
  - `pred_std = 0.626721`
  - `tgt_std = 1.110186`
  - `pred_frame_delta_l2_mean = 3.071444`
  - `tgt_frame_delta_l2_mean = 5.431798`
  - `pred_template_cosine_mean = 0.097432`
  - `tgt_template_cosine_mean = 0.046185`
  - `record_mean_code_margin_vs_best_other = -0.273942`

### Reading
- The new losses improved the producer in the intended structural directions:
  - variance increased:
    - `0.419583 -> 0.626721`
  - frame dynamics increased:
    - `1.916465 -> 3.071444`
  - template collapse decreased:
    - `0.137658 -> 0.097432`
  - record-specific margin became less negative:
    - `-0.363781 -> -0.273942`
- But pointwise closeness to the whitened target did not improve:
  - `cosine_mean` stayed slightly worse
  - `mae` and `rmse` both rose
- So the correct reading is:
  - the new losses improved code shape and separation traits
  - they did not yet produce a clean "closer in every sense" teacher mimic

## C. Fixed-Slice Source-Scaffold Oracle

### Artifacts
- fixed-slice packet exports:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_step8_fixedslice_tv3_pkt_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_step8_fixedslice_se2_pkt_r1_1/`
- fixed-slice normalized wavepca target packet exports:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_step8_fixedslice_tv3_wavepca16norm_pkt_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_step8_fixedslice_se2_wavepca16norm_pkt_r1_1/`
- fixed-slice oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_r1_1/`

### Key oracle numbers
- old producer from `573`:
  - `selected_dynamic_controls = 0.001125 / -0.000522`
  - `predicted_fine_structure_code_family = 0.545295 / 0.547317`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.537081 / 0.543211`
- new fidelity-loss producer:
  - `selected_dynamic_controls = 0.007272 / 0.008445`
  - `predicted_fine_structure_code_family = 0.618695 / 0.615445`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.614390 / 0.611940`

### Reading
- The deployable producer-side oracle improved materially.
- This is larger than the old low-signal fluctuations:
  - waveform `0.545295 -> 0.618695`
  - waveform-MLP `0.547317 -> 0.615445`
- So the new fidelity losses were not a no-op.
- They made the exported deployable code itself stronger on the same fixed slice.

## D. Corrected Bounded Stage5 Integration

### Important packaging pitfall
- An early attempt accidentally reused the default package-builder sampling behavior and produced a broken `3 train + 5 validation` dataset when the intended split was `8 train + 5 validation`.
- Those outputs must not be used as the main comparison:
  - `reports/runtime/stage5_train8_index_streaming_student_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_r1_1/`
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_r1_1/`
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_warmstart20_r1_1/`
- The corrected path explicitly pinned the train8 record ids before package build.

### Corrected artifacts
- train8 packet export:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_fidelity_loop8_step8_train8_pkt_r1_1/`
- corrected train8 Stage5 package index:
  - `reports/runtime/stage5_train8_index_streaming_student_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_train8explicit_r1_1/streaming_student_stage5_dataset_index.json`
- corrected merged `train8 + validation5` offline index:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_train8explicit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- corrected bounded Stage5 run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_train8explicit_warmstart20_r1_1/`

### Held-out result
- previous deployable geometry-code route from `574`:
  - `loss_total = 0.535322`
- new fidelity-loss geometry-code route:
  - `loss_total = 0.542880`

### Reading
- Better producer-side oracle and better producer-side structure traits did not automatically translate into a better bounded Stage5 validation loss under the current consumer/objective recipe.
- So the system state is now:
  - producer-side fidelity moved in the intended direction
  - downstream conversion of that improvement remains partial

## E. Corrected Speech-Emergence Read

### Artifacts
- previous deployable geometry-code speech-emergence:
  - `reports/runtime/stage5_train8val5_waveframeencoder_geomcode_warmstart20_speechemergence_r1_1/`
- new fidelity-loss geometry-code speech-emergence:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_fidelity_step8_geomcode_train8explicit_warmstart20_speechemergence_r1_1/`

### Aggregate comparison
- previous deployable geometry-code:
  - `decoded_zero_crossing_rate = 0.457168`
  - `decoded_spectral_centroid_hz = 10061.893555`
  - `decoded_spectral_high_band_energy_ratio = 0.757599`
  - `decoded_to_aligned_rms_ratio = 1.958084`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.788139`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.659590`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.758089`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.817157`
- new fidelity-loss geometry-code:
  - `decoded_zero_crossing_rate = 0.463930`
  - `decoded_spectral_centroid_hz = 10188.966797`
  - `decoded_spectral_high_band_energy_ratio = 0.763876`
  - `decoded_to_aligned_rms_ratio = 2.533511`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.676518`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.487106`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.780808`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.855660`

### Reading
- Several structure-facing machine traits improved:
  - `decoded_frame_template_cosine_gap_vs_aligned: 0.788139 -> 0.676518`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned: 0.659590 -> 0.487106`
  - `predicted_activity_to_aligned_frame_rms_corr: 0.758089 -> 0.780808`
  - `decoded_frame_rms_to_aligned_frame_rms_corr: 0.817157 -> 0.855660`
- But loudness and brightness drift worsened:
  - `decoded_spectral_centroid_hz: 10061.893555 -> 10188.966797`
  - `decoded_spectral_high_band_energy_ratio: 0.757599 -> 0.763876`
  - `decoded_to_aligned_rms_ratio: 1.958084 -> 2.533511`
- So this branch improved structural alignment signals without yet producing a net cleaner bounded Stage5 checkpoint.

## Main Conclusion
- The new fidelity losses were useful on the upstream side:
  - producer-side code statistics improved
  - fixed-slice deployable oracle improved materially
- But the current bounded Stage5 consumer/objective still does not convert those gains into a better held-out checkpoint cleanly.
- That means the project should not snap back to "producer changes do nothing".
- The stronger reading is:
  - producer-side fidelity is moving in the right direction
  - current downstream consumption of that improved code is still incomplete

## Next Recommended Direction
- Keep the `waveform_frame_encoder_v1` producer path as the active upstream contract line.
- Do not go back to the old hidden-source sweeps.
- The next producer-side experiment should be structural, not just another scalar loss rebalance:
  - increase predictor-side temporal context on top of the waveform-frame encoder branch
  - or change the compact contract to carry short local temporal structure more directly
- Continue to evaluate new producer variants with:
  - the same fixed-slice producer fidelity comparison
  - the same fixed-slice source-scaffold oracle
  - only then the corrected bounded `train8 + validation5` Stage5 integration
