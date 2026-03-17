# `C1.4` boundary pre/post target 显式化 100 step 报告

## 目的
- 在 `C1.3` 已证明“把弱边界提示并入主 `event loss / event_target` 流程比独立辅助损失更对”之后，继续验证更细一层的 boundary pre/post target 显式化是否能把 route-C 再往前推一点。
- 当前对照对象：
  - `B1.1-A`
  - `C1.3`
  - `C1.4`

先说人话：
- 这轮不是再换老师。
- 是在 `C1.3` 这位老师已经进主考卷之后，继续把“边界前一帧、后一帧该怎么判”写得更细，看成绩会不会再抬一点。

## 执行概况
- 配置：
  - `configs/offline_mvp_train_c1_4_smallscale_100_seeded_shuffle.json`
- 实验：
  - `EXP-20260314-020-offline-mvp-c1-4-100step-calibration`
- 运行阶段：
  - `small_scale_validation`
- `dry-run`：
  - 已通过
- 总耗时：
  - `3.243964s`

配套产物：
- `reports/eval/offline_mvp_ablations_exp020/ablation_eval.json`
- `reports/eval/offline_mvp_checkpoint_series_exp020/checkpoint_series_eval.json`
- `reports/eval/offline_mvp_special_eval_exp020/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval_series_exp020/special_eval_series.json`

## 当前 `C1.4` 观察口径
- 从当前配置与产物看，`C1.4` 重点仍属于 route-C 的同一条主线：
  - target-side weak boundary hints
  - event loss bias
  - 温和 event target override
- 相比 `C1.3`，本轮更像是在 boundary 前后帧目标口径上做显式化和细抠，而不是切换成新监督来源。

解释：
- 这不是“换教材”。
- 更像是把同一本教材里的评分细则写得更明确一点。

## step100 对照结果
### 1. 主验证集
- `B1.1-A`：
  - `target_loss_total = 2.680581`
- `C1.3`：
  - `target_loss_total = 2.683692`
- `C1.4`：
  - `target_loss_total = 2.681003`

### 2. 控制消融
- `zero_z_art.delta_target_loss_total`
  - `B1.1-A`: `1.330542`
  - `C1.3`: `1.329502`
  - `C1.4`: `1.329629`
- `zero_e_evt.delta_target_loss_total`
  - `B1.1-A`: `1.408664`
  - `C1.3`: `1.409978`
  - `C1.4`: `1.410986`

### 3. `target_special_eval`
- `delta_loss_total`
  - `B1.1-A`: `0.185337`
  - `C1.3`: `0.182364`
  - `C1.4`: `0.181996`
- `delta_loss_text_aux`
  - `B1.1-A`: `0.142376`
  - `C1.3`: `0.142412`
  - `C1.4`: `0.142410`

## checkpoint-series 观察
- `C1.4` 到 `step50` 仍出现明显中期回落：
  - `zero_z_art.delta_target_loss_total = -0.173311`
  - `zero_e_evt.delta_target_loss_total = -0.519136`
- 到 `step80/90/100` 才重新回到较强依赖：
  - `step80 zero_e_evt.delta_target_loss_total = 1.469595`
  - `step90 zero_e_evt.delta_target_loss_total = 1.742136`
  - `step100 zero_e_evt.delta_target_loss_total = 1.410986`

这说明：
- `C1.4` 并没有真正改写 route-C 的中期行为。
- 它更多只是把最终 checkpoint 稍微磨顺了一点。

## 结果解释
- `C1.4` 相对 `C1.3` 的改善是存在的，但量级很小：
  - 主验证提升约 `0.002689`
  - special-eval `delta_loss_total` 改善约 `0.000368`
- 相比 `B1.1-A`，`C1.4` 当前仍只能说“几乎打平”：
  - 主验证差距只有 `0.000422`
  - 控制消融和 special-eval 也都在非常接近的范围内
- 因此当前更稳妥的结论是：
  - `C1.4` 可以记为 route-C 的最新参考版本；
  - 但它还不能被解释成“route-C 已经明确胜出”。

先说人话：
- 这轮不是没进步。
- 但进步更像从 `98.8` 调到 `98.9`，不是从 `98` 跳到 `102`。

## 结论
- 当前可以确认：
  - `C1.4` 比 `C1.3` 略好；
  - route-C 到现在为止最合理的参考点可更新为 `C1.4`。
- 当前也同样确认：
  - `C1.4` 仍未给出足以明确超过 `B1.1-A` 的证据；
  - route-C 的中期依赖回落问题仍在。

## 当前建议
- 不把 `C1.4` 直接升为默认训练方案。
- 当前不建议继续把主要时间投入到：
  - 当前同一份 sidecar 上的 boundary target 常数微调
  - `C1.3 / C1.4` 周边的小步 tweak
- 若继续 route-C，优先考虑：
  - richer boundary label expression
  - 更明确的 pause / terminal / punctuation-type 区分
  - 或补更贴近运行时的非文本评估指标，先确认当前差异到底是不是“看得到但量太小”
