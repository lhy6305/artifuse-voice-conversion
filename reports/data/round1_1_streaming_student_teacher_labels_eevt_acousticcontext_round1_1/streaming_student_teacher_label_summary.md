# Stage3 streaming_student teacher-label export summary

## Anchor
- teacher_anchor.experiment_id: EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration
- teacher_anchor.source: route_handoff_anchor
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.metrics.json
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked

## Export
- record_count: 666
- frame_count: 1118127
- batch_size: 8
- max_records_per_slice: None
- teacher_e_evt_bridge_mode: acoustic_contextual_event_bridge_v1
- teacher_e_evt_target_shaping_mode: center_weighted_boundary_progressive_final_clause_v1
- index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_eevt_acousticcontext_round1_1/teacher_label_index.jsonl

## Feature Dims
- hidden: 64
- fused_hidden: 64
- z_art: 8
- event_logits: 8
- e_evt: 8
- acoustic: 4
- confidence: 1

## target_train
- record_count: 592
- duration_mean_sec: 6.158126
- frame_count_mean: 1695.342905
- confidence_mean: 0.489846
- low_confidence_frame_ratio_mean: 0.319015
- utterance_structure_type_counts: {'multi_clause_single_terminal': 276, 'multi_terminal': 156, 'other': 102, 'single_clause_terminal': 58}
- final_terminal_type_counts: {'none': 153, 'terminal_exclamation': 37, 'terminal_period': 308, 'terminal_question': 94}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 592}
- semantic_inventory_status_counts: {'matched_inventory': 592}
- semantic_label_status_counts: {'pending_upgrade': 592}
- semantic_utterance_structure_type_counts: {'multi_clause_single_terminal': 276, 'multi_terminal': 156, 'other': 102, 'single_clause_terminal': 58}
- semantic_final_terminal_type_counts: {'none': 153, 'terminal_exclamation': 37, 'terminal_period': 308, 'terminal_question': 94}
- timing_contract_version_counts: {'target_event_timing_semantic_sidecar_v1': 592}
- timing_inventory_status_counts: {'matched_semantic_sidecar': 592}
- timing_label_status_counts: {'pending_upgrade': 592}
- timing_alignment_type_counts: {'weak_punctuation_lexical_progress_v1': 592}
- teacher_event_bridge_mode_counts: {'acoustic_contextual_event_bridge_v1': 592}
- teacher_event_target_shaping_mode_counts: {'center_weighted_boundary_progressive_final_clause_v1': 592}
- sample_record_ids: ['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11', 'target::archive_firefly_12', 'target::archive_firefly_13', 'target::archive_firefly_14', 'target::archive_firefly_15', 'target::archive_firefly_16']

## target_validation
- record_count: 66
- duration_mean_sec: 6.173509
- frame_count_mean: 1699.530303
- confidence_mean: 0.486753
- low_confidence_frame_ratio_mean: 0.338887
- utterance_structure_type_counts: {'multi_clause_single_terminal': 31, 'multi_terminal': 18, 'other': 9, 'single_clause_terminal': 8}
- final_terminal_type_counts: {'none': 21, 'terminal_exclamation': 5, 'terminal_period': 32, 'terminal_question': 8}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 66}
- semantic_inventory_status_counts: {'matched_inventory': 66}
- semantic_label_status_counts: {'pending_upgrade': 66}
- semantic_utterance_structure_type_counts: {'multi_clause_single_terminal': 31, 'multi_terminal': 18, 'other': 9, 'single_clause_terminal': 8}
- semantic_final_terminal_type_counts: {'none': 21, 'terminal_exclamation': 5, 'terminal_period': 32, 'terminal_question': 8}
- timing_contract_version_counts: {'target_event_timing_semantic_sidecar_v1': 66}
- timing_inventory_status_counts: {'matched_semantic_sidecar': 66}
- timing_label_status_counts: {'pending_upgrade': 66}
- timing_alignment_type_counts: {'weak_punctuation_lexical_progress_v1': 66}
- teacher_event_bridge_mode_counts: {'acoustic_contextual_event_bridge_v1': 66}
- teacher_event_target_shaping_mode_counts: {'center_weighted_boundary_progressive_final_clause_v1': 66}
- sample_record_ids: ['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116', 'target::chapter3_3_firefly_207', 'target::chapter3_30_firefly_101', 'target::chapter3_2_firefly_131', 'target::chapter3_2_firefly_212', 'target::chapter3_3_firefly_246']

## target_special_eval
- record_count: 8
- duration_mean_sec: 1.057291
- frame_count_mean: 289.375
- confidence_mean: 0.489138
- low_confidence_frame_ratio_mean: 0.177271
- utterance_structure_type_counts: {'nonverbal': 8}
- final_terminal_type_counts: {'none': 8}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 8}
- semantic_inventory_status_counts: {'matched_inventory': 8}
- semantic_label_status_counts: {'pending_upgrade': 8}
- semantic_utterance_structure_type_counts: {'nonverbal': 8}
- semantic_final_terminal_type_counts: {'none': 8}
- timing_contract_version_counts: {'target_event_timing_semantic_sidecar_v1': 8}
- timing_inventory_status_counts: {'matched_semantic_sidecar': 8}
- timing_label_status_counts: {'pending_upgrade': 8}
- timing_alignment_type_counts: {'weak_punctuation_lexical_progress_v1': 8}
- teacher_event_bridge_mode_counts: {'acoustic_contextual_event_bridge_v1': 8}
- teacher_event_target_shaping_mode_counts: {'center_weighted_boundary_progressive_final_clause_v1': 8}
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101', 'target::no_text_voice/chapter3_21_firefly_108', 'target::no_text_voice/chapter3_22_firefly_115', 'target::no_text_voice/chapter3_29_firefly_139', 'target::no_text_voice/chapter3_2_firefly_102', 'target::no_text_voice/chapter3_30_firefly_144', 'target::no_text_voice/chapter3_3_firefly_110']

## Notes
- Teacher labels are pseudo labels exported from the formal offline_mvp route anchor, not physical ground truth.
- frame_confidence uses heuristic bootstrap_v1 and is meant for later weighting/filtering, not as a final confidence design.
- This export now materializes a bootstrap teacher_e_evt target so Stage3 can stop treating legacy heuristic event_probs as the final event contract.
- Stage3 may reuse these labels as assets, but should still keep its own training entry and loss contract separate from offline_mvp.
- teacher_e_evt bridge mode for this export = acoustic_contextual_event_bridge_v1.
- teacher_e_evt target shaping mode for this export = center_weighted_boundary_progressive_final_clause_v1.
