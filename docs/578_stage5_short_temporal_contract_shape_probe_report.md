# 578 Stage5 Short-Temporal Contract Shape Probe Report

## Summary
- Date: `2026-04-02`
- Goal:
  - test whether the next contract-shape move after `577` should be a true widened export rather than more target-side supervision changes
  - keep the best producer checkpoint from `576`
  - change only the exported deployable contract shape seen by Stage5
- Result:
  - naive short-temporal export does strengthen the deployable fixed-slice oracle materially:
    - `predicted_fine_structure_code_family` waveform `0.619678 -> 0.690647`
    - waveform-MLP `0.615552 -> 0.668257`
  - but the same widened contract hurts bounded `train8 + validation5` Stage5 badly:
    - held-out validation `0.417480 -> 0.548187`
  - a direct follow-up that rewrites the widened contract as `center + neighbor_deltas` does not solve it:
    - fixed-slice oracle stays essentially flat at `0.690642 / 0.663964`
    - bounded Stage5 remains poor at `0.558221`

## A. Repo Change
- minimal infra added so Stage3 packet export can carry a widened deployable contract:
  - `fine_structure_code.waveform_geometry_short_temporal_code`
  - `semantic_consumer_mode = streaming_student_waveform_geometry_short_temporal_code_v1`
- files:
  - `src/v5vc/streaming_student/downstream_control_packet.py`
  - `src/v5vc/streaming_student/stage5_handoff.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/stage5_source_scaffold_oracle_probe.py`
  - `src/v5vc/cli.py`
- export semantics:
  - the first widened contract is a derived `radius=1` stack of neighboring predicted compact codes
  - this is still deployable in the same sense as the compact code itself because it is built only from student-predicted code, not target-derived reference

## B. Source Packet And Package Artifacts

### `576` producer checkpoint reused
- checkpoint:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_r1_1/checkpoints/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_r1_1.step8.pt`

### Short-temporal packet exports
- validation3:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_tv3_pkt_shorttemporal_r1_1/`
- special-eval2:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_se2_pkt_shorttemporal_r1_1/`
- train8:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_train8_pkt_shorttemporal_r1_1/`

### Short-temporal Stage5 indexes
- fixed validation5:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporal_fixedslice_full5_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- matched train8 + validation5:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporal_train8explicit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- widened input size:
  - `84 / 84`

## C. Fixed-Slice Oracle Result

### Artifact
- probe:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporal_r1_1/`

### Comparison vs `576` framewise geometry code
- `576` framewise code:
  - `predicted_fine_structure_code_family = 0.619678 / 0.615552`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.611393 / 0.612625`
- widened short-temporal code:
  - `predicted_short_temporal_fine_structure_code_family = 0.690647 / 0.668257`
  - `selected_dynamic_plus_predicted_short_temporal_fine_structure_code = 0.683797 / 0.668099`

### Reading
- This is a real oracle gain, not noise.
- Simply widening the deployable contract around the same producer output makes the source-scaffold oracle stronger.
- So the previous `577` lesson was correctly specific:
  - changing only the target family was not enough
  - but changing the exported contract shape really does move the deployable signal class

## D. Bounded Stage5 Result For The Widened Contract

### Smoke
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporal_train8explicit_warmstart1_smoke_r1_1/`
- result:
  - widened-input warm-start is stable
  - shape-mismatch partial init skips:
    - `periodic_encoder.0.weight`
    - `noise_encoder.0.weight`

### Main run
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporal_train8explicit_warmstart20_r1_1/`
- held-out best validation:
  - `step20 = 0.548187`

### Comparison
- `576` framewise temporal-conv contract:
  - `0.417480`
- no-code baseline from `574`:
  - `0.433231`
- widened short-temporal contract:
  - `0.548187`

### Reading
- The widened contract is clearly worse on bounded held-out Stage5.
- So the oracle gain did not survive the current Stage5 consumer/objective path.

## E. Speech-Emergence Read For The Widened Contract

### Artifact
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporal_train8explicit_warmstart20_speechemergence_r1_1/`

### Baseline-vs-`576` comparison
- `576` framewise temporal-conv contract:
  - `decoded_zero_crossing_rate = 0.250777`
  - `decoded_spectral_centroid_hz = 4457.849121`
  - `decoded_spectral_high_band_energy_ratio = 0.305093`
  - `decoded_to_aligned_rms_ratio = 1.537689`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.885131`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.871404`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.981473`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.938219`
- widened short-temporal contract:
  - `decoded_zero_crossing_rate = 0.469337`
  - `decoded_spectral_centroid_hz = 10229.291016`
  - `decoded_spectral_high_band_energy_ratio = 0.746137`
  - `decoded_to_aligned_rms_ratio = 2.188950`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.674318`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.454576`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.429651`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.597234`

### Reading
- The widened contract pulls Stage5 back toward the older geometry-heavy bright basin:
  - much brighter
  - much higher high-band energy
  - much weaker activity / RMS alignment
  - smaller template and adjacent-frame gaps
- So the failure mode is not "the widened contract got ignored".
- The opposite happened:
  - Stage5 used it strongly enough to leave the calm `576` basin
  - but the current consumer/objective could not use that stronger local geometry in a way that stayed stable on held-out validation

## F. Delta Repack Follow-Up

### Probe idea
- maybe the problem was redundant static context from `[prev, center, next]`
- so a second analysis-side contract rewrite was tried:
  - `center_plus_neighbor_delta_v1`
  - same output width
  - contract stores:
    - `center`
    - `center - prev`
    - `next - center`

### Artifacts
- packet exports:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_tv3_pkt_shorttemporaldelta_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_se2_pkt_shorttemporaldelta_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_train8_pkt_shorttemporaldelta_r1_1/`
- oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporaldelta_r1_1/`
- bounded Stage5:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_shorttemporaldelta_train8explicit_warmstart20_r1_1/`

### Results
- oracle:
  - `predicted_short_temporal_fine_structure_code_family = 0.690642 / 0.663964`
- bounded Stage5:
  - `best validation = 0.558221`

### Reading
- The delta repack keeps essentially the same oracle strength.
- But it does not recover bounded Stage5.
- So the problem is not just redundant static overlap inside the widened export.

## Main Conclusion
- `578` closes a very specific and important gap:
  - a stronger deployable source-scaffold oracle does not automatically imply a better bounded Stage5 route
  - this is now proven not only across producer improvements, but also across exported contract-shape widening
- The new evidence is stronger than before:
  - the current Stage5 consumer/objective can absorb a stronger local-geometry contract
  - but in doing so it gets pulled back toward the bright geometry-heavy basin instead of preserving the calmer `576` regime
- So the next move should not be:
  - another static window repack
  - or a third small variant of `[context frames] -> flat concat`
- The next move should be:
  - a structured contract/consumer interface
  - for example a two-timescale code, a center-vs-delta split, or a dedicated short-temporal adaptor/gate inside Stage5 instead of blind feature concatenation

## Decision
- Keep `576` as the current best bounded Stage5 line.
- Treat both:
  - widened short-temporal stack
  - widened short-temporal delta repack
  as negative downstream-integration probes.
- Update the main plan:
  - upstream contract redesign is still active
  - but the next discriminative branch is now the interface between the stronger contract and Stage5, not a third analysis-side window reshaping of the same code.
