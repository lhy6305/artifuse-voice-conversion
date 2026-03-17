# Experiment Record

## Metadata
- experiment_id: EXP-20260314-003-offline-mvp-multistep
- date: 2026-03-14T14:56:11
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: round1 主流目标样本 624 条；源切分样本 537 条；目标固定验证切片 8 条；源固定验证切片 8 条
- known_exclusions: 目标异常格式 47 条已隔离；人工复核排除 `peak_005`、`peak_008`、`peak_014`、`peak_015`

## Objective
- baseline_or_change: 从单步训练验证扩展到最小多步训练与周期验证
- hypothesis: 当前无残差 scaffold 应能在固定切片验证下跑通 3 step 训练，并稳定落盘训练历史、验证历史和多份 checkpoint

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
- latency: pending

## Results
- summary: training_run_completed
- failures:
- follow_up: 将固定切片验证升级为正式评估切分，并开始接入 `z_art / e_evt` 消融；metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-003-offline-mvp-multistep.metrics.json

## Observed Metrics
- num_steps: 3
- latest_train.loss_total: 55.10185241699219
- latest_validation.loss_total: 52.068878173828125
- validation_history: 52.80699157714844 -> 52.435943603515625 -> 52.068878173828125
- checkpoint_final: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-003-offline-mvp-multistep.step3.pt
