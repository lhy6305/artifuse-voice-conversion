# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-27T22:05:33
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-27T22:05:00", "ended_at": "2026-03-27T22:05:33", "duration_sec": 32.555544}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "fusion_mode": "branch_mean_contrast_residual_v1", "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 1, "packages_per_step": 4, "validation_interval": 1, "checkpoint_interval": 1, "sampler_mode": "shuffle", "seed": 20260327, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "frame_spectral_flux_zero_target_jitter": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "multires_stft_short": 0.0, "noise_energy_frame_rms_excess_corr": 0.0, "noise_aper_energy_frame_rms_excess_corr": 0.0, "noise_energy_frame_rms_lagcorr_excess": 0.0, "noise_aper_energy_frame_rms_lagcorr_excess": 0.0, "waveform_decoder_base_logits_high_band_excess": 0.1, "waveform_decoder_base_logits_aper_lagcorr_excess": 0.0, "waveform_decoder_base_logits_noise_energy_lagcorr_excess": 0.0, "waveform_residual_shape_delta_noise_energy_lagcorr_excess": 0.0, "waveform_decoder_base_logits_active_template": 0.1, "waveform_decoder_base_logits_aper_abs_zero_lag_corr": 0.1, "waveform_decoder_base_logits_noise_energy_abs_zero_lag_corr": 0.1, "waveform_residual_shape_delta_noise_energy_abs_zero_lag_corr": 0.1, "frame_rms_lagcorr_max_lag_frames": 4, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}, "semantic_supervision": {"enabled": false, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45, "package_alpha": 0.2}}

## Step History
- step=1 loss_total=2.054299 loss_total_semantic_weighted=2.054299 packages_per_step=4 record_ids=['target::chapter3_3_firefly_221', 'target::chapter3_30_firefly_155', 'target::chapter3_21_firefly_110', 'target::chapter3_3_firefly_144']

## Validation History
- step=1 validation_source=validation_packages package_count=66 loss_total=2.034964 loss_total_semantic_weighted=2.034964

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_hbe_smoke_fullsplit1step_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_hbe_smoke_fullsplit1step_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_semantic_weighted_over_recorded_checkpoints", "step": 1, "loss_total": 2.034964, "selection_metric": "loss_total_semantic_weighted", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_hbe_smoke_fullsplit1step_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.
- When semantic_supervision.enabled=true, optimization uses a conservative package-level weighting derived from target_event_semantic_sidecar; raw loss_total remains logged alongside loss_total_semantic_weighted.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether target-side semantic weighting should stay as a bootstrap objective bias or later move into a more explicit design-state e_evt consumer path.
