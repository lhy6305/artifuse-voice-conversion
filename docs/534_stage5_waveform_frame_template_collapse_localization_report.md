# 534 Stage5 Waveform-Frame Template Collapse Localization Report

## Summary
- This round executed the next bounded follow-up after `533`.
- The remaining question was:
  - after rectangular reconstruction removes the old decoded `vuv` collapse
  - does the remaining `5/5 auto_reject` basin come mainly from:
    - a new decode-side artifact introduced by the rectangular contract
    - or a template-collapse pattern that already exists in `waveform_frames`
- The new result is now clear on the same `delta_direct_v1` review slice:
  - the dominant remaining blocker is already present in `waveform_frames`
  - rectangular reconstruction does not create that blocker
  - it mostly preserves the existing frame-level template-collapse while also preserving the decoded `vuv` rescue

## Code Change
- Promoted the new review probe into a real CLI:
  - `src/v5vc/stage5_waveform_frame_template_probe.py`
  - `src/v5vc/cli.py`
- Fixed a route-aggregate bug in the new probe so per-route metrics are accumulated correctly instead of being written into a temporary copy.

## Probe Run
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-frame-template-collapse-review --output-dir reports/runtime/stage5_wf_template_review_deltadirect_hann_vs_rect_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_hanngateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_wf_template_review_deltadirect_hann_vs_rect_r1_1/stage5_waveform_frame_template_collapse_review.json`
  - `reports/runtime/stage5_wf_template_review_deltadirect_hann_vs_rect_r1_1/stage5_waveform_frame_template_collapse_review.md`

## Aggregate Reading
- Stage-level metrics before reconstruction already satisfy the existing buzz-gate template-collapse thresholds:
  - `waveform_frames_template_cosine_mean = 0.992189`
  - `waveform_frames_adjacent_cosine_mean = 0.999529`
  - `waveform_frames_template_cosine_gap_vs_aligned = 0.959170`
- At the same time, `waveform_frames` still keep the repaired review-slice `vuv` separation:
  - `waveform_frames_vuv_high_band_ratio_gap = 0.002642`
- Real exported route comparison:
  - Hann no-gate:
    - `decoded_template_cosine_mean = 0.984943`
    - `decoded_vuv_high_band_ratio_gap = -0.066445`
    - `auto_reject_count = 1/5`
  - Rectangular no-gate:
    - `decoded_template_cosine_mean = 0.990030`
    - `decoded_vuv_high_band_ratio_gap = 0.017643`
    - `auto_reject_count = 5/5`
- Important comparison:
  - rectangular keeps the decoded template-collapse almost unchanged relative to `waveform_frames`
    - `template_gap_vs_waveform_frames = -0.002159`
  - Hann also keeps the same collapse family, only slightly weaker on this metric
    - `template_gap_vs_waveform_frames = -0.007246`
  - the large route split is not template-collapse
  - the large route split is only the decoded `vuv` path:
    - Hann `-0.066445`
    - rectangular `0.017643`

## Record-Level Reading
- All `5/5` reviewed records already satisfy the waveform-frame template-collapse condition before any reconstruction contract is applied.
- Representative examples:
  - `target::chapter3_26_firefly_114`
    - waveform-frames template cosine: `0.992726`
    - rectangular decoded template cosine: `0.991770`
    - rectangular decoded `vuv` gap: `0.025382`
  - `target::chapter4_7_firefly_105`
    - waveform-frames template cosine: `0.990351`
    - rectangular decoded template cosine: `0.989377`
    - rectangular decoded `vuv` gap: `0.017050`
  - `target::chapter3_30_firefly_132`
    - waveform-frames template cosine: `0.988225`
    - rectangular decoded template cosine: `0.985855`
    - rectangular decoded `vuv` gap: `0.023589`

## Interpretation
- `533` already proved that rectangular reconstruction is a real decoded positive control for `vuv` separation.
- `534` now proves that the remaining rectangular-route failure is not primarily:
  - a Hann-vs-rectangular reconstruction question
  - a decoded-only template-collapse introduced by the new export contract
- The sharper conclusion is:
  - `waveform_frames` are already highly template-collapsed before reconstruction
  - rectangular reconstruction mostly preserves that pre-existing collapse while also preserving decoded `vuv` separation
  - therefore the remaining blocker moved upstream again, but not all the way back to `base_logits`
  - the active question is now why `waveform_frames` themselves are almost fixed-template even after the `noise_hidden -> residual` local rescue

## Decision
- Keep `rectangular_overlap_count_norm` as the validated decoded positive control for the repaired `vuv` path.
- Retire the idea that the current `5/5 auto_reject` basin is mainly another reconstruction-contract mystery.
- Replace it with the sharper mainline statement:
  - the remaining blocker is `waveform_frames` template-collapse that survives both Hann and rectangular export

## Recommended Next Action
- Open the next bounded probe directly on the `waveform_frames` generator path.
- Prioritize:
  - `waveform_decoder_base_logits -> waveform_frames` amplitude and diversity shaping
  - the current waveform template and adjacent-cosine objective family
  - whether the residual direct-delta rescue restores `vuv` contrast without restoring frame diversity
- Do not go back to:
  - more Hann-family reconstruction sweeps
  - gate-side tuning
  - or more rectangular-vs-Hann export comparison without a new upstream signal
