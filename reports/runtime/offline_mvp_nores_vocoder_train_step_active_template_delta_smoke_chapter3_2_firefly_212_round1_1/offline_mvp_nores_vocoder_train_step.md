# Offline MVP No-Residual Vocoder Train Step

- generated_at: 2026-03-24T00:27:32
- training_package_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/validation/target__chapter3_2_firefly_212/train_targets/offline_mvp_nores_vocoder_train_targets.pt
- model: {"name": "no_residual_source_filter_vocoder_scaffold", "hidden_dim": 64, "harmonic_bins": 32, "noise_bins": 32, "decoder_frame_length": 400}
- optimizer: {"name": "Adam", "learning_rate": 0.001, "max_grad_norm": 5.0}
- loss_weights: {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.1, "frame_delta": 4.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}
- train_step: {"started_at": "2026-03-24T00:27:29", "ended_at": "2026-03-24T00:27:32", "duration_sec": 2.855141, "frame_count": 544, "grad_norm": 2.497555, "loss_metrics": {"loss_total": 4.852276, "loss_harmonic_envelope": 0.437448, "loss_noise_envelope": 0.307649, "loss_periodic_gate": 0.683687, "loss_noise_gate": 0.685189, "loss_activity_gate": 0.60987, "loss_waveform": 0.191609, "loss_stft": 0.950568, "loss_rms_guard": 0.593389, "loss_active_frame_template_excess_relu_0p02": 0.667314, "loss_frame_delta_unit_rms_l1": 0.738733, "periodic_gate_pred_mean": 0.577339, "noise_gate_pred_mean": 0.566376, "activity_gate_pred_mean": 0.580084, "periodic_gate_target_mean": 0.465849, "noise_gate_target_mean": 0.508164, "activity_gate_target_mean": 0.68593, "reconstruction_frame_gain_apply_mode": "pre_overlap_add", "decoded_waveform_rms": 0.207358, "target_waveform_rms": 0.114555, "decoded_to_target_rms_ratio": 1.810112}}
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_step_active_template_delta_smoke_chapter3_2_firefly_212_round1_1/offline_mvp_nores_vocoder_train_step.pt

## Notes
- This is a single-step Stage5 plumbing validation for the no-residual baseline route.
- The objective may combine proxy spectral/gate targets with optional aligned waveform/STFT bootstrap losses, but it is still not the final multi-resolution or adversarial vocoder recipe from the design doc.
- Use this step to verify loss, backward, optimizer, and checkpoint plumbing before adding adversarial or larger-scale decoder training.
