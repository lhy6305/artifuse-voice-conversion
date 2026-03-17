# `round1.1 / D1 / special-proxy-core + multi-terminal` 100 step 实跑报告

## 目的
- 验证在 `EXP-032` 骨架上，把 target-side 采样改成：
  - `challenge_proxy_core` 主池
  - `structural_multi_terminal` 次池
  是否能比现有 `round1.1` 主线更接近“低 validation 代价下救回 special”。

## 实验信息
- 实验：
  - `EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json`
- 训练输出：
  - `reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/`
- 评估输出：
  - `reports/eval/offline_mvp_ablations_exp017/`
  - `reports/eval/offline_mvp_special_eval_exp017/`
  - `reports/eval/offline_mvp_checkpoint_series_exp017/`
  - `reports/eval/offline_mvp_special_eval_series_exp017/`

## 当前配置
### sampler
- phase1 `step1-25`
  - primary:
    - `challenge_proxy_core`
  - secondary:
    - `structural_multi_terminal`
    - `max_slots = 1`
  - `priority_ratio = 0.75`
- phase2 `step26-45`
  - primary:
    - `challenge_proxy_core`
  - `priority_ratio = 0.25`
- `step46+`
  - seeded shuffle

### pool 规模
- primary `challenge_proxy_core = 16`
- phase1 union `= 172`
- phase2 priority `= 16`

## 关键结果
### 1. final 没有超过当前 anchor
- final `target_validation.loss_total = 2.846479`
- final `target_special_eval.delta_loss_total = 0.412091`
- final `zero_e_evt.delta_target_loss_total = 0.86209`
- final `zero_z_art.delta_target_loss_total = 0.271847`

对比当前 anchor `EXP-032 final`：
- `EXP-032 target_validation.loss_total = 2.672052`
- `EXP-032 target_special_eval.delta_loss_total = 0.103108`
- `EXP-032 zero_e_evt.delta_target_loss_total = 1.735497`
- `EXP-032 zero_z_art.delta_target_loss_total = 1.275259`

结论：
- `D1 final` 明显没有打赢 `EXP-032 final`。

### 2. 这条线确实形成了新的 late-window 形状，但不是新解
`D1` 的 late window：
- `step80`
  - `target_validation.loss_total = 3.823698`
  - `target_special_eval.delta_loss_total = -0.411991`
  - `zero_e_evt.delta_target_loss_total = 1.223908`
  - `zero_z_art.delta_target_loss_total = 0.471141`
- `step90`
  - `target_validation.loss_total = 3.394526`
  - `target_special_eval.delta_loss_total = -0.066697`
  - `zero_e_evt.delta_target_loss_total = 1.31487`
  - `zero_z_art.delta_target_loss_total = -0.052776`
- `step100`
  - `target_validation.loss_total = 2.846479`
  - `target_special_eval.delta_loss_total = 0.412091`
  - `zero_e_evt.delta_target_loss_total = 0.86209`
  - `zero_z_art.delta_target_loss_total = 0.271847`

解释：
- 它仍然是熟悉的 `80 / 90 / 100` 分叉。
- 但和 `035 / 039 / 042` 相比，`step80` 的 tradeoff 形状确实被改了一点：
  - validation 代价更小
  - `e_evt` 更强
  - 但 special 改善没有那么深

先说人话：
- 它不是没学到。
- 它学到的是一种更“温和”的 late-special 解，但还不够强到推翻 `EXP-032`。

### 3. 联合分析也确认：它没有成为新 anchor
把 `EXP-017` 并进 `032 / 035 / 039 / 042` 后：
- `best_final_validation_experiment` 仍是 `EXP-032 final`
- `best_final_special_experiment` 仍是 `EXP-032 final`
- `best_final_e_evt_experiment` 仍是 `EXP-032 final`
- gate replay 里：
  - `non_anchor_joint_beating_count = 0` 仍未被打破

## 当前结论
- `D1` 没有形成新的主线解。
- 但它提供了一个很重要的新事实：
  - 当 primary 改成 `challenge_proxy_core` 后，
  - late-window 的 `step80` 不再像 `035 / 039 / 042` 那样“special 很深但 e_evt 明显偏弱”，
  - 而是变成：
    - special 改善较浅
    - validation 代价较小
    - `e_evt` 反而更强

这说明：
- `challenge_proxy_core` 确实在改 tradeoff 形状；
- 只是当前搭配的 secondary 结构轴还不足以把这条线推成新 anchor。

## 当前建议
- 不把 `D1` 升为默认方案。
- 下一轮如果还沿 pool-aware sampling 继续，最值得动的不是 primary：
  - `challenge_proxy_core` 已经证明自己会改轨迹形状
- 更值得动的是 secondary 结构轴：
  - 优先比较
    - `structural_multi_terminal`
    - `structural_question_exclaim`
    - `structural_clause_ge4`
- 也就是说，下一轮该问的是：
  - “哪个 secondary axis 最能和 `challenge_proxy_core` 形成互补”
  - 而不是“还要不要继续用 `challenge_proxy_core`”
