# Stage3 downstream control packet

- packet_version: streaming_student_downstream_control_v1
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_vuvbalancedgate24_round1_1/checkpoints/streaming_student_stage_loop_vuvbalancedgate24_round1_1.step24.pt
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_parallel_control_branch_controlfamily_v1.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- split_name: target_validation
- branch_label: streaming_student_stage_loop_vuvbalancedgate24_round1_1
- sample_count: 3
- packet_ready_count: 3
- max_audio_sec: None
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- contract: {"event_target_family": "teacher_e_evt_v1", "event_projection_mode": "full_e_evt", "frame_length": 400, "hop_length": 160, "r_res_enabled": false, "f0_status": "analysis_only_affine_calibrated_to_target_reference", "aper_status": "analysis_only_affine_calibrated_to_target_reference", "energy_status": "analysis_only_affine_calibrated_to_target_reference"}
- named_control_readiness_summary: {"gate_version": "stage3_student_control_readiness_gate_v1", "negative_gate_only": true, "record_count": 3, "e_evt_exported_count": 3, "f0_ready_count": 0, "vuv_ready_count": 1, "aper_ready_count": 3, "energy_ready_count": 3, "all_core_controls_ready_count": 0, "auto_reject_count": 3, "review_required_count": 0, "all_records_auto_reject": true, "all_records_core_controls_ready": false}

## Records
### target::chapter3_3_firefly_162
- audio_path: F:\proj_dev\tmp\workdir4\data_prep\round1_1\firefly_mainstream\audio\chapter3_3_firefly_162.wav
- packet_path: F:/proj_dev/tmp/workdir4/reports/eval/streaming_student_checkpoint_selector_comparison_vuvbalancedgate24_vs_warm6step15_round1_1/packet_aware/packet_exports/step0024_streaming_student_stage_loop_vuvbalancedgate24_round1_1/records/target__chapter3_3_firefly_162.pt
- frame_count: 167
- packet_ready_for_named_e_evt_handoff: True
- named_control_readiness: {"gate_version": "stage3_student_control_readiness_gate_v1", "negative_gate_only": true, "packet_ready_for_named_e_evt_handoff": true, "e_evt_status": "analysis_only_exported", "z_art_status": "analysis_only_exported", "f0_status": "auto_reject_not_ready", "vuv_status": "review_required", "aper_status": "review_required", "energy_status": "review_required", "all_core_controls_ready": false, "route_open_recommended": false, "assessment": "auto_reject_named_control_incomplete"}
- event_target_family: teacher_e_evt_v1
- event_projection_mode: full_e_evt
- z_art_abs_mean: 0.578637
- e_evt_mean: 0.215248
- vuv_prob_mean: 0.797288
- aper_prob_mean: 0.537012
- energy_log_mean: -1.901389
- energy_norm_mean: 0.813909
- energy_stage5_norm_mean: 0.685927
- f0_log_proxy_mean: 7.81301
- f0_reference_voiced_frame_count: 157
- f0_proxy_reference_corr: 0.495445
- f0_calibrated_log2_mae: 0.17472
- vuv_reference_mae: 0.107152
- aper_reference_mae: 0.422272
- aper_calibrated_reference_mae: 0.095282
- energy_stage5_norm_reference_mae: 0.132352
- energy_stage5_norm_calibrated_reference_mae: 0.08455

