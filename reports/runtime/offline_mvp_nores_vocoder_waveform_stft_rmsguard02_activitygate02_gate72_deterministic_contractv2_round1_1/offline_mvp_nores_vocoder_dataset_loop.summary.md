# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-24T03:06:52
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-24T03:02:46", "ended_at": "2026-03-24T03:06:52", "duration_sec": 245.251286}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 72, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260318, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Step History
- step=1 loss_total=1.773865 packages_per_step=4 record_ids=['target::chapter3_29_firefly_131', 'target::archive_firefly_20', 'target::chapter3_30_firefly_153', 'target::chapter4_29_firefly_101']
- step=2 loss_total=1.56381 packages_per_step=4 record_ids=['target::archive_firefly_18', 'target::chapter3_30_firefly_134', 'target::chapter3_29_firefly_128', 'target::chapter3_2_firefly_143']
- step=3 loss_total=1.402512 packages_per_step=4 record_ids=['target::chapter3_29_firefly_125', 'target::chapter3_2_firefly_207', 'target::archive_firefly_13', 'target::chapter3_3_firefly_177']
- step=4 loss_total=1.297318 packages_per_step=4 record_ids=['target::chapter3_20_firefly_163', 'target::chapter3_20_firefly_105', 'target::chapter3_17_firefly_142', 'target::chapter3_2_firefly_194']
- step=5 loss_total=1.228681 packages_per_step=4 record_ids=['target::chapter3_2_firefly_187', 'target::chapter3_2_firefly_232', 'target::chapter3_30_firefly_133', 'target::chapter3_3_firefly_118']
- step=6 loss_total=1.189381 packages_per_step=4 record_ids=['target::chapter3_2_firefly_135', 'target::chapter3_2_firefly_179', 'target::chapter4_7_firefly_113', 'target::chapter3_17_firefly_114']
- step=7 loss_total=1.164333 packages_per_step=4 record_ids=['target::chapter3_30_firefly_116', 'target::chapter3_30_firefly_156', 'target::archive_firefly_5', 'target::chapter3_17_firefly_139']
- step=8 loss_total=1.145616 packages_per_step=4 record_ids=['target::chapter3_26_firefly_110', 'target::chapter3_2_firefly_185', 'target::chapter4_7_firefly_117', 'target::chapter3_3_firefly_238']
- step=9 loss_total=1.132003 packages_per_step=4 record_ids=['target::chapter3_30_firefly_130', 'target::chapter3_20_firefly_148', 'target::chapter3_2_firefly_140', 'target::chapter3_22_firefly_118']
- step=10 loss_total=1.074215 packages_per_step=4 record_ids=['target::chapter3_29_firefly_115', 'target::chapter3_20_firefly_143', 'target::chapter3_2_firefly_242', 'target::chapter3_2_firefly_226']
- step=11 loss_total=1.066126 packages_per_step=4 record_ids=['target::chapter3_3_firefly_106', 'target::chapter3_2_firefly_221', 'target::chapter3_20_firefly_157', 'target::chapter3_17_firefly_105']
- step=12 loss_total=1.073797 packages_per_step=4 record_ids=['target::chapter3_22_firefly_101', 'target::chapter3_2_firefly_182', 'target::chapter3_3_firefly_221', 'target::chapter3_2_firefly_248']
- step=13 loss_total=0.97407 packages_per_step=4 record_ids=['target::chapter3_3_firefly_203', 'target::chapter3_2_firefly_136', 'target::chapter3_2_firefly_175', 'target::chapter3_22_firefly_113']
- step=14 loss_total=1.041936 packages_per_step=4 record_ids=['target::chapter3_22_firefly_122', 'target::chapter3_3_firefly_200', 'target::chapter3_4_firefly_120', 'target::chapter3_3_firefly_102']
- step=15 loss_total=1.043613 packages_per_step=4 record_ids=['target::chapter3_20_firefly_132', 'target::chapter3_29_firefly_117', 'target::chapter3_29_firefly_104', 'target::chapter3_17_firefly_109']
- step=16 loss_total=0.91714 packages_per_step=4 record_ids=['target::chapter3_3_firefly_123', 'target::chapter3_17_firefly_125', 'target::chapter3_3_firefly_237', 'target::chapter3_3_firefly_144']
- step=17 loss_total=1.003131 packages_per_step=4 record_ids=['target::chapter3_4_firefly_138', 'target::chapter3_17_firefly_157', 'target::chapter3_17_firefly_101', 'target::chapter3_3_firefly_152']
- step=18 loss_total=0.960484 packages_per_step=4 record_ids=['target::chapter3_4_firefly_136', 'target::chapter3_29_firefly_138', 'target::chapter3_20_firefly_115', 'target::chapter3_18_firefly_104']
- step=19 loss_total=0.926072 packages_per_step=4 record_ids=['target::chapter3_2_firefly_156', 'target::chapter3_3_firefly_130', 'target::chapter3_2_firefly_247', 'target::chapter3_2_firefly_129']
- step=20 loss_total=0.890275 packages_per_step=4 record_ids=['target::chapter3_20_firefly_170', 'target::chapter3_2_firefly_114', 'target::chapter3_4_firefly_127', 'target::chapter3_20_firefly_162']
- step=21 loss_total=0.913623 packages_per_step=4 record_ids=['target::chapter3_20_firefly_147', 'target::chapter3_3_firefly_250', 'target::chapter3_2_firefly_122', 'target::chapter3_2_firefly_222']
- step=22 loss_total=0.930808 packages_per_step=4 record_ids=['target::chapter3_3_firefly_167', 'target::chapter4_7_firefly_120', 'target::chapter3_20_firefly_159', 'target::chapter3_3_firefly_151']
- step=23 loss_total=0.870078 packages_per_step=4 record_ids=['target::chapter3_2_firefly_208', 'target::chapter3_29_firefly_108', 'target::chapter3_20_firefly_102', 'target::chapter3_3_firefly_226']
- step=24 loss_total=0.82903 packages_per_step=4 record_ids=['target::chapter3_20_firefly_129', 'target::chapter3_2_firefly_218', 'target::chapter3_3_firefly_159', 'target::chapter3_2_firefly_198']
- step=25 loss_total=0.834149 packages_per_step=4 record_ids=['target::chapter3_2_firefly_174', 'target::chapter3_17_firefly_104', 'target::chapter3_3_firefly_116', 'target::chapter3_17_firefly_146']
- step=26 loss_total=0.885066 packages_per_step=4 record_ids=['target::chapter3_20_firefly_150', 'target::chapter3_2_firefly_236', 'target::archive_firefly_12', 'target::archive_firefly_17']
- step=27 loss_total=0.842905 packages_per_step=4 record_ids=['target::chapter3_22_firefly_124', 'target::chapter3_2_firefly_132', 'target::chapter3_2_firefly_234', 'target::chapter3_4_firefly_117']
- step=28 loss_total=0.874495 packages_per_step=4 record_ids=['target::chapter3_30_firefly_119', 'target::chapter3_2_firefly_250', 'target::chapter3_21_firefly_107', 'target::chapter3_3_firefly_219']
- step=29 loss_total=0.775063 packages_per_step=4 record_ids=['target::archive_firefly_19', 'target::chapter3_3_firefly_165', 'target::chapter3_2_firefly_225', 'target::chapter3_20_firefly_106']
- step=30 loss_total=0.798685 packages_per_step=4 record_ids=['target::chapter3_2_firefly_169', 'target::chapter3_2_firefly_245', 'target::chapter3_20_firefly_156', 'target::chapter3_5_firefly_103']
- step=31 loss_total=0.785864 packages_per_step=4 record_ids=['target::chapter3_17_firefly_111', 'target::chapter3_2_firefly_223', 'target::chapter3_2_firefly_215', 'target::chapter3_3_firefly_227']
- step=32 loss_total=0.771213 packages_per_step=4 record_ids=['target::chapter3_30_firefly_155', 'target::chapter3_2_firefly_125', 'target::chapter3_30_firefly_107', 'target::chapter3_21_firefly_114']
- step=33 loss_total=0.788783 packages_per_step=4 record_ids=['target::chapter3_20_firefly_136', 'target::archive_firefly_11', 'target::archive_firefly_1', 'target::chapter3_30_firefly_142']
- step=34 loss_total=0.80368 packages_per_step=4 record_ids=['target::chapter3_3_firefly_231', 'target::chapter3_5_firefly_106', 'target::chapter3_20_firefly_154', 'target::chapter3_29_firefly_111']
- step=35 loss_total=0.763572 packages_per_step=4 record_ids=['target::chapter3_29_firefly_127', 'target::chapter3_20_firefly_107', 'target::chapter3_2_firefly_162', 'target::chapter3_30_firefly_131']
- step=36 loss_total=0.743374 packages_per_step=4 record_ids=['target::chapter3_3_firefly_243', 'target::chapter3_2_firefly_219', 'target::chapter3_29_firefly_126', 'target::chapter3_30_firefly_124']
- step=37 loss_total=0.794311 packages_per_step=4 record_ids=['target::chapter3_30_firefly_113', 'target::chapter3_3_firefly_172', 'target::chapter3_2_firefly_147', 'target::chapter3_4_firefly_142']
- step=38 loss_total=0.770582 packages_per_step=4 record_ids=['target::chapter3_20_firefly_110', 'target::chapter3_3_firefly_163', 'target::chapter3_20_firefly_103', 'target::chapter3_2_firefly_106']
- step=39 loss_total=0.751596 packages_per_step=4 record_ids=['target::chapter3_18_firefly_102', 'target::chapter3_26_firefly_109', 'target::chapter3_3_firefly_189', 'target::chapter3_20_firefly_104']
- step=40 loss_total=0.795367 packages_per_step=4 record_ids=['target::chapter3_26_firefly_113', 'target::chapter3_30_firefly_128', 'target::chapter3_4_firefly_128', 'target::chapter3_17_firefly_121']
- step=41 loss_total=0.722812 packages_per_step=4 record_ids=['target::chapter3_2_firefly_211', 'target::chapter3_3_firefly_150', 'target::chapter3_20_firefly_122', 'target::chapter3_4_firefly_134']
- step=42 loss_total=0.715203 packages_per_step=4 record_ids=['target::chapter3_3_firefly_204', 'target::chapter3_20_firefly_113', 'target::chapter3_30_firefly_140', 'target::chapter3_4_firefly_108']
- step=43 loss_total=0.786306 packages_per_step=4 record_ids=['target::chapter3_20_firefly_178', 'target::chapter3_2_firefly_192', 'target::chapter3_3_firefly_251', 'target::chapter3_2_firefly_105']
- step=44 loss_total=0.73418 packages_per_step=4 record_ids=['target::chapter3_2_firefly_128', 'target::archive_firefly_9', 'target::chapter3_20_firefly_114', 'target::chapter3_17_firefly_135']
- step=45 loss_total=0.693423 packages_per_step=4 record_ids=['target::chapter3_2_firefly_180', 'target::chapter3_3_firefly_117', 'target::chapter3_4_firefly_132', 'target::chapter3_20_firefly_139']
- step=46 loss_total=0.739966 packages_per_step=4 record_ids=['target::chapter3_30_firefly_105', 'target::chapter3_2_firefly_112', 'target::chapter3_3_firefly_192', 'target::archive_firefly_10']
- step=47 loss_total=0.753574 packages_per_step=4 record_ids=['target::chapter3_20_firefly_152', 'target::chapter3_4_firefly_144', 'target::chapter3_3_firefly_248', 'target::chapter4_7_firefly_115']
- step=48 loss_total=0.796306 packages_per_step=4 record_ids=['target::chapter3_17_firefly_137', 'target::chapter3_20_firefly_182', 'target::chapter3_2_firefly_115', 'target::chapter3_29_firefly_135']
- step=49 loss_total=0.702089 packages_per_step=4 record_ids=['target::chapter3_3_firefly_136', 'target::chapter3_30_firefly_118', 'target::chapter3_3_firefly_129', 'target::chapter3_2_firefly_196']
- step=50 loss_total=0.794928 packages_per_step=4 record_ids=['target::chapter3_3_firefly_184', 'target::chapter3_22_firefly_103', 'target::chapter3_3_firefly_113', 'target::chapter3_2_firefly_195']
- step=51 loss_total=0.816338 packages_per_step=4 record_ids=['target::chapter3_26_firefly_104', 'target::chapter3_17_firefly_149', 'target::chapter3_4_firefly_130', 'target::chapter3_20_firefly_124']
- step=52 loss_total=0.762382 packages_per_step=4 record_ids=['target::chapter3_3_firefly_157', 'target::chapter3_3_firefly_191', 'target::chapter3_3_firefly_155', 'target::chapter3_17_firefly_110']
- step=53 loss_total=0.704109 packages_per_step=4 record_ids=['target::chapter3_3_firefly_187', 'target::chapter3_6_firefly_101', 'target::chapter3_2_firefly_126', 'target::chapter3_4_firefly_131']
- step=54 loss_total=0.648796 packages_per_step=4 record_ids=['target::chapter3_3_firefly_253', 'target::chapter3_3_firefly_169', 'target::chapter3_30_firefly_127', 'target::chapter3_3_firefly_229']
- step=55 loss_total=0.706557 packages_per_step=4 record_ids=['target::chapter3_2_firefly_224', 'target::chapter3_3_firefly_128', 'target::chapter3_20_firefly_116', 'target::chapter3_29_firefly_132']
- step=56 loss_total=0.753451 packages_per_step=4 record_ids=['target::chapter3_22_firefly_108', 'target::chapter3_3_firefly_147', 'target::chapter4_7_firefly_111', 'target::chapter3_17_firefly_153']
- step=57 loss_total=0.713081 packages_per_step=4 record_ids=['target::chapter3_3_firefly_201', 'target::chapter3_20_firefly_153', 'target::chapter3_3_firefly_121', 'target::chapter3_29_firefly_124']
- step=58 loss_total=0.658021 packages_per_step=4 record_ids=['target::chapter3_3_firefly_104', 'target::chapter3_26_firefly_108', 'target::chapter3_3_firefly_175', 'target::chapter3_17_firefly_117']
- step=59 loss_total=0.60745 packages_per_step=4 record_ids=['target::chapter3_2_firefly_104', 'target::chapter3_22_firefly_112', 'target::chapter3_3_firefly_224', 'target::chapter3_2_firefly_177']
- step=60 loss_total=0.746804 packages_per_step=4 record_ids=['target::chapter3_20_firefly_101', 'target::chapter3_2_firefly_167', 'target::chapter3_17_firefly_118', 'target::chapter3_22_firefly_123']
- step=61 loss_total=0.689158 packages_per_step=4 record_ids=['target::archive_firefly_4', 'target::chapter3_30_firefly_106', 'target::chapter3_2_firefly_110', 'target::chapter3_2_firefly_217']
- step=62 loss_total=0.64828 packages_per_step=4 record_ids=['target::chapter3_3_firefly_143', 'target::chapter3_3_firefly_146', 'target::chapter3_3_firefly_218', 'target::chapter3_2_firefly_116']
- step=63 loss_total=0.680248 packages_per_step=4 record_ids=['target::chapter3_20_firefly_171', 'target::chapter3_22_firefly_121', 'target::chapter3_3_firefly_107', 'target::chapter3_3_firefly_228']
- step=64 loss_total=0.745105 packages_per_step=4 record_ids=['target::chapter3_20_firefly_120', 'target::chapter3_20_firefly_158', 'target::chapter3_21_firefly_109', 'target::chapter3_3_firefly_125']
- step=65 loss_total=0.664867 packages_per_step=4 record_ids=['target::chapter3_17_firefly_116', 'target::chapter3_2_firefly_251', 'target::chapter3_30_firefly_148', 'target::chapter3_3_firefly_225']
- step=66 loss_total=0.669539 packages_per_step=4 record_ids=['target::chapter3_3_firefly_193', 'target::chapter3_3_firefly_112', 'target::chapter3_17_firefly_136', 'target::chapter3_3_firefly_235']
- step=67 loss_total=0.7088 packages_per_step=4 record_ids=['target::chapter3_3_firefly_140', 'target::chapter3_3_firefly_164', 'target::chapter3_21_firefly_111', 'target::chapter3_2_firefly_233']
- step=68 loss_total=0.737471 packages_per_step=4 record_ids=['target::chapter3_2_firefly_228', 'target::chapter3_2_firefly_158', 'target::chapter3_20_firefly_180', 'target::chapter3_20_firefly_125']
- step=69 loss_total=0.754232 packages_per_step=4 record_ids=['target::chapter3_3_firefly_119', 'target::chapter3_2_firefly_134', 'target::chapter3_30_firefly_135', 'target::chapter3_20_firefly_123']
- step=70 loss_total=0.61169 packages_per_step=4 record_ids=['target::chapter3_6_firefly_112', 'target::chapter3_3_firefly_222', 'target::chapter3_2_firefly_186', 'target::chapter3_2_firefly_166']
- step=71 loss_total=0.750708 packages_per_step=4 record_ids=['target::chapter3_20_firefly_168', 'target::chapter3_2_firefly_161', 'target::chapter3_4_firefly_115', 'target::chapter3_3_firefly_154']
- step=72 loss_total=0.754283 packages_per_step=4 record_ids=['target::chapter3_29_firefly_121', 'target::chapter3_20_firefly_117', 'target::chapter3_3_firefly_132', 'target::chapter3_3_firefly_139']

## Validation History
- step=12 validation_source=validation_packages package_count=66 loss_total=0.986235
- step=24 validation_source=validation_packages package_count=66 loss_total=0.818536
- step=36 validation_source=validation_packages package_count=66 loss_total=0.734092
- step=48 validation_source=validation_packages package_count=66 loss_total=0.689489
- step=60 validation_source=validation_packages package_count=66 loss_total=0.669387
- step=72 validation_source=validation_packages package_count=66 loss_total=0.658881

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step60.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 72, "loss_total": 0.658881, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
