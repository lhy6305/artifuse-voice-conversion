# Offline MVP No-Residual Vocoder Train Step

- generated_at: 2026-03-17T22:25:59
- training_package_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32}
- optimizer: {"name": "Adam", "learning_rate": 0.001, "max_grad_norm": 5.0}
- loss_weights: {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2}
- train_step: {"started_at": "2026-03-17T22:25:58", "ended_at": "2026-03-17T22:25:59", "duration_sec": 1.367454, "frame_count": 167, "grad_norm": 1.715228, "loss_metrics": {"loss_total": 1.009354, "loss_harmonic_envelope": 0.449511, "loss_noise_envelope": 0.294842, "loss_periodic_gate": 0.659462, "loss_noise_gate": 0.665541, "periodic_gate_pred_mean": 0.559478, "noise_gate_pred_mean": 0.521266, "periodic_gate_target_mean": 0.644517, "noise_gate_target_mean": 0.698585}}
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_step_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_step.pt

## Notes
- This is a single-step Stage5 plumbing validation for the no-residual baseline route.
- The objective is still a proxy spectral/gate target package, not the final waveform reconstruction or GAN training recipe from the design doc.
- Use this step to verify loss, backward, optimizer, and checkpoint plumbing before adding a decoder or longer training loop.
