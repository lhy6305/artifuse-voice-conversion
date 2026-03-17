# `C1.2` 100 step 轻权重回调报告

## 目的
- 在 `C1.1` 已证明“弱事件提示可接入，但主验证仍未赢过 `B1.1-A`”之后，验证把 `weak_event` 权重从 `0.2` 降到 `0.1` 是否能改善取舍。
- 当前对照对象：
  - `B1.1-A`
  - `C1.1`
  - `C1.2`

先说人话：
- 这轮是在试“别让这位新老师讲得太大声”，看能不能既保住提醒作用，又少干扰主课。

## 执行概况
- 配置：
  - `configs/offline_mvp_train_c1_2_smallscale_100_seeded_shuffle.json`
- 实验：
  - `EXP-20260314-018-offline-mvp-c1-2-100step-calibration`
- 运行阶段：
  - `small_scale_validation`
- 总耗时：
  - `2.930305s`

配套产物：
- `reports/eval/offline_mvp_ablations_exp018/ablation_eval.json`
- `reports/eval/offline_mvp_checkpoint_series_exp018/checkpoint_series_eval.json`
- `reports/eval/offline_mvp_special_eval_exp018/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval_series_exp018/special_eval_series.json`

## 当前 `C1.2` 与 `C1.1` 的唯一区别
- 仍然使用：
  - `B1.1-A` 的 `13` 维整句统计
  - 同一份 target-side `weak_event_hints`
- 唯一变更：
  - `weak_event = 0.1`
  - 相比 `C1.1` 的 `0.2` 更轻

## step100 对照结果
### 1. 主验证集
- `B1.1-A`：
  - `target_loss_total = 2.680581`
- `C1.1`：
  - `target_loss_total = 2.716403`
- `C1.2`：
  - `target_loss_total = 2.699184`

### 2. 控制消融
- `zero_z_art.delta_target_loss_total`
  - `B1.1-A`: `1.330542`
  - `C1.1`: `1.350602`
  - `C1.2`: `1.337895`
- `zero_e_evt.delta_target_loss_total`
  - `B1.1-A`: `1.408664`
  - `C1.1`: `1.433922`
  - `C1.2`: `1.419051`

### 3. `target_special_eval`
- `delta_loss_total`
  - `B1.1-A`: `0.185337`
  - `C1.1`: `0.148666`
  - `C1.2`: `0.166072`
- `delta_loss_text_aux`
  - `B1.1-A`: `0.142376`
  - `C1.1`: `0.142649`
  - `C1.2`: `0.142518`

## 与 `C1.1` 的直接比较
- `C1.2` 比 `C1.1` 的主验证 loss 略好：
  - `2.699184` vs `2.716403`
- 但它对 `z_art / e_evt` 的增强也同步略回落：
  - `zero_z_art`: `1.337895` vs `1.350602`
  - `zero_e_evt`: `1.419051` vs `1.433922`
- `special_eval` 基本与 `C1.1` 打平，没有形成新的明显改善。

## 结论
- `C1.2` 证明：
  - 把 `weak_event` 权重从 `0.2` 降到 `0.1`，不会把流程搞坏；
  - 并且能把 `C1.1` 略差的主验证 loss 拉回一点。
- 但当前同样明确：
  - `C1.2` 仍未超过 `B1.1-A`；
  - `C1.1 / C1.2` 两条曲线整体非常接近；
  - 仅靠 `weak_event` 在 `0.1` 到 `0.2` 之间的小范围调权，不足以形成明确突破。

先说人话：
- 调轻音量以后，课堂秩序稍微好一点了。
- 但课程本身没发生质变，所以现在不能继续把主要时间花在“再拧一点旋钮”上。

## 当前建议
- 不把 `C1.2` 升级为默认训练方案。
- 把 `C1.1 / C1.2` 一起归档为：
  - route-C 已证明可稳定接入的两版 baseline
  - 但当前都不足以取代 `B1.1-A`
- 若继续 route-C，下一步更合理的方向不是继续扫：
  - `weak_event = 0.05 / 0.15 / 0.25`
- 更合理的方向是优先改变：
  - 弱事件监督的注入方式
  - 或弱标签本身的表达形式
