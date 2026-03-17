# Experiment Record

## Metadata
- experiment_id: EXP-20260314-004-offline-mvp-timed-smallscale
- date: 2026-03-14T15:31:26
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: round1 主流目标样本 624 条；源切分样本 537 条；目标固定验证切片 8 条；源固定验证切片 8 条
- known_exclusions: 目标异常格式 47 条已隔离；人工复核排除 `peak_005`、`peak_008`、`peak_014`、`peak_015`

## Objective
- baseline_or_change: 为多步训练补时间落盘，验证开始时间、结束时间、总耗时和 step 耗时进入训练产物
- hypothesis: 小规模训练应在不改变当前模型结构的前提下，把 timing 信息同步写入 train_plan、step log 和 experiment metrics

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
- latency: timing fields recorded in small-scale validation only

## Results
- summary: training_run_completed
- failures:
- follow_up: 继续补标准输出时间打印和大规模训练门禁；metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-004-offline-mvp-timed-smallscale.metrics.json

## Observed Metrics
- run timing: 2026-03-14T15:37:51 -> 2026-03-14T15:37:52
- duration_sec: 0.88298
- latest_train.loss_total: 53.65851593017578
- latest_validation.loss_total: 50.49259948730469
- step durations: 0.074071 / 0.020739 / 0.015739