### target::chapter3_3_firefly_138
- audio_path: F:\proj_dev\tmp\workdir4\data_convert\dataset_firefly_raw\chapter3_3_firefly_138.wav
- packet_path: F:/proj_dev/tmp/workdir4/reports/eval/streaming_student_checkpoint_selector_comparison_vuvbalancedgate24_vs_warm6step15_round1_1/packet_aware/packet_exports/step0024_streaming_student_stage_loop_vuvbalancedgate24_round1_1/records/target__chapter3_3_firefly_138.pt
- frame_count: 1379
- packet_ready_for_named_e_evt_handoff: True
- named_control_readiness: {"gate_version": "stage3_student_control_readiness_gate_v1", "negative_gate_only": true, "packet_ready_for_named_e_evt_handoff": true, "e_evt_status": "analysis_only_exported", "z_art_status": "analysis_only_exported", "f0_status": "auto_reject_not_ready", "vuv_status": "auto_reject_not_ready", "aper_status": "review_required", "energy_status": "review_required", "all_core_controls_ready": false, "route_open_recommended": false, "assessment": "auto_reject_named_control_incomplete"}
- event_target_family: teacher_e_evt_v1
- event_projection_mode: full_e_evt
- z_art_abs_mean: 0.535974
- e_evt_mean: 0.21751
- vuv_prob_mean: 0.774628
- aper_prob_mean: 0.546407
- energy_log_mean: -2.333415
- energy_norm_mean: 0.756863
- energy_stage5_norm_mean: 0.596113
- f0_log_proxy_mean: 7.877737
- f0_reference_voiced_frame_count: 1161
- f0_proxy_reference_corr: 0.187293
- f0_calibrated_log2_mae: 0.431756
- vuv_reference_mae: 0.207186
- aper_reference_mae: 0.403445
- aper_calibrated_reference_mae: 0.137007
- energy_stage5_norm_reference_mae: 0.155933
- energy_stage5_norm_calibrated_reference_mae: 0.109106

### target::chapter3_4_firefly_106
- audio_path: F:\proj_dev\tmp\workdir4\data_convert\dataset_firefly_raw\chapter3_4_firefly_106.wav
- packet_path: F:/proj_dev/tmp/workdir4/reports/eval/streaming_student_checkpoint_selector_comparison_vuvbalancedgate24_vs_warm6step15_round1_1/packet_aware/packet_exports/step0024_streaming_student_stage_loop_vuvbalancedgate24_round1_1/records/target__chapter3_4_firefly_106.pt
- frame_count: 5815
- packet_ready_for_named_e_evt_handoff: True
- named_control_readiness: {"gate_version": "stage3_student_control_readiness_gate_v1", "negative_gate_only": true, "packet_ready_for_named_e_evt_handoff": true, "e_evt_status": "analysis_only_exported", "z_art_status": "analysis_only_exported", "f0_status": "auto_reject_not_ready", "vuv_status": "auto_reject_not_ready", "aper_status": "review_required", "energy_status": "review_required", "all_core_controls_ready": false, "route_open_recommended": false, "assessment": "auto_reject_named_control_incomplete"}
- event_target_family: teacher_e_evt_v1
- event_projection_mode: full_e_evt
- z_art_abs_mean: 0.43893
- e_evt_mean: 0.225922
- vuv_prob_mean: 0.660008
- aper_prob_mean: 0.564941
- energy_log_mean: -3.168967
- energy_norm_mean: 0.549958
- energy_stage5_norm_mean: 0.430573
- f0_log_proxy_mean: 8.013779
- f0_reference_voiced_frame_count: 4840
- f0_proxy_reference_corr: 0.608869
- f0_calibrated_log2_mae: 0.370633
- vuv_reference_mae: 0.255081
- aper_reference_mae: 0.365557
- aper_calibrated_reference_mae: 0.12198
- energy_stage5_norm_reference_mae: 0.120477
- energy_stage5_norm_calibrated_reference_mae: 0.130859

## Notes
- This export is the first student-side downstream packet candidate, not a Stage5 training result.
- Current e_evt is exported only when checkpoint semantic_supervision.event_target_family=teacher_e_evt_v1.
- F0 now also exports an analysis-only affine-calibrated Hz view against target-reference acoustic state; this is an audit aid, not yet a deployment-ready control contract.
- aper and energy now also export analysis-only affine-calibrated audit views against target reference; this is an audit aid, not yet a deployment-ready control contract.
- packet_ready_for_named_e_evt_handoff only means the named e_evt tensor/metadata contract is exportable; it is not a numeric readiness claim.
- named_control_readiness is a negative gate only: it can auto-reject clearly incomplete packets, but it does not prove a successful downstream handoff.
- r_res remains intentionally absent on this route.
