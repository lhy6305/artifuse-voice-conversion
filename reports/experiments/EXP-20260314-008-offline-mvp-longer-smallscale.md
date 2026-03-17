# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-008-offline-mvp-longer-smallscale
- date: 2026-03-14T17:11:12
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_smallscale_longer.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: hybrid_stratified_blocked split; target 554 train / 62 val / 8 special_eval; source 483 train / 54 val
- known_exclusions: target_special_eval 不进入常规 validation；no_text_voice 子集不含完整音节

## Objective
- baseline_or_change: 在相同结构上把小规模训练从 3 step 拉长到 20 step，并复查 z_art / e_evt 消融敏感度
- hypothesis: 更晚 checkpoint 上，z_art 应从“只改变输出”逐步转向“开始拉高 loss”；e_evt 退化应继续扩大

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed on round1 formal split
- z_art_ablation: completed; now shows positive loss degradation on the 20-step checkpoint
- e_evt_ablation: completed; degradation remains clearly stronger than z_art
- r_res_ablation: not applicable in current no-residual MVP
- target_special_eval_model: completed; challenge slice remains nonverbal and should stay isolated from normal validation
- latency: not started

## Results
- summary: 20-step small-scale training, ablation reevaluation, and model-level target_special_eval completed
- failures: none during this run; conclusions remain limited by small-scale training scope
- follow_up: compare multiple checkpoints and consider training-loop randomization before any larger-scale run; metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-008-offline-mvp-longer-smallscale.metrics.json
