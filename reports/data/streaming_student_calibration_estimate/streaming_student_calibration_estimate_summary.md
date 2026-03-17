# Stage3 Streaming Student Calibration Estimate Summary

- generated_at: 2026-03-17T11:51:39
- record_count: 11
- total_duration_sec: 135.964922
- output_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- estimator: waveform_feature_bootstrap_v1

## Aggregate Features
- rms_mean: 0.077185
- rms_std: 0.057269
- abs_mean: 0.052331
- zero_cross_mean: 0.09975
- zero_cross_std: 0.113114
- centroid_hz_mean: 1955.245728
- centroid_hz_std: 2561.308838
- low_ratio_mean: 0.571541
- lowmid_ratio_mean: 0.168218
- mid_ratio_mean: 0.089213
- high_ratio_mean: 0.171028
- low_high_ratio_mean: 498.351471

## Estimated Assets
- s_spk_target_dim: 16
- s_spk_target_status: heuristic_estimated
- s_spk_target_preview: [-0.339577, -0.327584, -0.299542, -0.215397, -0.301077, 0.134835]
- s_geom_target_dim: 8
- s_geom_target_status: heuristic_estimated
- s_geom_target_preview: [-0.086814, -0.321044, -0.340123, -0.252514, 0.052869, 0.983333]
- alpha_status: heuristic_estimated
- alpha_value: 1.15

## Notes
- This is a heuristic bootstrap estimator derived directly from calibration waveforms.
- The current estimate is intended to replace placeholder zero vectors, not to serve as a final calibration algorithm.
- alpha is a bounded scalar inferred from low-band spectral centroid and low/high energy balance.
- This asset replaces placeholder zeros with heuristic waveform-derived estimates.
- Treat these values as bootstrap conditioning priors until a dedicated calibration estimator exists.
