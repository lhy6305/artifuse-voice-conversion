# `round1.1 / D2+D3 / secondary axis comparison` 报告

## 目的
- 在已经确认 primary `challenge_proxy_core` 会改变 late-window 形状之后，
- 继续比较 secondary 结构轴：
  - `structural_question_exclaim`
  - `structural_clause_ge4`
- 目标是回答两个问题：
  - 哪条 secondary axis 真正能带来新行为，而不是复刻 `D1`
  - 它是否已经足以打赢当前 anchor `EXP-032 final`

## 实验信息
### D2
- 实验：
  - `EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json`
- 训练输出：
  - `reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/`
- 评估输出：
  - `reports/eval/offline_mvp_ablations_exp018/`
  - `reports/eval/offline_mvp_special_eval_exp018/`
  - `reports/eval/offline_mvp_checkpoint_series_exp018/`
  - `reports/eval/offline_mvp_special_eval_series_exp018/`

### D3
- 实验：
  - `EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json`
- 训练输出：
  - `reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/`
- 评估输出：
  - `reports/eval/offline_mvp_ablations_exp019/`
  - `reports/eval/offline_mvp_special_eval_exp019/`
  - `reports/eval/offline_mvp_checkpoint_series_exp019/`
  - `reports/eval/offline_mvp_special_eval_series_exp019/`

### 联合分析
- checkpoint selection：
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_plus_d1_d2_d3/`
- checkpoint gate replay：
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_plus_d1_d2_d3/`

## 当前配置差异
- 三条 `D1 / D2 / D3` 线共用同一个 primary：
  - `challenge_proxy_core`
- 差异只在 secondary：
  - `D1 = structural_multi_terminal`
  - `D2 = structural_question_exclaim`
  - `D3 = structural_clause_ge4`
- phase 设计保持一致：
  - phase1 `step1-25`
    - primary + secondary
    - `priority_ratio = 0.75`
  - phase2 `step26-45`
    - primary only
    - `priority_ratio = 0.25`
  - `step46+`
    - seeded shuffle

## 关键结果
### 1. `D2` 基本只是 `D1` 的近似拷贝
- `D1 final`
  - `target_validation.loss_total = 2.846479`
  - `target_special_eval.delta_loss_total = 0.412091`
  - `zero_e_evt.delta_target_loss_total = 0.86209`
  - `zero_z_art.delta_target_loss_total = 0.271847`
- `D2 final`
  - `target_validation.loss_total = 2.848954`
  - `target_special_eval.delta_loss_total = 0.411368`
  - `zero_e_evt.delta_target_loss_total = 0.855047`
  - `zero_z_art.delta_target_loss_total = 0.26885`

late-window 也几乎重合：
- `D1 step80 = 3.823698 / -0.411991 / 1.223908 / 0.471141`
- `D2 step80 = 3.821265 / -0.40801 / 1.216376 / 0.472709`
- `D1 step90 = 3.394526 / -0.066697 / 1.31487 / -0.052776`
- `D2 step90 = 3.395798 / -0.072839 / 1.306503 / -0.052078`

结论：
- 把 secondary 从 `multi_terminal` 换成 `question_exclaim`，
- 在当前 `25 / 45 / shuffle` 调度下，没有形成新的杠杆。

### 2. `D3` 是第一条真正改变 final 形状的 secondary axis
- `D3 final`
  - `target_validation.loss_total = 2.901056`
  - `target_special_eval.delta_loss_total = 0.133206`
  - `zero_e_evt.delta_target_loss_total = 1.135895`
  - `zero_z_art.delta_target_loss_total = 0.179408`

对比 `D1 / D2 final`：
- validation 更差
- special 明显更好
- `e_evt` 明显更强
- `z_art` 更弱

对比当前 anchor `EXP-032 final`：
- `EXP-032 = 2.672052 / 0.103108 / 1.735497 / 1.275259`
- `D3 final` 仍没有整体打赢 anchor
- 但它是第一条把 final special 拉回到接近 anchor 区间的 pool-aware 线

### 3. `D3` 的 late-window 比 `D1 / D2` 更深，但仍没有新解
`D3` late window：
- `step80`
  - `target_validation.loss_total = 4.119759`
  - `target_special_eval.delta_loss_total = -0.642442`
  - `zero_e_evt.delta_target_loss_total = 1.107988`
  - `zero_z_art.delta_target_loss_total = 0.513753`
- `step90`
  - `target_validation.loss_total = 3.457301`
  - `target_special_eval.delta_loss_total = -0.128113`
  - `zero_e_evt.delta_target_loss_total = 1.376727`
  - `zero_z_art.delta_target_loss_total = 0.050342`
- `step100`
  - `target_validation.loss_total = 2.901056`
  - `target_special_eval.delta_loss_total = 0.133206`
  - `zero_e_evt.delta_target_loss_total = 1.135895`
  - `zero_z_art.delta_target_loss_total = 0.179408`

解释：
- `step80` 比 `D1 / D2 step80` 更深地改善了 special，
- 但 validation 代价明显更大。
- `step90` 的 `e_evt` 强于 `D1 / D2 step90`，
- 但 `z_art` 仍然很低。
- `step100` 虽然把 final special 拉近 anchor，
- 但 validation 和 `z_art` 仍不够。

先说人话：
- `clause_ge4` 不是没用。
- 它是当前第一次让 secondary axis 真正改变 final 行为的选项。
- 但它还只是在旧 tradeoff 上找到了更有希望的一支，不是已经翻盘。

### 4. 联合 selection / gate replay 的结论没有变
把 `032 / 035 / 039 / 042 / 017 / 018 / 019` 一起看：
- `best_final_validation_experiment` 仍是 `EXP-032 final`
- `best_final_special_experiment` 仍是 `EXP-032 final`
- `best_final_e_evt_experiment` 仍是 `EXP-032 final`
- `best_positive_control_late_special_experiment` 变成了：
  - `EXP-019 step80`
  - `4.119759 / -0.642442 / 1.107988 / 0.513753`
- gate replay 中：
  - `non_anchor_joint_beating_count = 0` 仍未被打破

这表示：
- `D3` 已经成为“最值得继续挖的 non-anchor 分支”
- 但当前 gate 仍然只能在旧 tradeoff 间切换，不能直接把 `D3` 选成新主线解

## 当前结论
- `D2` 没有提供独立价值，当前可以视作 `D1` 的近似重复。
- `D3` 是当前最强的 secondary-axis follow-up：
  - final special 最接近 anchor
  - final `e_evt` 也明显高于 `D1 / D2`
  - 但 validation 和 `z_art` 仍不足
- 因此当前最合理的主张不是：
  - 再试更多“轻微换 secondary 名称”的组合
- 而是：
  - 保留 primary `challenge_proxy_core`
  - 把 secondary 收敛到 `structural_clause_ge4`
  - 下一轮优先改 phase 配比或 handoff，而不是继续横向扫 secondary

## 当前建议
1. 暂不继续扩展 `question_exclaim` 这条线。
2. secondary 默认优先级更新为：
   - `structural_clause_ge4`
   - `structural_multi_terminal`
   - `structural_question_exclaim`
3. 下一轮若继续做最小实验，优先只围绕：
   - `challenge_proxy_core + structural_clause_ge4`
   做 schedule / ratio / handoff 调整。
4. 在没有新证据前，不把任何 D 系 checkpoint 选择规则接入默认训练流程。
