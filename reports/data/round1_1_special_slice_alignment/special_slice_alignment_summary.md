# Special Slice Alignment Summary

## Goal
- Quantify how `target_special_eval` differs from train-side candidate cohorts.
- Decide whether the next step should keep training or first change the proxy-supervision principle.

## Special Signature
- Definition: `nonverbal_only` plus zero lexical, pause, terminal, clause, and clause-span support.
- target_special_eval record_count: 8
- target_special_eval nonverbal_only_count: 8
- target_special_eval duration_sec: {'count': 8, 'min': 0.470998, 'max': 2.114989, 'mean': 1.05729, 'median': 0.956985}
- target_special_eval lexical_char_count: {'count': 8, 'min': 0.0, 'max': 0.0, 'mean': 0.0, 'median': 0.0}
- target_special_eval clause_span_count: {'count': 8, 'min': 0.0, 'max': 0.0, 'mean': 0.0, 'median': 0.0}

## Split Coverage
- target_train: {'record_count': 592, 'nonverbal_only_count': 0, 'lexical_char_count_zero': 0, 'pause_boundary_count_zero': 67, 'terminal_boundary_count_zero': 102, 'clause_count_zero': 0, 'clause_span_count_zero': 0, 'special_signature_count': 0}
- target_validation: {'record_count': 66, 'nonverbal_only_count': 0, 'lexical_char_count_zero': 0, 'pause_boundary_count_zero': 9, 'terminal_boundary_count_zero': 9, 'clause_count_zero': 0, 'clause_span_count_zero': 0, 'special_signature_count': 0}
- target_special_eval: {'record_count': 8, 'nonverbal_only_count': 8, 'lexical_char_count_zero': 8, 'pause_boundary_count_zero': 8, 'terminal_boundary_count_zero': 8, 'clause_count_zero': 8, 'clause_span_count_zero': 8, 'special_signature_count': 8}

## Existing Pools
- micro_pause_none_singleton_strict: count=8, mean_special_distance=2.047626, min_special_distance=2.000764
- micro_pause_none_singleton_relaxed: count=10, mean_special_distance=2.183682, min_special_distance=2.000764
- micro_singleton_anypunct_relaxed: count=13, mean_special_distance=2.281462, min_special_distance=2.000764
- micro_singleton_anypunct_expansion: count=5, mean_special_distance=2.655601, min_special_distance=2.164731
- challenge_proxy_core: count=16, mean_special_distance=3.184231, min_special_distance=2.000764

## Heuristic Cohorts
- micro_pause_none_singleton_strict: count=8, mean_special_distance=2.047626, min_special_distance=2.000764
- micro_terminal_singleton_strict: count=1, mean_special_distance=2.164731, min_special_distance=2.164731
- micro_no_terminal_singleton_relaxed: count=10, mean_special_distance=2.183682, min_special_distance=2.000764
- micro_pause_none_singleton_relaxed: count=10, mean_special_distance=2.183682, min_special_distance=2.000764
- micro_singleton_anypunct_relaxed: count=13, mean_special_distance=2.281462, min_special_distance=2.000764

## Nearest Train Records
- target::chapter3_2_firefly_141: distance=2.000764, text=唔，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_3_firefly_250: distance=2.019547, text=二，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_3_firefly_249: distance=2.022272, text=一，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_3_firefly_124: distance=2.028578, text=欸，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_17_firefly_136: distance=2.050287, text=三，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_2_firefly_248: distance=2.059083, text=这，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_17_firefly_137: distance=2.093987, text=二，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_17_firefly_138: distance=2.106488, text=一，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_22_firefly_105: distance=2.164731, text=嗯。, lexical=1, pause=0, terminal=1, clause=1, clause_spans=1
- target::chapter3_4_firefly_125: distance=2.315928, text=唉，, lexical=1, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_29_firefly_107: distance=2.711547, text=请问，, lexical=2, pause=1, terminal=0, clause=1, clause_spans=1
- target::chapter3_2_firefly_235: distance=2.744266, text=天啊，, lexical=2, pause=1, terminal=0, clause=1, clause_spans=1

## Recommendation
- continue_training: True
- continue_current_d58_d59_line: False
- principle_change_required: True
- reason: No train-side record matches the target_special_eval special signature, and train-side clause-span support never drops to zero.
- recommended_proxy_cohort: micro_pause_none_singleton_strict
- recommended_proxy_cohort_count: 8
- recommended_supervision_direction: Pivot from clause-shape supervision to clause-free singleton sparse-frame supervision over the closest micro-utterance cohort.

## Notes
- special_signature is defined as nonverbal_only plus zero lexical, pause, terminal, clause, and clause-span support.
- special_distance is a simple normalized distance to the target_special_eval profile over duration and sparse-structure features.
- This report is diagnostic; it does not modify training sidecars or manifests.
