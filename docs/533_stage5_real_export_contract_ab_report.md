# 533 Stage5 Real Export Contract AB Report

## Summary
- This round promoted the reconstruction positive control into the real export path.
- A new export-side `reconstruction_contract_mode` was added so `decoded.wav` can now be rendered with:
  - `hann_window_sum_norm`
  - `rectangular_overlap_count_norm`
- The bounded AB was run on the same `delta_direct_v1` review slice with predicted activity gate disabled to stay aligned with the already-localized `decoded_no_gate` sink.
- The result is a real split:
  - `rectangular_overlap_count_norm` keeps the decoded `vuv` rescue when promoted from probe to real export
  - but it still does not open the route, because the machine buzz gate now rejects all `5/5`

## Code Change
- Added export-side reconstruction contract selection:
  - `src/v5vc/nores_vocoder_audio_export.py`
- Added CLI flag:
  - `--reconstruction-contract-mode`
  - wiring in `src/v5vc/cli.py`
- Also updated source-filter review replay so it can read decoded and aligned paths from the active export manifest:
  - `src/v5vc/stage5_source_filter_probe.py`

## Real Export AB
- Hann no-gate export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_hanngateoff_round1_1/nores_vocoder_audio_export.md`
- Rectangular no-gate export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/nores_vocoder_audio_export.md`

## Review Replays
- Hann no-gate `vuv-path` replay:
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_deltadirect_hanngateoff_round1_1/stage5_vuv_path_review.md`
- Rectangular no-gate `vuv-path` replay:
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/stage5_vuv_path_review.md`
- Hann no-gate source-filter replay:
  - `reports/runtime/stage5_source_filter_review_bundle_reviewslice_noisehidden_deltadirect_hanngateoff_round1_1/stage5_source_filter_review.md`
- Rectangular no-gate source-filter replay:
  - `reports/runtime/stage5_source_filter_review_bundle_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/stage5_source_filter_review.md`

## Hann No-Gate Reading
- Export-side buzz summary:
  - `auto_reject_count = 1/5`
  - `review_required_count = 4/5`
- Corrected `vuv-path` replay:
  - waveform-frames aggregate `vuv` gap: `0.002642`
  - decoded aggregate `vuv` gap: `-0.066445`
  - primary localization:
    - `decoded_waveform_vuv_separation_lost_after_frame_projection`
- Source-filter replay:
  - primary localization:
    - `vuv_separation_collapsed`

## Rectangular No-Gate Reading
- Export-side buzz summary:
  - `auto_reject_count = 5/5`
  - `review_required_count = 0/5`
- Corrected `vuv-path` replay:
  - waveform-frames aggregate `vuv` gap: `0.002642`
  - decoded aggregate `vuv` gap: `0.017643`
  - decoded non-positive count: `0/5`
  - primary localization:
    - `needs_manual_review`
- Source-filter replay:
  - primary localization:
    - `needs_more_localization`
  - decoded aggregate `vuv` high-band gap:
    - `0.017643`
  - decoded aggregate centroid gap:
    - `78.922558`
  - decoded template cosine mean:
    - `0.99003`

## Interpretation
- The positive part is real:
  - rectangular reconstruction keeps the decoded `vuv` rescue when moved from probe into actual `decoded.wav`
  - so the earlier reconstruction-contract conclusion was not only a probe artifact
- But the route is still not open:
  - machine buzz summary gets worse, not better
  - `rectangular` moves the route out of the old `vuv_separation_collapsed` basin
  - but leaves it in a different strongly auto-rejected basin, consistent with extreme template-like decoded frames
- This is an inference from the metrics:
  - the dominant remaining blocker is now no longer `vuv` collapse
  - it is more likely frame-level template collapse or another buzz-like regularity that the current heuristic still catches

## Decision
- Keep `rectangular_overlap_count_norm` as the first real export contract that preserves the decoded `vuv` rescue.
- Retire the idea that reconstruction-contract AB is still the main unknown.
- The new main unknown is:
  - why the rectangular decoded route remains `5/5 auto_reject` even after leaving the old `vuv` collapse basin

## Recommended Next Action
- Do a bounded follow-up on the rectangular real export route itself:
  - listen to the `5` decoded outputs
  - decompose the current buzz heuristic terms
  - localize whether the remaining blocker is mainly template collapse, adjacent-frame over-regularity, or another non-`vuv` artifact
- Do not go back to:
  - Hann-family normalization sweeps
  - gate-side tuning
  - `noise_hidden` sourcing
  - or residual-adapter feature routing
