# 568 Stage5 Fine-Structure Code Oracle And WavePCA16 Bootstrap Report

## Summary
- Date: `2026-04-01`
- Goal: continue from the direct waveform-reference oracle gate and test whether local waveform geometry can be compressed into a compact code that still opens the Stage5 route
- Result:
  - added a dedicated compact-code oracle probe over `PCA dim = 8/16/32/64/96/128`
  - added an analysis-only packet materializer that writes `fine_structure_code.waveform_pca_code`
  - added a Stage5 semantic consumer mode `streaming_student_waveform_pca_code_v1`
  - bootstrapped `wavepca16` packet exports, Stage5 dataset packages, train-step smoke, and dataset-loop smoke
- Main conclusion:
  - compact learned linear waveform geometry is viable
  - the route opens already at `dim8`
  - `wavepca16` is now a runnable analysis-only Stage5 upper-bound route

## A. Compact-Code Oracle Sweep
- Probe:
  - `reports/runtime/stage5_fine_structure_code_oracle_probe_reviewslice_full5_r1_1/`
- Compared families:
  - `selected_dynamic_controls`
  - `compact_reference`
  - `waveform_reference_upper_bound`
  - `waveform_pca_code_dim_{8,16,32,64,96,128}`
  - `selected_dynamic_plus_waveform_pca_code_dim_{...}`
- Key results:
  - `selected_dynamic_controls = 0.009515 / 0.012218`
  - `compact_reference = 0.017661 / 0.019218`
  - `waveform_reference_upper_bound = 0.999958 / 0.845117`
  - `waveform_pca_code_dim_8 = 0.531065 / 0.526204`
  - `waveform_pca_code_dim_16 = 0.646892 / 0.640087`
  - `waveform_pca_code_dim_32 = 0.794458 / 0.776159`
  - `waveform_pca_code_dim_64 = 0.871705 / 0.836442`
  - `waveform_pca_code_dim_96 = 0.919344 / 0.861502`
  - `waveform_pca_code_dim_128 = 0.949726 / 0.868634`
  - format above is `linear / mlp`
- Reading:
  - `dim8` already opens the route
  - increasing code dimension monotonically improves waveform recovery
  - the compact magnitude-style family stays weak, but a compact code learned directly from waveform frames does not

## B. New Analysis-Only Packet And Consumer Bootstrap
- New packet materializer:
  - `materialize-streaming-student-fine-structure-pca-packet-export`
- New Stage5 semantic consumer mode:
  - `streaming_student_waveform_pca_code_v1`
- Packet exports:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_tv8_pca16/`
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_se8_pca16/`
- Stage5 dataset package indexes:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_wavepca16_tv8_r1_1/`
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_wavepca16_se8_r1_1/`
- Effective input width:
  - `feature_dim = 16`
  - `periodic_input_dim = 52`
  - `noise_input_dim = 52`

## C. Smoke Verification
- Train-step smoke:
  - `reports/runtime/stage5_wavepca16_trainstep_smoke_tv8_r1_1/`
  - `loss_total = 1.035977`
- Dataset-loop smoke:
  - `reports/runtime/stage5_wavepca16_dataset_training_smoke_r1_1/`
  - validation trend:
    - `step1 = 0.935725`
    - `step2 = 0.894265`
    - `step3 = 0.858789`
- Bootstrap repair that was needed:
  - the first hand-merged `loopsmoke` dataset index was invalid because `train_packages / validation_packages` were accidentally written as `[null]`
  - after rebuilding the merged `full5` and `loopsmoke` indexes with proper arrays and UTF-8 without BOM, the dataset-loop smoke passed normally

## Decision
- Keep:
  - the compact waveform-code family as the new active upper-bound representation class
  - `wavepca16` as the bounded analysis-only Stage5 consumer route
- Do not keep assuming:
  - that only direct waveform-frame references can open the route
  - that a compact learned code would necessarily collapse back to the weak magnitude-style regime
- Next valid step:
  - run bounded Stage5 training and held-out speech-emergence probes on `wavepca16`, then compare the resulting machine behavior against richer-contract
