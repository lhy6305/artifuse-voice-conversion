# 542 Stage5 Review-Slice Hard-Pair Template-Push Microfit Report

## Summary
- This round executed the next bounded action after `541`:
  - keep the corrected `539` producer-plus-interface structure fixed
  - keep rectangular no-gate real export fixed
  - stop treating the old mixed `fail3 vs review2` grouping as one class
  - open a focused microfit on:
    - hard blockers:
      - `target::chapter3_26_firefly_114`
      - `target::chapter4_7_firefly_105`
    - near-open control:
      - `target::chapter3_30_firefly_132`
    - gate-sensitive border case:
      - `target::no_text_voice/chapter3_18_firefly_101`
- The result is the strongest bounded review-slice frontier so far:
  - subset `4` real rectangular no-gate export improves:
    - baseline `539 subset`: `3/4 auto_reject`
    - focused `templatepush_a`: `1/4 auto_reject`
    - focused `templatepush_b`: `0/4 auto_reject`
  - the same `templatepush_b` checkpoint also replays back onto the full `5`-record review slice at:
    - `0/5 auto_reject`
    - `5/5 review_required`
- The sharpened conclusion is:
  - the remaining hard blocker pair was real and directly movable with focused template-collapse pressure
  - this is the first current review-slice checkpoint that clears the machine negative gate on the full active `5`-record slice under real no-gate rectangular export
  - but this is still not a route-opening success, because `review_required 5/5` is still only a negative-gate escape, not positive evidence of speech quality

## Dataset Subset
- A bounded `4`-record dataset index was materialized at:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_hardpaircontrol4_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Included records:
  - `target::chapter3_26_firefly_114`
  - `target::chapter4_7_firefly_105`
  - `target::chapter3_30_firefly_132`
  - `target::no_text_voice/chapter3_18_firefly_101`
- Excluded:
  - `target::no_text_voice/chapter3_21_firefly_108`
- Reading:
  - this kept training localized to the hard pair, one near-open control, and one border case
  - `108` was held out and later used as an immediate replay check

## Training Runs

### `templatepush_a`
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_hardpaircontrol4_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepusha_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 6 --packages-per-step 4 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj fusion_branch_mean_contrast_gate fusion_branch_mean_contrast_proj --disable-resume-optimizer-from-init-checkpoint --waveform-frames-active-template-weight 0.05 --waveform-decoder-base-logits-active-template-weight 0.15 --waveform-decoder-base-logits-frame-delta-weight 0.1 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.15 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05`
- Best checkpoint:
  - step `6`

### `templatepush_b`
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_hardpaircontrol4_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 8 --packages-per-step 4 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj fusion_branch_mean_contrast_gate fusion_branch_mean_contrast_proj --disable-resume-optimizer-from-init-checkpoint --waveform-frames-active-template-weight 0.1 --waveform-decoder-base-logits-active-template-weight 0.25 --waveform-decoder-base-logits-frame-delta-weight 0.05 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.25 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05`
- Best checkpoint:
  - step `8`

## Focused Export Reading

### Subset `4` real no-gate rectangular export
- `templatepush_a`:
  - `auto_reject_count = 1/4`
  - only remaining auto-reject:
    - `target::chapter3_26_firefly_114`
- `templatepush_b`:
  - `auto_reject_count = 0/4`
  - `review_required_count = 4/4`

### Hard blocker pair
- `target::chapter3_26_firefly_114`
  - baseline `539`: `0.989295`
  - `templatepush_a`: `0.988169`
  - `templatepush_b`: `0.979284`
  - status:
    - `auto_reject_obvious_buzz -> auto_reject_obvious_buzz -> review_required`
- `target::chapter4_7_firefly_105`
  - baseline `539`: `0.985422`
  - `templatepush_a`: `0.983241`
  - `templatepush_b`: `0.968131`
  - status:
    - `auto_reject_obvious_buzz -> review_required -> review_required`

### Near-open control and border case
- `target::chapter3_30_firefly_132`
  - `0.977717 -> 0.973169 -> 0.944919`
  - remains `review_required`
- `target::no_text_voice/chapter3_18_firefly_101`
  - `0.985013 -> 0.982693 -> 0.967241`
  - moves from border case into clear `review_required`

## Replay Back To Full `5`
- The stronger `templatepush_b` checkpoint was replayed back onto the original `5`-record review slice:
  - output:
    - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_templatepushb_rectgateoff_round1_1/nores_vocoder_audio_export.json`
- Result:
  - baseline `539 full5`: `3/5 auto_reject + 2/5 review_required`
  - `templatepush_b full5`: `0/5 auto_reject + 5/5 review_required`
- Held-out `target::no_text_voice/chapter3_21_firefly_108` did not regress:
  - `decoded_frame_template_cosine_mean = 0.991612 -> 0.981898`
  - status stays `review_required`

## Source-Filter Review Reading
- Full-slice source-filter replay comparison:
  - baseline `539` aggregate:
    - `decoded_template_cosine_mean = 0.985812`
    - `decoded_vuv_high_band_ratio_mean = 0.060665`
    - `decoded_vuv_centroid_gap_hz_mean = 531.285059`
    - `decoded_vuv_centroid_gap_suppressed_count = 3`
  - `templatepush_b` aggregate:
    - `decoded_template_cosine_mean = 0.968295`
    - `decoded_vuv_high_band_ratio_mean = 0.111866`
    - `decoded_vuv_centroid_gap_hz_mean = 1206.279004`
    - `decoded_vuv_centroid_gap_suppressed_count = 0`
- Reading:
  - this is not only a threshold edge-case escape
  - the machine-side source-filter review also moves materially in the same direction
  - but the review still lands at:
    - `primary_localization = needs_more_localization`
  - so the result is a strong bounded gain, not final proof of speech-quality opening

## Decision
- Keep:
  - `templatepush_b` as the new strongest bounded review-slice frontier
  - producer-plus-interface trainable scope
  - rectangular no-gate export as the active readout
- Retire:
  - the old `539` checkpoint as the strongest bounded review-slice frontier
  - the assumption that the hard blocker pair requires another immediate structural widening before a focused loss move can help
- Do not write this round up as:
  - route solved
  - speech confirmed
  - or positive machine acceptance

## Recommended Next Action
- The next action should not be another blind same-family loss escalation first.
- First:
  - perform bounded listening and spectrogram review on the new `templatepush_b full5` export
  - confirm whether `review_required 5/5` is genuine near-speech improvement or still a lower-energy buzz family
- Only after that:
  - decide whether to promote this loss family to a broader validation-slice replay
  - or continue another same-scope microfit from `templatepush_b`
