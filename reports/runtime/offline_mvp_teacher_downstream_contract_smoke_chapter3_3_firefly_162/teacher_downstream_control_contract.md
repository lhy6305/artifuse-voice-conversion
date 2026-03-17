# Offline MVP Teacher Downstream Control Contract

- contract_version: offline_teacher_downstream_control_v1
- generated_at: 2026-03-17T22:02:35
- input_audio_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav
- teacher: {"experiment_id": "EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt", "route_handoff_path": "F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"}
- runtime: {"device": "cpu", "sample_rate": 44100, "frame_length": 400, "hop_length": 160, "frame_ms": 9.070295, "hop_ms": 3.628118, "chunk_samples": 2048, "chunk_ms": 46.439909, "frame_count": 167}
- conditioning: {"asset_path": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha": 1.15}

## Keys
- provided_keys: ["frame_start_ms", "z_art", "event_logits", "event_probs", "hidden", "fused_hidden", "acoustic.energy_log", "acoustic.abs_mean", "acoustic.zero_cross_rate", "acoustic.delta_energy", "conditioning.s_spk_target", "conditioning.s_geom_target", "conditioning.alpha"]
- derived_proxy_keys: ["energy_proxy", "voiced_proxy", "aperiodicity_proxy", "event_presence_proxy", "energy_change_proxy"]
- missing_design_keys: ["f0_hz", "r_res", "final_vocoder_waveform"]

## Summary Stats
- energy_log: {"mean": -2.634146, "std": 1.947793, "min": -7.936494, "max": -1.314453}
- zero_cross_rate: {"mean": 0.072153, "std": 0.01068, "min": 0.043322, "max": 0.089425}
- event_presence_proxy: {"mean": 0.698585, "std": 0.1838, "min": 0.288735, "max": 0.844864}
- voiced_proxy: {"mean": 0.644517, "std": 0.166266, "min": 0.282982, "max": 0.78796}
- energy_proxy: {"mean": 0.811496, "std": 0.34349, "min": 0.000381, "max": 0.995372}

## Verification
- frame_count_equal: True
- frame_alignment_equal: True

## Notes
- This contract is a teacher-first downstream control packet, not the final Stage5 vocoder contract from the design doc.
- aperiodicity_proxy is currently derived from acoustic.zero_cross_rate and should be treated as a provisional noise-control proxy only.
- voiced_proxy currently maps to event_probs[:, 3], which is the teacher's voiced-like event channel rather than a dedicated vuv head.
- No explicit f0_hz or r_res is available in the current offline teacher; downstream modules must treat those as missing or optional.
