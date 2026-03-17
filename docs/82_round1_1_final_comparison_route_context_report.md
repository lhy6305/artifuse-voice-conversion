# `round1.1 / final comparison with route context` 报告

## 背景
- selector 已经接进 experiment 立项。
- 当前还缺一个“联合 final comparison”入口:
  - 多个实验一起看时，能不能直接带上当前 route anchor
  - 并把其他实验相对该 anchor 的代价/收益直接列出来

## 本轮产物
- 新增正式命令:
  - `compare-offline-mvp-final-experiments`
- 支持:
  - 读取多个 experiment metrics
  - 可选读取 `--route-selection`
  - 在 comparison 输出里标出当前 route anchor
  - 直接写出各实验相对 route anchor 的 final delta

## 实跑验证
- 输入实验:
  - `D22`
  - `D26`
  - `D29`
- route context:
  - `default_minimax`
- 输出:
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d26_d29_default_minimax/final_experiment_comparison.md`

## 核心结果
- 当前 route anchor 已被正式标注为:
  - `D22`
- `D29` 相对 `D22`:
  - validation 更好 `-0.047019`
  - 但 special 更差 `+0.031768`
  - `e_evt` 更差 `-0.320554`
  - `z_art` 更差 `-0.074009`
- `D26` 相对 `D22`:
  - validation 更差 `+0.079704`
  - 但 special 更好 `-0.022107`
  - `e_evt` 略差 `-0.026385`
  - `z_art` 更好 `+0.021323`

这一步的价值在于:
- 以后如果 route 已经确定，
- 联合 comparison 不必再手工解释“某实验赢了什么、输了什么”，
- 可以直接相对 route anchor 读差值。

## 当前结论
1. 三锚流程现在已经接到联合比较入口。
2. 后续如果做 final comparison，默认应优先带上 `--route-selection`。
3. 不再建议只输出“按 validation 排序”的裸 comparison，而不带 route context。

## 下一步建议
1. 若继续推进流程层集成，更值得把这类 comparison 输出接进后续实验复盘或阶段汇总报告。
2. 暂不优先再扩新的 comparison 变体；当前 route-context final comparison 已足够支持主线决策。
