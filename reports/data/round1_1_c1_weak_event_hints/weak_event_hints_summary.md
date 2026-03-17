# `C1` 弱事件提示 sidecar 摘要

## 总览
- 记录数: `666`
- split_counts: `{'target_special_eval': 8, 'target_train': 592, 'target_validation': 66}`
- nonverbal_only_count: `8`
- records_with_pause_boundaries: `582`
- records_with_terminal_boundaries: `547`
- pause_boundary_total: `1276`
- terminal_boundary_total: `743`

## 句末类型分布
- final_terminal_type_counts: `{'none': 182, 'terminal_exclamation': 42, 'terminal_period': 340, 'terminal_question': 102}`

## 句型结构分布
- utterance_structure_type_counts: `{'multi_clause_single_terminal': 307, 'multi_terminal': 174, 'nonverbal': 8, 'other': 111, 'single_clause_terminal': 66}`
- clause_count_stats: `{'count': 666, 'min': 0, 'max': 10, 'mean': 3.010511, 'median': 3.0, 'stdev': 1.732452}`

## 说明
- 当前边界位置来自文本标点和字面进度的弱估计，不是强制对齐。
- 这批 sidecar 的目标是为后续 route-C 提供 target-side 弱事件监督底账。
- 当前 sidecar 已补充 clause 级跨度与句型结构类型，供后续 richer label expression 使用。
