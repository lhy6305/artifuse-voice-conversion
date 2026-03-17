# `B1.1-A` 100 step 实跑报告

## 目的
- 验证 `B1.1-A` 这版“更细的整句统计特征”是否比 `B1-offline-minimal` 更值得继续放大。
- 对照对象：
  - 无 `B1` 的 `step100`
  - `B1-offline-minimal` 的 `step100`

先说人话：
- 这轮是在检验“把教材写得更细一点”有没有带来真提升。
- 如果没有，就说明下一步该换老师类型，而不是继续打磨同一份教材。

## 执行概况
- 配置：
  - `configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json`
- 实验：
  - `EXP-20260314-016-offline-mvp-b1-1a-100step-calibration`
- 运行阶段：
  - `small_scale_validation`
- 总耗时：
  - `2.886782s`

配套产物：
- `reports/eval/offline_mvp_ablations_exp016/ablation_eval.json`
- `reports/eval/offline_mvp_checkpoint_series_exp016/checkpoint_series_eval.json`
- `reports/eval/offline_mvp_special_eval_exp016/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval_series_exp016/special_eval_series.json`

## 当前 `B1.1-A` 特征
相对 `B1-offline-minimal`，当前把 target-side `text_aux` 从 `7` 维扩到 `13` 维，新增的重点是：
- clause count
- average clause length
- short / long utterance flags
- multi-pause flag
- multi-terminal flag

解释：
- 这仍然是整句级统计，不是帧级弱对齐标签。

## step100 对照结果
### 1. 主验证集
- 无 `B1`：
  - `target_loss_total = 2.667123`
- `B1-offline-minimal`：
  - `target_loss_total = 2.676195`
- `B1.1-A`：
  - `target_loss_total = 2.680581`

### 2. 控制消融
- `zero_z_art.delta_target_loss_total`
  - 无 `B1`: `1.306952`
  - `B1`: `1.332663`
  - `B1.1-A`: `1.330542`
- `zero_e_evt.delta_target_loss_total`
  - 无 `B1`: `1.404717`
  - `B1`: `1.407506`
  - `B1.1-A`: `1.408664`

### 3. `target_special_eval`
- `delta_loss_total`
  - 无 `B1`: `0.263015`
  - `B1`: `0.216202`
  - `B1.1-A`: `0.185337`
- `delta_loss_text_aux`
  - 无 `B1`: `0.537801`
  - `B1`: `0.310898`
  - `B1.1-A`: `0.142376`

## 结论
- `B1.1-A` 没有把训练搞坏。
- 但它在主验证集上没有形成明确增益，甚至比 `B1` 略弱一点。
- 它的主要正面变化体现在 `target_special_eval` 的 `text_aux` 压力更小。
- 到 `step100`，`B1.1-A` 对 `z_art / e_evt` 的帮助与 `B1` 基本重合，没有出现新的明显提升。

先说人话：
- 这说明“教材细化”这一步不是白做，但也没有强到足以单独救场。
- 所以按既定路线，当前可以判定：`A` 还不够，需要继续进 `C`。

## 当前建议
- 不把 `B1.1-A` 升级为默认训练方案。
- 保留其结果作为 route-B 文本监督细化的已验证分支。
- 继续推进 `C1`：
  - target-side 弱对齐事件提示 sidecar
  - 为后续更贴近 `e_evt` 的监督接入做准备
