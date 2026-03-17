# Experiment Record

## Metadata
- experiment_id: EXP-20260314-005-offline-mvp-timed-stdout
- date: 2026-03-14T15:38:36
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: round1 主流目标样本 624 条；源切分样本 537 条；目标固定验证切片 8 条；源固定验证切片 8 条
- known_exclusions: 目标异常格式 47 条已隔离；人工复核排除 `peak_005`、`peak_008`、`peak_014`、`peak_015`

## Objective
- baseline_or_change: 为小规模训练补标准输出时间打印与大规模前置门禁后的实跑验证
- hypothesis: 当前小规模训练应在保留 timing 落盘的同时，向标准输出打印开始时间、每 step 时间和结束时间

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
- latency: small-scale timing printed and recorded

## Results
- summary: training_run_completed
- failures:
- follow_up: 进入正式拆分方案讨论前，不做大规模训练耗时承诺；metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-005-offline-mvp-timed-stdout.metrics.json

## Observed Metrics
- run_stage: small_scale_validation
- stdout timing printed: yes
- run timing: 2026-03-14T15:41:57 -> 2026-03-14T15:41:58
- duration_sec: 0.889291
- latest_train.loss_total: 54.736595153808594
- latest_validation.loss_total: 51.59565353393555
