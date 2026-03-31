# 549 Stage5 Step2 Paired Listening Bundle Preparation Report

## Summary
- This round executes the next bounded move after `548`.
- No new training was opened.
- Instead, a paired manual-review bundle is now prepared for the only still-interesting comparison left in the current focused regularizer family:
  - matched `step2` plain continuation control
  - matched `step2` hard-pair focused regularizer
- The new paired bundle is materialized at:
  - `reports/runtime/stage5_paired_listening_spectrogram_review_bundle_reviewslice_step2_control_vs_hardpairspeca_round1_1/stage5_paired_listening_spectrogram_review_bundle.json`
  - `reports/runtime/stage5_paired_listening_spectrogram_review_bundle_reviewslice_step2_control_vs_hardpairspeca_round1_1/stage5_paired_listening_spectrogram_review_bundle.md`
- Scope is intentionally restricted to the `4` records that matter for the next decision:
  - hard blocker pair:
    - `target::chapter3_26_firefly_114`
    - `target::chapter4_7_firefly_105`
  - near-open control:
    - `target::chapter3_30_firefly_132`
  - sidecar border case:
    - `target::no_text_voice/chapter3_18_firefly_101`

## Bundle Contents
- For each of the `4` selected records, the paired bundle now includes both variants side by side:
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
  - explicit `focused_minus_control` deltas for the main scalar sidecars

## Machine Preread
- The reason this paired bundle is the right next review object is now clear:
  - `548` already showed that the focused family has no durable advantage
  - the only remaining machine-side difference is a small transient `step2` drop in mean decoded peak-set Jaccard
- On the actual paired `step2` artifacts, the two variants are almost identical on the per-record metrics that matter most:
  - `114 decoded_frame_template_cosine_mean`:
    - control `0.968254`
    - focused `0.968285`
  - `105 decoded_frame_template_cosine_mean`:
    - control `0.949399`
    - focused `0.949434`
  - `132 decoded_frame_template_cosine_mean`:
    - control `0.908469`
    - focused `0.908523`
  - `132 decoded_frame_rms_to_aligned_frame_rms_corr`:
    - control `0.907614`
    - focused `0.907683`
- The only material machine-side distinction remains aggregate decoded peak sharing from `548`:
  - control mean decoded peak-set Jaccard `0.628687`
  - focused `0.565253`
- But even there:
  - hard-pair `114/105` decoded peak-set Jaccard remains unchanged at `0.6`
  - export status remains identical at `0/5 auto_reject + 5/5 review_required`

## Review Questions
- The paired bundle narrows the next human decision to exactly these questions:
  - does focused `step2` produce any audible or visible record-specific separation on `114` and `105` that control `step2` does not
  - does focused `step2` preserve `132` at least as well as control `step2`
  - does `101` remain only a sidecar border case rather than a misleading success cue

## Decision
- Keep:
  - the new paired `step2` bundle as the immediate next human-review artifact
- Do not keep:
  - any plan to continue the current focused logspec regularizer family before this paired review is completed
  - any wording that treats the small `step2` machine-side de-sharing signal as enough on its own

## Recommended Next Action
- The next pass should now be bounded manual review on:
  - `reports/runtime/stage5_paired_listening_spectrogram_review_bundle_reviewslice_step2_control_vs_hardpairspeca_round1_1`
- The stop rule is narrow:
  - if focused `step2` does not sound or look meaningfully more record-specific than control `step2`, retire the current focused regularizer family
  - if `132` is even slightly worse by human judgment, retire the family immediately
