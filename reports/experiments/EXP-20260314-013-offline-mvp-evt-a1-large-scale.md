# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-013-offline-mvp-evt-a1-large-scale
- date: 2026-03-14T18:53:32
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json

## Data
- target_manifest:
- source_manifest:
- data_filters:
- known_exclusions:

## Objective
- baseline_or_change:
- hypothesis:

## Model Scope
- offline_or_streaming:
- uses_text_in_training:
- uses_text_in_runtime:
- r_res_enabled:

## Checks
- data_integrity:
- z_art_ablation:
- e_evt_ablation:
- r_res_ablation:
- latency:

## Results
- summary: completed
- failures:
  - A1 当前参数组合未通过既定通过标准：
    - final validation `loss_total` 明显差于 `EXP-011`
    - `zero_e_evt` 提升有限
    - `z_art` late-stage 贡献被压弱
- follow_up: detailed report -> F:/proj_dev/tmp/workdir4/docs/18_e_evt_constraint_a1_run_report.md

## Run Summary
- mode:
  - large_scale
- sampler:
  - seeded_shuffle
- seed:
  - 20260314
- timing:
  - started_at: 2026-03-14T18:59:21
  - ended_at: 2026-03-14T18:59:32
  - duration_sec: 10.793655

## Main Results
- best_validation:
  - step125
  - loss_total: 5.266743
- final_validation:
  - step500
  - loss_total: 5.714126
- final_ablation:
  - zero_z_art.delta_target_loss_total: 0.949323
  - zero_e_evt.delta_target_loss_total: 0.378181
- final_special_eval:
  - regular_validation.loss_total: 1.903484
  - target_special_eval.loss_total: 2.192053
  - delta_loss_total: 0.288569

## Interpretation
- `A1` 确实让 `e_evt` 后期依赖度比 `EXP-011` 略高，但没有达到原草案建议门槛。
- 更关键的是，整体验证损失明显差于 `EXP-011`，同时 `z_art` 的 late-stage 贡献被压弱。
- 当前结论：
  - 这组 `A1` 参数不适合作为默认训练配置。
