# Offline MVP Teacher Downstream Control Contract

- contract_version: offline_teacher_downstream_control_v2
- generated_at: 2026-03-24T09:45:17
- input_audio_path: F:/proj_dev/tmp/workdir4/data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav
- teacher: {"experiment_id": "EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration", "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt", "route_handoff_path": "F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"}
- runtime: {"device": "cuda:0", "sample_rate": 44100, "frame_length": 400, "hop_length": 160, "frame_ms": 9.070295, "hop_ms": 3.628118, "chunk_samples": 1470, "chunk_ms": 33.333333, "frame_count": 825}
- conditioning: {"asset_path": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha": 1.15}
- source_acoustic_state: {"version": "source_acoustic_state_extraction_v1", "aper_version": "aper-v1", "stats": {"frame_count": 825, "voiced_frame_count": 498, "voiced_ratio": 0.603636, "f0_floor_hz": 50.0, "f0_ceil_hz": 550.0, "analysis_frame_length": 2646}}

## Keys
- provided_keys: {"v2_core": ["frame_start_ms", "z_art", "event_probs", "f0_hz", "vuv", "aper", "E", "conditioning.s_spk_target", "conditioning.s_geom_target", "conditioning.alpha"], "v2_optional": [], "v2_diagnostic": ["event_logits", "hidden", "fused_hidden", "acoustic.energy_log", "acoustic.abs_mean", "acoustic.zero_cross_rate", "acoustic.delta_energy"]}
- derived_proxy_keys: ["energy_proxy", "voiced_proxy", "aperiodicity_proxy", "event_presence_proxy", "energy_change_proxy"]
- missing_design_keys: ["r_res", "final_vocoder_waveform"]

## Summary Stats
- f0_hz: {"mean": 115.671204, "std": 125.631439, "min": 0.0, "max": 551.25}
- vuv: {"mean": 0.429263, "std": 0.339283, "min": 0.033333, "max": 0.806623}
- aper: {"mean": 0.486519, "std": 0.467782, "min": 0.001122, "max": 1.0}
- E: {"mean": -3.688381, "std": 0.384818, "min": -4.0, "max": -2.900651}
- energy_log: {"mean": -7.398345, "std": 0.684958, "min": -7.936509, "max": -5.875746}
- zero_cross_rate: {"mean": 0.048615, "std": 0.006364, "min": 0.043322, "max": 0.058645}
- event_presence_proxy: {"mean": 0.30541, "std": 0.021371, "min": 0.288734, "max": 0.355137}
- voiced_proxy: {"mean": 0.429263, "std": 0.339283, "min": 0.033333, "max": 0.806623}
- energy_proxy: {"mean": 0.629347, "std": 0.154534, "min": 0.5, "max": 0.900132}

## Notes
- This contract upgrades the teacher-first downstream packet to the C-prime v2-core baseline for the experimental Stage5 route.
- f0_hz / vuv / aper / E are produced by a deterministic source acoustic state extraction chain aligned to the teacher runtime frame grid.
- aper-v1 is a single scalar per frame in [0, 1], where 0 is more periodic and 1 is more aperiodic; it is intended for the noise branch only.
- r_res and final_vocoder_waveform remain intentionally absent because Phase C3 stays on the no-res baseline route.
