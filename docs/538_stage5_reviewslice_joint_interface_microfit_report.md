# 538 Stage5 Review-Slice Joint Interface Microfit Report

## Summary
- This round executed the next bounded action after `537`:
  - keep the active `delta_direct_v1` plus rectangular review-slice route fixed
  - keep the new pre-head adapter enabled
  - jointly unfreeze:
    - `waveform_decoder`
    - `waveform_decoder_input_adapter`
    - `waveform_decoder_input_gate`
    - `waveform_decoder_input_proj`
- The result is now more informative than either single-sided edit:
  - the joint interface run is the strongest current bounded output-head intervention on decoded template-collapse and spectral brightness
  - it also preserves a strong positive decoded `vuv` gap under real rectangular export
  - but it still does not open the route, because real export remains `5/5 auto_reject`
  - and the strongest geometry collapse still localizes to `decoder_hidden -> waveform_decoder_base_logits`
- The sharpened conclusion is:
  - moving from single-sided edits to a joint interface edit is a real improvement
  - but the current joint scope is still not enough
  - the next valid move should widen one step further upstream into the immediate producer of `decoder_hidden`, not replay another same-scope microfit

## Training Run

### Joint interface microfit
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt --device cuda:0 --num-steps 8 --packages-per-step 5 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj --disable-resume-optimizer-from-init-checkpoint --waveform-decoder-base-logits-active-template-weight 0.1 --waveform-decoder-base-logits-frame-delta-weight 0.1 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.1 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05`
- Output:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- Freeze summary:
  - trainable prefixes:
    - `waveform_decoder`
    - `waveform_decoder_input_adapter`
    - `waveform_decoder_input_gate`
    - `waveform_decoder_input_proj`
  - trainable parameter count:
    - `16`
- Best checkpoint:
  - step `8`
  - validation loss `35.516202`

## Training Reading
- Compared with `536` head-only:
  - best validation loss:
    - `35.514121 -> 35.516202`
  - `loss_waveform_decoder_base_logits_high_band_excess`
    - `0.135618 -> 0.129016`
  - `loss_waveform_decoder_base_logits_frame_adjacent_cosine_excess_relu_0p02`
    - `342.944055 -> 342.940295`
- Compared with `537` pre-head-only:
  - best validation loss:
    - `35.530248 -> 35.516202`
  - `loss_waveform_decoder_base_logits_high_band_excess`
    - `0.267618 -> 0.129016`
  - `loss_waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr`
    - `0.325633 -> 0.452062`
- Reading:
  - the joint run is not simply averaging the two earlier bounded interventions
  - it inherits more of the real route improvement from the head-only side
  - while also using the pre-head path enough to stay a distinct interface edit rather than a pure replay of `536`

## Probe Runs

### Review-slice waveform handoff
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-handoff --output-dir reports/runtime/stage5_waveform_handoff_probe_reviewslice_jointinterface_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Review-slice waveform decoder structure
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-decoder-structure --output-dir reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_jointinterface_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Real rectangular export
- Command:
  - `.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_jointinterface_rectgateoff_round1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_jointinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --listening-audio-source decoded --pitch-match-reference none --disable-predicted-activity-gate --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 0 --predicted-activity-gate-apply-mode pre_overlap_add --reconstruction-contract-mode rectangular_overlap_count_norm --decoder-branch-mean-mix-alpha 0.0`

### Rectangular review compare
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-frame-template-collapse-review --output-dir reports/runtime/stage5_wf_template_review_jointinterface_vs_prehead_vs_outputhead_vs_deltadirect_rect_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_outputhead_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_prehead_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_jointinterface_rectgateoff_round1_1/nores_vocoder_audio_export.json`

## Handoff Reading
- Compared with earlier routes:
  - baseline `535`
    - `waveform_frame_logits_template_cosine_mean = 0.993400`
    - `waveform_frames_template_cosine_mean = 0.992189`
  - head-only `536`
    - `0.992962`
    - `0.991705`
  - pre-head-only `537`
    - `0.992947`
    - `0.991691`
  - joint `538`
    - `0.992919`
    - `0.991672`
- Additional handoff reading:
  - `logits_to_frames_template_cosine_gap = -0.001246`
  - `waveform_frame_logits_fraction_abs_ge_1 = 0.067515`
  - `waveform_frame_logits_fraction_abs_ge_2 = 0.001056`
  - `decoder_to_logits_template_cosine_gap = 0.010223`
- Reading:
  - the joint run is now the best current bounded route on the local handoff template metrics
  - the gain is still small
  - collapse is still already present before final waveform reconstruction

## Structure Reading
- Baseline decoder collapse summary at the joint checkpoint:
  - `fused_hidden_template_cosine_mean = 0.982696`
  - `waveform_frames_template_cosine_mean = 0.992428`
  - `fused_to_waveform_template_cosine_gap = 0.009732`
  - diagnosis:
    - `collapse_not_localized_to_waveform_decoder`
