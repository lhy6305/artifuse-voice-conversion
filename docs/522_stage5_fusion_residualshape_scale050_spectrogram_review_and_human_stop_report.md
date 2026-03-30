# 522 Stage5 Fusion Residualshape Scale050 Spectrogram Review And Human Stop Report

## Summary
- The current best fixed-input Stage5 consumer-side candidate remains:
  - `fusionbranchmeancontrast_residualshape_scale050`
- But the latest human review closes the remaining ambiguity:
  - the `5` current `review_required` outputs are still all buzz
  - they are not near-speech outputs
- This round therefore stops any attempt to describe the current `review_required` slice as a qualitatively promising speech-like route.
- A spectrogram review bundle was generated so the conclusion does not rely only on prose:
  - `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_spectrogram_review_bundle.json`
  - `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_spectrogram_review_bundle.md`

## Human Conclusion Incorporated
- Human review conclusion for the current `5`-record review-required slice:
  - all are still buzz
  - visible brightness variation does exist
  - but the spectrum still shows comb-like equally spaced resonances instead of speech-like formant distribution
  - `UV/V` remains not meaningfully separated:
    - sand-like bands and voiced-looking resonances are not clearly differentiated

## Spectrogram Bundle

### Bundle root
- `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1`

### Included paired spectrograms
- `target::chapter3_30_firefly_132`
  - decoded:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____chapter3_30_firefly_132/decoded.linear_spectrogram.png`
  - aligned:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____chapter3_30_firefly_132/aligned.linear_spectrogram.png`
- `target::chapter3_26_firefly_114`
  - decoded:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____chapter3_26_firefly_114/decoded.linear_spectrogram.png`
  - aligned:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____chapter3_26_firefly_114/aligned.linear_spectrogram.png`
- `target::chapter4_7_firefly_105`
  - decoded:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____chapter4_7_firefly_105/decoded.linear_spectrogram.png`
  - aligned:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____chapter4_7_firefly_105/aligned.linear_spectrogram.png`
- `target::no_text_voice/chapter3_18_firefly_101`
  - decoded:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____no_text_voice_chapter3_18_firefly_101/decoded.linear_spectrogram.png`
  - aligned:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____no_text_voice_chapter3_18_firefly_101/aligned.linear_spectrogram.png`
- `target::no_text_voice/chapter3_21_firefly_108`
  - decoded:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____no_text_voice_chapter3_21_firefly_108/decoded.linear_spectrogram.png`
  - aligned:
    `reports/runtime/stage5_spectrogram_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/target____no_text_voice_chapter3_21_firefly_108/aligned.linear_spectrogram.png`

## Machine Readout That Matches The Human Review

### UV/V contrast is largely collapsed on decoded outputs
- The current machine-side proxy uses `periodic_gate_target` as a voiced mask and compares decoded voiced vs unvoiced frame spectral summaries.
- Across the `5` review-required records, decoded `unvoiced_minus_voiced_high_band_ratio` is effectively zero or negative:
  - `target::no_text_voice/chapter3_18_firefly_101`: `-0.008514`
  - `target::no_text_voice/chapter3_21_firefly_108`: `-0.001532`
  - `target::chapter3_30_firefly_132`: `-0.009926`
  - `target::chapter3_26_firefly_114`: `-0.008607`
  - `target::chapter4_7_firefly_105`: `-0.003956`
- The aligned targets do show the expected positive unvoiced-high-band lift:
  - `0.229597`
  - `0.058522`
  - `0.250189`
  - `0.459932`
  - `0.383502`
- This strongly supports the human claim that the current decoded route does not meaningfully separate unvoiced from voiced texture.

### Decoded voiced/unvoiced centroid separation is also much flatter than the targets
- Example target-side unvoiced-minus-voiced centroid differences:
  - `target::chapter3_30_firefly_132`: `2756.228028 Hz`
  - `target::chapter3_26_firefly_114`: `2964.080322 Hz`
  - `target::chapter4_7_firefly_105`: `2403.309326 Hz`
- The decoded counterparts are much smaller:
  - `1027.005371 Hz`
  - `37.37793 Hz`
  - `339.386719 Hz`
- This is consistent with the current decoded spectrum not carving out a real voiced/unvoiced contrast.

### Comb-like resonance reading remains a human-first conclusion
- A simple peak-spacing summary is included in the spectrogram bundle JSON.
- It is useful as a rough sidecar, but not yet strong enough to replace direct visual spectrogram reading.
- The definitive current conclusion about equally spaced resonance bands therefore remains:
  - human-confirmed by spectrogram reading
  - not yet fully captured by a robust machine metric

## Decision
- Keep `fusionbranchmeancontrast_residualshape_scale050` as the best current Stage5 consumer-side candidate in the narrow comparative sense.
- But do not describe it as near-speech or as a route that merely needs more listening confidence.
- The current widened `review_required` slice is still qualitatively failed.

## Recommended Next Action
- Stop spending time on more generic gate-level or family-level screens first.
- The next Stage5 move should target the now clearer structural diagnosis:
  - source-filter geometry / comb-like resonance behavior
  - and explicit voiced-vs-unvoiced separation in the decoded waveform path
