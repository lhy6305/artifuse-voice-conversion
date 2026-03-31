# 529 Stage5 Explicit Noise-Hidden Residual Microfit And Downstream Projection Blocker Report

## Summary
- This round executed the next bounded structural probe after `528`:
  - add a real explicit `noise_hidden -> residual` path
  - freeze the old Stage5 consumer
  - run the same `5`-record `fusionbranchmeancontrast_residualshape_scale050` review slice as a micro-fit
- Three variants were tested:
  - `gate_bias_only_v1`
  - `delta_direct_v1`
  - `gate_plus_delta_v1`
- The result is now sharp:
  - `delta_direct_v1` is the only local winner
  - it rescues aggregate waveform-frames `vuv` high-band gap from `-0.003187` to `0.002642`
  - this nearly matches the earlier local positive controls:
    - oracle `0.003254`
    - `noise_hidden` scaling comparator `0.003365`
- But the final decoded waveform does not improve:
  - decoded aggregate `vuv` high-band gap stays `-0.001537`
- So this round proves two things at once:
  - a new explicit `noise_hidden -> residual` path can recover the localized frame-space sink
  - the active blocker has now moved downstream from `waveform_decoder_base_logits -> waveform_frames` to `waveform_frames -> decoded waveform`
- Correction note:
  - the decode-side replay numbers in this report were later superseded by `530`
  - the first replay used a `vuv-path` probe version that still resolved `decoded_audio_path` from the original review bundle even when replaying a new export manifest
  - the micro-fit training result and frame-space rescue in this report remain valid
  - use `530` for the corrected decode-side localization and route decomposition

## Code Change
- Added a new explicit `noise_hidden -> residual` branch to the Stage5 scaffold:
  - `src/v5vc/offline_vocoder_scaffold.py`
- Added training-loop support for:
  - partial init from an older checkpoint
  - prefix-allowlist freezing
  - new branch-only optimization
  - `src/v5vc/offline_vocoder_training.py`
- Added export-time model reconstruction for the new branch config:
  - `src/v5vc/nores_vocoder_audio_export.py`
- Added CLI support for the new Stage5 micro-fit path:
  - `src/v5vc/cli.py`

## New Branch Variants
- `gate_bias_only_v1`
  - learn only an extra `noise_hidden -> residual_gate` bias path
- `delta_direct_v1`
  - learn only an extra `noise_hidden -> residual_delta` path
- `gate_plus_delta_v1`
  - learn both gate and delta paths together

## Review-Slice Dataset
- Reused the current human-review slice as a bounded dataset-level micro-fit target:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.md`
- The dataset contains the same `5` reviewed records:
  - `target::chapter3_26_firefly_114`
  - `target::chapter3_30_firefly_132`
  - `target::chapter4_7_firefly_105`
  - `target::no_text_voice/chapter3_18_firefly_101`
  - `target::no_text_voice/chapter3_21_firefly_108`

## Training Setup
- Init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- Shared setup across all three runs:
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_scale = 0.5`
  - `allow_partial_init_checkpoint_load = true`
  - `resume_optimizer_from_init_checkpoint = false`
  - `num_steps = 8`
  - `packages_per_step = 5`
  - freeze all old parameters and train only the new explicit branch

## Micro-Fit Runs
- `gate_bias_only_v1`
  - summary:
    - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehidden_gatebias_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
  - best checkpoint:
    - step `1`
    - validation loss `1.008347`
  - reading:
    - no meaningful movement from baseline
- `delta_direct_v1`
  - summary:
    - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehidden_deltadirect_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
  - best checkpoint:
    - step `8`
    - validation loss `0.946786`
  - reading:
    - this is the only strong positive branch
- `gate_plus_delta_v1`
  - summary:
    - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehiddenhybrid_microfit_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
  - best checkpoint:
    - step `8`
    - validation loss `1.008174`
  - reading:
    - essentially flat and not competitive with `delta_direct_v1`

## Export And Review-Probe Runs
- Exported best checkpoints back to the same `5`-record review slice:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_gatebias_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_hybrid_round1_1/`
- Re-ran `analyze-stage5-nores-vuv-path-review` on the exported outputs:
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_gatebias_round1_1/stage5_vuv_path_review.md`
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_deltadirect_round1_1/stage5_vuv_path_review.md`
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_hybrid_round1_1/stage5_vuv_path_review.md`

