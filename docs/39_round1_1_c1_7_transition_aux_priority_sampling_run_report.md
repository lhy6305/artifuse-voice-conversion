# `round1.1 / C1.7 / transition-aux + aggressive priority sampling` 100-step 报告

## 目的
- 在 `EXP-025` 已确认：
  - 独立 `clause_transition_aux` 终于形成了独立信号
  - 但在 uniform sampler 下，`step50` 还是没动
- 当前进一步验证：
  - 如果把 transition-rich target 记录在前中期显著加密，会不会把 route-C 动力学真正掰开

## 当前配置
- 实验：
  - `EXP-20260314-026-offline-mvp-c1-7-round1-1-transition-aux-priority-sampling-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_sampling_smallscale_100_seeded_shuffle.json`
- 新增采样策略：
  - `priority_interleave`
  - active until `step70`
  - `priority_ratio = 0.75`
  - priority 条件：
    - `clause_count >= 4`
    - 或 `utterance_structure_type = multi_terminal`
- 当前 priority 池规模：
  - `234 / 592`

先说人话：
- 这轮不是改判卷器。
- 是把“复杂分句、转折更强”的 target 台词，在训练前中期塞得更密。

## 关键结果
### 1. 它是第一轮真正大幅改写终点主验证的采样实验
- `EXP-021`
  - final `target_validation.loss_total = 2.760389`
- `EXP-025`
  - final `target_validation.loss_total = 2.778521`
- `EXP-026`
  - final `target_validation.loss_total = 2.648178`

解释：
- 这不是噪声级波动。
- aggressive priority sampling 确实把主验证线往前拉了一大截。

### 2. 但它把 special slice 明显拉坏了
- `EXP-025`
  - final `target_special_eval.delta_loss_total = 0.010553`
- `EXP-026`
  - final `target_special_eval.delta_loss_total = 0.101163`

解释：
- 这说明它在 lexical transition-rich 主线上更强，
- 但对 punctuation-only challenge slice 的相对压力更大了。

### 3. `step50` 也不是变好，而是更差
- `EXP-025`
  - `step50 zero_z_art.delta_target_loss_total = -0.274127`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854869`
- `EXP-026`
  - `step50 zero_z_art.delta_target_loss_total = -0.300652`
  - `step50 zero_e_evt.delta_target_loss_total = -0.933602`

解释：
- 这说明 aggressive 版本不是把中段问题修好。
- 而是把训练拉到了一个更偏 lexical 主线、但更不稳的轨道。

## 当前结论
- targeted sampling 现在已经被证明是强杠杆：
  - 它比单纯 loss tweak 更能改训练轨迹
- 但 `EXP-026` 的配法过猛：
  - main validation 最好
  - special slice 最差
  - `step50` 更坏

先说人话：
- 这轮像是把模型训练得更会做主线题了。
- 但偏科更严重，中途也更容易打摆子。

## 建议
- 不把 `EXP-026` 升为默认训练配置。
- 当前更合理的动作不是放弃 targeted sampling，而是：
  - 保留这个方向
  - 但把强度降下来，改成更软、更早结束的 curriculum
