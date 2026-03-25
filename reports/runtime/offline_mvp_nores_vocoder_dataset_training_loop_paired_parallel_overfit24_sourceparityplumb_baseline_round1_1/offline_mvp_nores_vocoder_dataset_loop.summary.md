# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-25T20:09:37
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_sourceparityplumb_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-25T20:09:32", "ended_at": "2026-03-25T20:09:37", "duration_sec": 4.401484}
- dataset: {"train_package_count": 2, "validation_package_count": 2}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 24, "packages_per_step": 2, "validation_interval": 24, "checkpoint_interval": 24, "sampler_mode": "sequential", "seed": 20260317, "deterministic": false, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.0, "waveform": 0.0, "stft": 0.0, "rms_guard": 0.0, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "multires_stft_short": 0.0, "use_predicted_activity_gate": false, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}, "semantic_supervision": {"enabled": false, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45, "package_alpha": 0.2}}

## Step History
- step=1 loss_total=1.056926 loss_total_semantic_weighted=1.056926 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=2 loss_total=0.93643 loss_total_semantic_weighted=0.93643 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=3 loss_total=0.842642 loss_total_semantic_weighted=0.842642 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=4 loss_total=0.778696 loss_total_semantic_weighted=0.778696 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=5 loss_total=0.737817 loss_total_semantic_weighted=0.737817 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=6 loss_total=0.711238 loss_total_semantic_weighted=0.711238 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=7 loss_total=0.69191 loss_total_semantic_weighted=0.69191 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=8 loss_total=0.675312 loss_total_semantic_weighted=0.675312 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=9 loss_total=0.667 loss_total_semantic_weighted=0.667 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=10 loss_total=0.658991 loss_total_semantic_weighted=0.658991 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=11 loss_total=0.652374 loss_total_semantic_weighted=0.652374 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=12 loss_total=0.644861 loss_total_semantic_weighted=0.644861 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=13 loss_total=0.638405 loss_total_semantic_weighted=0.638405 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=14 loss_total=0.630361 loss_total_semantic_weighted=0.630361 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=15 loss_total=0.624065 loss_total_semantic_weighted=0.624065 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=16 loss_total=0.619188 loss_total_semantic_weighted=0.619188 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=17 loss_total=0.612857 loss_total_semantic_weighted=0.612857 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=18 loss_total=0.606743 loss_total_semantic_weighted=0.606743 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=19 loss_total=0.600963 loss_total_semantic_weighted=0.600963 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=20 loss_total=0.596202 loss_total_semantic_weighted=0.596202 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=21 loss_total=0.591759 loss_total_semantic_weighted=0.591759 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=22 loss_total=0.586191 loss_total_semantic_weighted=0.586191 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=23 loss_total=0.580651 loss_total_semantic_weighted=0.580651 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- step=24 loss_total=0.575501 loss_total_semantic_weighted=0.575501 packages_per_step=2 record_ids=['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']

## Validation History
- step=24 validation_source=validation_packages package_count=2 loss_total=0.572382 loss_total_semantic_weighted=0.572382

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_semantic_weighted_over_recorded_checkpoints", "step": 24, "loss_total": 0.572382, "selection_metric": "loss_total_semantic_weighted", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.
- When semantic_supervision.enabled=true, optimization uses a conservative package-level weighting derived from target_event_semantic_sidecar; raw loss_total remains logged alongside loss_total_semantic_weighted.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether target-side semantic weighting should stay as a bootstrap objective bias or later move into a more explicit design-state e_evt consumer path.
