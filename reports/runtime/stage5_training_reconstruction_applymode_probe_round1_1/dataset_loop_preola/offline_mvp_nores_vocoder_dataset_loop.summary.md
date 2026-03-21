# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-21T17:26:40
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-21T17:26:39", "ended_at": "2026-03-21T17:26:40", "duration_sec": 1.748381}
- dataset: {"train_package_count": 2, "validation_package_count": 1}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 3, "packages_per_step": 2, "validation_interval": 1, "checkpoint_interval": 3, "sampler_mode": "sequential", "seed": 20260317, "deterministic": false, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.0, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=1.659013 packages_per_step=2 record_ids=['target::chapter3_22_firefly_105', 'target::chapter3_17_firefly_138']
- step=2 loss_total=1.501973 packages_per_step=2 record_ids=['target::chapter3_22_firefly_105', 'target::chapter3_17_firefly_138']
- step=3 loss_total=1.398098 packages_per_step=2 record_ids=['target::chapter3_22_firefly_105', 'target::chapter3_17_firefly_138']

## Validation History
- step=1 validation_source=validation_packages package_count=1 loss_total=1.518547
- step=2 validation_source=validation_packages package_count=1 loss_total=1.396164
- step=3 validation_source=validation_packages package_count=1 loss_total=1.286636

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/dataset_loop_preola/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step3.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/dataset_loop_preola/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step3.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 3, "loss_total": 1.286636, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/dataset_loop_preola/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step3.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
