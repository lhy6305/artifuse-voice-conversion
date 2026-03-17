# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-17T23:17:24
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-17T23:17:21", "ended_at": "2026-03-17T23:17:24", "duration_sec": 2.670399}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32}
- training: {"num_steps": 12, "packages_per_step": 8, "validation_interval": 3, "checkpoint_interval": 3, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2}}

## Step History
- step=1 loss_total=0.923097 packages_per_step=8 record_ids=['target::chapter3_2_firefly_110', 'target::chapter3_29_firefly_129', 'target::chapter3_3_firefly_145', 'target::chapter3_3_firefly_224', 'target::chapter3_3_firefly_126', 'target::chapter3_3_firefly_129', 'target::chapter3_5_firefly_101', 'target::chapter3_20_firefly_146']
- step=2 loss_total=0.80579 packages_per_step=8 record_ids=['target::chapter3_3_firefly_168', 'target::archive_firefly_11', 'target::chapter3_2_firefly_147', 'target::chapter3_20_firefly_117', 'target::chapter3_3_firefly_177', 'target::chapter3_3_firefly_130', 'target::chapter3_30_firefly_138', 'target::archive_firefly_19']
- step=3 loss_total=0.715172 packages_per_step=8 record_ids=['target::chapter3_20_firefly_179', 'target::chapter3_2_firefly_134', 'target::chapter3_29_firefly_101', 'target::chapter3_29_firefly_140', 'target::chapter3_2_firefly_221', 'target::chapter3_3_firefly_194', 'target::chapter3_3_firefly_136', 'target::chapter3_2_firefly_129']
- step=4 loss_total=0.697373 packages_per_step=8 record_ids=['target::chapter3_2_firefly_168', 'target::chapter3_17_firefly_111', 'target::archive_firefly_3', 'target::chapter3_2_firefly_226', 'target::chapter3_22_firefly_101', 'target::chapter3_29_firefly_123', 'target::chapter3_3_firefly_137', 'target::chapter3_3_firefly_238']
- step=5 loss_total=0.645397 packages_per_step=8 record_ids=['target::chapter3_17_firefly_116', 'target::chapter3_2_firefly_209', 'target::chapter3_30_firefly_157', 'target::chapter3_17_firefly_131', 'target::chapter3_30_firefly_107', 'target::archive_firefly_10', 'target::chapter3_22_firefly_124', 'target::chapter3_2_firefly_198']
- step=6 loss_total=0.644824 packages_per_step=8 record_ids=['target::chapter3_29_firefly_117', 'target::chapter3_26_firefly_106', 'target::chapter3_30_firefly_149', 'target::chapter3_2_firefly_182', 'target::archive_firefly_17', 'target::chapter3_3_firefly_142', 'target::chapter3_20_firefly_116', 'target::chapter3_20_firefly_173']
- step=7 loss_total=0.594033 packages_per_step=8 record_ids=['target::chapter3_4_firefly_116', 'target::chapter3_3_firefly_128', 'target::archive_firefly_8', 'target::chapter3_3_firefly_237', 'target::chapter3_3_firefly_103', 'target::chapter3_30_firefly_106', 'target::chapter3_3_firefly_105', 'target::chapter3_17_firefly_154']
- step=8 loss_total=0.609185 packages_per_step=8 record_ids=['target::chapter4_7_firefly_122', 'target::chapter3_20_firefly_111', 'target::chapter3_17_firefly_125', 'target::chapter3_17_firefly_143', 'target::chapter3_3_firefly_149', 'target::chapter3_3_firefly_161', 'target::chapter3_4_firefly_120', 'target::chapter3_2_firefly_246']
- step=9 loss_total=0.592728 packages_per_step=8 record_ids=['target::chapter3_30_firefly_102', 'target::chapter3_29_firefly_119', 'target::chapter3_17_firefly_144', 'target::chapter3_22_firefly_109', 'target::chapter3_17_firefly_137', 'target::chapter3_2_firefly_138', 'target::chapter3_2_firefly_108', 'target::chapter3_21_firefly_104']
- step=10 loss_total=0.564754 packages_per_step=8 record_ids=['target::chapter3_21_firefly_106', 'target::chapter3_20_firefly_150', 'target::chapter3_17_firefly_155', 'target::chapter3_2_firefly_213', 'target::archive_firefly_12', 'target::chapter3_2_firefly_187', 'target::chapter3_17_firefly_157', 'target::chapter3_3_firefly_112']
- step=11 loss_total=0.544614 packages_per_step=8 record_ids=['target::chapter3_2_firefly_211', 'target::chapter3_3_firefly_193', 'target::chapter3_21_firefly_110', 'target::chapter3_2_firefly_117', 'target::chapter3_20_firefly_169', 'target::chapter3_29_firefly_115', 'target::chapter3_2_firefly_158', 'target::chapter3_17_firefly_134']
- step=12 loss_total=0.560558 packages_per_step=8 record_ids=['target::chapter3_20_firefly_136', 'target::chapter3_5_firefly_103', 'target::chapter3_20_firefly_178', 'target::chapter3_29_firefly_102', 'target::chapter3_20_firefly_114', 'target::chapter3_4_firefly_144', 'target::chapter3_4_firefly_119', 'target::chapter3_3_firefly_204']

## Validation History
- step=3 validation_source=validation_packages package_count=66 loss_total=0.67612
- step=6 validation_source=validation_packages package_count=66 loss_total=0.599989
- step=9 validation_source=validation_packages package_count=66 loss_total=0.558026
- step=12 validation_source=validation_packages package_count=66 loss_total=0.539549

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step3.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step9.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 12, "loss_total": 0.539549, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation still reports proxy spectral/gate targets and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Only after the dataset path is stable should Stage5 move to decoder and waveform/STFT reconstruction objectives.
