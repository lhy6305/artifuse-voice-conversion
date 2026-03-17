# `round1.1 / checkpoint gate replay` 报告

## 目的
- 上一轮 `checkpoint selection` 联合分析已经确认：
  - `035 / 039 / 042` 的 late window 里确实存在更好的 special checkpoint
  - 但 `step80 / 90 / 100` 分别对应不同 tradeoff
- 本轮继续把这个问题收口成几种可解释的 gate 原型，直接回放：
  - validation 优先
  - special 优先
  - validation guard
  - `e_evt` 优先
  - 双控制优先

## 分析命令
- `.\python.exe manage.py analyze-offline-mvp-checkpoint-gates --experiment-metrics ... --output-dir reports/eval/offline_mvp_checkpoint_gate_replay_round1_1`

## 回放实验
- `EXP-032`
- `EXP-035`
- `EXP-039`
- `EXP-042`

## Anchor
- 当前 anchor 仍取这四条轨迹里最强的 final checkpoint：
  - `EXP-032 step100`
  - `target_validation.loss_total = 2.672052`
  - `target_special_eval.delta_loss_total = 0.103108`
  - `zero_e_evt.delta_target_loss_total = 1.735497`
  - `zero_z_art.delta_target_loss_total = 1.275259`

## 回放的 gate 原型
1. `final_validation`
   - 全轨迹只按 validation 选点
2. `late_special_unconstrained`
   - late window 内只按 special 选点
3. `late_special_validation_guard_1p25`
   - late window 内要求 `validation <= best_validation * 1.25`
   - 在此基础上按 special 选点
4. `late_special_event_priority`
   - 在 `1.25x validation guard` 之上，再要求 `zero_e_evt >= 1.0`
5. `late_special_dual_control_relaxed`
   - `validation <= best_validation * 1.5`
   - `zero_z_art >= 0.3`
   - `zero_e_evt >= 0.5`
6. `late_special_strict_positive_control`
   - `validation <= best_validation * 1.25`
   - `zero_z_art >= 0.1`
   - `zero_e_evt >= 0.5`

## 关键结果
### 1. 只要 gate 足够严格，就会退化回 final
- `final_validation`
  - 全部实验都选回各自 final checkpoint
- `late_special_strict_positive_control`
  - 结果也完全一样
  - 对 `035 / 039 / 042` 来说，能同时满足：
    - `validation guard`
    - `z_art` 不太低
    - `e_evt` 仍为正
    的 late checkpoint，最后只剩 `step100`

### 2. 想救回 special，当前只能在 `step80` 和 `step90` 两种代价之间二选一
- `late_special_unconstrained`
  - `035 / 039 / 042` 全部选到 `step80`
  - 平均相对 final：
    - `validation` 恶化 `+1.028644`
    - `special` 改善 `-0.68454`
    - `e_evt` 下降 `-0.20606`
    - `z_art` 回升 `+0.272127`
- `late_special_validation_guard_1p25`
  - `035 / 039 / 042` 全部选到 `step90`
  - 平均相对 final：
    - `validation` 恶化 `+0.463527`
    - `special` 改善 `-0.493718`
    - `e_evt` 回升 `+0.430689`
    - `z_art` 下降 `-0.139684`
- `late_special_event_priority`
  - 结果与 `late_special_validation_guard_1p25` 完全重合
  - 说明当前 `step90` 的核心特征确实就是：
    - validation 更好
    - `e_evt` 更强
    - 但 `z_art` 接近塌缩
- `late_special_dual_control_relaxed`
  - 结果与 `late_special_unconstrained` 完全重合
  - 说明当前 `step80` 的核心特征确实就是：
    - dual-control 还在
    - special 更好
    - 但 validation 代价明显

## 最关键结论
- 当前还没有任何一个 gate，能让 `035 / 039 / 042` 的非 final checkpoint 同时满足：
  - 比 final 有更好的 special
  - validation 代价仍足够小
  - `z_art / e_evt` 都不塌
  - 并且整体超过 `EXP-032 final`
- 更直接地说：
  - gate replay 证明了“checkpoint 选择”确实是个真问题
  - 但它还不是一把能单独救回主线的钥匙
- 当前所有可解释 gate 最后都落在三种结果之一：
  - 回到 final
  - 选 `step80`
  - 选 `step90`
- 而这三种结果都没有让非 `EXP-032` 实验真正打赢 anchor

先说人话：
- 现在已经可以排除一种很诱人的想法：
  - 不是“只要发明一个更聪明的 early-stop，就能把后面几条实验直接扶正”
- 更准确的说法是：
  - 它们确实有可挑的好点
  - 但这些好点各自都带着清晰代价
  - 目前还没有哪个 gate 能把这些代价一起吃掉

## 建议
1. 当前不要把 gate 直接写进训练主流程作为默认 checkpoint 选择器。
2. gate replay 先保留为离线诊断工具。
3. 若下一轮继续投在训练流程层，最多考虑：
   - 训练中额外记录更完整的 gate 指标
   - 但不要先假定 gate 本身能救回主线
4. 更合理的下一步优先级应转向：
   - 更强的数据视角改造
   - 或监督定义层级的更实质变化
   - 而不是继续围绕 `80 / 90 / 100` 的选点规则打转

## 产物入口
- `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1/checkpoint_gate_replay.json`
- `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1/checkpoint_gate_replay.md`
