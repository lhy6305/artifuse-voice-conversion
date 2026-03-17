# Offline MVP No-Residual Vocoder Dataset Training Loop

- generated_at: 2026-03-18T00:03:22
- dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json
- timing: {"started_at": "2026-03-18T00:03:01", "ended_at": "2026-03-18T00:03:22", "duration_sec": 20.123913}
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"num_steps": 12, "packages_per_step": 4, "validation_interval": 6, "checkpoint_interval": 6, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "waveform": 0.5, "stft": 0.5}}

## Step History
- step=1 loss_total=1.791887 packages_per_step=4 record_ids=['target::chapter3_2_firefly_110', 'target::chapter3_29_firefly_129', 'target::chapter3_3_firefly_145', 'target::chapter3_3_firefly_224']
- step=2 loss_total=1.621732 packages_per_step=4 record_ids=['target::chapter3_3_firefly_126', 'target::chapter3_3_firefly_129', 'target::chapter3_5_firefly_101', 'target::chapter3_20_firefly_146']
- step=3 loss_total=1.469574 packages_per_step=4 record_ids=['target::chapter3_3_firefly_168', 'target::archive_firefly_11', 'target::chapter3_2_firefly_147', 'target::chapter3_20_firefly_117']
- step=4 loss_total=1.34165 packages_per_step=4 record_ids=['target::chapter3_3_firefly_177', 'target::chapter3_3_firefly_130', 'target::chapter3_30_firefly_138', 'target::archive_firefly_19']
- step=5 loss_total=1.240695 packages_per_step=4 record_ids=['target::chapter3_20_firefly_179', 'target::chapter3_2_firefly_134', 'target::chapter3_29_firefly_101', 'target::chapter3_29_firefly_140']
- step=6 loss_total=1.165788 packages_per_step=4 record_ids=['target::chapter3_2_firefly_221', 'target::chapter3_3_firefly_194', 'target::chapter3_3_firefly_136', 'target::chapter3_2_firefly_129']
- step=7 loss_total=1.111568 packages_per_step=4 record_ids=['target::chapter3_2_firefly_168', 'target::chapter3_17_firefly_111', 'target::archive_firefly_3', 'target::chapter3_2_firefly_226']
- step=8 loss_total=1.066466 packages_per_step=4 record_ids=['target::chapter3_22_firefly_101', 'target::chapter3_29_firefly_123', 'target::chapter3_3_firefly_137', 'target::chapter3_3_firefly_238']
- step=9 loss_total=0.994175 packages_per_step=4 record_ids=['target::chapter3_17_firefly_116', 'target::chapter3_2_firefly_209', 'target::chapter3_30_firefly_157', 'target::chapter3_17_firefly_131']
- step=10 loss_total=0.929323 packages_per_step=4 record_ids=['target::chapter3_30_firefly_107', 'target::archive_firefly_10', 'target::chapter3_22_firefly_124', 'target::chapter3_2_firefly_198']
- step=11 loss_total=0.928802 packages_per_step=4 record_ids=['target::chapter3_29_firefly_117', 'target::chapter3_26_firefly_106', 'target::chapter3_30_firefly_149', 'target::chapter3_2_firefly_182']
- step=12 loss_total=0.853014 packages_per_step=4 record_ids=['target::archive_firefly_17', 'target::chapter3_3_firefly_142', 'target::chapter3_20_firefly_116', 'target::chapter3_20_firefly_173']

## Validation History
- step=6 validation_source=validation_packages package_count=66 loss_total=1.104648
- step=12 validation_source=validation_packages package_count=66 loss_total=0.811442

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 12, "loss_total": 0.811442, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_baseline12_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step12.pt"}

## Notes
- This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.
- Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.
- Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.

## Next Steps
- Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.
- Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.
- Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.
