# 539 Stage5 Review-Slice Producer-Interface Microfit Partial-Opening Report

## Summary
- This round executed the next bounded action after `538`:
  - keep the active `delta_direct_v1` plus rectangular review-slice route fixed
  - keep the current joint interface prefixes trainable
  - widen one more step upstream into the immediate `decoder_hidden` producer under `branch_mean_contrast_residual_v1`
  - jointly unfreeze:
    - `waveform_decoder`
    - `waveform_decoder_input_adapter`
    - `waveform_decoder_input_gate`
    - `waveform_decoder_input_proj`
    - `fusion_branch_mean_contrast_gate`
    - `fusion_branch_mean_contrast_proj`
- This is the strongest result on the current review slice so far:
  - handoff probe decoded routes are now `0/5 auto_reject`
  - real rectangular export is no longer `5/5 auto_reject`
  - it now reaches:
    - `auto_reject_count = 3/5`
    - `review_required_count = 2/5`
- The sharpened conclusion is:
  - producer-plus-interface widening is a real step beyond `538`
  - this is the first bounded run on the active line that partially opens the real export machine gate
  - but it is still not a route-opening success, because machine gate remains negative-only and `3/5` records still auto-reject
  - the next immediate task should shift from "widen training scope again by inertia" to "localize why handoff decoded routes now look open while real export still keeps a remaining `3/5` failure set"

## Training Run

### Producer-plus-interface microfit
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 8 --packages-per-step 5 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj fusion_branch_mean_contrast_gate fusion_branch_mean_contrast_proj --disable-resume-optimizer-from-init-checkpoint --waveform-decoder-base-logits-active-template-weight 0.1 --waveform-decoder-base-logits-frame-delta-weight 0.1 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.1 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05`
- Output:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- Freeze summary:
  - trainable prefixes:
    - `waveform_decoder`
    - `waveform_decoder_input_adapter`
    - `waveform_decoder_input_gate`
    - `waveform_decoder_input_proj`
    - `fusion_branch_mean_contrast_gate`
    - `fusion_branch_mean_contrast_proj`
  - trainable parameter count:
    - `20`
- Best checkpoint:
  - step `8`
  - validation loss `35.490608`

## Training Reading
- Compared with `538` joint interface:
  - best validation loss:
    - `35.516202 -> 35.490608`
  - `loss_waveform_decoder_base_logits_active_template_excess_relu_0p02`
    - `0.971627 -> 0.963041`
  - `loss_waveform_decoder_base_logits_frame_adjacent_cosine_excess_relu_0p02`
    - `342.940295 -> 342.878534`
  - `loss_waveform_decoder_base_logits_high_band_excess`
    - `0.129016 -> 0.042047`
- Reading:
  - this is not a flat replay of `538`
  - widening into the immediate fusion producer moves both validation loss and high-band pressure materially
  - the bounded producer-side capacity is therefore real leverage, not just bookkeeping scope inflation

## Probe Runs

### Review-slice waveform handoff
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-handoff --output-dir reports/runtime/stage5_waveform_handoff_probe_reviewslice_producerinterface_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Review-slice waveform decoder structure
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-decoder-structure --output-dir reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_producerinterface_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Real rectangular export
- Command:
  - `.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_producerinterface_rectgateoff_round1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --listening-audio-source decoded --pitch-match-reference none --disable-predicted-activity-gate --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 0 --predicted-activity-gate-apply-mode pre_overlap_add --reconstruction-contract-mode rectangular_overlap_count_norm --decoder-branch-mean-mix-alpha 0.0`

### Five-route rectangular review compare
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-frame-template-collapse-review --output-dir reports/runtime/stage5_wf_template_review_producerinterface_vs_joint_vs_prehead_vs_outputhead_vs_deltadirect_rect_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_outputhead_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_prehead_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_jointinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_producerinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json`

## Handoff Reading
- Aggregate handoff stage metrics move substantially:
  - `waveform_frame_logits_template_cosine_mean`
    - baseline `535`: `0.993400`
    - joint `538`: `0.992919`
    - producer-plus-interface `539`: `0.990774`
  - `waveform_frames_template_cosine_mean`
    - baseline `535`: `0.992189`
    - joint `538`: `0.991672`
    - producer-plus-interface `539`: `0.989148`
  - `decoder_to_logits_template_cosine_gap`
    - `0.010223 -> 0.008228` from `538` to `539`
  - `waveform_frame_logits_fraction_abs_ge_1`
    - `0.067515 -> 0.057902`
  - `waveform_frame_logits_fraction_abs_ge_2`
    - `0.001056 -> 0.000009`
- Route aggregates now show a major shift:
  - `decoded_no_gate`
    - `auto_reject_count = 0/5`
    - `decoded_frame_template_cosine_mean = 0.975153`
  - `decoded_pre_ola_gate`
    - `auto_reject_count = 0/5`
    - `decoded_frame_template_cosine_mean = 0.974622`
  - `decoded_post_ola_gate`
    - `auto_reject_count = 0/5`
    - `decoded_frame_template_cosine_mean = 0.974642`
- Reading:
  - the internal handoff route now looks materially less collapsed than any earlier bounded run
  - gate mode is no longer the active question here
  - the next unresolved gap is now between this near-open handoff reading and the still-partially-failed real export

