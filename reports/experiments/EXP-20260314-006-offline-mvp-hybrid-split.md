# Experiment Record

## Metadata
- experiment_id: EXP-20260314-006-offline-mvp-hybrid-split
- date: 2026-03-14T16:11:13
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: 正式 split `hybrid_stratified_blocked`；目标 `554 train / 62 val / 8 special_eval`；源 `483 train / 54 val`
- known_exclusions: 目标异常格式 47 条已隔离；`no_text_voice` 8 条已从常规验证集中拆出为 special_eval

## Objective
- baseline_or_change: 将用户确认的 `hybrid_stratified_blocked` 下沉为正式 split，并验证训练入口切换成功
- hypothesis: 训练入口应优先读取 `data.split_dir`，并使用正式 split 的训练/验证计数，而不是旧的尾部切片

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed
- z_art_ablation: pending
- e_evt_ablation: pending
- r_res_ablation: not_applicable_current_stage
- latency: small-scale timing recorded on formal split

## Results
- summary: training_run_completed
- failures:
- follow_up: 为 `target_special_eval` 增加独立评估入口，并继续补消融命令；metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-006-offline-mvp-hybrid-split.metrics.json

## Observed Metrics
- split_strategy: materialized_split
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- split_counts: target `554 / 62 / 8` ; source `483 / 54`
- run timing: 2026-03-14T16:15:21 -> 2026-03-14T16:15:22
- duration_sec: 0.714648
- latest_train.loss_total: 55.63977813720703
- latest_validation.loss_total: 51.20595169067383

## Special Eval
- report: F:/proj_dev/tmp/workdir4/reports/eval/round1_special_eval/special_eval.json
- overall_ok: True
- group_counts: `{"no_text_voice": 8}`
- punctuation_only_count: 8
- interpretation: challenge-only stress slice, not regular content validation
