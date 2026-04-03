# 580 Stage5 Center-Delta Adapter Semantic-Gate Probe Report

## Summary
- Date: `2026-04-02`
- Goal:
  - test whether the next interface branch after `579` should be an explicit Stage5 adaptor/gate rather than another contract repack
  - keep the same producer checkpoint and the same `center + neighbor_delta` package features as `579`
  - change only how Stage5 receives those semantic features
- Result:
  - the explicit adaptor/gate is the first positive downstream-integration result for the stronger short-temporal contract
  - matched `train8 + validation5` held-out validation improves from:
    - `579` static split consumer: `0.544851`
    - `580` center-delta adaptor/gate: `0.417454`
  - this is effectively tied with the old calm `576` framewise route at `0.417480`
  - speech-emergence also returns to the calm `576` basin instead of the bright widened-contract basin from `578/579`
  - but the route is still conservative:
    - validation gate means are only `periodic≈0.134`, `noise≈0.099`
    - adaptor-only finetune degrades badly to `0.511409`

## A. Code Change
- Files:
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
- New scaffold behavior:
  - branch semantic sidecars can be split off from the tail of each branch feature tensor
  - base `periodic_encoder` and `noise_encoder` now keep the old `36/36` warm-start-compatible base input dims
  - new semantic modules inject only gated residuals into branch hidden states:
    - `periodic_semantic_adapter/gate/proj`
    - `noise_semantic_adapter/gate/proj`
- New Stage5 semantic consumer:
  - `streaming_student_waveform_geometry_center_delta_adapter_v1`
  - package features stay the same as `579`:
    - periodic branch gets `center_code`
    - noise branch gets `neighbor_delta_code`
  - but package metadata now tells Stage5 to treat them as semantic sidecars rather than ordinary encoder input dims

## B. Dataset Artifacts

### Reused Stage3 packet exports
- train8:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_train8_pkt_centerdelta_r1_1/`
- validation3:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_tv3_pkt_centerdelta_r1_1/`
- special-eval2:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_loop8_step8_fixedslice_se2_pkt_centerdelta_r1_1/`

### New Stage5 package/index artifacts
- train packages:
  - `reports/runtime/stage5_train8_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_train8explicit_r1_1/`
- validation packages:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_fixedslice_tv3_r1_1/`
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_fixedslice_se2_r1_1/`
- merged matched train8 + validation5 index:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_train8explicit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`

## C. Smoke And Warm-Start Compatibility
- smoke:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_train8explicit_warmstart1_smoke_r1_1/`
- result:
  - stable
  - `loss_total = 0.571912`
  - old `templatepushb.step8` now warm-starts cleanly without encoder shape mismatch
  - missing keys are only the new semantic adaptor modules

## D. Main Bounded Stage5 Result

### Main run
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_train8explicit_warmstart20_r1_1/`
- best validation:
  - `step20 = 0.417454`

### Comparison
- `576` framewise temporal-conv route:
  - `0.417480`
- `578` flat short-temporal stack:
  - `0.548187`
- `578` center+delta repack:
  - `0.558221`
- `579` static center-vs-delta routing:
  - `0.544851`
- `580` explicit center-delta adaptor/gate:
  - `0.417454`

### Reading
- This is the first direct evidence that the stronger short-temporal contract itself was not the core problem.
- The bottleneck was the interface.
- Once the widened semantic features stop competing directly for encoder input space and instead enter through a gated hidden residual path, the widened route becomes survivable on bounded Stage5.

## E. Speech-Emergence Comparison

### Artifact
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapter_train8explicit_warmstart20_speechemergence_r1_1/`

### Baseline means
- `576` calm framewise route:
  - `decoded_zero_crossing_rate = 0.250777`
  - `decoded_spectral_centroid_hz = 4457.849121`
  - `decoded_spectral_high_band_energy_ratio = 0.305093`
  - `decoded_to_aligned_rms_ratio = 1.537689`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.885131`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.871404`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.981473`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.938219`
- `579` static center-delta split:
  - `decoded_zero_crossing_rate = 0.454449`
  - `decoded_spectral_centroid_hz = 9595.731445`
  - `decoded_spectral_high_band_energy_ratio = 0.722463`
  - `decoded_to_aligned_rms_ratio = 2.073328`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.630366`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.340550`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.255060`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.251343`
- `580` explicit adaptor/gate:
  - `decoded_zero_crossing_rate = 0.251473`
  - `decoded_spectral_centroid_hz = 4474.395508`
  - `decoded_spectral_high_band_energy_ratio = 0.305360`
  - `decoded_to_aligned_rms_ratio = 1.539419`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.884378`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.871184`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.979877`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.939731`

### Reading
- `580` does not look like `579` anymore.
- It snaps back almost exactly onto the calm `576` speech-emergence profile.
- So the adaptor/gate fixes the widened-contract collapse.
- But it also does not yet show a clearly new basin beyond `576`.

## F. Semantic Gate Probe

### Probe idea
- Since `580` ties `576` almost exactly, the key question becomes:
  - is the widened contract being used strongly
  - or only being softly tolerated

### Validation5 gate readout from `step20`
- full-train adaptor/gate checkpoint:
  - `periodic_semantic_gate_mean = 0.134489`
  - `noise_semantic_gate_mean = 0.099499`
  - `periodic_semantic_delta_abs_mean = 0.069620`
  - `noise_semantic_delta_abs_mean = 0.026756`
- reference branch hidden magnitude:
  - `periodic_hidden_abs_mean = 0.498547`
  - `noise_hidden_abs_mean = 0.323117`

### Reading
- The semantic sidecar is not zeroed out.
- But it is injected very conservatively relative to the base hidden scale.
- So the current adaptor/gate behaves more like a stabilizing narrow interface than a strong geometry-rewriting pathway.

## G. Adaptor-Only Freeze Control

### Probe idea
- test whether the widened contract can help as a purely additive residual on top of the old Stage5 route
- freeze the old scaffold
- train only:
  - `periodic_semantic_adapter`
  - `periodic_semantic_gate`
  - `periodic_semantic_proj`
  - `noise_semantic_adapter`
  - `noise_semantic_gate`
  - `noise_semantic_proj`

### Artifact
- run:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepcatarget_whitened_temporalconv_fidelity_step8_centerdeltaadapteronly_train8explicit_warmstart20_r1_1/`

### Result
- best validation:
  - `step20 = 0.511409`
- trainable parameter count:
  - `16`
- mean gate readout at `step20`:
  - `periodic_semantic_gate_mean = 0.242344`
  - `noise_semantic_gate_mean = 0.205593`
  - `periodic_semantic_delta_abs_mean = 0.237388`
  - `noise_semantic_delta_abs_mean = 0.267270`

### Reading
- Adaptor-only training overuses the semantic path and hurts held-out validation.
- So the current widened contract is not yet something that can simply be bolted onto the old calm route as an additive residual.
- Coordinated co-adaptation with part of the old Stage5 path is still required.

## Main Conclusion
- `580` changes the diagnosis materially:
  - the stronger short-temporal contract is not inherently doomed on Stage5
  - the real issue was the lack of an explicit interface layer
- But `580` also draws a hard boundary around the next step:
  - explicit adaptor/gate is necessary
  - current adaptor/gate is still mostly conservative
  - recovered bounded loss does not yet prove the widened geometry is being used strongly enough to open a new speech-structural regime
- The next branch should therefore stay at the interface level:
  - keep the adaptor/gate baseline from `580`
  - increase temporal expressivity or fusion strength around the adaptor
  - compare every new branch against both:
    - `580` full-train adaptor baseline
    - `580` adaptor-only freeze negative control

