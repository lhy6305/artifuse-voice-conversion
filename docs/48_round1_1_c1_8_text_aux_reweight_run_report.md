# `round1.1 / C1.8 / punctuation-oriented text_aux reweight` 100-step 报告

## 目的
- `EXP-033 / EXP-034` 已经说明：
  - 继续抠 phase1 采样配额，基本救不回 final special。
- 当前验证：
  - 保持 `EXP-032` 的两段式 pool-handoff 采样骨架不变。
  - 不再改 sampler，而是把 `b1_1_stats_v2` 的 `text_aux` 监督从 lexical-heavy 维度挪向 punctuation / structure 维度。

## 当前配置
- 实验：
  - `EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration`
- 采样骨架：
  - 完全复用 `EXP-032`
  - `step1-25`: `clause>=4 OR multi_terminal`, `3 priority slots`
  - `step26-45`: `clause>=4-only`, `1 priority slot`
  - `step46+`: seeded shuffle
- 新改动：
  - `losses.text_aux_reweight.enabled = true`
  - 降低 lexical-heavy 维度权重：
    - `token_count / lexical_char_density / avg_clause_chars / short_lexical / long_lexical`
  - 保留或提高 punctuation / structure 维度权重：
    - `pause_count / terminal_count / question_ratio / exclamation_ratio / clause_count / multi-pause flag / multi-terminal flag`

## 关键结果
- final `target_validation.loss_total = 2.889709`
  - 明显差于 `EXP-032` 的 `2.672052`
- final `target_special_eval.delta_loss_total = 0.39305`
  - 明显差于 `EXP-032` 的 `0.103108`
  - 说明这版不能作为 final checkpoint 配置
- final `zero_e_evt.delta_target_loss_total = 0.931855`
  - 明显弱于 `EXP-032` 的 `1.735497`
  - 说明 final `e_evt` 依赖被削弱了
- `step50 zero_e_evt.delta_target_loss_total = -0.52895`
  - 比 `EXP-032` 的 `-0.556712` 略好一点
- `step50 zero_z_art.delta_target_loss_total = -0.353743`
  - 比 `EXP-032` 的 `-0.187733` 更差
  - 说明中段问题没有真正修掉，只是从 `e_evt` 偏移到了更弱的整体控制稳定性

## 新发现
- 这版不是“完全没信号”，而是信号出现在训练后段而不是 final。
- `special_eval_series` 显示：
  - `step90 target_special_eval.delta_loss_total = -0.2803`
    - 明显好于当前所有已落盘的 final small-scale 结果
  - 但到 `step100` 反而翻到 `0.39305`
- 同时 `step100 delta_loss_text_aux_effective = 0.154599`
  - 比 raw `delta_loss_text_aux = 0.134214` 还更坏
  - 说明这版 reweight 真正改变了 stress 方向，不是 raw 指标偶然波动

## 结论
- punctuation-oriented `text_aux` reweight 确实是个真杠杆：
  - 它已经能显著改写 late-stage special behavior
  - 不再像 phase1 配额微调那样几乎不动
- 但“整段 100 step 常开”这版接法不成立：
  - final main validation 更差
  - final special 更差
  - final `e_evt` 依赖也更弱
- 当前更合理的下一步不是退回 sampler，而是把这条监督改成有阶段的 schedule：
  - 例如前中段保留 punctuation-oriented reweight
  - 后段逐步衰减或关闭
  - 目标是保留 `step90` 附近的 special 收益，同时避免 `step100` 的 final 翻车
