# offline MVP 控制消融报告

## 背景
- 本轮消融基于正式 split `hybrid_stratified_blocked`。
- 使用的 checkpoint 为：
  - `reports/training/offline_mvp/checkpoints/EXP-20260314-007-offline-mvp-ablation-ready.step3.pt`
- 评估命令为：
  - `.\python.exe manage.py evaluate-offline-mvp-ablations --experiment-metrics reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json`

## 当前实现边界
- 本轮只评估 `none / zero_z_art / zero_e_evt` 三种模式。
- 消融是在控制融合前直接置零，不涉及 `r_res`。
- 评估集只使用正式 hybrid validation split：
  - 目标 `62` 条
  - 源 `54` 条
- 当前仍是小规模训练后的早期 checkpoint，不代表最终模型结论。

## 结果摘要
- `EXP-20260314-007-offline-mvp-ablation-ready`
  - `zero_z_art.delta_target_loss_total = -0.008774`
  - `zero_z_art.delta_source_loss_total = -0.013562`
  - `zero_e_evt.delta_target_loss_total = 0.1936`
  - `zero_e_evt.delta_source_loss_total = 0.254943`
- `EXP-20260314-008-offline-mvp-longer-smallscale`
  - `zero_z_art.delta_target_loss_total = 0.079066`
  - `zero_z_art.delta_source_loss_total = 0.114091`
  - `zero_e_evt.delta_target_loss_total = 1.015739`
  - `zero_e_evt.delta_source_loss_total = 1.504668`

## 当前解释
- 当前结果已经证明：
  - `e_evt` 不再是名义控制量。
  - 在 3 step 和 20 step 两个 checkpoint 上，去掉 `e_evt` 都会明显拉高目标侧和源侧验证损失，并带来更大的输出偏移。
- `z_art` 当前状态是：
  - 在 3 step checkpoint 上，去掉后主要体现为输出变化，loss 退化不明显。
  - 在 20 step checkpoint 上，已经开始体现稳定的正向 loss 退化和更大的输出偏移。
- 当前更合理的解释是：
  - `z_art` 的监督贡献需要比 `e_evt` 更晚显现。
  - 当前已经不应再把 `z_art` 视为“可能没有真正被模型使用”。

## 风险与限制
- 当前 checkpoint 来自新控制融合结构，不能与旧实验 checkpoint 混用。
- 当前训练步数极少，消融结论只适合作为“控制链已接通”的阶段性证据。
- `target_special_eval` 仍未纳入模型级消融报告，因为它是 punctuation-only challenge slice。

## 下一步
1. 在相同 split 上继续做多 checkpoint 对比，观察 `z_art / e_evt` 敏感度是否继续扩大。
2. 继续把 `target_special_eval` 与常规 validation 分开汇报，不合并平均。
3. 后续如引入 `r_res`，必须新增 `zero_r_res` 或等价约束检查。

## 2026-03-14 large-scale 补充结果
- 实验：
  - `EXP-20260314-011-offline-mvp-large-scale-500`
- checkpoint-series 新观察：
  - `z_art` 在后期继续增强：
    - `step25 = 0.25163`
    - `step250 = 0.642675`
    - `step500 = 1.4106`
  - `e_evt` 则呈现“早期强、后期回落但仍为正”的形态：
    - `step25 = 1.79018`
    - `step250 = 0.333262`
    - `step500 = 0.286237`
- 当前补充解释：
  - large-scale 训练后，`z_art` 已成为更稳定、更强的关键控制量。
  - `e_evt` 没有失效，但当前后期依赖度明显低于 early checkpoint，需要单独调查是否被其他路径部分替代。
