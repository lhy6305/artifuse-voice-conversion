# target event semantic sidecar 摘要

## 总览
- semantic_contract_version: `target_event_semantic_sidecar_v1`
- semantic_label_space_version: `target_lexical_structure_semantics_v1`
- weak_event_hints_path: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl`
- target_supervision_inventory_path: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/b1_supervision/target_supervision_inventory.jsonl`
- record_count: `666`
- split_counts: `{'target_special_eval': 8, 'target_train': 592, 'target_validation': 66}`
- inventory_status_counts: `{'matched_inventory': 666}`

## 当前 semantic 可用性
- clean_text_available_count: `666`
- phone_sequence_available_count: `0`
- manner_sequence_available_count: `0`
- place_sequence_available_count: `0`
- forced_alignment_available_count: `0`
- future_label_status_counts: `{'pending_upgrade': 666}`

## 结构分布
- utterance_structure_type_counts: `{'multi_clause_single_terminal': 307, 'multi_terminal': 174, 'nonverbal': 8, 'other': 111, 'single_clause_terminal': 66}`
- final_terminal_type_counts: `{'none': 182, 'terminal_exclamation': 42, 'terminal_period': 340, 'terminal_question': 102}`
- lexical_char_count_stats: `{'count': 666, 'min': 0, 'max': 76, 'mean': 21.295796}`
- clause_count_stats: `{'count': 666, 'min': 0, 'max': 10, 'mean': 3.010511}`
- pause_boundary_count_stats: `{'count': 666, 'min': 0, 'max': 9, 'mean': 1.915916}`
- terminal_boundary_count_stats: `{'count': 666, 'min': 0, 'max': 4, 'mean': 1.115616}`

## 当前 runtime event_probs 元数据
- event_probs_version: `offline_mvp_heuristic_event_target_v1`
- event_prob_dimensions: `['energy_gate', 'abs_delta_gate', 'high_zero_cross', 'low_zero_cross_voiced_like', 'high_zero_cross_voiced_like', 'delta_energy_rise', 'delta_energy_fall', 'energy_norm']`
- semantic_status: `heuristic_frame_targets_not_design_e_evt`

## 说明
- 当前 8 维 `event_probs` 仍是旧 heuristic frame targets，不是假定为设计稿里的命名 `e_evt`。
- 这份 sidecar 把 target-side lexical / punctuation / clause 语义独立落盘，供后续 contract/semantic 升级直接消费。
- source-side 仍没有文本、phone、manner、place 或 forced alignment；这条 semantic 线当前只能先做 target-side bootstrap。
