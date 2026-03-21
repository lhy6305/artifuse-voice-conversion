# Offline MVP No-Residual Vocoder Training Loop

- generated_at: 2026-03-21T17:24:18
- training_package_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt
- validation_package_path: None
- timing: {"started_at": "2026-03-21T17:24:16", "ended_at": "2026-03-21T17:24:18", "duration_sec": 1.777551}
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- training: {"seed": 20260317, "deterministic": false, "num_steps": 3, "validation_interval": 1, "checkpoint_interval": 3, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.0, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "post_ola_envelope"}}
- train_frame_count: 167
- validation_frame_count: 167

## Step History
- step=1 loss_total=1.745658 grad_norm=3.080818 duration_sec=0.117418
- step=2 loss_total=1.503334 grad_norm=2.664076 duration_sec=0.075416
- step=3 loss_total=1.342589 grad_norm=2.654014 duration_sec=0.078669

## Validation History
- step=1 validation_source=train_targets_reused loss_total=1.503334
- step=2 validation_source=train_targets_reused loss_total=1.342589
- step=3 validation_source=train_targets_reused loss_total=1.208195

## Artifacts
- checkpoint_paths: ["F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/training_loop_postenv/checkpoints/offline_mvp_nores_vocoder_loop.step3.pt"]
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/training_loop_postenv/checkpoints/offline_mvp_nores_vocoder_loop.step3.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 3, "loss_total": 1.208195, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/training_loop_postenv/checkpoints/offline_mvp_nores_vocoder_loop.step3.pt"}

## Notes
- This is a minimal Stage5 multi-step loop for the no-residual baseline route.
- The loop currently optimizes one aligned train-target package repeatedly to verify optimizer/checkpoint/validation plumbing before dataset-level batching.
- Validation can optionally reuse the train package or read a separate package, and may include aligned waveform/STFT bootstrap losses, but it is still not the final multi-resolution or adversarial vocoder objective.

## Next Steps
- Replace the single-package loop with dataset-level package sampling once multiple aligned target packages exist.
- Decide whether the next Stage5 objective should keep using the bootstrap waveform/STFT path or move to a stronger multi-resolution decoder recipe.
- Keep final-vocoder language disabled until decoder, validation, and audio export are truly added.
