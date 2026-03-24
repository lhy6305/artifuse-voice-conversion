# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-24T11:15:49
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-24T11:15:15", "ended_at": "2026-03-24T11:15:49", "duration_sec": 33.863885}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 2, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260324, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.05, "frame_delta": 6.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=8.15045 packages_per_step=4 record_ids=['target::chapter3_17_firefly_155', 'target::chapter3_2_firefly_235', 'target::chapter3_20_firefly_122', 'target::chapter3_22_firefly_112']
- step=2 loss_total=7.465626 packages_per_step=4 record_ids=['target::chapter3_17_firefly_123', 'target::chapter3_20_firefly_140', 'target::chapter3_21_firefly_111', 'target::chapter3_20_firefly_116']
- step=3 loss_total=6.460034 packages_per_step=4 record_ids=['target::chapter3_2_firefly_246', 'target::chapter3_20_firefly_171', 'target::chapter3_30_firefly_104', 'target::chapter3_3_firefly_242']
- step=4 loss_total=6.959633 packages_per_step=4 record_ids=['target::chapter3_3_firefly_157', 'target::chapter3_17_firefly_120', 'target::chapter3_30_firefly_130', 'target::chapter3_2_firefly_139']

## Validation History
- step=2 validation_source=validation_packages package_count=66 loss_total=7.041812
- step=4 validation_source=validation_packages package_count=66 loss_total=6.86659

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template005_delta6_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step2.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template005_delta6_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template005_delta6_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 4, "loss_total": 6.86659, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template005_delta6_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
