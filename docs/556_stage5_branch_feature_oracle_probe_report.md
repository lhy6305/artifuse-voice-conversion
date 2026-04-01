# 556 Stage5 Branch-Feature Oracle Probe Report

## Summary
- Date: `2026-04-01`
- Goal: continue the post-`555` upstream localization step and test whether materially stronger record-generalizable fine waveform structure still exists at the raw Stage5 branch-input contract, before the periodic and noise input encoders run
- Result: the new branch-feature oracle probe is now implemented, wired into `manage.py`, and run on the current `templatepushb.step8` anchor over the full active `5`-record review slice
- Main conclusion:
  - coarse target structure is still highly recoverable directly from raw branch inputs and family slices
  - cross-record fine waveform structure is already weak at the raw Stage5 branch-input layer
  - the periodic and noise input encoders only reduce that already-weak signal slightly
  - therefore the main missing fine structure is not created by another downstream Stage5-local head, fusion, or early-encoder tweak
  - the next structural question moves earlier than the current Stage5 branch-input package itself

## Implementation
- New formal probe:
  - `src/v5vc/stage5_branch_feature_oracle_probe.py`
- New CLI entry:
  - `analyze-stage5-nores-branch-feature-oracle-probe`
- The probe fits the same cheap frozen-feature readouts used by `554` and `555`, but on the raw branch-input contract and semantic-family slices:
  - `periodic_branch_features`
  - `noise_branch_features`
  - `joint_branch_features`
  - `z_art_family`
  - `f0_hz_log_norm_family`
  - `event_family`
  - `acoustic_state_family`
  - `conditioning_family`
  - `periodic_hidden`
  - `noise_hidden`

## Runtime
- Checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Dataset index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Split:
  - `validation`
  - `5` records
- Output:
  - `reports/runtime/stage5_branch_feature_oracle_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1/`

## Key Results
- Coarse structure remains very strong before the encoders:
  - raw-input log-spectrum cosine stays around `0.957` to `0.961`
  - `periodic_branch_features` keeps `oracle_rms_corr = 0.999056` and `oracle_vuv_accuracy = 0.999685`
  - `noise_branch_features` keeps `oracle_rms_corr = 0.996698` and `oracle_vuv_accuracy = 1.0`
- Fine waveform recoverability is already weak in raw branch inputs:
  - `periodic_branch_features = 0.010253 / 0.012467`
  - `noise_branch_features = 0.017393 / 0.014108`
  - `joint_branch_features = 0.009443 / 0.009499`
  - format above is `linear / mlp`
- Family slices do not reveal a hidden strong temporal reservoir:
  - best dynamic family linear waveform cosine is only `acoustic_state_family = 0.020021`
  - best dynamic family waveform MLP cosine is only `f0_hz_log_norm_family = 0.019484`
  - `event_family = 0.012228 / 0.012376`
  - `z_art_family = 0.010485 / 0.011778`
- Static-family caution:
  - `conditioning_family` reaches `0.022368 / 0.022368`, which is slightly higher than the dynamic families
  - but it also has `oracle_rms_corr = 0.0` and `oracle_vuv_accuracy = 0.471101`
  - because this slice is frame-constant conditioning, that tiny score should be read only as weak record-level leakage rather than temporal fine waveform structure
- Early encoder loss is small relative to the already-weak raw signal:
  - `periodic_branch_features -> periodic_hidden` waveform drop is only `0.001814 / 0.000779`
  - `noise_branch_features -> noise_hidden` waveform drop is only `0.004939 / 0.000880`
  - format above is `linear / mlp`
- Formal probe diagnosis:
  - `fine_waveform_geometry_is_already_weak_in_stage5_branch_inputs`

## Interpretation
- This probe moves the localization one step earlier again instead of reversing `554` or `555`.
- The earlier producer-path reading from `555` is still valid:
  - `waveform_decoder_input_hidden -> waveform_decoder_base_logits` remains the sharpest visible downstream linear collapse site
- But `556` now closes the next ambiguity:
  - the current Stage5 branch inputs themselves do not contain strong record-generalizable fine waveform geometry
  - the periodic and noise input encoders are not the main place where a strong temporal waveform reservoir disappears
  - the raw family slices also do not hide a materially better branch-local signal that the current encoders merely fail to preserve
- So the problem has moved earlier than the current Stage5 package boundary:
  - either the packaged control and conditioning families are intrinsically too coarse for the missing target-specific fine structure
  - or the upstream representation and supervision pipeline is failing to form a usable fine-structure-bearing contract before Stage5 sees it

## Decision
- Keep:
  - the new branch-feature oracle probe as the current earliest Stage5-local localization reference after `555`
  - the reading that Stage5 still preserves coarse structure but never receives strong shared fine waveform geometry in the first place
- Stop treating as the default next move:
  - another local output-head redesign
  - another producer or fusion micro-tune
  - a story that the periodic or noise input encoders are the newly proven main collapse source

## Recommended Next Action
- The next structural work should move earlier than the current Stage5 branch-input package.
- Valid next directions now are:
  - inspect whether the upstream source-scaffold control contract can in principle carry the missing target-specific fine structure
  - or redesign upstream representation formation and supervision so that the Stage5 package exposes materially richer fine temporal detail than the current near-zero branch-input oracle signal
