# Stage3 Streaming Student Supervision Plan

- generated_at: 2026-03-24T22:19:15
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
- loss_metrics: {"loss_total": 19.392374, "loss_total_default_reference": 19.392374, "loss_total_semantic_disabled_reference": 17.482182, "loss_teacher_z_art": 3.159169, "loss_teacher_event": 6.229536, "loss_teacher_event_prior": 7.56251, "loss_teacher_energy_proxy": 24.426241, "loss_teacher_vuv_proxy": 0.726879, "loss_teacher_aper_proxy": 0.008258, "loss_teacher_proxy_acoustic": 24.729702, "loss_teacher_proxy_temporal": 0.006281, "loss_log_f0_correction_l1": 0.264726, "loss_aper_correction_l1": 0.33489, "teacher_confidence_weighted": true, "effective_weight_sum": 1350.021973, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_base_multiplier_mean": 1.36, "semantic_event_prior_multiplier_mean": 1.36, "semantic_event_multiplier_mean": 1.126, "semantic_z_art_multiplier_mean": 1.072}

## target_validation
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::chapter3_3_firefly_162']
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}}
- loss_metrics: {"loss_total": 15.864218, "loss_total_default_reference": 15.864218, "loss_total_semantic_disabled_reference": 15.140512, "loss_teacher_z_art": 4.452013, "loss_teacher_event": 5.818895, "loss_teacher_event_prior": 6.217607, "loss_teacher_energy_proxy": 9.448575, "loss_teacher_vuv_proxy": 0.766985, "loss_teacher_aper_proxy": 0.010593, "loss_teacher_proxy_acoustic": 9.706883, "loss_teacher_proxy_temporal": 0.010984, "loss_log_f0_correction_l1": 0.284211, "loss_aper_correction_l1": 0.34132, "teacher_confidence_weighted": true, "effective_weight_sum": 90.56897, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_base_multiplier_mean": 1.13, "semantic_event_prior_multiplier_mean": 1.13, "semantic_event_multiplier_mean": 1.0455, "semantic_z_art_multiplier_mean": 1.026}

## target_special_eval
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106']
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}}
- loss_metrics: {"loss_total": 12.877523, "loss_total_default_reference": 12.877523, "loss_total_semantic_disabled_reference": 13.957223, "loss_teacher_z_art": 3.424, "loss_teacher_event": 5.150774, "loss_teacher_event_prior": 4.39472, "loss_teacher_energy_proxy": 7.941979, "loss_teacher_vuv_proxy": 0.752622, "loss_teacher_aper_proxy": 0.007218, "loss_teacher_proxy_acoustic": 8.217709, "loss_teacher_proxy_temporal": 0.005654, "loss_log_f0_correction_l1": 0.276336, "loss_aper_correction_l1": 0.351622, "teacher_confidence_weighted": true, "effective_weight_sum": 71.284851, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 0.0, "semantic_nonverbal_sample_ratio": 1.0, "semantic_base_multiplier_mean": 0.8, "semantic_event_prior_multiplier_mean": 0.8, "semantic_event_multiplier_mean": 0.93, "semantic_z_art_multiplier_mean": 0.96}

## Notes
- This stage defines only the minimum teacher-supervised dry-run losses needed to move beyond pure data wiring.
- Current supervision intentionally avoids forcing a hidden-state distillation term because Stage3 and offline_mvp hidden dimensions are not yet aligned.
- Current semantic supervision only reweights teacher_event_prior / teacher_event / teacher_z_art by target-side structure semantics; it does not pretend to add phone/manner/place labels.
- Frontend proxy terms are heuristic and should be treated as bootstrap supervision, not final semantic commitments.

## Next Steps
- Decide which teacher_frame_confidence behaviors become actual weighting or filtering policy in real training.
- Add explicit Stage3 hidden-space projection only if hidden distillation is still needed after the base loss route is validated.
- Build a real training loop on top of this dry-run contract without opening r_res yet.
