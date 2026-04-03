# 574 Stage5 Waveframeencoder Bounded Integration And Normalized Upper-Bound Report

## Summary
- Date: `2026-04-02`
- Goal:
  - run the first matched bounded Stage5 comparison on the new deployable `waveform_frame_encoder_v1 -> waveform_geometry_code` route
  - compare it against both the no-code baseline and the existing analysis-only `wavepca16` upper bound on the same `train8 + validation5` slice
  - then remove a newly discovered confound by adding a `normalize_code=true` analysis-only upper-bound control
- Result:
  - the matched `train8 + validation5` dataset-loop comparison is now complete for:
    - `none`
    - deployable `waveform_geometry_code`
    - raw `wavepca16` upper bound
    - whitened `wavepca16` upper bound
  - a small infra extension was added so the PCA packet materializer can emit whitened codes directly via `--normalize-code`
  - the new normalized upper bound closes part of the gap to the deployable route, proving that Stage5 is sensitive to code distribution semantics
  - but packet-level fidelity against the whitened target remains weak, so the main bottleneck still sits upstream in producer-side code quality rather than in a pure Stage5 scale mismatch

## A. Matched `train8 + validation5` Stage5 Dataset-Loop Comparison
- Shared warm-start:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Shared training settings:
  - `num_steps = 20`
  - `packages_per_step = 2`
  - `validation_interval = 1`
  - `checkpoint_interval = 1`
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`

### Dataset indexes
- No-code baseline:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_none_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Deployable geometry code:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_geomcode_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Raw analysis-only upper bound:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepca16_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Whitened analysis-only upper bound:
  - `reports/runtime/stage5_train8val5_streaming_student_waveframeencoder_wavepca16norm_r1_1/offline_mvp_nores_vocoder_dataset_index.json`

### Validation outcomes at step20
- No-code baseline:
  - run: `reports/runtime/stage5_train8val5_waveframeencoder_none_warmstart20_r1_1/`
  - validation `loss_total = 0.433231`
- Deployable geometry code:
  - run: `reports/runtime/stage5_train8val5_waveframeencoder_geomcode_warmstart20_r1_1/`
  - validation `loss_total = 0.535322`
- Raw `wavepca16` upper bound:
  - run: `reports/runtime/stage5_train8val5_waveframeencoder_wavepca16_warmstart20_r1_1/`
  - validation `loss_total = 0.628067`
- Whitened `wavepca16` upper bound:
  - run: `reports/runtime/stage5_train8val5_waveframeencoder_wavepca16norm_warmstart20_r1_1/`
  - validation `loss_total = 0.569817`

### Immediate reading
- The deployable geometry-code route does not yet beat the no-code baseline on this first bounded held-out Stage5 comparison.
- The raw `wavepca16` upper bound also loses badly on the same held-out loss.
- Whitening the analysis-only upper bound improves it materially:
  - `0.628067 -> 0.569817`
- That means the old raw upper-bound comparison was partially confounded by code distribution semantics, not only by signal quality.

## B. Same-Slice Speech-Emergence Read
- Validation records:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`
  - `target::no_text_voice/chapter3_17_firefly_106`
  - `target::no_text_voice/chapter3_3_firefly_110`

### No-code baseline
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_none_warmstart20_speechemergence_r1_1/`
- aggregate:
  - `decoded_zero_crossing_rate = 0.223429`
  - `decoded_spectral_centroid_hz = 3955.553223`
  - `decoded_spectral_high_band_energy_ratio = 0.254494`
  - `decoded_to_aligned_rms_ratio = 1.468401`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.967185`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.962079`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.887496`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.869676`

### Deployable geometry code
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_geomcode_warmstart20_speechemergence_r1_1/`
- aggregate:
  - `decoded_zero_crossing_rate = 0.457168`
  - `decoded_spectral_centroid_hz = 10061.893555`
  - `decoded_spectral_high_band_energy_ratio = 0.757599`
  - `decoded_to_aligned_rms_ratio = 1.958084`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.758089`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.817157`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.788139`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.659590`

