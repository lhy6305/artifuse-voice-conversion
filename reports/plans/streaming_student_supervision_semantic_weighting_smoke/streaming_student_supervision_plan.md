# Stage3 Streaming Student Supervision Plan

- generated_at: 2026-03-24T22:09:31
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- loss_weights: {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}
- semantic_supervision: {"enabled": true, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "event_prior_alpha": 1.0, "event_alpha": 0.35, "z_art_alpha": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45}
- loss_weight_overrides_path: None
- use_teacher_confidence: True

## target_train
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::archive_firefly_1']
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}}
- loss_metrics: {"loss_total": 17.91655, "loss_total_default_reference": 17.91655, "loss_teacher_z_art": 3.521685, "loss_teacher_event": 5.741136, "loss_teacher_event_prior": 5.713325, "loss_teacher_energy_proxy": 22.707212, "loss_teacher_vuv_proxy": 0.719115, "loss_teacher_aper_proxy": 0.026345, "loss_teacher_proxy_acoustic": 23.003843, "loss_teacher_proxy_temporal": 0.00586, "loss_log_f0_correction_l1": 0.485522, "loss_aper_correction_l1": 0.490586, "teacher_confidence_weighted": true, "effective_weight_sum": 1350.021973, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_base_multiplier_mean": 1.36, "semantic_event_prior_multiplier_mean": 1.36, "semantic_event_multiplier_mean": 1.126, "semantic_z_art_multiplier_mean": 1.072}

## target_validation
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::chapter3_3_firefly_162']
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}}
- loss_metrics: {"loss_total": 15.932117, "loss_total_default_reference": 15.932117, "loss_teacher_z_art": 5.08963, "loss_teacher_event": 5.722661, "loss_teacher_event_prior": 5.641248, "loss_teacher_energy_proxy": 8.777738, "loss_teacher_vuv_proxy": 0.626724, "loss_teacher_aper_proxy": 0.009623, "loss_teacher_proxy_acoustic": 9.029206, "loss_teacher_proxy_temporal": 0.010116, "loss_log_f0_correction_l1": 0.504248, "loss_aper_correction_l1": 0.475738, "teacher_confidence_weighted": true, "effective_weight_sum": 90.56897, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_base_multiplier_mean": 1.13, "semantic_event_prior_multiplier_mean": 1.13, "semantic_event_multiplier_mean": 1.0455, "semantic_z_art_multiplier_mean": 1.026}

## target_special_eval
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106']
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}}
- loss_metrics: {"loss_total": 14.889469, "loss_total_default_reference": 14.889469, "loss_teacher_z_art": 4.406331, "loss_teacher_event": 5.727198, "loss_teacher_event_prior": 5.657568, "loss_teacher_energy_proxy": 7.272924, "loss_teacher_vuv_proxy": 0.652454, "loss_teacher_aper_proxy": 0.011839, "loss_teacher_proxy_acoustic": 7.54242, "loss_teacher_proxy_temporal": 0.005136, "loss_log_f0_correction_l1": 0.501352, "loss_aper_correction_l1": 0.48621, "teacher_confidence_weighted": true, "effective_weight_sum": 71.284851, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 0.0, "semantic_nonverbal_sample_ratio": 1.0, "semantic_base_multiplier_mean": 0.8, "semantic_event_prior_multiplier_mean": 0.8, "semantic_event_multiplier_mean": 0.93, "semantic_z_art_multiplier_mean": 0.96}

## Notes
- This stage defines only the minimum teacher-supervised dry-run losses needed to move beyond pure data wiring.
- Current supervision intentionally avoids forcing a hidden-state distillation term because Stage3 and offline_mvp hidden dimensions are not yet aligned.
- Current semantic supervision only reweights teacher_event_prior / teacher_event / teacher_z_art by target-side structure semantics; it does not pretend to add phone/manner/place labels.
- Frontend proxy terms are heuristic and should be treated as bootstrap supervision, not final semantic commitments.

## Next Steps
- Decide which teacher_frame_confidence behaviors become actual weighting or filtering policy in real training.
- Add explicit Stage3 hidden-space projection only if hidden distillation is still needed after the base loss route is validated.
- Build a real training loop on top of this dry-run contract without opening r_res yet.
