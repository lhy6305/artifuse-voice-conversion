# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-25T13:47:26
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-25T13:44:24", "ended_at": "2026-03-25T13:47:26", "duration_sec": 182.07992}
- dataset: {"train_package_count": 2, "validation_package_count": 2}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 72, "packages_per_step": 2, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "sequential", "seed": 20260325, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=1.7406 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=2 loss_total=1.589692 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=3 loss_total=1.469279 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=4 loss_total=1.372771 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=5 loss_total=1.309786 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=6 loss_total=1.255908 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=7 loss_total=1.234201 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=8 loss_total=1.210184 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=9 loss_total=1.190476 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=10 loss_total=1.167734 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=11 loss_total=1.144222 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=12 loss_total=1.125475 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=13 loss_total=1.104484 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=14 loss_total=1.094927 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=15 loss_total=1.076958 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=16 loss_total=1.057574 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=17 loss_total=1.045644 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=18 loss_total=1.03479 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=19 loss_total=1.022355 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=20 loss_total=1.005648 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=21 loss_total=0.992049 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=22 loss_total=0.976131 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=23 loss_total=0.964001 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=24 loss_total=0.953402 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=25 loss_total=0.94829 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=26 loss_total=0.943508 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=27 loss_total=0.937018 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=28 loss_total=0.930232 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=29 loss_total=0.921963 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=30 loss_total=0.915527 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=31 loss_total=0.909904 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=32 loss_total=0.899077 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=33 loss_total=0.895016 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=34 loss_total=0.886524 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=35 loss_total=0.886955 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=36 loss_total=0.881463 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=37 loss_total=0.878302 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=38 loss_total=0.870956 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=39 loss_total=0.865905 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=40 loss_total=0.858317 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=41 loss_total=0.862103 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=42 loss_total=0.853595 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=43 loss_total=0.853592 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=44 loss_total=0.851106 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=45 loss_total=0.845886 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=46 loss_total=0.844031 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=47 loss_total=0.842457 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=48 loss_total=0.836053 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=49 loss_total=0.837504 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=50 loss_total=0.836074 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=51 loss_total=0.835786 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=52 loss_total=0.832572 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=53 loss_total=0.83156 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=54 loss_total=0.825254 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=55 loss_total=0.825866 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=56 loss_total=0.822293 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=57 loss_total=0.821767 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=58 loss_total=0.821128 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=59 loss_total=0.816982 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=60 loss_total=0.81221 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=61 loss_total=0.816814 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=62 loss_total=0.81557 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=63 loss_total=0.812364 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=64 loss_total=0.812959 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=65 loss_total=0.81021 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=66 loss_total=0.80781 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=67 loss_total=0.810126 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=68 loss_total=0.808272 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=69 loss_total=0.808758 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=70 loss_total=0.808078 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=71 loss_total=0.804326 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=72 loss_total=0.805446 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']

## Validation History
- step=12 validation_source=validation_packages package_count=2 loss_total=1.104484
- step=24 validation_source=validation_packages package_count=2 loss_total=0.94829
- step=36 validation_source=validation_packages package_count=2 loss_total=0.878302
- step=48 validation_source=validation_packages package_count=2 loss_total=0.837504
- step=60 validation_source=validation_packages package_count=2 loss_total=0.816814
- step=72 validation_source=validation_packages package_count=2 loss_total=0.803014

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step60.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 72, "loss_total": 0.803014, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