- Coupling localization still stays at the same transition:
  - `strongest_transition = decoder_to_base_logits`
  - `decoder_to_base_logits_voicing_corr_jump = 1.453180`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Geometry localization still also stays at the same transition:
  - `decoder_to_base_logits_effective_rank_drop = 0.023507`
  - `decoder_to_base_logits_template_distance_drop = -0.695632`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Compared with the earlier bounded interface runs:
  - head-only `536`
    - `decoder_to_base_logits_template_distance_drop = -0.680016`
  - pre-head-only `537`
    - `decoder_to_base_logits_template_distance_drop = -0.701049`
  - joint `538`
    - `decoder_to_base_logits_template_distance_drop = -0.695632`
- Variant reading remains familiar:
  - `waveform_decoder_base_logits_only`
    - `mean_waveform_mean_abs_delta_vs_baseline = 0.003817`
    - `mean_waveform_frames_template_cosine_mean = 0.992485`
  - `fused_hidden_frame_mean`
    - `mean_waveform_mean_abs_delta_vs_baseline = 0.012637`
    - `mean_waveform_frames_template_cosine_mean = 1.000000`
- Reading:
  - joint editing improves the heard route more than `537`
  - but it still does not break the main geometry bottleneck
  - the immediate producer side of `decoder_hidden` is now the most credible next narrow extension

## Real Export Reading
- The decisive route-opening check is still negative:
  - rectangular export buzz summary:
    - `auto_reject_count = 5/5`
    - `review_required_count = 0/5`
- On the real exported route:
  - `decoded_frame_template_cosine_mean = 0.988889`
  - `decoded_frame_adjacent_cosine_mean = 0.998169`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.500206`
  - `spectral_centroid_gap_hz = 5000.668933`
  - `spectral_high_band_energy_ratio_gap = 0.353070`
- Four-route rectangular comparison:
  - baseline `535`
    - `decoded_frame_template_cosine_mean = 0.990030`
    - `decoded_vuv_high_band_ratio_gap = 0.017643`
  - head-only `536`
    - `decoded_frame_template_cosine_mean = 0.989072`
    - `decoded_vuv_high_band_ratio_gap = 0.032176`
  - pre-head-only `537`
    - `decoded_frame_template_cosine_mean = 0.989364`
    - `decoded_vuv_high_band_ratio_gap = 0.019217`
  - joint `538`
    - `decoded_frame_template_cosine_mean = 0.988889`
    - `decoded_vuv_high_band_ratio_gap = 0.029999`
- Reading:
  - joint `538` is now the best current bounded route on decoded template-collapse
  - it is also the best current bounded route on spectral brightness reduction
  - head-only `536` still keeps a slightly larger decoded `vuv` gap
  - neither result opens the route because both remain `5/5 auto_reject`

## Combined Interpretation
- `536` proved that last-stack-only editing can move the route but is too narrow.
- `537` proved that pre-head-only editing is also too weak.
- `538` now shows the first clear bounded joint-interface win:
  - handoff template metrics are the best so far
  - decoded template-collapse and brightness are the best so far
  - decoded `vuv` contrast stays strongly positive
- But `538` also keeps the core blocker unchanged:
  - real export remains `5/5 auto_reject`
  - the main geometry collapse still sits at `decoder_hidden -> waveform_decoder_base_logits`
  - collapsing `fused_hidden` to its frame mean still barely changes the route
- Therefore the correct updated reading is:
  - joint interface editing is the right direction
  - but the next increment must widen one step upstream into the producer of `decoder_hidden`
  - the most concrete current candidate under `branch_mean_contrast_residual_v1` is the fusion residual producer:
    - `fusion_branch_mean_contrast_gate`
    - `fusion_branch_mean_contrast_proj`
    - and, if needed, the paired normalization on that same narrow producer path

## Decision
- Keep:
  - `delta_direct_v1` plus rectangular reconstruction as the decoded positive control
  - the new pre-head adapter plumbing
  - the conclusion that joint interface editing is stronger than either single-sided bounded edit
- Retire:
  - another replay of head-only scope
  - another replay of pre-head-only scope
  - another same-scope joint replay without widening producer-side capacity
- Do not write this round up as:
  - route opening
  - output-head solved
  - or evidence that the current frame-space collapse is already fixed

## Recommended Next Action
- Open the next bounded producer-plus-interface microfit on the same review slice.
- The narrowest concrete next target is:
  - current joint interface prefixes
  - plus the immediate `decoder_hidden` producer inside `branch_mean_contrast_residual_v1`:
    - `fusion_branch_mean_contrast_gate`
    - `fusion_branch_mean_contrast_proj`
- Do not spend the next round on:
  - Hann vs rectangular
  - gate semantics
  - final `tanh`
  - head-only replay
  - pre-head-only replay
  - same-scope joint replay without producer-side widening
