# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-27T18:29:11
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-27T18:27:34", "ended_at": "2026-03-27T18:29:11", "duration_sec": 96.989526}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "fusion_mode": "branch_mean_contrast_residual_v1", "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 24, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260327, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "frame_spectral_flux_zero_target_jitter": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "multires_stft_short": 0.0, "noise_energy_frame_rms_excess_corr": 0.0, "noise_aper_energy_frame_rms_excess_corr": 0.0, "noise_energy_frame_rms_lagcorr_excess": 0.2, "noise_aper_energy_frame_rms_lagcorr_excess": 0.2, "frame_rms_lagcorr_max_lag_frames": 4, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}, "semantic_supervision": {"enabled": false, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45, "package_alpha": 0.2}}

## Step History
- step=1 loss_total=1.761277 loss_total_semantic_weighted=1.761277 packages_per_step=4 record_ids=['target::chapter3_3_firefly_221', 'target::chapter3_30_firefly_155', 'target::chapter3_21_firefly_110', 'target::chapter3_3_firefly_144']
- step=2 loss_total=1.551686 loss_total_semantic_weighted=1.551686 packages_per_step=4 record_ids=['target::chapter4_7_firefly_102', 'target::chapter3_2_firefly_245', 'target::chapter3_2_firefly_127', 'target::chapter3_3_firefly_185']
- step=3 loss_total=1.430432 loss_total_semantic_weighted=1.430432 packages_per_step=4 record_ids=['target::chapter3_3_firefly_214', 'target::chapter3_20_firefly_176', 'target::chapter3_29_firefly_123', 'target::chapter3_20_firefly_141']
- step=4 loss_total=1.337122 loss_total_semantic_weighted=1.337122 packages_per_step=4 record_ids=['target::chapter3_20_firefly_150', 'target::chapter3_17_firefly_109', 'target::chapter3_6_firefly_108', 'target::chapter3_3_firefly_157']
- step=5 loss_total=1.278152 loss_total_semantic_weighted=1.278152 packages_per_step=4 record_ids=['target::chapter3_30_firefly_119', 'target::chapter3_3_firefly_231', 'target::chapter3_20_firefly_108', 'target::chapter3_2_firefly_175']
- step=6 loss_total=1.275036 loss_total_semantic_weighted=1.275036 packages_per_step=4 record_ids=['target::chapter3_30_firefly_128', 'target::chapter3_3_firefly_158', 'target::chapter3_17_firefly_145', 'target::chapter3_4_firefly_122']
- step=7 loss_total=1.169605 loss_total_semantic_weighted=1.169605 packages_per_step=4 record_ids=['target::chapter3_30_firefly_113', 'target::chapter3_6_firefly_107', 'target::chapter3_3_firefly_123', 'target::chapter3_2_firefly_180']
- step=8 loss_total=1.110793 loss_total_semantic_weighted=1.110793 packages_per_step=4 record_ids=['target::chapter3_17_firefly_151', 'target::chapter3_6_firefly_111', 'target::chapter3_2_firefly_149', 'target::chapter3_3_firefly_103']
- step=9 loss_total=1.098841 loss_total_semantic_weighted=1.098841 packages_per_step=4 record_ids=['target::chapter3_3_firefly_203', 'target::chapter3_20_firefly_126', 'target::chapter3_2_firefly_197', 'target::chapter3_17_firefly_139']
- step=10 loss_total=1.102467 loss_total_semantic_weighted=1.102467 packages_per_step=4 record_ids=['target::chapter3_2_firefly_174', 'target::chapter3_2_firefly_217', 'target::chapter3_3_firefly_186', 'target::chapter3_2_firefly_185']
- step=11 loss_total=1.155877 loss_total_semantic_weighted=1.155877 packages_per_step=4 record_ids=['target::chapter3_4_firefly_139', 'target::chapter3_3_firefly_176', 'target::chapter3_20_firefly_173', 'target::chapter3_17_firefly_138']
- step=12 loss_total=1.095767 loss_total_semantic_weighted=1.095767 packages_per_step=4 record_ids=['target::chapter3_2_firefly_244', 'target::chapter3_17_firefly_107', 'target::chapter4_7_firefly_116', 'target::chapter3_2_firefly_228']
- step=13 loss_total=1.059824 loss_total_semantic_weighted=1.059824 packages_per_step=4 record_ids=['target::chapter3_2_firefly_179', 'target::chapter3_2_firefly_215', 'target::chapter3_30_firefly_106', 'target::archive_firefly_3']
- step=14 loss_total=1.092665 loss_total_semantic_weighted=1.092665 packages_per_step=4 record_ids=['target::chapter3_4_firefly_129', 'target::chapter3_3_firefly_119', 'target::chapter4_29_firefly_102', 'target::chapter3_30_firefly_129']
- step=15 loss_total=1.029516 loss_total_semantic_weighted=1.029516 packages_per_step=4 record_ids=['target::chapter3_5_firefly_104', 'target::chapter3_20_firefly_148', 'target::chapter3_21_firefly_105', 'target::chapter3_30_firefly_104']
- step=16 loss_total=0.977924 loss_total_semantic_weighted=0.977924 packages_per_step=4 record_ids=['target::chapter3_3_firefly_201', 'target::chapter3_2_firefly_139', 'target::chapter3_29_firefly_119', 'target::chapter3_17_firefly_144']
- step=17 loss_total=0.972267 loss_total_semantic_weighted=0.972267 packages_per_step=4 record_ids=['target::chapter3_29_firefly_127', 'target::chapter3_4_firefly_114', 'target::archive_firefly_16', 'target::chapter3_3_firefly_232']
- step=18 loss_total=0.916688 loss_total_semantic_weighted=0.916688 packages_per_step=4 record_ids=['target::chapter3_30_firefly_133', 'target::chapter3_2_firefly_213', 'target::chapter3_17_firefly_103', 'target::chapter3_20_firefly_136']
- step=19 loss_total=0.935157 loss_total_semantic_weighted=0.935157 packages_per_step=4 record_ids=['target::chapter3_2_firefly_108', 'target::chapter3_20_firefly_115', 'target::chapter3_4_firefly_136', 'target::chapter3_2_firefly_250']
- step=20 loss_total=0.943944 loss_total_semantic_weighted=0.943944 packages_per_step=4 record_ids=['target::chapter3_21_firefly_103', 'target::chapter3_20_firefly_169', 'target::chapter3_3_firefly_135', 'target::chapter3_4_firefly_141']
- step=21 loss_total=0.858242 loss_total_semantic_weighted=0.858242 packages_per_step=4 record_ids=['target::chapter3_3_firefly_236', 'target::chapter3_3_firefly_241', 'target::chapter3_3_firefly_216', 'target::chapter3_2_firefly_119']
- step=22 loss_total=0.857563 loss_total_semantic_weighted=0.857563 packages_per_step=4 record_ids=['target::chapter3_2_firefly_204', 'target::chapter3_29_firefly_102', 'target::chapter3_3_firefly_131', 'target::chapter3_22_firefly_112']
- step=23 loss_total=0.845714 loss_total_semantic_weighted=0.845714 packages_per_step=4 record_ids=['target::chapter3_2_firefly_125', 'target::chapter3_30_firefly_108', 'target::chapter3_2_firefly_104', 'target::chapter3_20_firefly_110']
- step=24 loss_total=0.829762 loss_total_semantic_weighted=0.829762 packages_per_step=4 record_ids=['target::chapter3_3_firefly_128', 'target::chapter3_3_firefly_161', 'target::chapter3_30_firefly_141', 'target::chapter3_17_firefly_111']

## Validation History
- step=12 validation_source=validation_packages package_count=66 loss_total=1.01808 loss_total_semantic_weighted=1.01808
- step=24 validation_source=validation_packages package_count=66 loss_total=0.825358 loss_total_semantic_weighted=0.825358

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_nea02_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_nea02_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_nea02_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_semantic_weighted_over_recorded_checkpoints", "step": 24, "loss_total": 0.825358, "selection_metric": "loss_total_semantic_weighted", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_nea02_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.
- When semantic_supervision.enabled=true, optimization uses a conservative package-level weighting derived from target_event_semantic_sidecar; raw loss_total remains logged alongside loss_total_semantic_weighted.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether target-side semantic weighting should stay as a bootstrap objective bias or later move into a more explicit design-state e_evt consumer path.