## Structure Reading
- Baseline decoder collapse summary at the new checkpoint:
  - `fused_hidden_template_cosine_mean = 0.982546`
  - `waveform_frames_template_cosine_mean = 0.990223`
  - `fused_to_waveform_template_cosine_gap = 0.007677`
  - diagnosis:
    - `collapse_not_localized_to_waveform_decoder`
- Coupling localization still stays at the same transition:
  - `strongest_transition = decoder_to_base_logits`
  - `decoder_to_base_logits_voicing_corr_jump = 1.470894`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Geometry localization also still reports the same transition:
  - `decoder_to_base_logits_effective_rank_drop = 0.023623`
  - `decoder_to_base_logits_template_distance_drop = -0.783778`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Reading:
  - the old localization label does not disappear
  - but the route-level results are no longer consistent with a simple "nothing important moved" reading
  - the structure probe now has to be read together with the route split:
    - handoff decoded routes are no longer auto-reject
    - real export still partly fails
  - this means the next high-value question is no longer only "how to widen training scope"
  - it is also "which remaining export-side or route-materialization step still turns the now-improved handoff path back into a partial failure set"

## Real Export Reading
- Real rectangular export now partially opens the machine gate:
  - `auto_reject_count = 3/5`
  - `review_required_count = 2/5`
- Auto-reject records:
  - `target::chapter3_26_firefly_114`
  - `target::chapter4_7_firefly_105`
  - `target::no_text_voice/chapter3_18_firefly_101`
- Review-required records:
  - `target::chapter3_30_firefly_132`
  - `target::no_text_voice/chapter3_21_firefly_108`
- Aggregate exported decoded metrics:
  - `decoded_frame_template_cosine_mean = 0.985812`
  - `decoded_frame_adjacent_cosine_mean = 0.997886`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.464940`
  - `spectral_centroid_gap_hz = 4777.123015`
  - `spectral_high_band_energy_ratio_gap = 0.315689`

## Five-Route Comparison
- Real rectangular export comparison:
  - baseline `535`
    - `auto_reject = 5/5`
    - `decoded_frame_template_cosine_mean = 0.990030`
    - `decoded_vuv_high_band_ratio_gap = 0.017643`
  - head-only `536`
    - `auto_reject = 5/5`
    - `decoded_frame_template_cosine_mean = 0.989072`
    - `decoded_vuv_high_band_ratio_gap = 0.032176`
  - pre-head-only `537`
    - `auto_reject = 5/5`
    - `decoded_frame_template_cosine_mean = 0.989364`
    - `decoded_vuv_high_band_ratio_gap = 0.019217`
  - joint `538`
    - `auto_reject = 5/5`
    - `decoded_frame_template_cosine_mean = 0.988889`
    - `decoded_vuv_high_band_ratio_gap = 0.029999`
  - producer-plus-interface `539`
    - `auto_reject = 3/5`
    - `decoded_frame_template_cosine_mean = 0.985812`
    - `decoded_vuv_high_band_ratio_gap = 0.060665`
- Reading:
  - `539` is the first real export result that materially escapes the old uniform auto-reject basin
  - it is also the strongest bounded route so far on decoded template-collapse and decoded `vuv`
  - but `review_required 2/5` is still not positive evidence of success

## Combined Interpretation
- `536` showed that last-stack-only editing can move the route.
- `537` showed that pre-head-only widening is not enough.
- `538` showed that joint interface editing is stronger than either single-sided edit.
- `539` now adds the first bounded real partial opening:
  - internal handoff decoded routes reach `0/5 auto_reject`
  - real exported rectangular route improves to `3/5 auto_reject, 2/5 review_required`
- This changes the decision frame:
  - the next step should not be another blind widening of trainable scope by inertia
  - the next step should localize the new handoff-vs-export gap on the improved checkpoint
  - only after that localization should we decide whether the next move is:
    - more producer-side training capacity
    - export-contract alignment
    - or a remaining subset-specific collapse diagnosis

## Decision
- Keep:
  - `delta_direct_v1` plus rectangular reconstruction as the decoded positive control
  - the producer-plus-interface scope as the new strongest bounded training recipe
  - the conclusion that widening into the immediate `decoder_hidden` producer is real leverage
- Retire:
  - the old assumption that all current bounded real exports are still stuck in uniform `5/5 auto_reject`
  - another same-family widening step without first localizing the renewed handoff-vs-export divergence
- Do not write this round up as:
  - route solved
  - machine-confirmed success
  - or proof that the remaining `3/5` failures are minor

## Recommended Next Action
- Open the next bounded localization pass on the `539` checkpoint itself.
- The concrete next question is:
  - why do `analyze-stage5-nores-waveform-handoff` decoded routes now read `0/5 auto_reject`
  - while the real exported rectangular route still stays at `3/5 auto_reject`
- Good next targets are:
  - replay-level localization between handoff decoded_no_gate assets and real exported `decoded.wav`
  - confirmation of exact reconstruction/materialization semantics on the active `539` checkpoint
  - subset-specific diagnosis on the remaining `3` auto-reject records before opening another training loop
- Do not spend the next round on:
  - another blind scope-widening microfit first
  - Hann vs rectangular
  - gate semantics
  - or replaying the old single-sided interface edits