## Aggregate Results
- Baseline from `524`:
  - `base_logits_vuv_high_band_ratio_mean = -0.000914`
  - `waveform_frames_vuv_high_band_ratio_mean = -0.003187`
  - `decoded_vuv_high_band_ratio_mean = -0.001537`
  - `primary_localization = waveform_frames_vuv_separation_lost_after_base_logits`
- `gate_bias_only_v1`:
  - `waveform_frames_vuv_high_band_ratio_mean = -0.003188`
  - `decoded_vuv_high_band_ratio_mean = -0.001537`
  - `primary_localization = waveform_frames_vuv_separation_lost_after_base_logits`
- `gate_plus_delta_v1`:
  - `waveform_frames_vuv_high_band_ratio_mean = -0.003213`
  - `decoded_vuv_high_band_ratio_mean = -0.001537`
  - `primary_localization = waveform_frames_vuv_separation_lost_after_base_logits`
- `delta_direct_v1`:
  - `waveform_frames_vuv_high_band_ratio_mean = 0.002642`
  - `decoded_vuv_high_band_ratio_mean = -0.001537`
  - `primary_localization = decoded_waveform_vuv_separation_lost_after_frame_projection`

## Delta-Direct Reading
- `delta_direct_v1` improves waveform-frames aggregate `vuv` gap by:
  - `+0.005829` versus baseline
- Remaining gap to the earlier local comparators is now small:
  - gap to oracle `0.003254`: `0.000612`
  - gap to `noise_hidden_rms_soft_residual_gain500 = 0.003365`: `0.000723`
- This means the earlier structural conclusion from `528` is now upgraded:
  - the old residual adapter really was the bottleneck for local frame-space use of `noise_hidden`
  - a new explicit direct delta path is enough to recover most of the lost local leverage

## Downstream Blocker Shift
- The crucial negative result is that decoded aggregate `vuv` gap does not move:
  - baseline `-0.001537`
  - `delta_direct_v1` `-0.001537`
- The primary localization therefore changes from:
  - `waveform_frames_vuv_separation_lost_after_base_logits`
  - to `decoded_waveform_vuv_separation_lost_after_frame_projection`
- This is the practical handoff point for the next round:
  - stop arguing about carrier source
  - stop arguing about whether an explicit `noise_hidden -> residual` route can help
  - both questions are now answered
  - the new active blocker sits in the downstream frame projection / decode path

## Slice-Level Reading
- The two records that already fail at `base_logits` still fail there:
  - `target::no_text_voice/chapter3_18_firefly_101`
  - `target::no_text_voice/chapter3_21_firefly_108`
- The positive shift from `delta_direct_v1` mainly helps the three records that previously lost their small positive gap by `waveform_frames`.
- One record remains machine-auto-rejected in the exported slice:
  - `target::chapter3_26_firefly_114`
- The review bundle status still stays qualitatively blocked:
  - `auto_reject_count = 1`
  - `review_required_count = 4`
- So this is still a localization result, not a decoded route opening.

## CLI Verification
- After wiring the new training-loop flags into the real command dispatch, a bounded CLI smoke also completed successfully:
  - command:
    - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/_cli_smoke_noisehidden_deltadirect --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt --device auto --num-steps 1 --packages-per-step 5 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.001 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes noise_hidden_residual_adapter noise_hidden_residual_delta_proj --allow-partial-init-checkpoint-load --disable-resume-optimizer-from-init-checkpoint`
  - result:
    - completed successfully
    - latest checkpoint:
      - `reports/runtime/_cli_smoke_noisehidden_deltadirect/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt`

## Decision
- Keep `delta_direct_v1` as the first validated explicit `noise_hidden -> residual` positive branch.
- Retire:
  - `gate_bias_only_v1`
  - `gate_plus_delta_v1`
  - further gate-side tuning on this line
- Retire the old framing that the active sink is still mainly `waveform_decoder_base_logits -> waveform_frames`.
- Update the active blocker to:
  - `waveform_frames -> decoded waveform`
  - more concretely, frame projection / overlap-add decode side

## Recommended Next Action
- Open the next bounded Stage5 probe on the downstream path after `waveform_frames`.
- Suggested next probe question:
  - where does the rescued frame-space `vuv` separation disappear before final decoded waveform
- Good next structures to isolate include:
  - frame projection weights
  - overlap-add reconstruction path
  - any explicit frame-to-waveform gain or synthesis mixing stage that can erase the recovered residual contrast
