# Offline MVP No-Residual Vocoder Train Targets

- generated_at: 2026-03-17T22:25:55
- training_package_version: offline_mvp_nores_vocoder_train_targets_v1
- source_scaffold_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_smoke_v2_chapter3_3_firefly_162/teacher_vocoder_input_scaffold.pt
- target_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav
- source_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav
- runtime: {"sample_rate": 44100, "frame_length": 400, "hop_length": 160}
- frame_count: 167
- periodic_input_dim: 35
- noise_input_dim: 29
- harmonic_target_dim: 32
- noise_target_dim: 32
- spectrogram_stats: {"stft_freq_bins": 201, "harmonic_source_bins": 100, "noise_source_bins": 101, "harmonic_target_mean": 0.292054, "noise_target_mean": 0.01774}

## Notes
- This package provides a minimal Stage5 spectral reconstruction target set for the no-residual baseline route.
- Targets are frame-aligned to the teacher runtime semantics and remain a proxy objective, not the final waveform/GAN training contract from the design doc.
- periodic_gate_target uses voiced_proxy, and noise_gate_target uses max(aperiodicity_proxy, event_presence_proxy).
