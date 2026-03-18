# Offline MVP No-Residual Vocoder Train Step

- generated_at: 2026-03-18T18:17:08
- training_package_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/validation/target__chapter3_22_firefly_114/train_targets/offline_mvp_nores_vocoder_train_targets.pt
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- optimizer: {"name": "Adam", "learning_rate": 0.001, "max_grad_norm": 5.0}
- loss_weights: {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "use_predicted_activity_gate": true}
- train_step: {"started_at": "2026-03-18T18:17:06", "ended_at": "2026-03-18T18:17:08", "duration_sec": 1.849723, "frame_count": 765, "grad_norm": 2.805664, "loss_metrics": {"loss_total": 1.659649, "loss_harmonic_envelope": 0.389128, "loss_noise_envelope": 0.234097, "loss_periodic_gate": 0.711001, "loss_noise_gate": 0.715252, "loss_activity_gate": 0.685093, "loss_waveform": 0.196748, "loss_stft": 0.938507, "loss_rms_guard": 0.232638, "periodic_gate_pred_mean": 0.537282, "noise_gate_pred_mean": 0.44233, "activity_gate_pred_mean": 0.537282, "periodic_gate_target_mean": 0.458785, "noise_gate_target_mean": 0.497802, "activity_gate_target_mean": 0.647367, "decoded_waveform_rms": 0.191632, "target_waveform_rms": 0.151857, "decoded_to_target_rms_ratio": 1.261925}}
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_activitygate_train_step_smoke_chapter3_22_firefly_114/offline_mvp_nores_vocoder_train_step.pt

## Notes
- This is a single-step Stage5 plumbing validation for the no-residual baseline route.
- The objective may combine proxy spectral/gate targets with optional aligned waveform/STFT bootstrap losses, but it is still not the final multi-resolution or adversarial vocoder recipe from the design doc.
- Use this step to verify loss, backward, optimizer, and checkpoint plumbing before adding adversarial or larger-scale decoder training.
