# 537 Stage5 Review-Slice Pre-Head Adapter Microfit Report

## Summary
- This round executed the next bounded action after `536`:
  - keep the active `delta_direct_v1` plus rectangular review-slice route fixed
  - widen scope beyond the last `waveform_decoder` stack
  - insert a small zero-init pre-head adapter between `decoder_hidden` and `waveform_decoder`
  - train only that new adapter interface on the same `5`-record review slice
- The answer is now clearer:
  - widening scope from the last stack to a tiny single-sided pre-head adapter is directionally valid
  - it does move local handoff template-collapse metrics slightly
  - but it still does not open the real rectangular export route
  - and it still leaves the main geometry collapse at `decoder_hidden -> waveform_decoder_base_logits`
- The sharpened conclusion is:
  - `535` output-head localization remains correct
  - `536` head-only last-stack microfit was too narrow
  - `537` pre-head-adapter-only microfit is still too weak by itself
  - the next valid move is a wider joint interface edit, not another single-sided replay

## Implementation Support Added
- This round added reusable plumbing for a bounded pre-head interface probe:
  - `src/v5vc/offline_vocoder_scaffold.py`
    - new zero-init `waveform_decoder_input_adapter`
    - new `waveform_decoder_input_gate`
    - new `waveform_decoder_input_proj`
    - new forward outputs for adapter diagnostics
  - `src/v5vc/offline_vocoder_training.py`
    - training-loop support for the new adapter path
  - `src/v5vc/nores_vocoder_audio_export.py`
    - checkpoint reconstruction and export-manifest support for the new path
    - branch labels now distinguish `prehead`
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
    - manual probe-side forward reconstruction now replays the pre-head adapter correctly
  - `src/v5vc/cli.py`
    - new CLI flags:
      - `--use-waveform-decoder-input-adapter`
      - `--waveform-decoder-input-adapter-scale`
- A CPU CLI smoke run under `reports/runtime/_cli_smoke_prehead_adapter/` completed successfully before the formal review-slice run.

## Training Run

### Pre-head adapter microfit
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehidden_deltadirect_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 8 --packages-per-step 5 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.001 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj --allow-partial-init-checkpoint-load --disable-resume-optimizer-from-init-checkpoint --waveform-decoder-base-logits-active-template-weight 0.1 --waveform-decoder-base-logits-frame-delta-weight 0.1 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.1 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05`
- Output:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- Freeze summary:
  - trainable prefixes:
    - `waveform_decoder_input_adapter`
    - `waveform_decoder_input_gate`
    - `waveform_decoder_input_proj`
  - trainable parameter count:
    - `10`
- Best checkpoint:
  - step `6`
  - validation loss `35.530248`

## Probe Runs

### Review-slice waveform handoff
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-handoff --output-dir reports/runtime/stage5_waveform_handoff_probe_reviewslice_prehead_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Review-slice waveform decoder structure
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-decoder-structure --output-dir reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_prehead_microfit_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`

### Real rectangular export
- Command:
  - `.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_prehead_rectgateoff_round1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_prehead_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --listening-audio-source decoded --pitch-match-reference none --disable-predicted-activity-gate --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 0 --predicted-activity-gate-apply-mode pre_overlap_add --reconstruction-contract-mode rectangular_overlap_count_norm --decoder-branch-mean-mix-alpha 0.0`

