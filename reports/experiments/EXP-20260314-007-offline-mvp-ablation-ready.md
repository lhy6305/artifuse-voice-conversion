# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-007-offline-mvp-ablation-ready
- date: 2026-03-14T16:40:32
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: hybrid_stratified_blocked split; target 554 train / 62 val / 8 special_eval; source 483 train / 54 val
- known_exclusions: target_special_eval 不进入常规 validation；旧控制融合前 checkpoint 不兼容本实验

## Objective
- baseline_or_change: 引入真实控制融合后，重新生成兼容 checkpoint，并执行首轮 z_art / e_evt 消融
- hypothesis: zero_e_evt 和 zero_z_art 至少应对输出造成可见偏移；其中 e_evt 在当前早期训练阶段更可能先体现损失退化

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed on round1 formal split
- z_art_ablation: completed; output shift observed, loss degradation not yet obvious
- e_evt_ablation: completed; validation loss and output shift both degraded
- r_res_ablation: not applicable in current no-residual MVP
- target_special_eval_model: completed; total loss lower than regular validation but text_aux stress much higher
- latency: not started

## Results
- summary: small-scale training and first ablation evaluation completed
- failures: old checkpoints cannot be reused after control-fusion architecture change
- follow_up: extend small-scale training and recheck z_art sensitivity plus target_special_eval on later checkpoints; metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json
