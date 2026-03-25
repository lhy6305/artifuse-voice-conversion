# paired parallel source semantic parity sidecar 摘要

## 总览
- semantic_contract_version: `paired_parallel_source_semantic_parity_sidecar_v1`
- semantic_label_space_version: `source_paired_parallel_bootstrap_semantics_v1`
- transfer_type: `paired_parallel_target_to_source_same_content_v1`
- pair_spec_paths: `['F:/proj_dev/tmp/workdir4/data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl', 'F:/proj_dev/tmp/workdir4/data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl']`
- target_event_semantic_sidecar_path: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl`
- target_event_timing_semantic_sidecar_path: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl`
- record_count: `2`
- split_membership_counts: `{'train': 2, 'validation': 2}`
- parity_status_counts: `{'matched_target_semantic_and_timing': 2}`

## 统计
- semantic_ready_for_source_side_bootstrap_count: `2`
- source_estimated_frame_count_stats: `{'count': 2, 'min': 657, 'max': 660, 'mean': 658.5}`
- lexical_char_count_stats: `{'count': 2, 'min': 10, 'max': 10, 'mean': 10.0}`
- clause_region_count_stats: `{'count': 2, 'min': 1, 'max': 2, 'mean': 1.5}`
- pause_boundary_event_count_stats: `{'count': 2, 'min': 0, 'max': 1, 'mean': 0.5}`
- terminal_boundary_event_count_stats: `{'count': 2, 'min': 1, 'max': 1, 'mean': 1.0}`
- timeline_event_count_stats: `{'count': 2, 'min': 2, 'max': 4, 'mean': 3.0}`
- source_to_target_duration_ratio_stats: `{'count': 2, 'min': 0.909098, 'max': 0.95239, 'mean': 0.930744}`
- source_duration_metadata_drift_sec_stats: `{'count': 2, 'min': 1.11873, 'max': 1.491224, 'mean': 1.304977}`
- target_duration_metadata_drift_sec_stats: `{'count': 2, 'min': 0.0, 'max': 0.0, 'mean': 0.0}`

## 结构分布
- utterance_structure_type_counts: `{'multi_clause_single_terminal': 1, 'single_clause_terminal': 1}`
- label_status_counts: `{'pending_upgrade': 2}`

## 说明
- 该 sidecar 通过 paired parallel 同内容 target 语义向 source 侧做 parity bootstrap，不代表 source-native text/phone semantic 已完成。
- timing 来自 target lexical ratios 向 source frame 轴的投影，不是 source forced alignment。
- 这一步的目标是补 source-side / parity-aware semantic assets，为后续更上游的 supervision 路线提供基础。 
