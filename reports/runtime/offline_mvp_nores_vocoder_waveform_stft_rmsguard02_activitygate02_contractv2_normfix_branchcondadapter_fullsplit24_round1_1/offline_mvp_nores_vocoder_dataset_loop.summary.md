# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-26T18:48:09
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-26T18:46:47", "ended_at": "2026-03-26T18:48:09", "duration_sec": 81.848294}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 24, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260318, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "frame_spectral_flux_zero_target_jitter": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "multires_stft_short": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}, "semantic_supervision": {"enabled": false, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45, "package_alpha": 0.2}}

## Step History
- step=1 loss_total=1.800856 loss_total_semantic_weighted=1.800856 packages_per_step=4 record_ids=['target::chapter3_29_firefly_131', 'target::archive_firefly_20', 'target::chapter3_30_firefly_153', 'target::chapter4_29_firefly_101']
- step=2 loss_total=1.546003 loss_total_semantic_weighted=1.546003 packages_per_step=4 record_ids=['target::archive_firefly_18', 'target::chapter3_30_firefly_134', 'target::chapter3_29_firefly_128', 'target::chapter3_2_firefly_143']
- step=3 loss_total=1.368562 loss_total_semantic_weighted=1.368562 packages_per_step=4 record_ids=['target::chapter3_29_firefly_125', 'target::chapter3_2_firefly_207', 'target::archive_firefly_13', 'target::chapter3_3_firefly_177']
- step=4 loss_total=1.300142 loss_total_semantic_weighted=1.300142 packages_per_step=4 record_ids=['target::chapter3_20_firefly_163', 'target::chapter3_20_firefly_105', 'target::chapter3_17_firefly_142', 'target::chapter3_2_firefly_194']
- step=5 loss_total=1.216054 loss_total_semantic_weighted=1.216054 packages_per_step=4 record_ids=['target::chapter3_2_firefly_187', 'target::chapter3_2_firefly_232', 'target::chapter3_30_firefly_133', 'target::chapter3_3_firefly_118']
- step=6 loss_total=1.187918 loss_total_semantic_weighted=1.187918 packages_per_step=4 record_ids=['target::chapter3_2_firefly_135', 'target::chapter3_2_firefly_179', 'target::chapter4_7_firefly_113', 'target::chapter3_17_firefly_114']
- step=7 loss_total=1.179568 loss_total_semantic_weighted=1.179568 packages_per_step=4 record_ids=['target::chapter3_30_firefly_116', 'target::chapter3_30_firefly_156', 'target::archive_firefly_5', 'target::chapter3_17_firefly_139']
- step=8 loss_total=1.176074 loss_total_semantic_weighted=1.176074 packages_per_step=4 record_ids=['target::chapter3_26_firefly_110', 'target::chapter3_2_firefly_185', 'target::chapter4_7_firefly_117', 'target::chapter3_3_firefly_238']
- step=9 loss_total=1.161723 loss_total_semantic_weighted=1.161723 packages_per_step=4 record_ids=['target::chapter3_30_firefly_130', 'target::chapter3_20_firefly_148', 'target::chapter3_2_firefly_140', 'target::chapter3_22_firefly_118']
- step=10 loss_total=1.103615 loss_total_semantic_weighted=1.103615 packages_per_step=4 record_ids=['target::chapter3_29_firefly_115', 'target::chapter3_20_firefly_143', 'target::chapter3_2_firefly_242', 'target::chapter3_2_firefly_226']
- step=11 loss_total=1.082648 loss_total_semantic_weighted=1.082648 packages_per_step=4 record_ids=['target::chapter3_3_firefly_106', 'target::chapter3_2_firefly_221', 'target::chapter3_20_firefly_157', 'target::chapter3_17_firefly_105']
- step=12 loss_total=1.094132 loss_total_semantic_weighted=1.094132 packages_per_step=4 record_ids=['target::chapter3_22_firefly_101', 'target::chapter3_2_firefly_182', 'target::chapter3_3_firefly_221', 'target::chapter3_2_firefly_248']
- step=13 loss_total=1.001331 loss_total_semantic_weighted=1.001331 packages_per_step=4 record_ids=['target::chapter3_3_firefly_203', 'target::chapter3_2_firefly_136', 'target::chapter3_2_firefly_175', 'target::chapter3_22_firefly_113']
- step=14 loss_total=1.046197 loss_total_semantic_weighted=1.046197 packages_per_step=4 record_ids=['target::chapter3_22_firefly_122', 'target::chapter3_3_firefly_200', 'target::chapter3_4_firefly_120', 'target::chapter3_3_firefly_102']
- step=15 loss_total=1.037202 loss_total_semantic_weighted=1.037202 packages_per_step=4 record_ids=['target::chapter3_20_firefly_132', 'target::chapter3_29_firefly_117', 'target::chapter3_29_firefly_104', 'target::chapter3_17_firefly_109']
- step=16 loss_total=0.923008 loss_total_semantic_weighted=0.923008 packages_per_step=4 record_ids=['target::chapter3_3_firefly_123', 'target::chapter3_17_firefly_125', 'target::chapter3_3_firefly_237', 'target::chapter3_3_firefly_144']
- step=17 loss_total=0.996738 loss_total_semantic_weighted=0.996738 packages_per_step=4 record_ids=['target::chapter3_4_firefly_138', 'target::chapter3_17_firefly_157', 'target::chapter3_17_firefly_101', 'target::chapter3_3_firefly_152']
- step=18 loss_total=0.930414 loss_total_semantic_weighted=0.930414 packages_per_step=4 record_ids=['target::chapter3_4_firefly_136', 'target::chapter3_29_firefly_138', 'target::chapter3_20_firefly_115', 'target::chapter3_18_firefly_104']
- step=19 loss_total=0.908555 loss_total_semantic_weighted=0.908555 packages_per_step=4 record_ids=['target::chapter3_2_firefly_156', 'target::chapter3_3_firefly_130', 'target::chapter3_2_firefly_247', 'target::chapter3_2_firefly_129']
- step=20 loss_total=0.866794 loss_total_semantic_weighted=0.866794 packages_per_step=4 record_ids=['target::chapter3_20_firefly_170', 'target::chapter3_2_firefly_114', 'target::chapter3_4_firefly_127', 'target::chapter3_20_firefly_162']
- step=21 loss_total=0.900016 loss_total_semantic_weighted=0.900016 packages_per_step=4 record_ids=['target::chapter3_20_firefly_147', 'target::chapter3_3_firefly_250', 'target::chapter3_2_firefly_122', 'target::chapter3_2_firefly_222']
- step=22 loss_total=0.91163 loss_total_semantic_weighted=0.91163 packages_per_step=4 record_ids=['target::chapter3_3_firefly_167', 'target::chapter4_7_firefly_120', 'target::chapter3_20_firefly_159', 'target::chapter3_3_firefly_151']
- step=23 loss_total=0.852117 loss_total_semantic_weighted=0.852117 packages_per_step=4 record_ids=['target::chapter3_2_firefly_208', 'target::chapter3_29_firefly_108', 'target::chapter3_20_firefly_102', 'target::chapter3_3_firefly_226']
- step=24 loss_total=0.792205 loss_total_semantic_weighted=0.792205 packages_per_step=4 record_ids=['target::chapter3_20_firefly_129', 'target::chapter3_2_firefly_218', 'target::chapter3_3_firefly_159', 'target::chapter3_2_firefly_198']

## Validation History
- step=12 validation_source=validation_packages package_count=66 loss_total=1.014239 loss_total_semantic_weighted=1.014239
- step=24 validation_source=validation_packages package_count=66 loss_total=0.807557 loss_total_semantic_weighted=0.807557

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchcondadapter_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchcondadapter_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchcondadapter_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_semantic_weighted_over_recorded_checkpoints", "step": 24, "loss_total": 0.807557, "selection_metric": "loss_total_semantic_weighted", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchcondadapter_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.
- When semantic_supervision.enabled=true, optimization uses a conservative package-level weighting derived from target_event_semantic_sidecar; raw loss_total remains logged alongside loss_total_semantic_weighted.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether target-side semantic weighting should stay as a bootstrap objective bias or later move into a more explicit design-state e_evt consumer path.
