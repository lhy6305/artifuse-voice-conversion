# Stage3 Streaming Student Checkpoint Eval

- experiment_id: streaming_student_semantic_weighting_smoke
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_semantic_weighting_smoke/checkpoints/streaming_student_semantic_weighting_smoke.step1.pt
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- training: {"batch_size": 1, "loss_weights": {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}, "semantic_supervision": {"enabled": true, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "event_prior_alpha": 1.0, "event_alpha": 0.35, "z_art_alpha": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45}, "loss_weight_overrides_path": null, "use_teacher_confidence": true}

## target_validation
- record_count: 1
- batch_count: 1
- loss_metrics: {"loss_total": 14.118607, "loss_total_default_reference": 14.118607, "loss_teacher_z_art": 4.814943, "loss_teacher_event": 5.526057, "loss_teacher_event_prior": 5.362447, "loss_teacher_energy_proxy": 3.916521, "loss_teacher_vuv_proxy": 0.7136, "loss_teacher_aper_proxy": 0.080663, "loss_teacher_proxy_acoustic": 3.96208, "loss_teacher_proxy_temporal": 0.01045, "loss_log_f0_correction_l1": 0.010002, "loss_aper_correction_l1": 0.204495, "teacher_confidence_weighted": true, "effective_weight_sum": 90.56897, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_base_multiplier_mean": 1.13, "semantic_event_prior_multiplier_mean": 1.13, "semantic_event_multiplier_mean": 1.0455, "semantic_z_art_multiplier_mean": 1.026}
- sample_record_id_batches: [['target::chapter3_3_firefly_162']]

## target_special_eval
- record_count: 1
- batch_count: 1
- loss_metrics: {"loss_total": 12.948247, "loss_total_default_reference": 12.948247, "loss_teacher_z_art": 4.078648, "loss_teacher_event": 5.508897, "loss_teacher_event_prior": 5.398388, "loss_teacher_energy_proxy": 2.183432, "loss_teacher_vuv_proxy": 0.707373, "loss_teacher_aper_proxy": 0.073374, "loss_teacher_proxy_acoustic": 2.232101, "loss_teacher_proxy_temporal": 0.005262, "loss_log_f0_correction_l1": 0.01267, "loss_aper_correction_l1": 0.207938, "teacher_confidence_weighted": true, "effective_weight_sum": 71.284851, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 0.0, "semantic_nonverbal_sample_ratio": 1.0, "semantic_base_multiplier_mean": 0.8, "semantic_event_prior_multiplier_mean": 0.8, "semantic_event_multiplier_mean": 0.93, "semantic_z_art_multiplier_mean": 0.96}
- sample_record_id_batches: [['target::no_text_voice/chapter3_17_firefly_106']]

## Notes
- This evaluation uses the stored Stage3 checkpoint with the current teacher-label and calibration assets.
- Unlike the in-loop sampled validation, this report walks the full selected slice sequentially.
- These losses are still teacher-supervised proxy losses, not final user-facing quality metrics.
