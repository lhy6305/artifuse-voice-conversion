# `C1.3` event-target bias / override 100 step 报告

## 目的
- 在 `C1.1 / C1.2` 已证明“弱边界提示可接入，但只靠独立 `weak_event` 辅助损失仍不够”之后，验证更贴近 `docs/25` 原意的接法：
  - target-side `event loss bias`
  - target-side 温和 `event target override`
- 当前对照对象：
  - `B1.1-A`
  - `C1.1`
  - `C1.2`
  - `C1.3`

先说人话：
- 这轮不再让弱边界提示单独开一门副课。
- 而是让它直接参与主课判卷，看这样会不会更有效。

## 执行概况
- 配置：
  - `configs/offline_mvp_train_c1_3_smallscale_100_seeded_shuffle.json`
- 实验：
  - `EXP-20260314-019-offline-mvp-c1-3-100step-calibration`
- 运行阶段：
  - `small_scale_validation`
- `dry-run`：
  - 已通过
- 总耗时：
  - `3.194774s`

配套产物：
- `reports/eval/offline_mvp_ablations_exp019/ablation_eval.json`
- `reports/eval/offline_mvp_checkpoint_series_exp019/checkpoint_series_eval.json`
- `reports/eval/offline_mvp_special_eval_exp019/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval_series_exp019/special_eval_series.json`

## 当前 `C1.3` 接入方式
### 与 `C1.1 / C1.2` 的核心差别
- `C1.1 / C1.2`
  - 主要依赖独立的 `loss_weak_event`
- `C1.3`
  - `weak_event = 0.0`
  - 改为在边界帧上直接影响：
    - `event loss` 权重
    - `event_target` 的局部 override

### 当前 override / bias 口径
- 仍然使用：
  - `B1.1-A` 的 `13` 维 target-side 文本统计
  - 同一份 `target_weak_event_hints.jsonl`
- 在 pause / terminal 边界窗口上：
  - 对 `event_target` 的 `delta` 相关维度做更强约束
  - 对 `fall` 相关维度做温和提升
  - 对对应帧的 `event loss` 做额外 bias

解释：
- 这一步不是继续调“副科分数”。
- 是把边界提示直接接到了主 event 判分逻辑里。

## step100 对照结果
### 1. 主验证集
- `B1.1-A`：
  - `target_loss_total = 2.680581`
- `C1.1`：
  - `target_loss_total = 2.716403`
- `C1.2`：
  - `target_loss_total = 2.699184`
- `C1.3`：
  - `target_loss_total = 2.683692`

### 2. 控制消融
- `zero_z_art.delta_target_loss_total`
  - `B1.1-A`: `1.330542`
  - `C1.1`: `1.350602`
  - `C1.2`: `1.337895`
  - `C1.3`: `1.329502`
- `zero_e_evt.delta_target_loss_total`
  - `B1.1-A`: `1.408664`
  - `C1.1`: `1.433922`
  - `C1.2`: `1.419051`
  - `C1.3`: `1.409978`

### 3. `target_special_eval`
- `delta_loss_total`
  - `B1.1-A`: `0.185337`
  - `C1.1`: `0.148666`
  - `C1.2`: `0.166072`
  - `C1.3`: `0.182364`
- `delta_loss_text_aux`
  - `B1.1-A`: `0.142376`
  - `C1.1`: `0.142649`
  - `C1.2`: `0.142518`
  - `C1.3`: `0.142412`

## 结果解释
- `C1.3` 相对 `C1.1 / C1.2` 的提升是明确的：
  - 主验证 loss 已经被拉回到几乎追平 `B1.1-A`
  - 说明当前 route-C 的问题，不只是“提示本身不够用”，也包括“接线方式不对”
- 但 `C1.3` 当前还没有给出“明确超过 `B1.1-A`”的证据：
  - 二者差距非常小
  - 更像是追平，而不是反超
- `checkpoint-series` 仍然显示：
  - 中期依旧会出现 `zero_e_evt` 回落甚至转负的区段
  - 到 `step90/100` 才重新回升

## 结论
- 当前可以确认：
  - `C1.3` 是 route-C 目前最合理的一版接入方式
  - 它比 `C1.1 / C1.2` 的独立辅助损失路线更对
- 当前也同样确认：
  - 它还不足以单独宣布 route-C 已经明显优于 `B1.1-A`

先说人话：
- 这次终于能看出“接法”确实很重要。
- 但新接法目前只是把成绩拉回到接近上一版，还没到能说“已经翻盘”的地步。

## 当前建议
- 不把 `C1.3` 直接升为默认训练方案。
- 把 `C1.3` 记为：
  - route-C 当前最优 baseline
  - 但尚未形成清晰领先
- 若继续 route-C，优先改：
  - 弱标签表达本身
  - 或 pause / terminal 的表达粒度
- 不建议继续主要投入在：
  - `C1.3` 周边的小步 boost / weight 调参
