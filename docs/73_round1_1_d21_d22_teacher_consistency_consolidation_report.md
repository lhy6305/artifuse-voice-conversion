# `round1.1 / D21+D22 / teacher-consistency consolidation` 报告

## 目的
- 在 `gate / late LR decay / averaging / bucket splitting` 都已证明不能单独打破主线 tradeoff 后，
- 正式验证一条新的训练分解路线：
  - 不再继续换 supervision bucket；
  - 而是用 frozen teacher 把已知好的 challenge-adjacent 行为钉住，
  - 再用短 consolidation phase 把 validation 往下压。

本轮只做最小原型：
- 一致性只蒸馏 `event_logits + z_art`
- 只作用于 `challenge_proxy_core`
- 先不蒸馏 acoustic

## 代码与配置
### 新增训练能力
- `src/v5vc/train_entry.py`
  - 新增 `training.init_checkpoint_path`
  - 新增 `training.teacher_consistency`
  - 支持从 checkpoint 初始化 student
  - 支持加载 frozen teacher checkpoint，并在 target batch 上计算 pool-gated teacher consistency

### D21
- 实验:
  - `EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration`
- 配置:
  - `configs/offline_mvp_train_d21_round1_1_d10_final_consolidation_teacher_consistency_smallscale_30_seeded_shuffle.json`
- 设计:
  - `student init = D10 final`
  - `teacher = D10 final`
  - `pool_memberships = ["challenge_proxy_core"]`
  - `num_steps = 30`

### D22
- 实验:
  - `EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration`
- 配置:
  - `configs/offline_mvp_train_d22_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_smallscale_30_seeded_shuffle.json`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - 其余 consolidation 机制与 `D21` 保持一致

## 关键结果
### 1. teacher consistency 不是挂空配置，两个实验都在真正生效
- `D21 step10`
  - `loss_teacher_consistency = 0.024265`
  - `loss_teacher_event_consistency = 0.014654`
  - `loss_teacher_z_art_consistency = 0.009611`
- `D21 step30`
  - `loss_teacher_consistency = 0.28094`
- `D22 step1`
  - `loss_teacher_consistency = 0.029021`
- `D22 step30`
  - `loss_teacher_consistency = 0.385431`

解释：
- 这轮不是“teacher 没接上”。
- 两条线都在 `challenge_proxy_core` 上持续感受到 teacher pull。

### 2. `D21` 大幅改善 validation，但没有保住 `D10` 的 final special
- `D21 final`
  - `target_validation.loss_total = 2.441712`
  - `target_special_eval.delta_loss_total = 0.181901`
  - `zero_e_evt.delta_target_loss_total = 2.919652`
  - `zero_z_art.delta_target_loss_total = 0.391864`

对比 `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`:
- validation 显著更好
- final special 明显更差，且已翻正
- `e_evt` 与 `z_art` 都回落

解释：
- `D10 -> D10` 单锚 consistency 没有把 `D10` 的 challenge 终盘保下来。
- 它更像把模型推向了“validation 更强，但 special 保不住”的新平衡。

### 3. `D22` 是这条 family 里更有价值的点，但仍没满足通过标准
- `D22 final`
  - `target_validation.loss_total = 2.444194`
  - `target_special_eval.delta_loss_total = 0.140001`
  - `zero_e_evt.delta_target_loss_total = 3.299035`
  - `zero_z_art.delta_target_loss_total = 0.438936`

对比 `D21 final = 2.441712 / 0.181901 / 2.919652 / 0.391864`:
- validation 近似持平
- special 更好
- `e_evt` 更强
- `z_art` 也更好

对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`:
- validation 显著更好
- special 仍然翻正
- `e_evt` 接近但仍低于 `D7`
- `z_art` 明显低于 `D7`

解释：
- `D22` 不是纯负例。
- 它是 teacher-consistency family 里第一个形成独立价值的点：
  - validation 很强
  - `e_evt` 也保持得比较高
- 但它仍没有达到“既保住 `D10` 的 special，又不牺牲 `D7` 控制”的目标。

### 4. 这条 family 的真实问题，不是“teacher 没拉住”，而是当前 gate 太窄
- `D21 / D22` 都只在 `challenge_proxy_core` 上蒸馏
- 结果是:
  - consistency 可以稳定生效
  - 但 formal `target_special_eval` 仍然没有被保住

这说明更准确的诊断是：
- `challenge_proxy_core` 足够让模型记住一部分 challenge-adjacent 行为
- 但它还不足以单独约束 formal special slice 的最终形状
- 当前更像是：
  - teacher gate 太窄
  - 而不只是 weight 太小

## 当前结论
- teacher-consistency consolidation 这条大方向值得保留。
- `D21` 证明了单锚 `D10 -> D10` 不是合适默认路线。
- `D22` 证明了“`D7 init + D10 teacher`”确实能形成新行为，
  但它仍然没有通过当前通过标准：
  - special 未保住
  - `z_art` 仍不足

## 当前建议
1. 保留 `teacher_consistency` 能力，不回退代码。
2. 不把 `D21 / D22` 升为默认方案。
3. 当前若继续沿这条 family 推进，优先级应转向:
   - 扩 teacher gate 覆盖
   - 而不是继续做纯 `weight` sweep
4. 下一轮更值得先试的是:
   - `D7 init + D10 teacher`
   - teacher gate 从 `challenge_proxy_core` 扩到
     `challenge_proxy_core + challenge_proxy_relaxed`
   - 或 `challenge_proxy_core + short_pause_no_terminal`
5. 暂不继续优先做:
   - 单锚 `D10 -> D10` 的更多微调
   - 当前窄 gate 上的纯 weight / lr sweep
