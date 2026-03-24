# B1 Supervision Inventory

## Summary
- This inventory records which supervision sources are already available offline in round1.
- It is designed to support route B without assuming any network downloads or new third-party packages.

先说人话：
- 目标侧现在已经有可直接用的文本和标点停顿线索。
- 源侧现在没有文本，所以暂时不能走同等级的文本监督。
- `target_special_eval` 仍然只是非完整发声 challenge slice，不能拿来当正常 lexical supervision。

## Target Summary
- record_count: `666`
- split_counts: `{'target_special_eval': 8, 'target_train': 592, 'target_validation': 66}`
- nonverbal_only_count: `8`
- records_with_pause_hints: `666`
- avg_lexical_chars_per_record: `21.295796`
- avg_audio_duration_sec: `6.098379`
- avg_lexical_chars_per_sec: `3.492042`
- punctuation_category_counts: `{'pause_colon': 2, 'pause_comma': 1299, 'pause_enumeration': 36, 'terminal_exclamation': 77, 'terminal_period': 488, 'terminal_question': 178}`

## Source Summary
- record_count: `537`
- split_counts: `{'source_train': 483, 'source_validation': 54}`
- records_with_text: `0`
- avg_audio_duration_sec: `1.220391`

## Immediate Implications
- Route B can start from target-side punctuation and text-aware supervision immediately.
- Route B cannot yet assume source-side phone or manner supervision in round1.
- The safest first upgrade is to separate future lexical/event labels from the current heuristic frame targets instead of replacing training code in one jump.

## Artifacts
- target_inventory_path: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/b1_supervision/target_supervision_inventory.jsonl`
- source_inventory_path: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/b1_supervision/source_supervision_inventory.jsonl`

## Notes
- This inventory intentionally stays offline and uses only currently materialized manifests.
- Target-side text supervision is available now; source-side text supervision is not available in round1.
- target_special_eval remains a nonverbal challenge slice and should not be treated as normal lexical supervision.
- Phone/manner/place labels are not yet available in the workspace and remain future label slots.
