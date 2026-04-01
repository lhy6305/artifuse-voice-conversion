# 561 Stage5 Richer Source-Contract Consumer Plumbing Report

## Summary
- Date: `2026-04-01`
- Goal: stop at localization and actually land the first bounded upstream-contract redesign on the active streaming-student Stage5 route
- Result:
  - added a new Stage5 `semantic_consumer_mode = streaming_student_richer_source_contract_v1`
  - the new mode appends richer upstream packet families into both Stage5 branches during package build
  - verified package build on a 1-sample smoke and on the full5 review slice
  - verified Stage5 single-step training smoke on the richer-contract package path
- Main conclusion:
  - the first richer upstream contract is now real plumbing, not just a probe idea
  - it is machine-verified as package-buildable and train-step-consumable
  - it is not yet a quality result and should not be overread as evidence that the route is solved

## Implementation
- Code path:
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- New mode:
  - `streaming_student_richer_source_contract_v1`
- Current richer feature family:
  - packet `reference_controls`
    - `f0_hz`
    - `vuv`
    - `aper`
    - `energy_log`
    - `energy_stage5_norm`
  - packet `diagnostics`
    - `coarse_log_f0`
    - `log_f0_correction`
    - `event_logits`
    - `event_prior_probs`
  - packet `conditioning`
    - `alpha`
    - `speaker_embedding`
    - `geom_embedding`
- Feature shape:
  - richer sidecar dim = `48`
  - previous Stage5 branch input dim = `36`
  - richer-contract Stage5 branch input dim = `84`
- Compatibility rule:
  - this mode is for new Stage5 package/training routes
  - do not reuse old `36/36` no-res checkpoints on this `84/84` input contract

## Runtime Verification
- 1-sample smoke build:
  - output: `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8_richercontract_smoke/`
  - semantic consumer summary confirms:
    - `feature_dim = 48`
    - `source_contract_reference_feature_dim = 5`
    - `source_contract_diagnostic_feature_dim = 18`
    - `source_contract_conditioning_feature_dim = 25`
    - `periodic_input_dim = 84`
    - `noise_input_dim = 84`
- Full5 review-slice richer-contract dataset:
  - because the active full5 slice spans two packet exports, it was rebuilt as:
    - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_tv8_r1_1/`
    - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_se8_r1_1/`
  - then merged into:
    - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - merged validation summary:
    - `validation_package_count = 5`
    - `periodic_input_dims = [84]`
    - `noise_input_dims = [84]`
- Stage5 single-step training smoke:
  - output: `reports/runtime/stage5_richercontract_trainstep_smoke_r1_1/`
  - result:
    - `loss_total = 1.053148`
    - `grad_norm = 2.355891`
    - `duration_sec = 2.541918`
  - interpretation:
    - the richer-contract package is accepted by the Stage5 training path
    - forward, backward, optimizer, and checkpoint save all complete normally

## Additional Bugfix
- While pushing the smoke run through, an existing CLI mismatch surfaced:
  - `run-offline-mvp-nores-vocoder-train-step` dispatch referenced dynamic-basis / noise-hidden-residual arguments that were not fully wired through the parser and step function
- Fixed:
  - added the missing parser arguments in `src/v5vc/cli.py`
  - aligned `run_offline_mvp_nores_vocoder_training_step` in `src/v5vc/offline_vocoder_training.py`
- This bugfix is not specific to the richer-contract route, but the new smoke run exposed it immediately

## Decision
- Keep:
  - the `557` to `560` diagnosis that current old contracts are weak
  - the move from probe-only work into real upstream-contract implementation
- Do not claim yet:
  - that the richer contract already improves decoded quality
  - that the active missing fine waveform geometry problem is solved
- Next valid machine step:
  - launch bounded Stage5 training experiments on the new `84/84` richer-contract review-slice dataset
  - only after machine-side checkpoint/export evidence becomes promising should human listening audit be reintroduced
