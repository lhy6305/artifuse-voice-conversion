# `round1.1 / C1.7 / clause-transition auxiliary loss` 100-step 报告

## 目的
- 在 `EXP-024` 已确认：
  - clause-transition 方向不是完全没法接
  - 但把它继续塞进 `event_boundary_bias` 几乎等于没形成独立信号
- 当前改成：
  - 保留原 `C1.4` boundary recipe
  - 额外加一条独立的 `clause_transition_aux` loss

先说人话：
- 这轮不再继续改“同一个判卷器”。
- 而是单独加一张卷子，专门检查 clause end 前后几帧学得像不像。

## 当前配置
- 实验：
  - `EXP-20260314-025-offline-mvp-c1-7-round1-1-clause-transition-aux-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_smallscale_100_seeded_shuffle.json`
- 相比 `EXP-024` 的主要变化：
  - 移除 `clause_transition_target_overrides`
  - 新增独立 `clause_transition_aux`
  - 在 clause end 的：
    - boundary `delta / fall`
    - pre `presence / energy`
    - post `presence / energy`
  - 上做独立概率回归损失

解释：
- 这轮结构化监督不再靠修改主 `event_target`。
- 而是作为附加学习压力独立进入总 loss。

## 关键结果
### 1. 它确实形成了独立信号
- final `target_validation.loss_clause_transition_aux = 0.051682`
- final `target_special_eval.loss_clause_transition_aux = 0.0`
- final ablation:
  - `none target.loss_clause_transition_aux = 0.062756`
  - `zero_e_evt target.loss_clause_transition_aux = 0.062756`

解释：
- 这说明这条 aux loss 不是假接线。
- 它在正常 lexical target validation 上真实存在。
- 只是当前 special slice 是 punctuation-only，所以这条 loss 在 special slice 上天然为零。

### 2. final special gap 有改善，但不够赢
- `EXP-021`
  - final `target_special_eval.delta_loss_total = 0.028766`
- `EXP-024`
  - final `target_special_eval.delta_loss_total = 0.028482`
- `EXP-025`
  - final `target_special_eval.delta_loss_total = 0.010553`
- `EXP-023`
  - final `target_special_eval.delta_loss_total = 0.008379`

解释：
- 独立 aux loss 比 `EXP-021 / EXP-024` 更像在发挥作用。
- 但仍没有超过 `EXP-023` 的最好 special gap。

### 3. 主验证反而比 base 更差一点
- `EXP-021`
  - final `target_validation.loss_total = 2.760389`
- `EXP-024`
  - final `target_validation.loss_total = 2.760679`
- `EXP-025`
  - final `target_validation.loss_total = 2.778521`

解释：
- 这说明新增独立监督不是“白拿收益”。
- 当前配法已经开始带来额外训练压力，但没把主线推得更好。

### 4. `step50` 还是没动
- `EXP-021`
  - `step50 zero_z_art.delta_target_loss_total = -0.273851`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854462`
- `EXP-024`
  - `step50 zero_z_art.delta_target_loss_total = -0.273854`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854465`
- `EXP-025`
  - `step50 zero_z_art.delta_target_loss_total = -0.274127`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854869`

解释：
- 当前最关键的问题还是没被改写。
- 而且这次几乎不是“稍差一点”，而是仍在同一个坏区间里。

## 当前结论
- 独立 `clause_transition_aux` 比 `EXP-024` 前进一步：
  - 终于能确认结构化监督不再完全被原 boundary bias 吞掉
  - 它已经在 lexical validation 上留下了可测的独立 loss
- 但它还没有强到能改写训练动力学：
  - `step50` 没改善
  - main validation 更差一点
  - final special gap 也没拿到当前最好值

从结果推断：
- 当前问题不只是“监督有没有独立通道”。
- 还包括：
  - 这类样本在 uniform `seeded_shuffle` 下出现密度不够
  - clause-transition 信号进入训练的时机和频率不够强

先说人话：
- 现在可以确认，不是完全白做。
- 但只是“多了一点独立声音”，还不足以改场上的主旋律。

## 建议
- 不把 `EXP-025` 升为默认训练配置。
- 下一步更合理的是：
  - 保留独立 auxiliary loss 这条方向
  - 但把重点转到多 clause target 记录的 targeted sampling / curriculum
  - 或单独提高 clause-transition-rich 样本在前中期训练中的出现密度
