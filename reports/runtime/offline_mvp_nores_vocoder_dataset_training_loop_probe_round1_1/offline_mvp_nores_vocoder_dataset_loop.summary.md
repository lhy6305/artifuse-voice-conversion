# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-17T22:54:18
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-17T22:54:17", "ended_at": "2026-03-17T22:54:18", "duration_sec": 1.417011}
- dataset: {"train_package_count": 8, "validation_package_count": 2}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 1, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2}}

## Step History
- step=1 loss_total=1.050081 packages_per_step=4 record_ids=['target::chapter3_3_firefly_154', 'target::chapter3_29_firefly_140', 'target::chapter3_3_firefly_124', 'target::chapter3_17_firefly_137']
- step=2 loss_total=0.888035 packages_per_step=4 record_ids=['target::chapter3_22_firefly_105', 'target::chapter3_3_firefly_249', 'target::chapter3_17_firefly_136', 'target::chapter3_17_firefly_138']
- step=3 loss_total=0.773256 packages_per_step=4 record_ids=['target::chapter3_3_firefly_249', 'target::chapter3_17_firefly_137', 'target::chapter3_22_firefly_105', 'target::chapter3_29_firefly_140']
- step=4 loss_total=0.751396 packages_per_step=4 record_ids=['target::chapter3_17_firefly_138', 'target::chapter3_17_firefly_136', 'target::chapter3_3_firefly_124', 'target::chapter3_3_firefly_154']

## Validation History
- step=1 validation_source=validation_packages package_count=2 loss_total=0.902686
- step=2 validation_source=validation_packages package_count=2 loss_total=0.803836
- step=3 validation_source=validation_packages package_count=2 loss_total=0.737672
- step=4 validation_source=validation_packages package_count=2 loss_total=0.694789

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_probe_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step2.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_probe_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_probe_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 4, "loss_total": 0.694789, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_probe_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation still reports proxy spectral/gate targets and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Only after the dataset path is stable should Stage5 move to decoder and waveform/STFT reconstruction objectives.