### Rectangular review compare
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-frame-template-collapse-review --output-dir reports/runtime/stage5_wf_template_review_prehead_vs_outputhead_vs_deltadirect_rect_r1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_outputhead_rectgateoff_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_prehead_rectgateoff_round1_1/nores_vocoder_audio_export.json`

## Handoff Reading
- Compared with the `535` baseline:
  - `waveform_frame_logits_template_cosine_mean`
    - `0.993400 -> 0.992947`
  - `waveform_frames_template_cosine_mean`
    - `0.992189 -> 0.991691`
  - `logits_to_frames_template_cosine_gap`
    - `-0.001211 -> -0.001257`
  - `waveform_frame_logits_fraction_abs_ge_1`
    - `0.070934 -> 0.069811`
  - `waveform_frame_logits_fraction_abs_ge_2`
    - `0.001039 -> 0.000741`
- Reading:
  - the pre-head adapter does move local pre-export collapse metrics in the expected direction
  - it still does not change the earlier diagnosis that the route is already collapsed before final activation
  - the improvement scale remains small

## Structure Reading
- Baseline decoder collapse summary at the new checkpoint:
  - `fused_hidden_template_cosine_mean = 0.982696`
  - `waveform_frames_template_cosine_mean = 0.992271`
  - `fused_to_waveform_template_cosine_gap = 0.009575`
  - diagnosis:
    - `collapse_not_localized_to_waveform_decoder`
- Coupling localization still stays at the same transition:
  - `strongest_transition = decoder_to_base_logits`
  - `decoder_to_base_logits_voicing_corr_jump = 1.049450`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Geometry localization also still stays at the same transition:
  - `decoder_to_base_logits_effective_rank_drop = 0.023692`
  - `decoder_to_base_logits_template_distance_drop = -0.701049`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Compared with `536`:
  - the new pre-head-only path does not improve the main geometry diagnosis
  - `decoder_to_base_logits_template_distance_drop`
    - `-0.680016 -> -0.701049`
- Variant reading remains familiar:
  - `waveform_decoder_base_logits_only`
    - `mean_waveform_mean_abs_delta_vs_baseline = 0.003794`
    - `mean_waveform_frames_template_cosine_mean = 0.992320`
  - `fused_hidden_frame_mean`
    - `mean_waveform_mean_abs_delta_vs_baseline = 0.012930`
    - `mean_waveform_frames_template_cosine_mean = 1.000000`
- Reading:
  - even after widening from the last stack to a pre-head adapter, the heard path still behaves like a template-heavy projector
  - the new adapter does not move the core `decoder_hidden -> waveform_decoder_base_logits` bottleneck enough

## Real Export Reading
- The decisive route-opening check is still negative:
  - rectangular export buzz summary:
    - `auto_reject_count = 5/5`
    - `review_required_count = 0/5`
- On the real exported route:
  - `decoded_frame_template_cosine_mean = 0.989364`
  - `decoded_frame_adjacent_cosine_mean = 0.998274`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.566448`
  - `spectral_centroid_gap_hz = 5597.151756`
  - `spectral_high_band_energy_ratio_gap = 0.408275`
- Compared with the earlier rectangular routes:
  - baseline `535` decoded `vuv` high-band gap:
    - `0.017643`
  - head-only `536` decoded `vuv` high-band gap:
    - `0.032176`
  - pre-head `537` decoded `vuv` high-band gap:
    - `0.019217`
- Compared on decoded template-collapse:
  - baseline `535`
    - `decoded_frame_template_cosine_mean = 0.990030`
  - head-only `536`
    - `decoded_frame_template_cosine_mean = 0.989072`
  - pre-head `537`
    - `decoded_frame_template_cosine_mean = 0.989364`
- Reading:
  - pre-head-only microfit is not a no-op
  - but it does not beat the earlier head-only route on the real rectangular export
  - and it still stays fully inside the obvious-buzz family

## Combined Interpretation
- `535` localized the active blocker to `decoder_hidden -> waveform_decoder_base_logits`.
- `536` proved that the final `waveform_decoder` stack alone is too narrow.
- `537` now proves that a tiny single-sided pre-head adapter alone is also too weak:
  - local handoff template metrics move slightly
  - real export remains `5/5 auto_reject`
  - the strongest geometry collapse still stays at `decoder_hidden -> waveform_decoder_base_logits`
  - the real rectangular route does not improve beyond the earlier head-only result
- Therefore the right updated reading is not:
  - output-head localization was wrong
  - pre-head widening solved the interface
  - or another adapter-only replay is likely to open the route
- The right updated reading is:
  - the target interface is still correct
  - but the next bounded intervention must edit more of that interface jointly

## Decision
- Keep:
  - `delta_direct_v1` plus rectangular reconstruction as the decoded positive control
  - the current localization that the active blocker remains `decoder_hidden -> waveform_decoder_base_logits`
  - the new pre-head adapter plumbing as reusable infrastructure for the next round
- Retire:
  - the idea that a last-stack-only microfit is enough
  - the idea that a pre-head-adapter-only microfit is enough
- Do not write this round up as:
  - a route opening
  - a localization reversal
  - or proof that the pre-head side is irrelevant

## Recommended Next Action
- Open the next bounded joint interface edit on the same review slice.
- Good next options are:
  - joint microfit that unfreezes both the new pre-head adapter path and `waveform_decoder`
  - or a slightly wider producer-side interface microfit that lets `decoder_hidden` geometry move together with the projector
- Do not spend the next round on:
  - Hann vs rectangular
  - gate semantics
  - final `tanh`
  - another `waveform_decoder`-only replay
  - another adapter-only replay
