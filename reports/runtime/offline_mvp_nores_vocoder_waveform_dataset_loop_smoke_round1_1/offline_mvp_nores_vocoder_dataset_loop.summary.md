# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-18T00:01:56
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-18T00:01:47", "ended_at": "2026-03-18T00:01:56", "duration_sec": 8.740809}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 2, "packages_per_step": 2, "validation_interval": 1, "checkpoint_interval": 1, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "waveform": 0.5, "stft": 0.5}}

## Step History
- step=1 loss_total=1.801747 packages_per_step=2 record_ids=['target::chapter3_2_firefly_110', 'target::chapter3_29_firefly_129']
- step=2 loss_total=1.600885 packages_per_step=2 record_ids=['target::chapter3_3_firefly_145', 'target::chapter3_3_firefly_224']

## Validation History
- step=1 validation_source=validation_packages package_count=66 loss_total=1.62506
- step=2 validation_source=validation_packages package_count=66 loss_total=1.482311

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_dataset_loop_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_dataset_loop_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step2.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_dataset_loop_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step2.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 2, "loss_total": 1.482311, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_dataset_loop_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step2.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
