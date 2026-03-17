# Offline MVP No-Residual Vocoder Train Step

- generated_at: 2026-03-18T00:10:00
- training_package_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- optimizer: {"name": "Adam", "learning_rate": 0.001, "max_grad_norm": 5.0}
- loss_weights: {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.5}
- train_step: {"started_at": "2026-03-18T00:09:58", "ended_at": "2026-03-18T00:10:00", "duration_sec": 1.524549, "frame_count": 167, "grad_norm": 3.398391, "loss_metrics": {"loss_total": 2.299453, "loss_harmonic_envelope": 0.448234, "loss_noise_envelope": 0.289309, "loss_periodic_gate": 0.684409, "loss_noise_gate": 0.617539, "loss_waveform": 0.31281, "loss_stft": 1.359374, "loss_rms_guard": 0.930856, "periodic_gate_pred_mean": 0.546134, "noise_gate_pred_mean": 0.640239, "periodic_gate_target_mean": 0.644517, "noise_gate_target_mean": 0.698585, "decoded_waveform_rms": 0.354806, "target_waveform_rms": 0.13987, "decoded_to_target_rms_ratio": 2.536679}}
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_rmsguard_train_step_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_step.pt

## Notes
- This is a single-step Stage5 plumbing validation for the no-residual baseline route.
- The objective may combine proxy spectral/gate targets with optional aligned waveform/STFT bootstrap losses, but it is still not the final multi-resolution or adversarial vocoder recipe from the design doc.
- Use this step to verify loss, backward, optimizer, and checkpoint plumbing before adding adversarial or larger-scale decoder training.
