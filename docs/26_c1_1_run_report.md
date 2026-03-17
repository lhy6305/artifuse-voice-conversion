# `C1.1` 100 step 实跑报告

## 目的
- 验证 `C1` 生成的 target-side 弱事件提示，是否能以额外 `weak_event` 损失的形式，给 `e_evt` 路径带来比 `B1.1-A` 更明确的增益。
- 当前对照对象：
  - `B1.1-A`
  - 当前 `C1.1`

先说人话：
- 这轮是在测试“告诉模型哪里像停顿、哪里像句末”这位新老师，能不能比只看整句统计更有用。

## 执行概况
- 配置：
  - `configs/offline_mvp_train_c1_1_smallscale_100_seeded_shuffle.json`
- 实验：
  - `EXP-20260314-017-offline-mvp-c1-1-100step-calibration`
- 运行阶段：
  - `small_scale_validation`
- 总耗时：
  - `2.906128s`

配套产物：
- `reports/eval/offline_mvp_ablations_exp017/ablation_eval.json`
- `reports/eval/offline_mvp_checkpoint_series_exp017/checkpoint_series_eval.json`
- `reports/eval/offline_mvp_special_eval_exp017/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval_series_exp017/special_eval_series.json`

## 当前 `C1.1` 接入方式
- target-side 继续保留 `B1.1-A` 的 `13` 维整句文本统计特征。
- 额外接入 target-side `weak_event_hints`：
  - `pause_boundaries`
  - `terminal_boundaries`
- 训练时新增：
  - `loss_weak_event`
  - `weak_event = 0.2`

解释：
- 这一步仍不是 forced alignment。
- 它是在已有启发式 `event_target` 之外，再给模型一个“这些位置更像边界”的弱提醒。

## step100 对照结果
### 1. 主验证集
- `B1.1-A`：
  - `target_loss_total = 2.680581`
- `C1.1`：
  - `target_loss_total = 2.716403`

### 2. 控制消融
- `zero_z_art.delta_target_loss_total`
  - `B1.1-A`: `1.330542`
  - `C1.1`: `1.350602`
- `zero_e_evt.delta_target_loss_total`
  - `B1.1-A`: `1.408664`
  - `C1.1`: `1.433922`

### 3. `target_special_eval`
- `delta_loss_total`
  - `B1.1-A`: `0.185337`
  - `C1.1`: `0.148666`
- `delta_loss_text_aux`
  - `B1.1-A`: `0.142376`
  - `C1.1`: `0.142649`

## checkpoint-series 观察
- `zero_e_evt.delta_target_loss_total`
  - `step10 = 1.293261`
  - `step20 = 1.733756`
  - `step50 = -0.520147`
  - `step100 = 1.433922`
- `zero_z_art.delta_target_loss_total`
  - `step50 = -0.173357`
  - `step80 = 0.929486`
  - `step90 = -0.156280`
  - `step100 = 1.350602`

解释：
- 当前 `C1.1` 不是一路平滑变好。
- 中期仍会出现明显回落，到后期才重新把 `e_evt / z_art` 依赖拉回来。

## 结论
- `C1.1` 已证明：
  - 弱事件提示可以稳定接入当前 offline MVP；
  - 到 `step100`，`z_art / e_evt` 敏感度比 `B1.1-A` 略强。
- 但当前也明确：
  - 它没有把主验证集拉到比 `B1.1-A` 更好；
  - 因此不能直接升为默认训练路线。

先说人话：
- 这位新老师不是坏老师。
- 但第一版教法还没强到能赢过上一版，所以还需要再试一个更轻的接法。

## 当前建议
- 不把 `C1.1` 升级为默认方案。
- 继续保留 `C1.1` 结果，作为 route-C 首个“已验证可接入”的版本。
- 下一步先做：
  - `C1.2`
  - 仅把 `weak_event` 权重从 `0.2` 降到 `0.1`
  - 观察是否能保住控制链增益，同时把主验证 loss 拉回去
