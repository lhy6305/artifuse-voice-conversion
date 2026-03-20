# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-20T22:12:45
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1_clean_no_reverb/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-20T22:08:22", "ended_at": "2026-03-20T22:12:45", "duration_sec": 263.515605}
- dataset: {"train_package_count": 578, "validation_package_count": 63}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 72, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260318, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "use_predicted_activity_gate": true}}

## Step History
- step=1 loss_total=1.697381 packages_per_step=4 record_ids=['target::chapter3_3_firefly_128', 'target::chapter3_17_firefly_142', 'target::chapter3_4_firefly_143', 'target::chapter3_3_firefly_227']
- step=2 loss_total=1.498163 packages_per_step=4 record_ids=['target::chapter3_3_firefly_230', 'target::chapter3_26_firefly_109', 'target::chapter3_2_firefly_112', 'target::chapter3_29_firefly_111']
- step=3 loss_total=1.374232 packages_per_step=4 record_ids=['target::chapter3_30_firefly_127', 'target::chapter3_17_firefly_157', 'target::chapter3_30_firefly_107', 'target::chapter3_3_firefly_147']
- step=4 loss_total=1.291148 packages_per_step=4 record_ids=['target::archive_firefly_13', 'target::chapter3_3_firefly_193', 'target::chapter3_3_firefly_126', 'target::chapter4_29_firefly_101']
- step=5 loss_total=1.25313 packages_per_step=4 record_ids=['target::chapter3_20_firefly_105', 'target::chapter3_20_firefly_148', 'target::chapter3_2_firefly_156', 'target::chapter3_30_firefly_135']
- step=6 loss_total=1.194307 packages_per_step=4 record_ids=['target::chapter3_20_firefly_115', 'target::chapter3_20_firefly_157', 'target::chapter3_3_firefly_220', 'target::chapter3_20_firefly_134']
- step=7 loss_total=1.108976 packages_per_step=4 record_ids=['target::chapter3_20_firefly_170', 'target::chapter3_2_firefly_129', 'target::chapter3_2_firefly_244', 'target::chapter3_2_firefly_191']
- step=8 loss_total=1.12502 packages_per_step=4 record_ids=['target::chapter3_17_firefly_114', 'target::chapter3_2_firefly_186', 'target::chapter3_3_firefly_164', 'target::chapter3_2_firefly_167']
- step=9 loss_total=1.140089 packages_per_step=4 record_ids=['target::chapter3_18_firefly_104', 'target::chapter3_22_firefly_101', 'target::chapter3_17_firefly_105', 'target::chapter3_3_firefly_247']
- step=10 loss_total=1.030793 packages_per_step=4 record_ids=['target::chapter3_26_firefly_113', 'target::chapter3_20_firefly_136', 'target::chapter4_7_firefly_113', 'target::chapter3_3_firefly_195']
- step=11 loss_total=1.110285 packages_per_step=4 record_ids=['target::chapter3_29_firefly_108', 'target::chapter3_20_firefly_150', 'target::chapter3_20_firefly_132', 'target::chapter3_29_firefly_115']
- step=12 loss_total=1.051609 packages_per_step=4 record_ids=['target::chapter3_29_firefly_125', 'target::chapter3_30_firefly_143', 'target::chapter3_30_firefly_112', 'target::chapter3_30_firefly_142']
- step=13 loss_total=1.043374 packages_per_step=4 record_ids=['target::chapter3_17_firefly_109', 'target::chapter3_4_firefly_141', 'target::chapter3_17_firefly_125', 'target::chapter3_4_firefly_115']
- step=14 loss_total=0.965716 packages_per_step=4 record_ids=['target::chapter3_2_firefly_116', 'target::chapter3_3_firefly_117', 'target::archive_firefly_18', 'target::archive_firefly_11']
- step=15 loss_total=0.99183 packages_per_step=4 record_ids=['target::chapter4_7_firefly_117', 'target::archive_firefly_20', 'target::chapter3_26_firefly_110', 'target::chapter3_17_firefly_116']
- step=16 loss_total=0.984736 packages_per_step=4 record_ids=['target::chapter3_4_firefly_111', 'target::chapter3_20_firefly_156', 'target::chapter3_20_firefly_162', 'target::chapter3_3_firefly_186']
- step=17 loss_total=0.955426 packages_per_step=4 record_ids=['target::chapter3_2_firefly_162', 'target::chapter3_30_firefly_155', 'target::chapter3_3_firefly_251', 'target::chapter3_30_firefly_138']
- step=18 loss_total=0.945142 packages_per_step=4 record_ids=['target::chapter3_2_firefly_208', 'target::chapter3_29_firefly_131', 'target::chapter4_7_firefly_107', 'target::chapter3_3_firefly_218']
- step=19 loss_total=0.913818 packages_per_step=4 record_ids=['target::chapter3_20_firefly_147', 'target::chapter3_30_firefly_103', 'target::chapter3_2_firefly_218', 'target::chapter3_2_firefly_122']
- step=20 loss_total=0.938091 packages_per_step=4 record_ids=['target::chapter3_4_firefly_130', 'target::chapter3_3_firefly_106', 'target::chapter3_2_firefly_179', 'target::chapter3_26_firefly_104']
- step=21 loss_total=0.882197 packages_per_step=4 record_ids=['target::chapter3_20_firefly_102', 'target::chapter3_30_firefly_133', 'target::chapter3_30_firefly_140', 'target::chapter3_2_firefly_158']
- step=22 loss_total=0.881244 packages_per_step=4 record_ids=['target::chapter3_30_firefly_157', 'target::chapter3_2_firefly_143', 'target::chapter3_17_firefly_104', 'target::chapter3_2_firefly_245']
- step=23 loss_total=0.822585 packages_per_step=4 record_ids=['target::chapter3_17_firefly_146', 'target::chapter3_30_firefly_108', 'target::archive_firefly_12', 'target::archive_firefly_17']
- step=24 loss_total=0.870169 packages_per_step=4 record_ids=['target::chapter3_2_firefly_106', 'target::chapter3_4_firefly_128', 'target::chapter3_2_firefly_136', 'target::chapter3_2_firefly_192']
- step=25 loss_total=0.830415 packages_per_step=4 record_ids=['target::chapter3_2_firefly_211', 'target::chapter3_3_firefly_180', 'target::chapter3_4_firefly_122', 'target::chapter3_29_firefly_127']
- step=26 loss_total=0.835072 packages_per_step=4 record_ids=['target::archive_firefly_19', 'target::chapter3_4_firefly_135', 'target::chapter3_2_firefly_229', 'target::chapter3_20_firefly_106']
- step=27 loss_total=0.793793 packages_per_step=4 record_ids=['target::chapter3_3_firefly_172', 'target::chapter3_2_firefly_224', 'target::chapter3_3_firefly_235', 'target::chapter3_3_firefly_240']
- step=28 loss_total=0.777306 packages_per_step=4 record_ids=['target::chapter3_4_firefly_119', 'target::chapter3_3_firefly_226', 'target::chapter3_29_firefly_128', 'target::chapter3_2_firefly_147']
- step=29 loss_total=0.852006 packages_per_step=4 record_ids=['target::chapter3_3_firefly_175', 'target::chapter3_3_firefly_149', 'target::chapter3_2_firefly_221', 'target::chapter3_3_firefly_208']
- step=30 loss_total=0.775829 packages_per_step=4 record_ids=['target::chapter3_3_firefly_237', 'target::chapter3_29_firefly_138', 'target::chapter3_3_firefly_253', 'target::archive_firefly_1']
- step=31 loss_total=0.735428 packages_per_step=4 record_ids=['target::chapter3_2_firefly_193', 'target::chapter3_3_firefly_127', 'target::chapter3_3_firefly_243', 'target::chapter3_20_firefly_163']
- step=32 loss_total=0.734183 packages_per_step=4 record_ids=['target::chapter3_3_firefly_216', 'target::chapter3_3_firefly_238', 'target::chapter3_3_firefly_167', 'target::chapter3_20_firefly_154']
- step=33 loss_total=0.676972 packages_per_step=4 record_ids=['target::chapter3_3_firefly_231', 'target::chapter3_20_firefly_107', 'target::chapter3_2_firefly_225', 'target::chapter3_3_firefly_217']
- step=34 loss_total=0.752673 packages_per_step=4 record_ids=['target::chapter3_29_firefly_126', 'target::chapter3_4_firefly_114', 'target::chapter3_2_firefly_234', 'target::chapter3_2_firefly_223']
- step=35 loss_total=0.782541 packages_per_step=4 record_ids=['target::chapter3_20_firefly_183', 'target::chapter3_30_firefly_113', 'target::chapter3_20_firefly_110', 'target::chapter3_3_firefly_139']
- step=36 loss_total=0.695614 packages_per_step=4 record_ids=['target::chapter3_2_firefly_114', 'target::chapter3_29_firefly_104', 'target::chapter3_18_firefly_102', 'target::chapter3_30_firefly_106']
- step=37 loss_total=0.729268 packages_per_step=4 record_ids=['target::chapter3_2_firefly_242', 'target::chapter3_20_firefly_104', 'target::chapter3_22_firefly_124', 'target::chapter3_30_firefly_105']
- step=38 loss_total=0.657827 packages_per_step=4 record_ids=['target::chapter3_4_firefly_108', 'target::chapter3_17_firefly_121', 'target::chapter3_2_firefly_194', 'target::chapter3_2_firefly_213']
- step=39 loss_total=0.743958 packages_per_step=4 record_ids=['target::chapter3_20_firefly_122', 'target::chapter3_4_firefly_120', 'target::chapter3_3_firefly_178', 'target::chapter3_20_firefly_113']
- step=40 loss_total=0.71421 packages_per_step=4 record_ids=['target::chapter3_30_firefly_118', 'target::chapter3_2_firefly_110', 'target::chapter3_20_firefly_178', 'target::chapter3_3_firefly_250']
- step=41 loss_total=0.697004 packages_per_step=4 record_ids=['target::chapter3_2_firefly_126', 'target::chapter3_2_firefly_169', 'target::archive_firefly_9', 'target::chapter3_20_firefly_114']
- step=42 loss_total=0.715822 packages_per_step=4 record_ids=['target::chapter3_17_firefly_135', 'target::chapter3_3_firefly_236', 'target::chapter3_2_firefly_228', 'target::chapter3_3_firefly_248']
- step=43 loss_total=0.671494 packages_per_step=4 record_ids=['target::chapter3_20_firefly_139', 'target::chapter3_30_firefly_130', 'target::chapter3_3_firefly_144', 'target::archive_firefly_10']
- step=44 loss_total=0.643715 packages_per_step=4 record_ids=['target::chapter3_20_firefly_152', 'target::chapter3_3_firefly_123', 'target::chapter3_29_firefly_124', 'target::chapter3_3_firefly_202']
- step=45 loss_total=0.759488 packages_per_step=4 record_ids=['target::chapter3_17_firefly_137', 'target::chapter3_20_firefly_182', 'target::chapter3_29_firefly_132', 'target::chapter3_29_firefly_117']
- step=46 loss_total=0.632857 packages_per_step=4 record_ids=['target::chapter3_3_firefly_112', 'target::chapter3_30_firefly_123', 'target::chapter3_2_firefly_180', 'target::chapter3_2_firefly_132']
- step=47 loss_total=0.642232 packages_per_step=4 record_ids=['target::chapter3_22_firefly_103', 'target::chapter3_2_firefly_219', 'target::chapter3_2_firefly_177', 'target::chapter3_17_firefly_149']
- step=48 loss_total=0.638475 packages_per_step=4 record_ids=['target::chapter3_3_firefly_192', 'target::chapter3_20_firefly_124', 'target::chapter3_2_firefly_128', 'target::chapter3_3_firefly_165']
- step=49 loss_total=0.674747 packages_per_step=4 record_ids=['target::chapter3_3_firefly_131', 'target::chapter3_17_firefly_110', 'target::chapter3_3_firefly_161', 'target::chapter3_3_firefly_225']
- step=50 loss_total=0.652601 packages_per_step=4 record_ids=['target::chapter3_4_firefly_127', 'target::chapter3_2_firefly_135', 'target::chapter3_20_firefly_128', 'target::chapter3_3_firefly_177']
- step=51 loss_total=0.584149 packages_per_step=4 record_ids=['target::chapter3_2_firefly_174', 'target::chapter3_3_firefly_179', 'target::chapter3_3_firefly_156', 'target::chapter4_7_firefly_111']
- step=52 loss_total=0.707136 packages_per_step=4 record_ids=['target::chapter3_20_firefly_116', 'target::chapter3_22_firefly_108', 'target::chapter3_3_firefly_102', 'target::chapter3_3_firefly_209']
- step=53 loss_total=0.675467 packages_per_step=4 record_ids=['target::chapter3_17_firefly_153', 'target::chapter3_2_firefly_185', 'target::chapter3_20_firefly_153', 'target::chapter3_2_firefly_236']
- step=54 loss_total=0.612621 packages_per_step=4 record_ids=['target::chapter3_3_firefly_229', 'target::chapter3_26_firefly_108', 'target::chapter3_2_firefly_125', 'target::chapter3_17_firefly_117']
- step=55 loss_total=0.586388 packages_per_step=4 record_ids=['target::chapter3_22_firefly_112', 'target::chapter3_3_firefly_221', 'target::chapter3_2_firefly_161', 'target::chapter3_20_firefly_101']
- step=56 loss_total=0.619037 packages_per_step=4 record_ids=['target::chapter3_29_firefly_135', 'target::chapter3_17_firefly_118', 'target::chapter3_22_firefly_123', 'target::archive_firefly_4']
- step=57 loss_total=0.600226 packages_per_step=4 record_ids=['target::chapter4_7_firefly_116', 'target::chapter3_2_firefly_198', 'target::chapter3_3_firefly_219', 'target::chapter3_3_firefly_185']
- step=58 loss_total=0.63552 packages_per_step=4 record_ids=['target::chapter3_2_firefly_115', 'target::chapter3_22_firefly_121', 'target::chapter3_30_firefly_141', 'target::chapter3_17_firefly_138']
- step=59 loss_total=0.573078 packages_per_step=4 record_ids=['target::chapter3_20_firefly_120', 'target::chapter3_20_firefly_158', 'target::chapter3_21_firefly_109', 'target::chapter3_3_firefly_224']
- step=60 loss_total=0.676824 packages_per_step=4 record_ids=['target::chapter3_20_firefly_171', 'target::chapter3_22_firefly_122', 'target::chapter3_2_firefly_207', 'target::chapter3_2_firefly_250']
- step=61 loss_total=0.607536 packages_per_step=4 record_ids=['target::chapter3_21_firefly_114', 'target::chapter3_30_firefly_139', 'target::chapter3_2_firefly_196', 'target::chapter3_2_firefly_140']
- step=62 loss_total=0.608368 packages_per_step=4 record_ids=['target::chapter3_22_firefly_118', 'target::chapter3_3_firefly_124', 'target::chapter3_3_firefly_150', 'target::chapter3_3_firefly_242']
- step=63 loss_total=0.538064 packages_per_step=4 record_ids=['target::chapter3_3_firefly_223', 'target::chapter3_3_firefly_146', 'target::chapter3_22_firefly_113', 'target::chapter3_3_firefly_200']
- step=64 loss_total=0.525732 packages_per_step=4 record_ids=['target::chapter3_4_firefly_132', 'target::archive_firefly_5', 'target::chapter3_17_firefly_111', 'target::chapter3_3_firefly_189']
- step=65 loss_total=0.623613 packages_per_step=4 record_ids=['target::chapter3_21_firefly_111', 'target::chapter3_2_firefly_215', 'target::chapter3_3_firefly_188', 'target::chapter3_4_firefly_117']
- step=66 loss_total=0.572156 packages_per_step=4 record_ids=['target::chapter3_20_firefly_180', 'target::chapter3_20_firefly_125', 'target::chapter3_30_firefly_152', 'target::chapter3_2_firefly_134']
- step=67 loss_total=0.588435 packages_per_step=4 record_ids=['target::chapter3_30_firefly_124', 'target::chapter3_20_firefly_123', 'target::chapter3_3_firefly_104', 'target::chapter3_2_firefly_217']
- step=68 loss_total=0.613021 packages_per_step=4 record_ids=['target::chapter3_2_firefly_171', 'target::chapter3_2_firefly_226', 'target::chapter3_20_firefly_168', 'target::chapter3_26_firefly_112']
- step=69 loss_total=0.631558 packages_per_step=4 record_ids=['target::chapter3_3_firefly_130', 'target::chapter3_29_firefly_121', 'target::chapter3_20_firefly_117', 'target::chapter3_30_firefly_148']
- step=70 loss_total=0.603649 packages_per_step=4 record_ids=['target::chapter3_3_firefly_116', 'target::chapter3_2_firefly_127', 'target::chapter3_17_firefly_156', 'target::chapter4_7_firefly_103']
- step=71 loss_total=0.63946 packages_per_step=4 record_ids=['target::chapter3_20_firefly_151', 'target::chapter3_29_firefly_119', 'target::chapter3_3_firefly_113', 'target::chapter3_22_firefly_107']
- step=72 loss_total=0.544275 packages_per_step=4 record_ids=['target::chapter3_2_firefly_117', 'target::chapter3_21_firefly_115', 'target::chapter3_21_firefly_110', 'target::chapter3_3_firefly_137']

## Validation History
- step=12 validation_source=validation_packages package_count=63 loss_total=1.001105
- step=24 validation_source=validation_packages package_count=63 loss_total=0.821727
- step=36 validation_source=validation_packages package_count=63 loss_total=0.69905
- step=48 validation_source=validation_packages package_count=63 loss_total=0.619125
- step=60 validation_source=validation_packages package_count=63 loss_total=0.587077
- step=72 validation_source=validation_packages package_count=63 loss_total=0.570703

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step60.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 72, "loss_total": 0.570703, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
