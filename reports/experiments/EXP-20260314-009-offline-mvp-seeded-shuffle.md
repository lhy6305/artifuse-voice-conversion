# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-009-offline-mvp-seeded-shuffle
- date: 2026-03-14T17:18:18
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_smallscale_seeded_shuffle.json

## Data
- target_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/target_train.jsonl
- source_manifest: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests/source_train.jsonl
- data_filters: hybrid_stratified_blocked split; target 554 train / 62 val / 8 special_eval; source 483 train / 54 val
- known_exclusions: target_special_eval 不进入常规 validation；no_text_voice 子集不含完整音节

## Objective
- baseline_or_change: 引入固定 seed 与 shuffle_train_records，并用多 checkpoint 消融检查控制量敏感度趋势
- hypothesis: 若训练采样能力工作正常，checkpoint-series 中 z_art / e_evt 的退化应随 step 上升而逐步增强

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed on round1 formal split
- z_art_ablation: completed across checkpoint series; target/source loss deltas rise monotonically
- e_evt_ablation: completed across checkpoint series; stronger monotonic degradation than z_art
- r_res_ablation: not applicable in current no-residual MVP
- latency: not started

## Results
- summary: seeded-shuffle small-scale training and checkpoint-series ablation completed
- failures: none; current question is default-policy choice rather than implementation blockage
- follow_up: compare seeded-shuffle with sequential runs and hand decision back to user before changing defaults; metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-009-offline-mvp-seeded-shuffle.metrics.json
