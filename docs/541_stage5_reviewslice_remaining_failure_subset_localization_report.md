# 541 Stage5 Review-Slice Remaining-Failure Subset Localization Report

## Summary
- This round executed the next bounded action after `540`:
  - keep the corrected `539` producer-plus-interface checkpoint fixed
  - keep the active real export route fixed at `rectangular_overlap_count_norm`
  - localize the remaining `3/5 auto_reject` records against the `2/5 review_required` records on the same corrected frontier
- Two reusable review CLIs were widened just enough for this comparison:
  - `analyze-stage5-nores-source-filter-review`
  - `analyze-stage5-nores-vuv-path-review`
- Both now accept:
  - `--target-record-ids`
  - `--prefer-audio-export-status`
- The new conclusion is:
  - the remaining failure set is not a single unresolved `vuv` collapse family
  - the remaining `3` auto-reject records split into:
    - a hard no-gate template-collapse pair:
      - `target::chapter3_26_firefly_114`
      - `target::chapter4_7_firefly_105`
    - a gate-sensitive borderline record:
      - `target::no_text_voice/chapter3_18_firefly_101`
  - the current `2` review-required records are not both positive controls:
    - `target::chapter3_30_firefly_132` is the cleaner near-open control
    - `target::no_text_voice/chapter3_21_firefly_108` is still heavily collapsed and only escapes auto-reject because the envelope-following side of the negative gate does not trigger

## Code Changes
- `src/v5vc/stage5_source_filter_probe.py`
  - add `target_record_ids` filtering
  - add optional audio-export status override
- `src/v5vc/stage5_vuv_path_probe.py`
  - add `target_record_ids` filtering
  - add optional audio-export status override
- `src/v5vc/cli.py`
  - wire `--target-record-ids`
  - wire `--prefer-audio-export-status`
  - for both review commands above

## Probe Runs

### Auto-reject subset `3`
- Source-filter review:
  - `.\python.exe manage.py analyze-stage5-nores-source-filter-review --output-dir reports/runtime/stage5_source_filter_review_reviewslice_producerinterface_rect_fail3_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --dataset-indexes reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_producerinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json --prefer-audio-export-status --target-record-ids target::chapter3_26_firefly_114 target::chapter4_7_firefly_105 target::no_text_voice/chapter3_18_firefly_101`
- Vuv-path review:
  - `.\python.exe manage.py analyze-stage5-nores-vuv-path-review --output-dir reports/runtime/stage5_vuv_path_review_reviewslice_producerinterface_rect_fail3_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_producerinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json --prefer-audio-export-status --target-record-ids target::chapter3_26_firefly_114 target::chapter4_7_firefly_105 target::no_text_voice/chapter3_18_firefly_101`

### Review-required subset `2`
- Source-filter review:
  - `.\python.exe manage.py analyze-stage5-nores-source-filter-review --output-dir reports/runtime/stage5_source_filter_review_reviewslice_producerinterface_rect_review2_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --dataset-indexes reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_producerinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json --prefer-audio-export-status --target-record-ids target::chapter3_30_firefly_132 target::no_text_voice/chapter3_21_firefly_108`
- Vuv-path review:
  - `.\python.exe manage.py analyze-stage5-nores-vuv-path-review --output-dir reports/runtime/stage5_vuv_path_review_reviewslice_producerinterface_rect_review2_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_producerinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json --prefer-audio-export-status --target-record-ids target::chapter3_30_firefly_132 target::no_text_voice/chapter3_21_firefly_108`

## Subset Reading

### `vuv` is no longer the main split
- Auto-reject subset `3` aggregate:
  - `decoded_vuv_high_band_ratio_mean = 0.063510`
  - `base_logits_vuv_high_band_ratio_mean = 0.053669`
  - `waveform_frames_vuv_high_band_ratio_mean = 0.071609`
- Review-required subset `2` aggregate:
  - `decoded_vuv_high_band_ratio_mean = 0.056398`
  - `base_logits_vuv_high_band_ratio_mean = 0.047755`
  - `waveform_frames_vuv_high_band_ratio_mean = 0.066730`
