# Offline MVP Teacher Downstream Control Contract

- contract_version: offline_teacher_downstream_control_v1
- generated_at: 2026-03-21T18:12:41
- input_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav
- teacher: {"experiment_id": "EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt", "route_handoff_path": "F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"}
- runtime: {"device": "cpu", "sample_rate": 48000, "frame_length": 400, "hop_length": 160, "frame_ms": 8.333333, "hop_ms": 3.333333, "chunk_samples": 1600, "chunk_ms": 33.333333, "frame_count": 418}
- conditioning: {"asset_path": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha": 1.15}

## Keys
- provided_keys: ["frame_start_ms", "z_art", "event_logits", "event_probs", "hidden", "fused_hidden", "acoustic.energy_log", "acoustic.abs_mean", "acoustic.zero_cross_rate", "acoustic.delta_energy", "conditioning.s_spk_target", "conditioning.s_geom_target", "conditioning.alpha"]
- derived_proxy_keys: ["energy_proxy", "voiced_proxy", "aperiodicity_proxy", "event_presence_proxy", "energy_change_proxy"]
- missing_design_keys: ["f0_hz", "r_res", "final_vocoder_waveform"]

## Summary Stats
- energy_log: {"mean": -2.426501, "std": 0.954425, "min": -5.235012, "max": -1.173985}
- zero_cross_rate: {"mean": 0.078069, "std": 0.0103, "min": 0.054528, "max": 0.089521}
- event_presence_proxy: {"mean": 0.688926, "std": 0.128163, "min": 0.382796, "max": 0.860886}
- voiced_proxy: {"mean": 0.629812, "std": 0.11983, "min": 0.361279, "max": 0.809834}
- energy_proxy: {"mean": 0.874334, "std": 0.20562, "min": 0.077987, "max": 0.996502}

## Notes
- This contract is a teacher-first downstream control packet, not the final Stage5 vocoder contract from the design doc.
- aperiodicity_proxy is currently derived from acoustic.zero_cross_rate and should be treated as a provisional noise-control proxy only.
- voiced_proxy currently maps to event_probs[:, 3], which is the teacher's voiced-like event channel rather than a dedicated vuv head.
- No explicit f0_hz or r_res is available in the current offline teacher; downstream modules must treat those as missing or optional.
