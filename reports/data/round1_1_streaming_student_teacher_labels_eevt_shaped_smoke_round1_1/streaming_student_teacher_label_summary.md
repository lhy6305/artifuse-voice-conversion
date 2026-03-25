# Stage3 streaming_student teacher-label export summary

## Anchor
- teacher_anchor.experiment_id: EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration
- teacher_anchor.source: route_handoff_anchor
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.metrics.json
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked

## Export
- record_count: 6
- frame_count: 8539
- batch_size: 4
- max_records_per_slice: 2
- teacher_e_evt_target_shaping_mode: center_weighted_boundary_progressive_final_clause_v1
- index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_eevt_shaped_smoke_round1_1/teacher_label_index.jsonl

## Feature Dims
- hidden: 64
- fused_hidden: 64
- z_art: 8
- event_logits: 8
- e_evt: 8
- acoustic: 4
- confidence: 1

## target_train
- record_count: 2
- duration_mean_sec: 14.136486
- frame_count_mean: 3894.5
- confidence_mean: 0.459166
- low_confidence_frame_ratio_mean: 0.426243
- utterance_structure_type_counts: {'multi_terminal': 1, 'other': 1}
- final_terminal_type_counts: {'none': 1, 'terminal_period': 1}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 2}
- semantic_inventory_status_counts: {'matched_inventory': 2}
- semantic_label_status_counts: {'pending_upgrade': 2}
- semantic_utterance_structure_type_counts: {'multi_terminal': 1, 'other': 1}
- semantic_final_terminal_type_counts: {'none': 1, 'terminal_period': 1}
- timing_contract_version_counts: {'target_event_timing_semantic_sidecar_v1': 2}
- timing_inventory_status_counts: {'matched_semantic_sidecar': 2}
- timing_label_status_counts: {'pending_upgrade': 2}
- timing_alignment_type_counts: {'weak_punctuation_lexical_progress_v1': 2}
- teacher_event_target_shaping_mode_counts: {'center_weighted_boundary_progressive_final_clause_v1': 2}
- sample_record_ids: ['target::archive_firefly_1', 'target::archive_firefly_10']

## target_validation
- record_count: 2
- duration_mean_sec: 0.79449
- frame_count_mean: 217.0
- confidence_mean: 0.534599
- low_confidence_frame_ratio_mean: 0.155745
- utterance_structure_type_counts: {'single_clause_terminal': 2}
- final_terminal_type_counts: {'terminal_period': 2}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 2}
- semantic_inventory_status_counts: {'matched_inventory': 2}
- semantic_label_status_counts: {'pending_upgrade': 2}
- semantic_utterance_structure_type_counts: {'single_clause_terminal': 2}
- semantic_final_terminal_type_counts: {'terminal_period': 2}
- timing_contract_version_counts: {'target_event_timing_semantic_sidecar_v1': 2}
- timing_inventory_status_counts: {'matched_semantic_sidecar': 2}
- timing_label_status_counts: {'pending_upgrade': 2}
- timing_alignment_type_counts: {'weak_punctuation_lexical_progress_v1': 2}
- teacher_event_target_shaping_mode_counts: {'center_weighted_boundary_progressive_final_clause_v1': 2}
- sample_record_ids: ['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184']

## target_special_eval
- record_count: 2
- duration_mean_sec: 0.580499
- frame_count_mean: 158.0
- confidence_mean: 0.514625
- low_confidence_frame_ratio_mean: 0.171126
- utterance_structure_type_counts: {'nonverbal': 2}
- final_terminal_type_counts: {'none': 2}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 2}
- semantic_inventory_status_counts: {'matched_inventory': 2}
- semantic_label_status_counts: {'pending_upgrade': 2}
- semantic_utterance_structure_type_counts: {'nonverbal': 2}
- semantic_final_terminal_type_counts: {'none': 2}
- timing_contract_version_counts: {'target_event_timing_semantic_sidecar_v1': 2}
- timing_inventory_status_counts: {'matched_semantic_sidecar': 2}
- timing_label_status_counts: {'pending_upgrade': 2}
- timing_alignment_type_counts: {'weak_punctuation_lexical_progress_v1': 2}
- teacher_event_target_shaping_mode_counts: {'center_weighted_boundary_progressive_final_clause_v1': 2}
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101']

## Notes
- Teacher labels are pseudo labels exported from the formal offline_mvp route anchor, not physical ground truth.
- frame_confidence uses heuristic bootstrap_v1 and is meant for later weighting/filtering, not as a final confidence design.
- This export now materializes a bootstrap teacher_e_evt target so Stage3 can stop treating legacy heuristic event_probs as the final event contract.
- Stage3 may reuse these labels as assets, but should still keep its own training entry and loss contract separate from offline_mvp.
- teacher_e_evt target shaping mode for this export = center_weighted_boundary_progressive_final_clause_v1.
