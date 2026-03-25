# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-25T15:01:28
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-25T15:01:23", "ended_at": "2026-03-25T15:01:28", "duration_sec": 4.770911}
- dataset: {"train_package_count": 2, "validation_package_count": 2}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 1, "packages_per_step": 1, "validation_interval": 1, "checkpoint_interval": 1, "sampler_mode": "sequential", "seed": 20260325, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.0, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=1.705199 packages_per_step=1 record_ids=['paired::parallel_firefly_107_to_target_firefly_107']

## Validation History
- step=1 validation_source=validation_packages package_count=2 loss_total=1.557057

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/tmp_direct_call_mrstftshort020_probe/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/tmp_direct_call_mrstftshort020_probe/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 1, "loss_total": 1.557057, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/tmp_direct_call_mrstftshort020_probe/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
