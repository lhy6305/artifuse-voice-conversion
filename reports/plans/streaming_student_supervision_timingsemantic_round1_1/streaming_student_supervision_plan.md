# Stage3 Streaming Student Supervision Plan

- generated_at: 2026-03-25T21:07:47
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- loss_weights: {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}
- semantic_supervision: {"enabled": true, "required_contract_version": "target_event_semantic_sidecar_v1", "required_timing_contract_version": "target_event_timing_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "timing_ready_bonus": 0.04, "timing_multi_clause_bonus": 0.04, "timing_pause_present_bonus": 0.03, "timing_terminal_present_bonus": 0.03, "nonverbal_penalty": 0.2, "event_prior_alpha": 1.0, "event_alpha": 0.35, "z_art_alpha": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45}
- loss_weight_overrides_path: None
- use_teacher_confidence: True

## target_train
- record_count: 592
- dry_run_batch_size: 4
- sample_record_ids: ['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11', 'target::archive_firefly_12']
- semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 4}, "semantic_label_status_counts": {"pending_upgrade": 4}}
- timing_semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 4}, "timing_label_status_counts": {"pending_upgrade": 4}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 4}, "timing_multi_clause_count": 4, "timing_pause_present_count": 4, "timing_terminal_present_count": 3}
- loss_metrics: {"loss_total": 22.507067, "loss_total_default_reference": 22.507067, "loss_total_semantic_disabled_reference": 19.93078, "loss_teacher_z_art": 7.813498, "loss_teacher_event": 6.566605, "loss_teacher_event_prior": 7.730862, "loss_teacher_energy_proxy": 16.590944, "loss_teacher_vuv_proxy": 0.698912, "loss_teacher_aper_proxy": 0.038994, "loss_teacher_proxy_acoustic": 16.879463, "loss_teacher_proxy_temporal": 0.005807, "loss_log_f0_correction_l1": 0.283753, "loss_aper_correction_l1": 0.222308, "teacher_confidence_weighted": true, "effective_weight_sum": 7914.069336, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "timing_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_timing_ready_sample_ratio": 1.0, "semantic_timing_multi_clause_sample_ratio": 1.0, "semantic_timing_pause_present_sample_ratio": 1.0, "semantic_timing_terminal_present_sample_ratio": 0.75, "semantic_base_multiplier_mean": 1.4175, "semantic_event_prior_multiplier_mean": 1.4175, "semantic_event_multiplier_mean": 1.146125, "semantic_z_art_multiplier_mean": 1.0835}

## target_validation
- record_count: 66
- dry_run_batch_size: 4
- sample_record_ids: ['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116', 'target::chapter3_3_firefly_207']
- semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 4}, "semantic_label_status_counts": {"pending_upgrade": 4}}
- timing_semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 4}, "timing_label_status_counts": {"pending_upgrade": 4}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 4}, "timing_multi_clause_count": 0, "timing_pause_present_count": 0, "timing_terminal_present_count": 4}
- loss_metrics: {"loss_total": 20.059671, "loss_total_default_reference": 20.059671, "loss_total_semantic_disabled_reference": 18.778149, "loss_teacher_z_art": 8.754841, "loss_teacher_event": 6.039706, "loss_teacher_event_prior": 6.596114, "loss_teacher_energy_proxy": 7.41343, "loss_teacher_vuv_proxy": 0.699649, "loss_teacher_aper_proxy": 0.035216, "loss_teacher_proxy_acoustic": 7.671777, "loss_teacher_proxy_temporal": 0.008703, "loss_log_f0_correction_l1": 0.280548, "loss_aper_correction_l1": 0.243542, "teacher_confidence_weighted": true, "effective_weight_sum": 604.951477, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "timing_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 1.0, "semantic_nonverbal_sample_ratio": 0.0, "semantic_timing_ready_sample_ratio": 1.0, "semantic_timing_multi_clause_sample_ratio": 0.0, "semantic_timing_pause_present_sample_ratio": 0.0, "semantic_timing_terminal_present_sample_ratio": 1.0, "semantic_base_multiplier_mean": 1.2, "semantic_event_prior_multiplier_mean": 1.2, "semantic_event_multiplier_mean": 1.07, "semantic_z_art_multiplier_mean": 1.04}

## target_special_eval
- record_count: 8
- dry_run_batch_size: 4
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101', 'target::no_text_voice/chapter3_21_firefly_108', 'target::no_text_voice/chapter3_22_firefly_115']
- semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 4}, "semantic_label_status_counts": {"pending_upgrade": 4}}
- timing_semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 4}, "timing_label_status_counts": {"pending_upgrade": 4}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 4}, "timing_multi_clause_count": 0, "timing_pause_present_count": 0, "timing_terminal_present_count": 0}
- loss_metrics: {"loss_total": 16.974245, "loss_total_default_reference": 16.974245, "loss_total_semantic_disabled_reference": 17.936234, "loss_teacher_z_art": 6.29074, "loss_teacher_event": 5.429201, "loss_teacher_event_prior": 4.53556, "loss_teacher_energy_proxy": 11.491331, "loss_teacher_vuv_proxy": 0.69563, "loss_teacher_aper_proxy": 0.041962, "loss_teacher_proxy_acoustic": 11.804756, "loss_teacher_proxy_temporal": 0.004981, "loss_log_f0_correction_l1": 0.305362, "loss_aper_correction_l1": 0.209667, "teacher_confidence_weighted": true, "effective_weight_sum": 541.467468, "semantic_supervision_enabled": true, "semantic_sidecar_present_ratio": 1.0, "timing_sidecar_present_ratio": 1.0, "semantic_weight_applied_ratio": 1.0, "semantic_clean_text_sample_ratio": 0.0, "semantic_nonverbal_sample_ratio": 1.0, "semantic_timing_ready_sample_ratio": 1.0, "semantic_timing_multi_clause_sample_ratio": 0.0, "semantic_timing_pause_present_sample_ratio": 0.0, "semantic_timing_terminal_present_sample_ratio": 0.0, "semantic_base_multiplier_mean": 0.84, "semantic_event_prior_multiplier_mean": 0.84, "semantic_event_multiplier_mean": 0.944, "semantic_z_art_multiplier_mean": 0.968}

## Notes
- This stage defines only the minimum teacher-supervised dry-run losses needed to move beyond pure data wiring.
- Current supervision intentionally avoids forcing a hidden-state distillation term because Stage3 and offline_mvp hidden dimensions are not yet aligned.
- Current semantic supervision only reweights teacher_event_prior / teacher_event / teacher_z_art by target-side structure and timing semantics; it does not pretend to add phone/manner/place labels.
- Frontend proxy terms are heuristic and should be treated as bootstrap supervision, not final semantic commitments.

## Next Steps
- Decide which teacher_frame_confidence behaviors become actual weighting or filtering policy in real training.
- Add explicit Stage3 hidden-space projection only if hidden distillation is still needed after the base loss route is validated.
- Build a real training loop on top of this dry-run contract without opening r_res yet.
