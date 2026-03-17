# Offline MVP No-Residual Vocoder Training Loop

- generated_at: 2026-03-17T22:30:39
- training_package_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt
- validation_package_path: None
- timing: {"started_at": "2026-03-17T22:30:38", "ended_at": "2026-03-17T22:30:39", "duration_sec": 1.414744}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32}
- training: {"num_steps": 3, "validation_interval": 1, "checkpoint_interval": 1, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2}}
- train_frame_count: 167
- validation_frame_count: 167

## Step History
- step=1 loss_total=1.001534 grad_norm=1.861914 duration_sec=0.030908
- step=2 loss_total=0.864256 grad_norm=1.546417 duration_sec=0.004046
- step=3 loss_total=0.767466 grad_norm=1.386794 duration_sec=0.003999

## Validation History
- step=1 validation_source=train_targets_reused loss_total=0.864256
- step=2 validation_source=train_targets_reused loss_total=0.767466
- step=3 validation_source=train_targets_reused loss_total=0.704201

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/checkpoints/offline_mvp_nores_vocoder_loop.step1.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/checkpoints/offline_mvp_nores_vocoder_loop.step2.pt", "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/checkpoints/offline_mvp_nores_vocoder_loop.step3.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/checkpoints/offline_mvp_nores_vocoder_loop.step3.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 3, "loss_total": 0.704201, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/checkpoints/offline_mvp_nores_vocoder_loop.step3.pt"}

## Notes
- This is a minimal Stage5 multi-step loop for the no-residual baseline route.
- The loop currently optimizes one aligned train-target package repeatedly to verify optimizer/checkpoint/validation plumbing before dataset-level batching.
- Validation can optionally reuse the train package or read a separate package, but it still evaluates proxy spectral/gate targets rather than a final waveform objective.

## Next Steps
- Replace the single-package loop with dataset-level package sampling once multiple aligned target packages exist.
- Decide whether the next Stage5 objective should stay on spectral/gate proxy targets or move closer to waveform/STFT decoder reconstruction.
- Keep final-vocoder language disabled until decoder, validation, and audio export are truly added.
