# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-26T21:48:53
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_eevttargetcontract_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-26T21:47:14", "ended_at": "2026-03-26T21:48:53", "duration_sec": 98.609973}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400, "waveform_decoder_mode": "fused_single"}
- training: {"num_steps": 24, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260326, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "frame_adjacent_cosine": 0.0, "frame_spectral_flux_zero_target_jitter": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "fused_hidden_branch_mean": 0.0, "periodic_waveform_frame_delta": 0.0, "periodic_waveform_frame_adjacent_cosine": 0.0, "periodic_waveform_frame_rms_floor": 0.0, "periodic_waveform_stft": 0.0, "periodic_waveform_high_band_excess": 0.0, "multires_stft_short": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}, "semantic_supervision": {"enabled": false, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45, "package_alpha": 0.2}}

## Step History
- step=1 loss_total=2.066151 loss_total_semantic_weighted=2.066151 packages_per_step=4 record_ids=['target::chapter3_3_firefly_185', 'target::chapter3_2_firefly_221', 'target::chapter3_17_firefly_126', 'target::chapter3_3_firefly_241']
- step=2 loss_total=1.793228 loss_total_semantic_weighted=1.793228 packages_per_step=4 record_ids=['target::chapter3_2_firefly_134', 'target::chapter3_3_firefly_112', 'target::chapter3_20_firefly_183', 'target::chapter3_17_firefly_148']
- step=3 loss_total=1.654197 loss_total_semantic_weighted=1.654197 packages_per_step=4 record_ids=['target::chapter4_7_firefly_122', 'target::chapter3_3_firefly_125', 'target::chapter4_7_firefly_114', 'target::chapter3_3_firefly_223']
- step=4 loss_total=1.507972 loss_total_semantic_weighted=1.507972 packages_per_step=4 record_ids=['target::chapter3_20_firefly_161', 'target::chapter4_7_firefly_120', 'target::chapter3_30_firefly_135', 'target::chapter3_3_firefly_208']
- step=5 loss_total=1.377292 loss_total_semantic_weighted=1.377292 packages_per_step=4 record_ids=['target::chapter3_20_firefly_153', 'target::chapter3_3_firefly_151', 'target::chapter3_18_firefly_102', 'target::chapter3_3_firefly_179']
- step=6 loss_total=1.238227 loss_total_semantic_weighted=1.238227 packages_per_step=4 record_ids=['target::chapter3_3_firefly_142', 'target::chapter3_3_firefly_158', 'target::chapter3_3_firefly_224', 'target::chapter3_3_firefly_202']
- step=7 loss_total=1.25437 loss_total_semantic_weighted=1.25437 packages_per_step=4 record_ids=['target::chapter3_3_firefly_238', 'target::chapter3_17_firefly_142', 'target::chapter3_2_firefly_120', 'target::chapter4_7_firefly_106']
- step=8 loss_total=1.212086 loss_total_semantic_weighted=1.212086 packages_per_step=4 record_ids=['target::chapter3_3_firefly_164', 'target::chapter3_2_firefly_151', 'target::chapter3_3_firefly_195', 'target::chapter3_22_firefly_125']
- step=9 loss_total=1.105652 loss_total_semantic_weighted=1.105652 packages_per_step=4 record_ids=['target::chapter3_3_firefly_235', 'target::chapter3_3_firefly_136', 'target::chapter3_3_firefly_178', 'target::chapter3_3_firefly_226']
- step=10 loss_total=1.13262 loss_total_semantic_weighted=1.13262 packages_per_step=4 record_ids=['target::chapter3_2_firefly_112', 'target::chapter3_2_firefly_107', 'target::chapter3_21_firefly_101', 'target::chapter3_20_firefly_154']
- step=11 loss_total=1.089196 loss_total_semantic_weighted=1.089196 packages_per_step=4 record_ids=['target::chapter3_29_firefly_123', 'target::chapter3_3_firefly_216', 'target::chapter3_2_firefly_174', 'target::chapter3_20_firefly_170']
- step=12 loss_total=1.025923 loss_total_semantic_weighted=1.025923 packages_per_step=4 record_ids=['target::chapter3_6_firefly_102', 'target::chapter3_2_firefly_205', 'target::chapter3_2_firefly_246', 'target::chapter3_4_firefly_143']
- step=13 loss_total=1.043098 loss_total_semantic_weighted=1.043098 packages_per_step=4 record_ids=['target::chapter3_30_firefly_126', 'target::chapter3_4_firefly_110', 'target::chapter3_30_firefly_131', 'target::chapter3_2_firefly_106']
- step=14 loss_total=0.965831 loss_total_semantic_weighted=0.965831 packages_per_step=4 record_ids=['target::chapter3_2_firefly_124', 'target::chapter3_2_firefly_226', 'target::chapter3_3_firefly_130', 'target::chapter3_21_firefly_110']
- step=15 loss_total=1.027393 loss_total_semantic_weighted=1.027393 packages_per_step=4 record_ids=['target::chapter3_3_firefly_251', 'target::archive_firefly_5', 'target::chapter3_21_firefly_103', 'target::chapter3_3_firefly_248']
- step=16 loss_total=0.957694 loss_total_semantic_weighted=0.957694 packages_per_step=4 record_ids=['target::chapter3_30_firefly_157', 'target::chapter3_2_firefly_161', 'target::chapter3_2_firefly_191', 'target::chapter3_17_firefly_117']
- step=17 loss_total=0.977336 loss_total_semantic_weighted=0.977336 packages_per_step=4 record_ids=['target::chapter3_30_firefly_113', 'target::chapter3_20_firefly_124', 'target::chapter3_3_firefly_120', 'target::chapter3_29_firefly_128']
- step=18 loss_total=0.957962 loss_total_semantic_weighted=0.957962 packages_per_step=4 record_ids=['target::chapter3_2_firefly_129', 'target::chapter3_21_firefly_106', 'target::chapter3_22_firefly_111', 'target::chapter3_3_firefly_187']
- step=19 loss_total=0.942799 loss_total_semantic_weighted=0.942799 packages_per_step=4 record_ids=['target::chapter3_30_firefly_152', 'target::chapter3_17_firefly_141', 'target::chapter3_20_firefly_150', 'target::chapter3_3_firefly_128']
- step=20 loss_total=0.977835 loss_total_semantic_weighted=0.977835 packages_per_step=4 record_ids=['target::archive_firefly_12', 'target::chapter3_2_firefly_141', 'target::chapter3_17_firefly_131', 'target::chapter3_4_firefly_125']
- step=21 loss_total=0.89959 loss_total_semantic_weighted=0.89959 packages_per_step=4 record_ids=['target::chapter3_2_firefly_185', 'target::chapter3_3_firefly_220', 'target::chapter3_17_firefly_155', 'target::chapter3_2_firefly_197']
- step=22 loss_total=0.867649 loss_total_semantic_weighted=0.867649 packages_per_step=4 record_ids=['target::chapter3_2_firefly_159', 'target::chapter3_2_firefly_193', 'target::chapter3_3_firefly_228', 'target::chapter3_22_firefly_124']
- step=23 loss_total=0.825129 loss_total_semantic_weighted=0.825129 packages_per_step=4 record_ids=['target::chapter3_22_firefly_119', 'target::chapter3_2_firefly_202', 'target::chapter3_20_firefly_151', 'target::chapter3_2_firefly_213']
- step=24 loss_total=0.943915 loss_total_semantic_weighted=0.943915 packages_per_step=4 record_ids=['target::chapter3_4_firefly_144', 'target::chapter3_17_firefly_138', 'target::chapter3_4_firefly_116', 'target::chapter3_2_firefly_194']

## Validation History
- step=12 validation_source=validation_packages package_count=66 loss_total=1.031313 loss_total_semantic_weighted=1.031313
- step=24 validation_source=validation_packages package_count=66 loss_total=0.832195 loss_total_semantic_weighted=0.832195

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_eevttargetcontract_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_eevttargetcontract_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_eevttargetcontract_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_semantic_weighted_over_recorded_checkpoints", "step": 24, "loss_total": 0.832195, "selection_metric": "loss_total_semantic_weighted", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_eevttargetcontract_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.
- When semantic_supervision.enabled=true, optimization uses a conservative package-level weighting derived from target_event_semantic_sidecar; raw loss_total remains logged alongside loss_total_semantic_weighted.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether target-side semantic weighting should stay as a bootstrap objective bias or later move into a more explicit design-state e_evt consumer path.
