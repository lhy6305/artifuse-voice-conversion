# 521 Stage5 Fusion Residualshape Scale050 Human Review Bundle Report

## Summary
- The current best fixed-input Stage5 consumer-side candidate is:
  - `fusionbranchmeancontrast_residualshape_scale050`
- This family is not decoded-ready yet, but it is the first current fixed-input Stage5 family that produces a non-empty `review_required` slice on both widened screens:
  - `tv8`: `5/8 auto_reject`, `3/8 review_required`
  - `se8`: `6/8 auto_reject`, `2/8 review_required`
- This round packages those `5` non-auto-reject outputs into a single human-review bundle so the next decision does not depend only on machine heuristics.

## Bundle Artifact
- JSON:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Markdown:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.md`

## Included Records

### tv8 review_required records
- `target::chapter3_30_firefly_132`
  - decoded:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/target__chapter3_30_firefly_132__decoded.wav`
  - aligned target:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/target__chapter3_30_firefly_132__aligned_target.wav`
- `target::chapter3_26_firefly_114`
  - decoded:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/target__chapter3_26_firefly_114__decoded.wav`
  - aligned target:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/target__chapter3_26_firefly_114__aligned_target.wav`
- `target::chapter4_7_firefly_105`
  - decoded:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/target__chapter4_7_firefly_105__decoded.wav`
  - aligned target:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/target__chapter4_7_firefly_105__aligned_target.wav`

### se8 review_required records
- `target::no_text_voice/chapter3_18_firefly_101`
  - decoded:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/target__no_text_voice_chapter3_18_firefly_101__decoded.wav`
  - aligned target:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/target__no_text_voice_chapter3_18_firefly_101__aligned_target.wav`
- `target::no_text_voice/chapter3_21_firefly_108`
  - decoded:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/target__no_text_voice_chapter3_21_firefly_108__decoded.wav`
  - aligned target:
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/target__no_text_voice_chapter3_21_firefly_108__aligned_target.wav`

## Suggested Listening Order
- First:
  - `target::no_text_voice/chapter3_18_firefly_101`
  - rationale:
    lowest current `spectral_high_band_energy_ratio_gap = 0.185457`
    and lowest `spectral_centroid_gap_hz = 3176.42598` among the review-required slice
- Second:
  - `target::chapter3_30_firefly_132`
  - rationale:
    strongest current `tv8` review-required balance with
    `decoded_frame_template_cosine_mean = 0.977174`
    and `spectral_high_band_energy_ratio_gap = 0.257854`
- Third:
  - `target::chapter3_26_firefly_114`
  - rationale:
    strongest current envelope following among the `tv8` review-required slice, but still more template-collapsed than `chapter3_30_firefly_132`
- Fourth:
  - `target::chapter4_7_firefly_105`
- Fifth:
  - `target::no_text_voice/chapter3_21_firefly_108`
  - rationale:
    still review-required, but currently the weakest review-required case because
    `decoded_frame_rms_to_aligned_frame_rms_corr = 0.289677`
    and brightness remains relatively high

## Decision
- Human review is now justified and useful on this line.
- The right listening scope is not all decoded outputs.
- The right listening scope is the current `5`-record review-required slice under `fusionbranchmeancontrast_residualshape_scale050`.
- After listening review, the next Stage5 decision should use both:
  - the machine screen
  - and the human quality read on this narrow review-required slice

## Recommended Next Action
- Listen to the `5` review-required records in the bundled order above.
- Use that listening result to decide whether:
  - the residual-shape family is genuinely approaching speech
  - or it is only escaping auto-reject heuristics without becoming perceptually useful
