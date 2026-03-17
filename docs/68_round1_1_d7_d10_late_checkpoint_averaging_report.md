# `round1.1 / D7+D10 / late checkpoint averaging probe` 报告

## 目的
- 在 `gate replay` 已确认:
  - 纯 checkpoint 选择只能在旧 tradeoff 之间切换
- 在 `D13 / D14` 已确认:
  - 全局 late LR decay 会把 explicit-control 线拖进 under-converged final
- 转向一个不需要重训的新 phase 机制:
  - 对现有 late checkpoints 做 weight averaging
- 核心问题是:
  - `step90` 与 `step100` 的互补性，是否能通过权重平均转成更好的 final balance

## 实验信息
### averaged-D7
- source checkpoints:
  - `D7 step90`
  - `D7 step100`
- averaged checkpoint:
  - `reports/eval/offline_mvp_checkpoint_average_d7_step90_100/d7_step90_100_avg.pt`

### averaged-D10
- source checkpoints:
  - `D10 step90`
  - `D10 step100`
- averaged checkpoint:
  - `reports/eval/offline_mvp_checkpoint_average_d10_step90_100/d10_step90_100_avg.pt`

## 工程补充
- 已新增正式命令:
  - `average-offline-mvp-checkpoints`
- 能力范围:
  - 对多个同构 checkpoint 的 `model_state_dict` 做均匀平均
  - 输出可直接交给现有 special_eval / ablation 命令使用

## 关键结果
### 1. averaging 确实能做出“中间态”，但没有做出新解
- `D7 step90+100 avg`
  - `target_validation.loss_total = 2.978639`
  - `target_special_eval.delta_loss_total = -0.098031`
  - `zero_e_evt.delta_target_loss_total = 3.035429`
  - `zero_z_art.delta_target_loss_total = 0.569171`
- `D10 step90+100 avg`
  - `target_validation.loss_total = 3.030039`
  - `target_special_eval.delta_loss_total = -0.090497`
  - `zero_e_evt.delta_target_loss_total = 2.858374`
  - `zero_z_art.delta_target_loss_total = 0.59141`

对比:
- `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`

解释:
- 两个 averaged checkpoint 都落在:
  - 更负的 final special
  - 但更差的 validation
  - `e_evt` 也低于原 final
- 也就是说:
  - averaging 的确把 `step90` 和 `step100` 做成了中间态
  - 但没有产生比原 final 更强的新平衡点

### 2. `D7` 的 averaging 比 `D13` 健康，但仍不如 `D7 final`
- `D7 step90+100 avg = 2.978639 / -0.098031 / 3.035429 / 0.569171`
- `D13 final = 3.27992 / -0.22848 / 2.950196 / 0.683167`

解释:
- 相比全局 late LR decay:
  - averaging 没有把 validation 拉坏到 `3.28+`
  - `e_evt` 也更强
- 但相比 `D7 final`:
  - validation 仍明显更差
  - `e_evt` 也回落
- 说明 averaging 比“重训式全局降 LR”更温和
- 但它仍然只能在已有 tradeoff 内折中

### 3. `D10` 的 averaging 也没有把“validation 更贵”这件事救回来
- `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
- `D10 step90+100 avg = 3.030039 / -0.090497 / 2.858374 / 0.59141`

解释:
- averaged-D10 拿到了更负的 final special
- 但 validation 继续变差
- `e_evt` 也进一步回落
- 因而这不是 `D10` 的升级版，只是更 special-biased 的次级折中点

## 当前结论
- late checkpoint averaging 是一个有效的工程工具。
- 但在当前 `D7 / D10` 轨迹上:
  - 它只能生成“位于 step90 与 step100 之间”的中间态
  - 不能创造新的 joint-winning checkpoint
- 这与之前的 gate replay 结论一致:
  - late mechanics 可以换 tradeoff
  - 但当前并不能单独打破 tradeoff

## 当前建议
1. 保留 `average-offline-mvp-checkpoints` 作为正式工具。
2. 不把 averaged-D7 或 averaged-D10 升为默认方案。
3. 暂不继续优先扩展更多 late checkpoint averaging sweep。
4. 当前更值得的下一步应重新回到:
   - 新的目标形状
   - 或更强的 supervision 变化
   - 而不是继续在 late mechanics 上找“魔法折中”

