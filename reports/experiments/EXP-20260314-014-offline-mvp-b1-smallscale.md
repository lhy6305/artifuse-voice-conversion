# Experiment Record

## Metadata
- experiment_id: EXP-20260314-014-offline-mvp-b1-smallscale
- date: 2026-03-14T19:50:35
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_seeded_shuffle.json

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
- follow_up: report -> F:/proj_dev/tmp/workdir4/docs/21_b1_offline_minimal_report.md

## Main Results
- training:
  - completed_steps: 20
  - duration_sec: 1.28162
  - target_text_feature_version: b1_punct_v1
  - target_batch_text_feature_shape: [4, 7]
- validation:
  - final_loss_total: 35.865547
  - final_target_loss_text_aux: 0.181097
- ablation:
  - zero_z_art.delta_target_loss_total: 0.207014
  - zero_e_evt.delta_target_loss_total: 1.733871

## Interpretation
- `B1-offline-minimal` 已成功把目标侧更丰富的文本/标点监督接入训练，而源侧继续保持纯音频监督。
- 当前小规模结果显示主流程稳定，且控制消融敏感度更强。
- 但总体验证 loss 仍与旧 seeded-shuffle 小规模基线基本打平，尚不足以下结论说 `B1` 已明显更优。