### Raw `wavepca16` upper bound
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepca16_warmstart20_speechemergence_r1_1/`
- aggregate:
  - `decoded_zero_crossing_rate = 0.478114`
  - `decoded_spectral_centroid_hz = 10462.314453`
  - `decoded_spectral_high_band_energy_ratio = 0.784186`
  - `decoded_to_aligned_rms_ratio = 2.318634`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.298477`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.374305`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.371296`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.218995`

### Whitened `wavepca16` upper bound
- probe:
  - `reports/runtime/stage5_train8val5_waveframeencoder_wavepca16norm_warmstart20_speechemergence_r1_1/`
- aggregate:
  - `decoded_zero_crossing_rate = 0.470059`
  - `decoded_spectral_centroid_hz = 10340.246094`
  - `decoded_spectral_high_band_energy_ratio = 0.771153`
  - `decoded_to_aligned_rms_ratio = 1.868267`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.564513`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.674031`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.553939`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.333881`

### Reading
- Whitening the upper bound improves several Stage5-facing metrics relative to the raw upper bound:
  - `decoded_to_aligned_rms_ratio: 2.318634 -> 1.868267`
  - `predicted_activity_to_aligned_frame_rms_corr: 0.298477 -> 0.564513`
  - `decoded_frame_rms_to_aligned_frame_rms_corr: 0.374305 -> 0.674031`
  - validation `loss_total: 0.628067 -> 0.569817`
- So the Stage5 consumer is genuinely sensitive to the code distribution semantics, not just to the code family label.
- But whitening does not erase the larger pattern:
  - both upper-bound routes remain very bright / high-band heavy
  - both still stay worse than the no-code baseline on held-out objective
  - the deployable route still does not approach the stronger structure-facing upper-bound behavior cleanly

## C. Producer-Side Fidelity Against The Whitened Target
- A direct packet-level comparison was run between:
  - deployable `fine_structure_code.waveform_geometry_code`
  - the same PCA codebook projected with `normalize_code=true`
- Comparison scope:
  - fixed validation5
  - train8

### Fixed validation5 aggregate
- `cosine_mean = -0.016703`
- `mae = 0.858329`
- `rmse = 1.191049`
- `pred_std = 0.419583`
- `tgt_std = 1.110186`
- `pred_frame_delta_l2_mean = 1.916465`
- `tgt_frame_delta_l2_mean = 5.431798`
- `pred_template_cosine_mean = 0.137658`
- `tgt_template_cosine_mean = 0.046185`
- `record_mean_code_cosine_to_own_target = -0.055464`
- `record_mean_code_best_other_cosine = 0.308317`
- `record_mean_code_margin_vs_best_other = -0.363781`

### Train8 aggregate
- `cosine_mean = 0.115071`
- `mae = 0.731024`
- `rmse = 1.076103`
- `pred_std = 0.431100`
- `tgt_std = 1.045329`
- `pred_frame_delta_l2_mean = 2.103812`
- `tgt_frame_delta_l2_mean = 5.117176`
- `pred_template_cosine_mean = 0.131635`
- `tgt_template_cosine_mean = 0.020160`
- `record_mean_code_cosine_to_own_target = 0.062472`
- `record_mean_code_best_other_cosine = 0.330457`
- `record_mean_code_margin_vs_best_other = -0.267985`

### Reading
- The deployable code is still much flatter than the whitened target:
  - lower variance
  - much weaker adjacent-frame dynamics
  - much higher template similarity
- Record identity is not yet preserved robustly in code space:
  - mean-record-code similarity to the true target is still worse than to the best wrong record on both slices
- So the main producer-side issue is not just small residual error.
- The deployable code is still missing the amplitude, temporal movement, and record-specific separation that the whitened upper bound has.

## D. Infra Change
- Files changed:
  - `src/v5vc/streaming_student/fine_structure_code_packet.py`
  - `src/v5vc/cli.py`
- New CLI capability:
  - `manage.py materialize-streaming-student-fine-structure-pca-packet-export --normalize-code`
- Purpose:
  - emit analysis-only `waveform_pca_code` in the whitened `code_std`-normalized space
  - make future upper-bound comparisons line up with deployable producer-side supervision semantics

## Decision
- Keep:
  - `waveform_frame_encoder_v1` as the active producer-side line
  - the whitened upper bound as the new reference consumer alongside the raw upper bound
- New judgment:
  - Stage5 code-distribution semantics do matter; the old raw upper-bound comparison was partially confounded
  - but the larger blocker is still upstream producer fidelity, not a pure Stage5 scale mismatch
- Next valid step:
  - improve producer-side code fidelity in the whitened code space
  - specifically target:
    - higher code variance
    - stronger frame-to-frame code dynamics
    - better record-specific separation margin
  - do not reopen a generic Stage5-local regularizer sweep before those producer-side code metrics move
