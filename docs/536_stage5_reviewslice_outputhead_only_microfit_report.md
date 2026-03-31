# 536 Stage5 Review-Slice Output-Head-Only Microfit Report

## Summary
- This round executed the next bounded action after `535`:
  - keep the repaired `delta_direct_v1` review-slice route fixed
  - keep rectangular reconstruction only as the decoded positive control
  - unfreeze only the `waveform_decoder` prefix
  - ask whether the current `decoder_hidden -> waveform_decoder_base_logits` bottleneck can be moved by head-only recalibration
- The answer is now narrower:
  - the output head is not fully rigid
  - a `waveform_decoder`-only microfit can move some second-order base-logits and decoded metrics
  - but it does not remove the main projection-collapse diagnosis
  - and it does not open the real rectangular export route
- The sharpened conclusion is:
  - the active blocker is still the `decoder_hidden -> waveform_decoder_base_logits` interface
  - but head-only surgery on the final `waveform_decoder` stack is too weak by itself on the current review slice

## Training Run

### Output-head-only microfit
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_outputhead_microfit_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehidden_deltadirect_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 8 --packages-per-step 5 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder --waveform-decoder-base-logits-active-template-weight 0.1 --waveform-decoder-base-logits-frame-delta-weight 0.1 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.1 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05`
- Output:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_outputhead_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_outputhead_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- Freeze summary:
  - trainable prefixes:
    - `waveform_decoder`
  - trainable parameter count:
    - `6`
- Best checkpoint:
  - step `8`
  - validation loss `35.514121`

## Training Reading
- The bounded head-only run is not a no-op:
  - validation `loss_waveform_decoder_base_logits_aper_abs_zero_lag_corr` improves to `0.383095`
  - validation `loss_waveform_decoder_base_logits_noise_energy_abs_zero_lag_corr_active` improves to `0.740000`
  - validation `loss_waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr` improves to `0.467072`
  - validation `loss_waveform_decoder_base_logits_high_band_excess` improves to `0.135618`
- But the strongest collapse-shape terms barely move:
  - validation `loss_waveform_decoder_base_logits_active_template_excess_relu_0p02 = 0.971630`
  - validation `loss_waveform_decoder_base_logits_frame_delta_unit_rms_l1 = 0.995193`
  - validation `loss_waveform_decoder_base_logits_frame_adjacent_cosine_excess_relu_0p02 = 342.944055`
- Reading:
  - the final waveform decoder can respond enough to reshuffle some control coupling and brightness terms
  - but bounded head-only edits do not materially break the local fixed-template basin

## Probe Runs

### Review-slice waveform handoff
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-handoff --output-dir reports/runtime/stage5_waveform_handoff_probe_reviewslice_outputhead_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_outputhead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Review-slice waveform decoder structure
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-decoder-structure --output-dir reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_outputhead_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_outputhead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Real rectangular export
- Command:
  - `.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_outputhead_rectgateoff_round1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_outputhead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --listening-audio-source decoded --pitch-match-reference none --disable-predicted-activity-gate --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 0 --predicted-activity-gate-apply-mode pre_overlap_add --reconstruction-contract-mode rectangular_overlap_count_norm --decoder-branch-mean-mix-alpha 0.0`

### Rectangular review compare
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-frame-template-collapse-review --output-dir reports/runtime/stage5_wf_template_review_outputhead_vs_deltadirect_rect_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_outputhead_rectgateoff_round1_1/nores_vocoder_audio_export.json`

## Handoff Reading
- Compared with the `535` baseline:
  - `waveform_frame_logits_template_cosine_mean`
    - `0.993400 -> 0.992962`
  - `waveform_frames_template_cosine_mean`
    - `0.992189 -> 0.991705`
  - `waveform_frame_logits_fraction_abs_ge_1`
    - `0.070934 -> 0.064510`
- Reading:
  - the head-only run does move the pre-`tanh` route
  - but only at second-order scale
  - the route diagnosis still says:
    - `tanh_is_main_new_collapse_site = false`
    - `logits_show_heavy_saturation_pressure = false`
- Important scope note:
  - this handoff probe uses the current heard-route decode semantics
  - it is not the real rectangular positive-control export

## Structure Reading
- Geometry remains localized to the same transition:
  - `decoder_to_base_logits_effective_rank_drop`
    - `0.023670 -> 0.023571`
  - `decoder_to_base_logits_template_distance_drop`
    - `-0.666438 -> -0.680016`
  - diagnosis stays:
    - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Coupling is movable, but not in a route-opening way:
  - `decoder_to_base_logits_voicing_corr_jump`
    - `0.511328 -> 1.437692`
  - `decoder_to_base_logits_abs_aper_corr_jump`
    - `0.710864 -> -0.039503`
  - `decoder_to_base_logits_abs_aper_energy_product_corr_jump`
    - `-0.125443 -> 0.316063`
- Reading:
  - the `waveform_decoder` weights can substantially reshuffle which controls dominate the base-logits RMS profile
  - but they do not remove the main projection-collapse site
  - the strongest geometry bottleneck still sits at `decoder_hidden -> waveform_decoder_base_logits`

## Real Export Reading
- The decisive route-opening check is still negative:
  - rectangular export buzz summary:
    - `auto_reject_count = 5/5`
    - `review_required_count = 0/5`
- Compared with the earlier `delta_direct_v1 + rectangular` control:
  - decoded template cosine mean:
    - `0.990030 -> 0.989072`
  - decoded `vuv` high-band gap:
    - `0.017643 -> 0.032176`
- Reading:
  - head-only microfit preserves the repaired decoded `vuv` route
  - it even improves the rectangular decoded `vuv` contrast and template metrics slightly
  - but those gains remain second-order because the exported route still lands in `5/5 auto_reject`

## Combined Interpretation
- `535` localized the remaining blocker to the output-head projection.
- `536` now adds the missing bounded intervention result:
  - direct `waveform_decoder`-only recalibration is not enough
  - it can move coupling terms and slightly improve template and decoded `vuv`
  - but it does not change the main geometry-collapse location
  - and it does not open the real export route
- Therefore the correct updated target is not:
  - reconstruction
  - gate tuning
  - final `tanh`
  - or abandoning output-head localization altogether
- The correct updated target is:
  - the broader `decoder_hidden -> waveform_decoder_base_logits` interface
  - likely via a larger editable scope than the final `waveform_decoder` stack alone

## Decision
- Keep:
  - `delta_direct_v1` plus rectangular reconstruction as the decoded positive control
  - the localization that the active failure still centers on `decoder_hidden -> waveform_decoder_base_logits`
- Retire:
  - the idea that head-only last-stack recalibration is likely to be enough by itself
- Do not write this round up as:
  - output-head solved
  - or output-head disproved

## Recommended Next Action
- Open the next bounded probe on the output-head interface rather than the last stack alone.
- Good next options are:
  - a trainable pre-head adapter inserted between `decoder_hidden` and `waveform_decoder`
  - or a joint microfit that unfreezes both the pre-head producer side and `waveform_decoder`
- Do not spend the next round on:
  - Hann vs rectangular
  - gate semantics
  - final `tanh`
  - or another `waveform_decoder`-only replay of the same bounded recipe
