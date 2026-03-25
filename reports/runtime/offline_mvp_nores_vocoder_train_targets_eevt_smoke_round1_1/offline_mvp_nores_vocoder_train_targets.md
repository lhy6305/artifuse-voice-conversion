# Offline MVP No-Residual Vocoder Train Targets

- generated_at: 2026-03-25T22:47:40
- training_package_version: offline_mvp_nores_vocoder_train_targets_v2
- source_scaffold_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_eevt_smoke_round1_1/teacher_vocoder_input_scaffold.pt
- target_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav
- source_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav
- target_event_semantic_sidecar_present: False
- target_semantic_overview: {"semantic_source": "missing", "semantic_contract_version": null, "semantic_label_space_version": null, "semantic_inventory_status": "missing", "semantic_label_status": "missing", "semantic_utterance_structure_type": "unknown", "semantic_final_terminal_type": "unknown", "semantic_clause_count": 0, "semantic_pause_boundary_count": 0, "semantic_terminal_boundary_count": 0, "semantic_nonverbal_only": false, "semantic_clean_text_available": false, "semantic_phone_sequence_available": false, "semantic_manner_sequence_available": false, "semantic_place_sequence_available": false, "semantic_forced_alignment_available": false}
- target_event_timing_semantic_sidecar_present: False
- target_timing_semantic_overview: {"timing_source": "missing", "timing_contract_version": null, "timing_label_space_version": null, "timing_inventory_status": "missing", "timing_alignment_type": null, "timing_label_status": "missing", "timeline_event_count": 0, "clause_region_count": 0, "pause_boundary_event_count": 0, "terminal_boundary_event_count": 0, "weak_time_alignment_ready_for_target_side_bootstrap": false}
- source_semantic_parity_sidecar_present: False
- source_semantic_parity_overview: {"parity_source": "missing", "parity_contract_version": null, "parity_label_space_version": null, "parity_status": "missing", "parity_transfer_type": null, "parity_label_status": "missing", "parity_utterance_structure_type": "unknown", "parity_clause_count": 0, "parity_pause_boundary_count": 0, "parity_terminal_boundary_count": 0, "semantic_ready_for_source_side_bootstrap": false, "native_source_semantic_available": false}
- semantic_consumer: {"semantic_consumer_mode": "none", "semantic_tag": "target_semantic_consumer_none", "feature_dim": 0, "feature_names": [], "semantic_sidecar_present": false, "timing_semantic_sidecar_present": false, "source_semantic_parity_sidecar_present": false, "feature_source": "disabled", "feature_values": []}
- runtime: {"sample_rate": 48000, "frame_length": 400, "hop_length": 160}
- frame_count: 457
- aligned_waveform_samples: 73360
- periodic_input_dim: 36
- noise_input_dim: 36
- harmonic_target_dim: 32
- noise_target_dim: 32
- spectrogram_stats: {"stft_freq_bins": 201, "harmonic_source_bins": 100, "noise_source_bins": 101, "harmonic_target_mean": 0.047385, "noise_target_mean": 7.5e-05}

## Notes
- This package provides a minimal Stage5 spectral reconstruction target set for the no-residual baseline route.
- Targets are frame-aligned to the teacher runtime semantics and remain a proxy objective, not the final waveform/GAN training contract from the design doc.
- periodic_gate_target now uses explicit vuv, while noise_gate_target uses max(aper * E_log_rms_norm, event_presence_proxy) so unvoiced low-energy frames do not force the noise branch fully open.
- aligned_waveform is retained so later decoder/waveform-STFT bootstrap runs can reuse the same package contract.
