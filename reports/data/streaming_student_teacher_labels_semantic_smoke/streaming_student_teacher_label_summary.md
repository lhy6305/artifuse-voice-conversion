# Stage3 streaming_student teacher-label export summary

## Anchor
- teacher_anchor.experiment_id: EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration
- teacher_anchor.source: route_handoff_anchor
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.metrics.json
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked

## Export
- record_count: 3
- frame_count: 3349
- batch_size: 1
- max_records_per_slice: 1
- index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl

## Feature Dims
- hidden: 64
- fused_hidden: 64
- z_art: 8
- event_logits: 8
- acoustic: 4
- confidence: 1

## target_train
- record_count: 1
- duration_mean_sec: 11.087982
- frame_count_mean: 3054.0
- confidence_mean: 0.44205
- low_confidence_frame_ratio_mean: 0.483955
- utterance_structure_type_counts: {'multi_terminal': 1}
- final_terminal_type_counts: {'terminal_period': 1}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 1}
- semantic_inventory_status_counts: {'matched_inventory': 1}
- semantic_label_status_counts: {'pending_upgrade': 1}
- semantic_utterance_structure_type_counts: {'multi_terminal': 1}
- semantic_final_terminal_type_counts: {'terminal_period': 1}
- sample_record_ids: ['target::archive_firefly_1']

## target_validation
- record_count: 1
- duration_mean_sec: 0.612993
- frame_count_mean: 167.0
- confidence_mean: 0.542329
- low_confidence_frame_ratio_mean: 0.161677
- utterance_structure_type_counts: {'single_clause_terminal': 1}
- final_terminal_type_counts: {'terminal_period': 1}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 1}
- semantic_inventory_status_counts: {'matched_inventory': 1}
- semantic_label_status_counts: {'pending_upgrade': 1}
- semantic_utterance_structure_type_counts: {'single_clause_terminal': 1}
- semantic_final_terminal_type_counts: {'terminal_period': 1}
- sample_record_ids: ['target::chapter3_3_firefly_162']

## target_special_eval
- record_count: 1
- duration_mean_sec: 0.470998
- frame_count_mean: 128.0
- confidence_mean: 0.556913
- low_confidence_frame_ratio_mean: 0.039062
- utterance_structure_type_counts: {'nonverbal': 1}
- final_terminal_type_counts: {'none': 1}
- semantic_contract_version_counts: {'target_event_semantic_sidecar_v1': 1}
- semantic_inventory_status_counts: {'matched_inventory': 1}
- semantic_label_status_counts: {'pending_upgrade': 1}
- semantic_utterance_structure_type_counts: {'nonverbal': 1}
- semantic_final_terminal_type_counts: {'none': 1}
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106']

## Notes
- Teacher labels are pseudo labels exported from the formal offline_mvp route anchor, not physical ground truth.
- frame_confidence uses heuristic bootstrap_v1 and is meant for later weighting/filtering, not as a final confidence design.
- Stage3 may reuse these labels as assets, but should still keep its own training entry and loss contract separate from offline_mvp.
