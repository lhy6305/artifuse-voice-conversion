# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-25T14:26:56
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-25T14:21:52", "ended_at": "2026-03-25T14:26:56", "duration_sec": 303.630014}
- dataset: {"train_package_count": 2, "validation_package_count": 2}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "periodic_plus_noise_residual_shape_recurrent"}
- training: {"num_steps": 72, "packages_per_step": 2, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "sequential", "seed": 20260325, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.55, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.2, "periodic_waveform_frame_delta": 0.25, "periodic_waveform_frame_adjacent_cosine": 0.01, "periodic_waveform_frame_rms_floor": 0.65, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=5.481162 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=2 loss_total=5.263213 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=3 loss_total=5.102672 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=4 loss_total=4.976827 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=5 loss_total=4.882229 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=6 loss_total=4.814736 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=7 loss_total=4.770559 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=8 loss_total=4.733007 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=9 loss_total=4.700058 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=10 loss_total=4.668216 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=11 loss_total=4.63905 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=12 loss_total=4.610455 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=13 loss_total=4.584847 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=14 loss_total=4.565143 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=15 loss_total=4.542973 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=16 loss_total=4.520561 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=17 loss_total=4.509809 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=18 loss_total=4.494172 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=19 loss_total=4.480262 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=20 loss_total=4.463516 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=21 loss_total=4.448759 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=22 loss_total=4.436751 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=23 loss_total=4.427478 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=24 loss_total=4.419648 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=25 loss_total=4.406902 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=26 loss_total=4.402265 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=27 loss_total=4.392758 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=28 loss_total=4.380136 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=29 loss_total=4.377696 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=30 loss_total=4.363195 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=31 loss_total=4.359544 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=32 loss_total=4.351206 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=33 loss_total=4.350033 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=34 loss_total=4.344975 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=35 loss_total=4.337245 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=36 loss_total=4.33227 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=37 loss_total=4.326137 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=38 loss_total=4.322261 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=39 loss_total=4.317561 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=40 loss_total=4.315205 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=41 loss_total=4.313956 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=42 loss_total=4.307709 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=43 loss_total=4.301912 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=44 loss_total=4.299797 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=45 loss_total=4.295237 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=46 loss_total=4.290833 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=47 loss_total=4.28813 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=48 loss_total=4.288884 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=49 loss_total=4.283016 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=50 loss_total=4.287181 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=51 loss_total=4.281671 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=52 loss_total=4.280302 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=53 loss_total=4.27524 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=54 loss_total=4.276535 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=55 loss_total=4.269707 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=56 loss_total=4.272662 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=57 loss_total=4.26974 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=58 loss_total=4.263227 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=59 loss_total=4.259315 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=60 loss_total=4.263321 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=61 loss_total=4.253154 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=62 loss_total=4.250643 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=63 loss_total=4.251527 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=64 loss_total=4.247319 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=65 loss_total=4.251153 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=66 loss_total=4.247901 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=67 loss_total=4.24669 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=68 loss_total=4.246526 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=69 loss_total=4.242743 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=70 loss_total=4.237916 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=71 loss_total=4.241207 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=72 loss_total=4.239958 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']

## Validation History
- step=12 validation_source=validation_packages package_count=2 loss_total=4.584847
- step=24 validation_source=validation_packages package_count=2 loss_total=4.406902
- step=36 validation_source=validation_packages package_count=2 loss_total=4.326137
- step=48 validation_source=validation_packages package_count=2 loss_total=4.283016
- step=60 validation_source=validation_packages package_count=2 loss_total=4.253154
- step=72 validation_source=validation_packages package_count=2 loss_total=4.23636

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step60.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 72, "loss_total": 4.23636, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
