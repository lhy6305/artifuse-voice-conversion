# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-18T01:03:50
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-18T01:02:39", "ended_at": "2026-03-18T01:03:50", "duration_sec": 70.135011}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 48, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2}}

## Step History
- step=1 loss_total=2.027613 packages_per_step=4 record_ids=['target::chapter3_2_firefly_110', 'target::chapter3_29_firefly_129', 'target::chapter3_3_firefly_145', 'target::chapter3_3_firefly_224']
- step=2 loss_total=1.802408 packages_per_step=4 record_ids=['target::chapter3_3_firefly_126', 'target::chapter3_3_firefly_129', 'target::chapter3_5_firefly_101', 'target::chapter3_20_firefly_146']
- step=3 loss_total=1.615944 packages_per_step=4 record_ids=['target::chapter3_3_firefly_168', 'target::archive_firefly_11', 'target::chapter3_2_firefly_147', 'target::chapter3_20_firefly_117']
- step=4 loss_total=1.458381 packages_per_step=4 record_ids=['target::chapter3_3_firefly_177', 'target::chapter3_3_firefly_130', 'target::chapter3_30_firefly_138', 'target::archive_firefly_19']
- step=5 loss_total=1.298709 packages_per_step=4 record_ids=['target::chapter3_20_firefly_179', 'target::chapter3_2_firefly_134', 'target::chapter3_29_firefly_101', 'target::chapter3_29_firefly_140']
- step=6 loss_total=1.234616 packages_per_step=4 record_ids=['target::chapter3_2_firefly_221', 'target::chapter3_3_firefly_194', 'target::chapter3_3_firefly_136', 'target::chapter3_2_firefly_129']
- step=7 loss_total=1.127846 packages_per_step=4 record_ids=['target::chapter3_2_firefly_168', 'target::chapter3_17_firefly_111', 'target::archive_firefly_3', 'target::chapter3_2_firefly_226']
- step=8 loss_total=1.043515 packages_per_step=4 record_ids=['target::chapter3_22_firefly_101', 'target::chapter3_29_firefly_123', 'target::chapter3_3_firefly_137', 'target::chapter3_3_firefly_238']
- step=9 loss_total=0.987341 packages_per_step=4 record_ids=['target::chapter3_17_firefly_116', 'target::chapter3_2_firefly_209', 'target::chapter3_30_firefly_157', 'target::chapter3_17_firefly_131']
- step=10 loss_total=0.966773 packages_per_step=4 record_ids=['target::chapter3_30_firefly_107', 'target::archive_firefly_10', 'target::chapter3_22_firefly_124', 'target::chapter3_2_firefly_198']
- step=11 loss_total=0.991218 packages_per_step=4 record_ids=['target::chapter3_29_firefly_117', 'target::chapter3_26_firefly_106', 'target::chapter3_30_firefly_149', 'target::chapter3_2_firefly_182']
- step=12 loss_total=0.940052 packages_per_step=4 record_ids=['target::archive_firefly_17', 'target::chapter3_3_firefly_142', 'target::chapter3_20_firefly_116', 'target::chapter3_20_firefly_173']
- step=13 loss_total=0.891166 packages_per_step=4 record_ids=['target::chapter3_4_firefly_116', 'target::chapter3_3_firefly_128', 'target::archive_firefly_8', 'target::chapter3_3_firefly_237']
- step=14 loss_total=0.976809 packages_per_step=4 record_ids=['target::chapter3_3_firefly_103', 'target::chapter3_30_firefly_106', 'target::chapter3_3_firefly_105', 'target::chapter3_17_firefly_154']
- step=15 loss_total=0.905589 packages_per_step=4 record_ids=['target::chapter4_7_firefly_122', 'target::chapter3_20_firefly_111', 'target::chapter3_17_firefly_125', 'target::chapter3_17_firefly_143']
- step=16 loss_total=0.930401 packages_per_step=4 record_ids=['target::chapter3_3_firefly_149', 'target::chapter3_3_firefly_161', 'target::chapter3_4_firefly_120', 'target::chapter3_2_firefly_246']
- step=17 loss_total=0.891248 packages_per_step=4 record_ids=['target::chapter3_30_firefly_102', 'target::chapter3_29_firefly_119', 'target::chapter3_17_firefly_144', 'target::chapter3_22_firefly_109']
- step=18 loss_total=0.896583 packages_per_step=4 record_ids=['target::chapter3_17_firefly_137', 'target::chapter3_2_firefly_138', 'target::chapter3_2_firefly_108', 'target::chapter3_21_firefly_104']
- step=19 loss_total=0.831855 packages_per_step=4 record_ids=['target::chapter3_21_firefly_106', 'target::chapter3_20_firefly_150', 'target::chapter3_17_firefly_155', 'target::chapter3_2_firefly_213']
- step=20 loss_total=0.816804 packages_per_step=4 record_ids=['target::archive_firefly_12', 'target::chapter3_2_firefly_187', 'target::chapter3_17_firefly_157', 'target::chapter3_3_firefly_112']
- step=21 loss_total=0.780542 packages_per_step=4 record_ids=['target::chapter3_2_firefly_211', 'target::chapter3_3_firefly_193', 'target::chapter3_21_firefly_110', 'target::chapter3_2_firefly_117']
- step=22 loss_total=0.778714 packages_per_step=4 record_ids=['target::chapter3_20_firefly_169', 'target::chapter3_29_firefly_115', 'target::chapter3_2_firefly_158', 'target::chapter3_17_firefly_134']
- step=23 loss_total=0.782798 packages_per_step=4 record_ids=['target::chapter3_20_firefly_136', 'target::chapter3_5_firefly_103', 'target::chapter3_20_firefly_178', 'target::chapter3_29_firefly_102']
- step=24 loss_total=0.801432 packages_per_step=4 record_ids=['target::chapter3_20_firefly_114', 'target::chapter3_4_firefly_144', 'target::chapter3_4_firefly_119', 'target::chapter3_3_firefly_204']
- step=25 loss_total=0.768099 packages_per_step=4 record_ids=['target::chapter3_2_firefly_136', 'target::archive_firefly_14', 'target::chapter3_26_firefly_105', 'target::chapter3_3_firefly_167']
- step=26 loss_total=0.751159 packages_per_step=4 record_ids=['target::chapter3_3_firefly_227', 'target::chapter3_22_firefly_103', 'target::chapter3_17_firefly_149', 'target::chapter3_20_firefly_139']
- step=27 loss_total=0.733244 packages_per_step=4 record_ids=['target::chapter3_2_firefly_195', 'target::chapter3_2_firefly_242', 'target::chapter3_2_firefly_106', 'target::chapter3_20_firefly_112']
- step=28 loss_total=0.737737 packages_per_step=4 record_ids=['target::chapter3_6_firefly_107', 'target::archive_firefly_7', 'target::chapter3_2_firefly_185', 'target::chapter3_2_firefly_184']
- step=29 loss_total=0.754085 packages_per_step=4 record_ids=['target::chapter3_3_firefly_195', 'target::chapter3_17_firefly_148', 'target::chapter3_2_firefly_234', 'target::chapter3_3_firefly_119']
- step=30 loss_total=0.774938 packages_per_step=4 record_ids=['target::chapter3_3_firefly_176', 'target::chapter3_20_firefly_177', 'target::chapter3_4_firefly_135', 'target::chapter3_4_firefly_133']
- step=31 loss_total=0.746107 packages_per_step=4 record_ids=['target::chapter3_3_firefly_134', 'target::chapter3_3_firefly_231', 'target::chapter3_2_firefly_245', 'target::chapter3_3_firefly_175']
- step=32 loss_total=0.707936 packages_per_step=4 record_ids=['target::chapter3_2_firefly_127', 'target::chapter3_20_firefly_183', 'target::chapter3_3_firefly_153', 'target::chapter3_20_firefly_170']
- step=33 loss_total=0.687033 packages_per_step=4 record_ids=['target::chapter3_3_firefly_240', 'target::chapter3_2_firefly_214', 'target::chapter3_26_firefly_102', 'target::chapter3_3_firefly_217']
- step=34 loss_total=0.739267 packages_per_step=4 record_ids=['target::chapter3_2_firefly_107', 'target::chapter3_29_firefly_132', 'target::chapter3_30_firefly_130', 'target::chapter3_3_firefly_208']
- step=35 loss_total=0.718103 packages_per_step=4 record_ids=['target::chapter3_29_firefly_111', 'target::chapter3_4_firefly_104', 'target::chapter3_21_firefly_102', 'target::chapter3_2_firefly_230']
- step=36 loss_total=0.74607 packages_per_step=4 record_ids=['target::chapter3_20_firefly_103', 'target::chapter3_2_firefly_235', 'target::chapter3_2_firefly_141', 'target::chapter3_2_firefly_122']
- step=37 loss_total=0.726166 packages_per_step=4 record_ids=['target::chapter3_2_firefly_176', 'target::chapter3_29_firefly_131', 'target::chapter3_2_firefly_202', 'target::chapter3_2_firefly_224']
- step=38 loss_total=0.73822 packages_per_step=4 record_ids=['target::chapter3_4_firefly_123', 'target::chapter3_20_firefly_167', 'target::chapter3_21_firefly_111', 'target::chapter3_4_firefly_102']
- step=39 loss_total=0.720298 packages_per_step=4 record_ids=['target::chapter3_3_firefly_251', 'target::chapter3_2_firefly_172', 'target::chapter3_3_firefly_160', 'target::chapter3_2_firefly_153']
- step=40 loss_total=0.745768 packages_per_step=4 record_ids=['target::chapter3_26_firefly_109', 'target::chapter3_2_firefly_193', 'target::chapter3_2_firefly_249', 'target::chapter3_3_firefly_200']
- step=41 loss_total=0.657558 packages_per_step=4 record_ids=['target::chapter3_17_firefly_145', 'target::chapter3_2_firefly_216', 'target::chapter3_4_firefly_137', 'target::chapter3_26_firefly_104']
- step=42 loss_total=0.675117 packages_per_step=4 record_ids=['target::chapter3_3_firefly_152', 'target::chapter3_2_firefly_189', 'target::chapter3_2_firefly_181', 'target::chapter3_17_firefly_120']
- step=43 loss_total=0.693994 packages_per_step=4 record_ids=['target::chapter3_4_firefly_101', 'target::chapter3_4_firefly_121', 'target::chapter3_22_firefly_112', 'target::chapter3_20_firefly_115']
- step=44 loss_total=0.73947 packages_per_step=4 record_ids=['target::chapter3_4_firefly_143', 'target::chapter3_29_firefly_110', 'target::chapter3_2_firefly_250', 'target::chapter3_3_firefly_107']
- step=45 loss_total=0.672829 packages_per_step=4 record_ids=['target::chapter3_3_firefly_242', 'target::chapter3_2_firefly_233', 'target::chapter3_3_firefly_143', 'target::chapter3_30_firefly_113']
- step=46 loss_total=0.643921 packages_per_step=4 record_ids=['target::chapter3_3_firefly_243', 'target::chapter3_22_firefly_116', 'target::chapter3_3_firefly_127', 'target::chapter3_22_firefly_113']
- step=47 loss_total=0.687191 packages_per_step=4 record_ids=['target::chapter3_3_firefly_133', 'target::chapter3_20_firefly_155', 'target::chapter3_2_firefly_225', 'target::chapter3_2_firefly_251']
- step=48 loss_total=0.680666 packages_per_step=4 record_ids=['target::chapter3_2_firefly_180', 'target::chapter3_6_firefly_102', 'target::chapter3_4_firefly_111', 'target::chapter3_3_firefly_232']

## Validation History
- step=12 validation_source=validation_packages package_count=66 loss_total=0.907863
- step=24 validation_source=validation_packages package_count=66 loss_total=0.75061
- step=36 validation_source=validation_packages package_count=66 loss_total=0.69899
- step=48 validation_source=validation_packages package_count=66 loss_total=0.655545

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 48, "loss_total": 0.655545, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
