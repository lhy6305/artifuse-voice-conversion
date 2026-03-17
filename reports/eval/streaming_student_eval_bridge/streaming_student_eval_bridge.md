# Stage3 Streaming Student Eval Bridge

- generated_at: 2026-03-17T11:52:58
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning_source: {"asset_status": "heuristic_bootstrap_estimated", "alpha_value": 1.15, "speaker_dim": 16, "geom_dim": 8, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- frame_contract: {"frame_length": 400, "hop_length": 160}

## target_validation
- record_count: 8
- batch_count: 2
- duration_stats_sec: {"count": 8, "min": 0.612993, "max": 2.113991, "mean": 1.448614, "median": 1.467483, "stdev": 0.484203}
- punctuation_ratio: {"count": 8, "min": 0.125, "max": 0.5, "mean": 0.27381, "median": 0.285714, "stdev": 0.111795}
- group_counts: {"<root>": 8}
- shared_hidden_abs_mean: 0.491278
- z_art_abs_mean: 0.308614
- z_art_delta_abs_mean: 0.003985
- event_prob_mean: 0.496799
- event_presence_prob_mean: 0.647264
- coarse_log_f0_mean: 0.114498
- coarse_log_f0_delta_abs_mean: 0.002866
- vuv_prob_mean: 0.493651
- aperiodicity_mean: 0.11775
- energy_mean: -0.479579
- log_f0_correction_abs_mean: 0.300874
- aper_correction_abs_mean: 0.403875

## target_special_eval
- record_count: 8
- batch_count: 2
- duration_stats_sec: {"count": 8, "min": 0.470998, "max": 2.114989, "mean": 1.057291, "median": 0.956985, "stdev": 0.464816}
- punctuation_ratio: {"count": 8, "min": 1.0, "max": 1.0, "mean": 1.0, "median": 1.0, "stdev": 0.0}
- group_counts: {"no_text_voice": 8}
- shared_hidden_abs_mean: 0.49325
- z_art_abs_mean: 0.322394
- z_art_delta_abs_mean: 0.001981
- event_prob_mean: 0.496297
- event_presence_prob_mean: 0.651265
- coarse_log_f0_mean: 0.135961
- coarse_log_f0_delta_abs_mean: 0.001498
- vuv_prob_mean: 0.489411
- aperiodicity_mean: 0.109677
- energy_mean: -0.520833
- log_f0_correction_abs_mean: 0.290792
- aper_correction_abs_mean: 0.407481

## Comparisons
- delta_shared_hidden_abs_mean: 0.001972
- delta_z_art_abs_mean: 0.01378
- delta_z_art_delta_abs_mean: -0.002004
- delta_event_prob_mean: -0.000502
- delta_event_presence_prob_mean: 0.004001
- delta_coarse_log_f0_mean: 0.021463
- delta_coarse_log_f0_delta_abs_mean: -0.001368
- delta_vuv_prob_mean: -0.00424
- delta_aperiodicity_mean: -0.008073
- delta_energy_mean: -0.041254
- delta_log_f0_correction_abs_mean: -0.010082
- delta_aper_correction_abs_mean: 0.003606

## Notes
- This bridge validates Stage3 output contracts and summary wiring, not model quality.
- When no real calibration asset is available, the bridge uses deterministic placeholder conditioning.
- Do not interpret bridge deltas as a replacement for offline_mvp route metrics.
