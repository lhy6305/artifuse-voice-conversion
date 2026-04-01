# 562 Stage5 Richer-Contract Dataset-Loop Smoke And Partial-Init Report

## Summary
- Date: `2026-04-01`
- Goal: continue past package plumbing and verify that the new richer-contract Stage5 route can actually run through the dataset-level training loop, including warm-start from the previous Stage5 checkpoint family
- Result:
  - built a loop-smoke dataset index for the richer-contract full5 review slice
  - ran a 3-step random-init dataset-loop smoke successfully
  - exposed and fixed two loop-side compatibility gaps
  - ran a 3-step partial-init warm-start dataset-loop smoke successfully from the old `templatepushb.step8` anchor
- Main conclusion:
  - the richer-contract route is now verified end-to-end through Stage5 dataset training, not just single-package build or one-step backward
  - old checkpoints remain incompatible for direct reuse as-is, but they are now usable as partial init when shape-mismatched first-layer weights are skipped explicitly

## Runtime Artifacts
- Richer-contract review-slice dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Loop-smoke-compatible index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_loopsmoke_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - this duplicates the same 5 richer-contract packages into both `train_packages` and `validation_packages` only for bounded startup verification
- Random-init loop smoke:
  - `reports/runtime/stage5_richercontract_dataset_training_smoke_r1_1/`
- Warm-start loop smoke:
  - `reports/runtime/stage5_richercontract_dataset_training_warmstart_smoke_r1_1/`

## Machine Results
- Random-init richer-contract loop smoke:
  - step losses:
    - `1.044976`
    - `0.903801`
    - `0.772228`
  - validation losses:
    - `0.891822`
    - `0.794656`
    - `0.722739`
  - best checkpoint:
    - `.../stage5_richercontract_dataset_training_smoke_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step3.pt`
- Warm-start richer-contract loop smoke from old `templatepushb.step8`:
  - init checkpoint:
    - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
  - step losses:
    - `1.039297`
    - `0.909187`
    - `0.788542`
  - validation losses:
    - `0.896395`
    - `0.794914`
    - `0.725259`
  - partial-init summary:
    - `missing_keys = ["periodic_encoder.0.weight", "noise_encoder.0.weight"]`
    - `skipped_shape_mismatch_keys = ["periodic_encoder.0.weight", "noise_encoder.0.weight"]`
  - best checkpoint:
    - `.../stage5_richercontract_dataset_training_warmstart_smoke_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step3.pt`

## Bugfixes Landed While Running The Loop
- Dataset-loop index compatibility:
  - `run-offline-mvp-nores-vocoder-dataset-training-loop` previously rejected `streaming_student_stage5_dataset_index_v1`
  - fixed by allowing the streaming-student Stage5 dataset index version on the same no-res package schema
- Partial-init shape mismatch handling:
  - previous `strict=False` loading still crashed when old checkpoint weights had wrong shapes for widened `84`-dim richer-contract inputs
  - fixed by filtering out shape-mismatched keys when `allow_partial_init_checkpoint_load` is enabled

## Interpretation
- What is now proven:
  - richer-contract packages build cleanly
  - single-package train-step works
  - dataset-level training loop works
  - old Stage5 checkpoints can be reused as partial init except for the widened first encoder layers
- What is not yet proven:
  - audible quality improvement
  - better cross-record fine waveform behavior
  - whether warm-start is materially better than random-init after a meaningful training horizon

## Decision
- Keep:
  - the richer-contract implementation path as the active structural route
  - the new partial-init filtering for widened-input Stage5 experiments
- Next valid machine step:
  - launch a longer bounded richer-contract Stage5 training run and compare random-init vs partial-init checkpoints on machine-side review/export metrics
- Human listening:
  - still not needed yet
  - only reintroduce it after a longer richer-contract checkpoint family produces a machine-side reason to listen
