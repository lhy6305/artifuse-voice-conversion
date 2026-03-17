# Stage3 Streaming Student Scaffold Plan

## Status
- experiment_id: streaming_student_stage_scaffold
- created_at: 2026-03-17T11:13:41
- mode: streaming_student_stage
- run_stage: scaffold_bootstrap
- status: scaffold_ready

## Data
- manifest_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/manifests
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- target_train_count: 592
- target_validation_count: 66
- target_special_eval_count: 8
- source_train_count: 483
- source_validation_count: 54

## Contract
- shared_hidden_dim: 96
- z_art_dim: 8
- event_dim: 8
- r_res_dim: 0

## Dry Run Shapes
- frame_mask: [2, 38]
- frame_features: [2, 38, 2]
- shared_hidden: [2, 38, 96]
- coarse_log_f0: [2, 38, 1]
- vuv_logits: [2, 38, 1]
- aperiodicity: [2, 38, 1]
- energy: [2, 38, 1]
- event_prior_logits: [2, 38, 8]
- student_hidden: [2, 38, 96]
- conditioning: [2, 38, 32]
- z_art: [2, 38, 8]
- event_logits: [2, 38, 8]
- event_probs: [2, 38, 8]
- r_res: [2, 38, 0]
- log_f0_correction: [2, 38, 1]
- aper_correction: [2, 38, 1]

## Next Steps
- Add teacher-label dataset wiring for frontend/student supervision without reusing offline_mvp training loops directly.
- Define calibration asset format for s_spk_target, s_geom_target, and alpha before any real student training.
- Build a stage3 eval bridge that maps scaffold outputs into offline_mvp-compatible control summaries before opening new experiments.

## Notes
- Stage3 bootstrap keeps the same frame contract as offline_mvp for evaluation bridge planning.
- r_res stays disabled until the frontend/student contract and calibration assets are stable.
