# Experiment Record

## Metadata
- experiment_id: EXP-20260314-002-offline-mvp-step1
- date: 2026-03-14T14:48:14
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: round1 主流目标样本 624 条；源切分样本 537 条；源边界静区阈值 -38 dBFS 且连续 500 ms
- known_exclusions: 目标异常格式 47 条已隔离；人工复核排除 `peak_005`、`peak_008`、`peak_014`、`peak_015`

## Objective
- baseline_or_change: 从真实前向 dry-run 下沉到真实单步训练验证
- hypothesis: 在 `r_res` 关闭且运行时不使用文本的前提下，当前无残差 scaffold 至少应能跑通一次前向、损失、反向传播和 checkpoint 写盘

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
- summary: single_step_completed
- failures:
- follow_up: 扩展为多步训练循环，并补最小验证集评估；metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-002-offline-mvp-step1.metrics.json

## Observed Metrics
- loss_total: 51.73610305786133
- target.loss_total: 15.529247283935547
- source.loss_total: 36.20685577392578
- grad_norm: 28.910484313964844
- checkpoint: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-002-offline-mvp-step1.step1.pt
