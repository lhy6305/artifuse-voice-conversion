# 543 Stage5 TemplatepushB Listening Bundle And Machine Preread Report

## Summary
- This round executed the next bounded action after `542`:
  - do not open another training loop first
  - prepare a concrete full-slice listening and spectrogram bundle for the new `templatepush_b` frontier
  - record what the machine-side preread can already support without pretending that manual listening has been completed
- A new review bundle is now materialized at:
  - `reports/runtime/stage5_listening_spectrogram_review_bundle_reviewslice_full5_templatepushb_round1_1/stage5_listening_spectrogram_review_bundle.json`
  - `reports/runtime/stage5_listening_spectrogram_review_bundle_reviewslice_full5_templatepushb_round1_1/stage5_listening_spectrogram_review_bundle.md`
- The machine-side preread is now clear:
  - `templatepush_b` is not only a threshold-edge escape
  - full-slice source-filter metrics move materially in the same direction as the negative-gate gain
  - but the current result is still only:
    - `0/5 auto_reject`
    - `5/5 review_required`
  - therefore human listening is now justified and prepared, but still not replaceable by the machine-side preread

## Bundle Contents
- For each of the active `5` review-slice records, the bundle now includes:
  - `decoded.wav`
  - `aligned_target.wav`
  - `audit_proxy.wav`
  - `decoded.linear_spectrogram.png`
  - `aligned.linear_spectrogram.png`
  - machine sidecars:
    - `decoded_frame_template_cosine_mean`
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    - `vuv_contrast_summary`
    - `peak_spacing_summary`

## Machine Preread

### Aggregate reading
- Old `539` full-slice source-filter aggregate:
  - `decoded_template_cosine_mean = 0.985812`
  - `decoded_vuv_high_band_ratio_mean = 0.060665`
  - `decoded_vuv_centroid_gap_hz_mean = 531.285059`
  - `decoded_vuv_centroid_gap_suppressed_count = 3`
- New `templatepush_b` full-slice source-filter aggregate:
  - `decoded_template_cosine_mean = 0.968295`
  - `decoded_vuv_high_band_ratio_mean = 0.111866`
  - `decoded_vuv_centroid_gap_hz_mean = 1206.279004`
  - `decoded_vuv_centroid_gap_suppressed_count = 0`
- Reading:
  - the full-slice replay improves on both template-collapse and voiced/unvoiced contrast sidecars
  - this is materially stronger than merely slipping under one auto-reject threshold

### Record-level reading
- `target::chapter3_26_firefly_114`
  - `status: auto_reject_obvious_buzz -> review_required`
  - `decoded_frame_template_cosine_mean: 0.989296 -> 0.979284`
- `target::chapter4_7_firefly_105`
  - `status: auto_reject_obvious_buzz -> review_required`
  - `decoded_frame_template_cosine_mean: 0.985422 -> 0.968131`
- `target::no_text_voice/chapter3_18_firefly_101`
  - `status: auto_reject_obvious_buzz -> review_required`
  - `decoded_frame_template_cosine_mean: 0.985013 -> 0.967241`
- `target::chapter3_30_firefly_132`
  - `status: review_required -> review_required`
  - `decoded_frame_template_cosine_mean: 0.977717 -> 0.944919`
- `target::no_text_voice/chapter3_21_firefly_108`
  - held-out replay also improves:
    - `0.991612 -> 0.981898`

## What The Machine Preread Can And Cannot Claim
- What it can claim:
  - the new frontier is a real bounded gain over `539`
  - all `5` current review-slice records now deserve human listening rather than immediate machine rejection
  - the gain is structurally consistent across:
    - decoded template collapse
    - source-filter vuv contrast
    - spectral brightness and centroid sidecars
- What it cannot claim:
  - that any record is already speech-like by human judgment
  - that the route is open
  - that `review_required 5/5` means positive acceptance

## Decision
- Keep:
  - `templatepush_b` as the active bounded frontier
  - the new listening-plus-spectrogram bundle as the required next review artifact
- Retire:
  - any immediate plan to continue same-family training before bounded review
  - any wording that treats the current state as solved only because `auto_reject_count = 0`

## Recommended Next Action
- The next pass should be explicit bounded manual review on:
  - `reports/runtime/stage5_listening_spectrogram_review_bundle_reviewslice_full5_templatepushb_round1_1`
- The review question is now narrow:
  - are these `5` records still lower-energy buzz/template artifacts
  - or has the route crossed into genuine near-speech territory
- Only after that review should the project decide between:
  - promoting `templatepush_b` into a broader slice replay
  - or continuing another same-scope microfit
