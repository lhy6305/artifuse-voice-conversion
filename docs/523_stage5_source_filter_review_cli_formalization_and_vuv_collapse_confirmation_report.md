# 523 Stage5 Source-Filter Review CLI Formalization And VUV Collapse Confirmation Report

## Summary
- This round converted the earlier ad-hoc Stage5 spectrogram and vuv review into a reusable CLI probe:
  - `analyze-stage5-nores-source-filter-review`
- The new probe reads:
  - the existing Stage5 human-review bundle
  - one or more Stage5 dataset indexes
  - the original Stage5 training packages for the reviewed records
- It then exports:
  - paired decoded and aligned spectrogram PNGs
  - voiced vs unvoiced spectral sidecars
  - resonance peak-spacing sidecars
  - a machine-readable JSON plus markdown summary
- The formalized probe reproduces the same practical conclusion as the earlier ad-hoc stop:
  - the current `fusionbranchmeancontrast_residualshape_scale050` review-required slice still shows collapsed vuv separation
  - the route is still buzz and not near-speech

## Code Change
- Added reusable probe module:
  - `src/v5vc/stage5_source_filter_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-source-filter-review`
- CLI wiring lives in:
  - `src/v5vc/cli.py`

## Probe Run
- Review bundle:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Dataset indexes:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8/streaming_student_stage5_dataset_index.json`
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_se8/streaming_student_stage5_dataset_index.json`
- Output:
  - `reports/runtime/stage5_source_filter_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_source_filter_review.json`
  - `reports/runtime/stage5_source_filter_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_source_filter_review.md`

## Aggregate Findings
- `record_count = 5`
  - `primary_localization = vuv_separation_collapsed`
- Aggregate vuv high-band contrast:
  - decoded mean `unvoiced_minus_voiced_high_band_ratio = -0.001537`
  - aligned mean `unvoiced_minus_voiced_high_band_ratio = 0.099338`
- Aggregate vuv centroid contrast:
  - decoded mean `unvoiced_minus_voiced_centroid_hz = 208.908496`
  - aligned mean `unvoiced_minus_voiced_centroid_hz = 1243.492761`
- Support counts:
  - decoded non-positive vuv high-band gap in `4/5`
  - aligned positive vuv high-band gap in `5/5`
  - decoded centroid-gap suppression in `4/5`
- The remaining `1/5` decoded record is not a rescue signal:
  - it only reaches a tiny positive decoded vuv high-band gap
  - it still remains far below the aligned target contrast

## Reading
- This formalized probe does not replace human spectrogram reading.
- It does remove the need to keep rebuilding one-off scripts for the same Stage5 failure family.
- The machine result now consistently supports the current human stop conclusion:
  - the current residual-shape `scale050` route is still not speech-like
  - the next Stage5 move should target vuv separation and source-filter geometry directly
- Peak-spacing remains only a sidecar:
  - useful for resonance regularity hints
  - not yet strong enough to act as the main decision metric by itself

## Decision
- Keep `fusionbranchmeancontrast_residualshape_scale050` only as the narrow best current fixed-input Stage5 family.
- Do not present its current review-required slice as near-speech.
- Use the new CLI probe as the default follow-up tool for any blocker-localized Stage5 residual-shape diagnosis before opening another family screen.
