# 579 Stage5 Center-Delta Split Consumer Probe Report

## Summary
- Date: `2026-04-02`
- Goal:
  - test the first structured consumer-interface branch after `578`
  - keep the same `576` producer checkpoint
  - stop feeding the widened short-temporal contract as one flat sidecar
  - instead split the deployable contract into:
    - `center_code` for the periodic branch
    - `neighbor_delta_code` for the noise branch
- Result:
  - the split consumer is real and stable end to end
  - fixed-slice oracle shows:
    - `center_code` keeps the old framewise signal
    - `neighbor_delta_code` carries its own weaker but still material signal
    - the combined split contract stays at the same `~0.684` oracle level as the flat widened contract
  - bounded Stage5 improves only slightly over the flat widened contract:
    - `0.548187 -> 0.544851`
  - but it still stays far worse than the calmer `576` framewise route at `0.417480`
  - speech-emergence shows a mixed failure:
    - slightly less bright than the flat widened contract
    - but activity/RMS alignment collapses even further

## A. New Interface
- packet export now carries:
  - `fine_structure_code.waveform_geometry_center_code`
  - `fine_structure_code.waveform_geometry_neighbor_delta_code`
- new Stage5 semantic consumer:
  - `streaming_student_waveform_geometry_center_delta_split_v1`
- semantics:
  - periodic branch appends only `center_code`
  - noise branch appends only `neighbor_delta_code`

## B. Artifacts

### Packet exports
- validation3:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_tv3_pkt_centerdelta_r1_1/`
- special-eval2:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_se2_pkt_centerdelta_r1_1/`
- train8:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_train8_pkt_centerdelta_r1_1/`

### Stage5 indexes
- fixed validation5:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdelta_fixedslice_full5_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- matched train8 + validation5:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdelta_train8explicit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- widened input size:
  - `periodic = 52`
  - `noise = 68`

## C. Fixed-Slice Oracle

### Artifact
- probe:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdelta_r1_1/`

### Key numbers
- old framewise compact code:
  - `predicted_fine_structure_code_family = 0.619678 / 0.615552`
- widened short-temporal flat contract:
  - `predicted_short_temporal_fine_structure_code_family = 0.690647 / 0.668257`
- new split pieces:
  - `predicted_center_fine_structure_code_family = 0.619678 / 0.615552`
  - `predicted_neighbor_delta_fine_structure_code_family = 0.562416 / 0.553037`
  - `selected_dynamic_plus_predicted_center_delta_split = 0.683793 / 0.661966`

### Reading
- The split consumer does not lose the widened contract's upstream signal.
- It cleanly decomposes the widened signal:
  - center branch keeps the old compact code
  - neighbor-delta branch still carries meaningful waveform geometry
- So the branch is valid as a consumer-interface experiment, not a broken wiring artifact.

## D. Bounded Stage5

### Smoke
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdelta_train8explicit_warmstart1_smoke_r1_1/`
- result:
  - stable
  - widened-input partial init again skips:
    - `periodic_encoder.0.weight`
    - `noise_encoder.0.weight`

### Main run
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdelta_train8explicit_warmstart20_r1_1/`
- best validation:
  - `step20 = 0.544851`

### Comparison
- `576` framewise temporal-conv consumer:
  - `0.417480`
- `578` flat short-temporal stack:
  - `0.548187`
- `578` delta repack:
  - `0.558221`
- new center-delta split consumer:
  - `0.544851`

### Reading
- The split consumer is slightly better than the two flat widened variants.
- But the gain is tiny and nowhere near enough.
- The widened-contract downstream survival problem is therefore not solved by a simple branchwise split alone.

## E. Speech-Emergence

### Artifact
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdelta_train8explicit_warmstart20_speechemergence_r1_1/`

### Comparison
- flat widened short-temporal:
  - `decoded_spectral_centroid_hz = 10229.291016`
  - `decoded_spectral_high_band_energy_ratio = 0.746137`
  - `decoded_to_aligned_rms_ratio = 2.188950`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.674318`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.454576`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.429651`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.597234`
- center-delta split:
  - `decoded_spectral_centroid_hz = 9595.731445`
  - `decoded_spectral_high_band_energy_ratio = 0.722463`
  - `decoded_to_aligned_rms_ratio = 2.073328`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.630366`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.340550`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.255060`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.251343`
- `576` framewise temporal-conv:
  - `decoded_spectral_centroid_hz = 4457.849121`
  - `decoded_spectral_high_band_energy_ratio = 0.305093`
  - `decoded_to_aligned_rms_ratio = 1.537689`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.885131`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.871404`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.981473`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.938219`

### Reading
- The split consumer softens the flat widened route slightly:
  - lower centroid
  - lower high-band ratio
  - lower RMS ratio
- But it also destroys the calm-route alignment traits:
  - activity correlation collapses
  - decoded frame-RMS correlation collapses
- So this is not yet the right interface.

## Main Conclusion
- `579` improves the diagnosis:
  - the widened short-temporal contract is not failing only because it is flattened into one big vector
  - even a first structured consumer split is not enough
- The current failure now looks more specific:
  - Stage5 needs a stronger interface than simple branchwise feature routing
  - the contract likely needs an explicit adaptor/gate or a dedicated temporal consumer block that decides when local deltas should matter

## Decision
- Keep `576` as the current best bounded Stage5 route.
- Treat `579` as a useful but still negative interface probe.
- The next branch should not be:
  - another flat repack
  - or just another static branch split
- The next branch should be:
  - a dedicated Stage5 short-temporal adaptor/gate on top of the stronger contract
  - or a two-timescale center-vs-delta fusion module rather than plain feature concatenation into existing encoders
