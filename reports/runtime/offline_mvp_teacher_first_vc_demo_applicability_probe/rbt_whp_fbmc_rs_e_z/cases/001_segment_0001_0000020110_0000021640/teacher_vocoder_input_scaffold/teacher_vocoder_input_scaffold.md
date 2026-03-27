# Offline MVP Teacher Vocoder Input Scaffold

- generated_at: 2026-03-27T12:32:08
- contract_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_e_z/cases/001_segment_0001_0000020110_0000021640/teacher_contract/teacher_downstream_control_contract.pt
- scaffold_version: offline_teacher_vocoder_input_scaffold_v3
- source_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav
- source_runtime: {"sample_rate": 48000, "frame_length": 400, "hop_length": 160, "chunk_samples": 1600}
- frame_count: 457
- periodic_branch_feature_dim: 36
- noise_branch_feature_dim: 36
- available_controls: {"z_art_dim": 8, "event_dim": 8, "e_evt_dim": 8, "speaker_dim": 16, "geom_dim": 8, "f0_hz_dim": 1, "f0_hz_log_norm_dim": 1, "vuv_dim": 1, "aper_dim": 1, "E_dim": 1, "E_log_rms_norm_dim": 1}
- event_semantics: {"event_probs_version": "offline_mvp_heuristic_event_target_v1", "event_prob_dimensions": ["energy_gate", "abs_delta_gate", "high_zero_cross", "low_zero_cross_voiced_like", "high_zero_cross_voiced_like", "delta_energy_rise", "delta_energy_fall", "energy_norm"], "semantic_status": "heuristic_frame_targets_not_design_e_evt", "e_evt_contract_version": "design_state_e_evt_v1", "e_evt_label_space_version": "design_state_e_evt_bootstrap_bridge_v1", "e_evt_dimensions": ["p_frication", "p_stop_closure", "p_burst", "p_voicing", "a_aper", "p_pause_boundary", "p_terminal_boundary", "p_final_clause"], "e_evt_timing_sidecar_used": false, "e_evt_source_semantic_parity_used": false, "e_evt_boundary_source": "none"}
- missing_design_keys: {"periodic_branch": [], "noise_branch": ["r_res"], "global": ["final_vocoder_waveform"]}

## Notes
- This scaffold is a consumer-side adapter for the C-prime v2-core contract rather than a final vocoder implementation.
- periodic_branch_features now consume explicit f0_hz / vuv / E semantics through bounded consumer-side normalizations rather than raw Hz/log-RMS magnitudes.
- noise_branch_features now consume explicit bootstrap e_evt together with aper / vuv / normalized E, while legacy event_probs are retained only as diagnostic compatibility controls.
- Because this runtime packet has no source-aware boundary sidecar, the downstream e_evt boundary dimensions remain zero-filled diagnostics rather than claimed true boundary supervision.