- Reading:
  - both subsets already keep positive `vuv` contrast at:
    - `waveform_decoder_base_logits`
    - `waveform_frames`
    - final decoded waveform
  - both subset-level vuv-path diagnoses remain:
    - `needs_manual_review`
    - with the same secondaries:
      - `residual_shape_delta_not_unvoiced_focused`
      - `noise_gate_not_dominant_on_unvoiced_frames`
  - therefore the remaining `539` split is not a simple replay of the earlier `vuv`-collapse blocker

### The remaining `3` auto-reject records are not homogeneous
- `target::chapter3_26_firefly_114`
  - `decoded_no_gate` stays `auto_reject_obvious_buzz`
  - `decoded_pre_ola_gate` stays `auto_reject_obvious_buzz`
  - `decoded_post_ola_gate` stays `auto_reject_obvious_buzz`
  - template cosine stays above the auto-reject threshold:
    - `0.989295 -> 0.989171 -> 0.989198`
- `target::chapter4_7_firefly_105`
  - `decoded_no_gate` stays `auto_reject_obvious_buzz`
  - `decoded_pre_ola_gate` stays `auto_reject_obvious_buzz`
  - `decoded_post_ola_gate` stays `auto_reject_obvious_buzz`
  - template cosine stays above the auto-reject threshold:
    - `0.985422 -> 0.985189 -> 0.985215`
- `target::no_text_voice/chapter3_18_firefly_101`
  - `decoded_no_gate` is still `auto_reject_obvious_buzz`
  - `decoded_pre_ola_gate` and `decoded_post_ola_gate` drop to `review_required`
  - the change is extremely narrow:
    - `decoded_frame_template_cosine_mean = 0.985013` on `decoded_no_gate`
    - `decoded_frame_template_cosine_mean = 0.984834` on `decoded_pre_ola_gate`
    - current negative gate threshold is:
      - `AUTO_REJECT_TEMPLATE_COSINE_MEAN = 0.985`
- Reading:
  - the remaining auto-reject set already splits into:
    - a hard template-collapse pair that gate replay does not rescue
    - one borderline record that can fall below the machine threshold with only a tiny gate-side template reduction

### `review_required 2/5` is not a clean positive-control bucket
- `target::chapter3_30_firefly_132`
  - `decoded_no_gate` is already below the main template threshold:
    - `decoded_frame_template_cosine_mean = 0.977717`
  - it is the better current near-open control
- `target::no_text_voice/chapter3_21_firefly_108`
  - `decoded_no_gate` is still heavily collapsed:
    - `decoded_frame_template_cosine_mean = 0.991612`
  - it escapes auto-reject only because the envelope-following side does not trigger:
    - `predicted_activity_to_aligned_frame_rms_corr = 0.347759`
    - below `AUTO_REJECT_ACTIVITY_CORR = 0.75`
- Reading:
  - do not average `review_required 2/5` into a pseudo-success class
  - only `target::chapter3_30_firefly_132` should currently be treated as the better same-frontier control for the hard blocker pair

## Decision
- Keep:
  - the corrected `539` producer-plus-interface checkpoint as the active bounded frontier
  - rectangular reconstruction as the active real export contract
  - the new subset-targetable source-filter and vuv-path review entry points
- Retire:
  - the idea that the remaining `3/5` auto-reject records form one homogeneous failure class
  - the idea that `review_required 2/5` is a clean positive bucket
  - the idea that the next move should go back to global `vuv` rescue or generic gate semantics on this checkpoint

## Recommended Next Action
- If another bounded training loop is opened, do not target the old mixed `fail3 vs review2` grouping.
- Instead:
  - use `target::chapter3_26_firefly_114` and `target::chapter4_7_firefly_105` as the hard no-gate template-collapse blocker pair
  - treat `target::no_text_voice/chapter3_18_firefly_101` as a gate-sensitive border case, not the main structural blocker
  - treat `target::chapter3_30_firefly_132` as the better near-open control
  - do not treat `target::no_text_voice/chapter3_21_firefly_108` as a positive control
- Concretely:
  - the next bounded objective should push no-gate decoded template cosine below the auto-reject threshold on the hard pair
  - not reopen a global `vuv` or gate-family detour first
