# 训练采样与 checkpoint 系列报告

## 目的
- 记录离线 MVP 训练入口新增的可复现采样能力：
  - 固定 `seed`
  - 可选 `shuffle_train_records`
- 记录首轮 seeded-shuffle 小规模训练与多 checkpoint 消融趋势。

## 当前实现
- 训练配置新增字段：
  - `training.seed`
  - `training.shuffle_train_records`
- 训练计划新增字段：
  - `reproducibility.seed`
  - `reproducibility.shuffle_train_records`
  - `reproducibility.target_sampler_seed`
  - `reproducibility.source_sampler_seed`
  - `training_run.sampler_mode`
- 新命令：
  - `.\python.exe manage.py evaluate-offline-mvp-checkpoint-series --config configs/offline_mvp_train_smallscale_seeded_shuffle.json --experiment-metrics reports/experiments/EXP-20260314-009-offline-mvp-seeded-shuffle.metrics.json`

## 当前实验
- 实验：`EXP-20260314-009-offline-mvp-seeded-shuffle`
- 配置：`configs/offline_mvp_train_smallscale_seeded_shuffle.json`
- 关键设置：
  - `seed = 20260314`
  - `shuffle_train_records = true`
  - `num_steps = 20`

## 当前结果
- validation `loss_total`
  - step 5: `49.157608`
  - step 10: `45.160576`
  - step 15: `40.778854`
  - step 20: `35.849232`

## checkpoint-series 趋势
- `zero_z_art.delta_target_loss_total`
  - step 5: `0.048894`
  - step 10: `0.096982`
  - step 15: `0.150881`
  - step 20: `0.207483`
- `zero_e_evt.delta_target_loss_total`
  - step 5: `1.053401`
  - step 10: `1.295615`
  - step 15: `1.530421`
  - step 20: `1.737457`
- `zero_z_art.delta_source_loss_total`
  - step 5: `0.069221`
  - step 10: `0.132976`
  - step 15: `0.209152`
  - step 20: `0.299056`
- `zero_e_evt.delta_source_loss_total`
  - step 5: `1.368172`
  - step 10: `1.709776`
  - step 15: `2.074558`
  - step 20: `2.455875`

## 当前解释
- 训练随机化和固定 seed 已经跑通，且产物可复现。
- 在当前 seeded-shuffle 实验中：
  - `z_art` 的消融退化随 checkpoint 单调增大。
  - `e_evt` 的消融退化也随 checkpoint 单调增大，且幅度持续明显高于 `z_art`。
- 这说明当前 checkpoint-series 命令已经能稳定观察控制量随训练推进被“越来越用上”的过程。

## 当前边界
- 当前报告证明的是：
  - 训练采样能力与趋势分析能力已经具备。
- 当前报告还不能证明的是：
  - shuffled 训练一定优于 sequential 训练。
- 是否把 seeded-shuffle 设为默认训练方案，仍需结合对比报告交由用户判断。
