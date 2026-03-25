# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-25T15:29:31
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-25T15:29:01", "ended_at": "2026-03-25T15:29:31", "duration_sec": 30.144579}
- dataset: {"train_package_count": 2, "validation_package_count": 2}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 24, "packages_per_step": 2, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "sequential", "seed": 20260325, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.0, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "multires_stft_short": 0.05, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=1.617127 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=2 loss_total=1.481545 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=3 loss_total=1.375495 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=4 loss_total=1.280533 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=5 loss_total=1.215745 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=6 loss_total=1.165838 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=7 loss_total=1.137396 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=8 loss_total=1.111861 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=9 loss_total=1.089511 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=10 loss_total=1.067808 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=11 loss_total=1.044147 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=12 loss_total=1.032534 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=13 loss_total=1.012997 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=14 loss_total=0.998548 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=15 loss_total=0.985289 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=16 loss_total=0.973491 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=17 loss_total=0.957582 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=18 loss_total=0.944902 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=19 loss_total=0.932704 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=20 loss_total=0.91993 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=21 loss_total=0.905767 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=22 loss_total=0.89335 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=23 loss_total=0.884724 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=24 loss_total=0.876108 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']

## Validation History
- step=12 validation_source=validation_packages package_count=2 loss_total=1.012997
- step=24 validation_source=validation_packages package_count=2 loss_total=0.869588

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort005_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort005_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort005_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 24, "loss_total": 0.869588, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort005_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
