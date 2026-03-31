# 524 Stage5 Review-Slice VUV Path Localization Probe Report

## Summary
- This round kept the same `5`-record `fusionbranchmeancontrast_residualshape_scale050` review slice and added a reusable path-level probe:
  - `analyze-stage5-nores-vuv-path-review`
- The new probe reuses:
  - the existing human-review bundle
  - the existing Stage5 audio export manifests
  - the existing checkpoint and training-package mappings
- It localizes where the current vuv separation collapses inside the active fused-single waveform path instead of only at the final decoded waveform.

## Code Change
- Added reusable probe module:
  - `src/v5vc/stage5_vuv_path_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-vuv-path-review`
- Also refreshed the earlier source-filter review artifact under the same `vuv` naming convention:
  - `reports/runtime/stage5_source_filter_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_source_filter_review.json`

## Probe Run
- Review bundle:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Audio export manifests:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_vuv_path_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_path_review.json`
  - `reports/runtime/stage5_vuv_path_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_path_review.md`

## Aggregate Findings
- `record_count = 5`
  - aggregate `primary_localization = waveform_frames_vuv_separation_lost_after_base_logits`
- Aggregate high-band vuv contrast:
  - aligned mean `unvoiced_minus_voiced_high_band_ratio = 0.099338`
  - base-logits mean `unvoiced_minus_voiced_high_band_ratio = -0.000914`
  - waveform-frames mean `unvoiced_minus_voiced_high_band_ratio = -0.003187`
  - decoded mean `unvoiced_minus_voiced_high_band_ratio = -0.001537`
- Support counts:
  - `base_logits_vuv_separation_missing = 2/5`
  - `waveform_frames_vuv_separation_lost_after_base_logits = 3/5`
  - `waveform_frames_vuv_nonpositive_count = 5/5`
  - `residual_shape_delta_vuv_nonpositive_count = 5/5`
- Gate and residual sidecars are also consistently negative:
  - `noise_gate_not_dominant_on_unvoiced_frames = 5/5`
  - `residual_shape_delta_not_unvoiced_focused = 5/5`

## Reading
- The new probe narrows the old decoded-only statement into a path statement:
  - `2/5` records already lose vuv separation at `waveform_decoder_base_logits`
  - the other `3/5` keep only tiny positive base-logits gaps:
    - `0.001311`
    - `0.001893`
    - `0.000754`
  - those tiny traces disappear immediately at `waveform_frames`
- Therefore the current review slice is not mainly failing at:
  - post-decode waveform rendering
  - predicted activity gating
  - or a residual-shape branch that is almost rescuing unvoiced structure
- The practical current sink is:
  - very weak or missing vuv contrast by `waveform_decoder_base_logits`
  - then full collapse by `waveform_decoder_base_logits -> waveform_frames`

## Decision
- Keep the earlier source-filter review CLI as the decoded-side negative confirmation.
- Use the new vuv-path review CLI as the default follow-up localization step on the same review slice before opening another Stage5 family screen.
- The next Stage5 move should target:
  - stronger vuv retention through `waveform_decoder_base_logits -> waveform_frames`
  - and explicit unvoiced emphasis, because neither `residual_shape_delta` nor the current gate balance is rescuing the slice
