# 525 Stage5 Review-Slice VUV Retention Counterfactual Probe Report

## Summary
- This round added a bounded counterfactual probe on the same `5`-record `fusionbranchmeancontrast_residualshape_scale050` review slice:
  - `analyze-stage5-nores-vuv-retention-probe`
- The probe does not retrain anything.
- It only perturbs `waveform_frame_logits` after the current checkpoint already produced:
  - `waveform_decoder_base_logits`
  - `waveform_residual_shape_delta`
- The practical question was:
  - is the current review slice missing an unvoiced direction entirely
  - or is there still some local leverage if unvoiced emphasis is made more explicit

## Code Change
- Added reusable probe module:
  - `src/v5vc/stage5_vuv_retention_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-vuv-retention-probe`

## Probe Run
- Review bundle:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Audio export manifests:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_vuv_retention_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_retention_probe.json`
  - `reports/runtime/stage5_vuv_retention_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_retention_probe.md`

## Variants
- `baseline`
  - original checkpoint path
- `unvoiced_centered_gain150`
  - `1.5x` centered logit contrast on target-side unvoiced frames
- `unvoiced_centered_gain200`
  - `2.0x` centered logit contrast on target-side unvoiced frames
- `voiced_shrink090__unvoiced_centered_gain150`
  - voiced `0.9x`, unvoiced `1.5x` centered contrast
- `residual_unvoiced_gain300`
  - `3.0x` residual-shape delta on target-side unvoiced frames only
- `residual_unvoiced_gain300__unvoiced_centered_gain150`
  - combine both manipulations

## Aggregate Findings
- Baseline:
  - waveform-frames mean `vuv` high-band gap = `-0.003187`
  - decoded mean `vuv` high-band gap = `-0.001538`
- Best waveform-frames rescue:
  - `residual_unvoiced_gain300`
  - waveform-frames mean `vuv` high-band gap = `0.003254`
  - gain vs baseline = `+0.006441`
- This same best variant also makes all `5/5` record-level waveform-frames `vuv` high-band gaps positive:
  - `0.002877`
  - `0.000700`
  - `0.003718`
  - `0.004895`
  - `0.004080`
- In contrast, the centered-logit variants do not rescue the local collapse:
  - `unvoiced_centered_gain150`: waveform-frames mean `-0.009062`
  - `unvoiced_centered_gain200`: waveform-frames mean `-0.009912`
  - voiced-shrink plus unvoiced-gain: waveform-frames mean `-0.010401`
- Decoded-side means do improve under several variants, but that is not the same as fixing the main localized sink:
  - best decoded mean comes from `residual_unvoiced_gain300__unvoiced_centered_gain150 = 0.023175`
  - yet waveform-frames mean is still slightly negative at `-0.001072`
- No variant changes the current machine status class:
  - `auto_reject_count = 0`
  - `review_required_count = 5`
  - for every tested variant

## Reading
- The result is not:
  - a training-free fix
  - or a claim that the route is suddenly near-speech
- The result is:
  - simple generic centered-logit boosting is the wrong local intervention
  - explicit unvoiced-focused residual injection has real local leverage on the active sink
- Therefore the current path does not look fully directionless.
- It does look under-equipped to express unvoiced structure through the current residual/noise-side route unless that route is made much more explicitly unvoiced-focused.

## Decision
- Keep the `524` conclusion that the main sink is `waveform_decoder_base_logits -> waveform_frames`.
- Refine the next move:
  - do not start from generic base-logit gain shaping
  - do not start from more gate-side tweaks
  - do start from an explicit unvoiced-focused residual or noise-side Stage5 probe
- The current best local design hint is:
  - a residual-shape or noise-oriented branch whose contribution is stronger and more selectively unvoiced than the current checkpoint provides
