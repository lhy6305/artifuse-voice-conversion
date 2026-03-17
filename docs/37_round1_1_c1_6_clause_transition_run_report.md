# `round1.1 / C1.6 / clause-transition` 100-step 报告

## 目的
- 在 `EXP-023` 已证明：
  - 结构化标签可以接上训练
  - 但 clause body floor 没修掉 `step50`
- 当前进一步把监督重点改到：
  - clause end
  - inter-clause transition
  - final-vs-middle transition 差异

先说人话：
- 这轮不是再强调“句子中间那一段要有点活性”。
- 而是改成教模型：分句收尾时，尤其是 middle 和 final，前后状态该怎么变。

## 当前配置
- 实验：
  - `EXP-20260314-024-offline-mvp-c1-6-round1-1-clause-transition-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_6_round1_1_clause_transition_smallscale_100_seeded_shuffle.json`
- 相比 `EXP-023` 的主要变化：
  - 不再使用 `clause_role_target_overrides`
  - 改为 `clause_transition_target_overrides`
  - 基于 `clause["frame_end_index"]` 构建 `clause_transition_strengths`
  - 对 `middle / final / single` 的 clause end 施加不同的：
    - `boundary_delta_target`
    - `boundary_fall_target`
    - pre/post `presence`
    - pre/post `energy`

解释：
- 这轮的核心不是 clause body。
- 是 clause 收尾前后那几帧的过渡形状。

## 关键结果
### 1. 它几乎和 `EXP-021` 重合
- `EXP-021`
  - final `target_validation.loss_total = 2.760389`
  - final `target_special_eval.delta_loss_total = 0.028766`
  - final `zero_e_evt.delta_target_loss_total = 1.781482`
- `EXP-024`
  - final `target_validation.loss_total = 2.760679`
  - final `target_special_eval.delta_loss_total = 0.028482`
  - final `zero_e_evt.delta_target_loss_total = 1.781535`

解释：
- 这不是“差一点”。
- 更准确地说，是训练终点几乎回到了 `EXP-021` 的原轨道。

### 2. `step50` 完全没被改写
- `EXP-021`
  - `step50 zero_z_art.delta_target_loss_total = -0.273851`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854462`
- `EXP-024`
  - `step50 zero_z_art.delta_target_loss_total = -0.273854`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854465`

解释：
- 这组数字已经不是“趋势没明显改善”。
- 而是几乎逐位重现。

### 3. 它也没有延续 `EXP-023` 的结构化偏移
- `EXP-023`
  - final `target_validation.loss_total = 2.777409`
  - final `target_special_eval.delta_loss_total = 0.008379`
  - final `zero_e_evt.delta_target_loss_total = 1.807451`
- `EXP-024`
  - final `target_validation.loss_total = 2.760679`
  - final `target_special_eval.delta_loss_total = 0.028482`
  - final `zero_e_evt.delta_target_loss_total = 1.781535`

解释：
- `EXP-024` 不像是在 `EXP-023` 基础上把教法修正了。
- 更像是退回了 base `C1.4 / round1.1` 那条线。

## 当前结论
- clause-transition 这条方向本身没有“接不上”的问题：
  - 新代码路径已经真实执行
  - 训练、ablation、checkpoint-series、`special_eval_series` 全部跑通
- 但当前这版接法没有形成独立有效信号。

从结果推断：
- 当前 `clause_transition_target_overrides` 仍然是叠在原有 `event_boundary_bias` 上。
- 而多数 clause end 本来就和 pause / terminal 边界高度重合。
- 所以新增监督大概率被原有边界信号吞掉了，没有把优化轨迹真正掰开。

先说人话：
- 这不是“clause end 方向错了”。
- 更像是“还是在原来的判卷器上贴标签，贴了但没贴出独立效果”。

## 建议
- 不把 `EXP-024` 升为默认训练配置。
- 如果继续推进 route-C，下一步更合理的是：
  - 做独立的 clause-transition auxiliary loss
  - 或单独抽样 clause-end frame 做专门监督
  - 而不是继续把结构化信号塞进同一个 `event_boundary_bias` override 通道
