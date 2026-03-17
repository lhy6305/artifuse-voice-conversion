# `round1.1 / D4+D5 / clause_ge4 schedule follow-ups` 报告

## 目的
- 在 `D3` 已确认 `structural_clause_ge4` 是当前最强 secondary axis 之后，
- 只围绕 schedule / handoff 做最小跟进，
- 验证是否能把 `D3` 的 special 收益留到 final，同时把 validation 拉回 anchor 附近。

## 实验信息
### D4
- 实验：
  - `EXP-20260315-020-offline-mvp-d4-round1-1-special-proxy-core-clause-ge4-early-handoff-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_d4_round1_1_special_proxy_core_clause_ge4_early_handoff_smallscale_100_seeded_shuffle.json`
- 训练输出：
  - `reports/training/offline_mvp_d4_special_proxy_core_clause_ge4_early_handoff_exp020/`
- 评估输出：
  - `reports/eval/offline_mvp_ablations_exp020/`
  - `reports/eval/offline_mvp_special_eval_exp020/`
  - `reports/eval/offline_mvp_checkpoint_series_exp020/`
  - `reports/eval/offline_mvp_special_eval_series_exp020/`

### D5
- 实验：
  - `EXP-20260315-021-offline-mvp-d5-round1-1-special-proxy-core-clause-ge4-late-handoff-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_d5_round1_1_special_proxy_core_clause_ge4_late_handoff_smallscale_100_seeded_shuffle.json`
- 训练输出：
  - `reports/training/offline_mvp_d5_special_proxy_core_clause_ge4_late_handoff_exp021/`
- 评估输出：
  - `reports/eval/offline_mvp_ablations_exp021/`
  - `reports/eval/offline_mvp_special_eval_exp021/`
  - `reports/eval/offline_mvp_checkpoint_series_exp021/`
  - `reports/eval/offline_mvp_special_eval_series_exp021/`

### 联合分析
- checkpoint selection：
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_plus_d1_d2_d3_d4_d5/`
- checkpoint gate replay：
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_plus_d1_d2_d3_d4_d5/`

## 配置差异
三条 `D3 / D4 / D5` 线共用：
- primary:
  - `challenge_proxy_core`
- secondary:
  - `structural_clause_ge4`

差异只在 schedule：
- `D3`
  - phase1 `step1-25`
    - `priority_ratio = 0.75`
    - primary + secondary
  - phase2 `step26-45`
    - `priority_ratio = 0.25`
    - primary only
  - `step46+`
    - seeded shuffle
- `D4`
  - phase1 `step1-20`
    - `priority_ratio = 0.5`
    - primary + secondary
  - phase2 `step21-60`
    - `priority_ratio = 0.25`
    - primary only
  - `step61+`
    - seeded shuffle
- `D5`
  - phase1 同 `D4`
  - phase2 `step21-70`
    - `priority_ratio = 0.25`
    - primary only
  - `step71+`
    - seeded shuffle

## 关键结果
### 1. `D4` 是当前最均衡的 `clause_ge4` schedule
- `D4 final`
  - `target_validation.loss_total = 2.729466`
  - `target_special_eval.delta_loss_total = -0.00228`
  - `zero_e_evt.delta_target_loss_total = 1.527013`
  - `zero_z_art.delta_target_loss_total = 0.199795`

对比 `D3 final = 2.901056 / 0.133206 / 1.135895 / 0.179408`：
- validation 明显更好
- special 更好
- `e_evt` 更强
- `z_art` 也略好

对比 anchor `EXP-032 final = 2.672052 / 0.103108 / 1.735497 / 1.275259`：
- validation 已非常接近
- final special 已经优于 anchor
- `e_evt` 仍落后
- `z_art` 仍明显不足

这说明：
- 把 `clause_ge4` 的 early pressure 收软，并把 primary-only handoff 拉长到 `60`，
- 确实把 `D3` 从“有效但太贵”推到了“接近可用”。

### 2. `D5` 证明再往后拖 handoff 只会继续换 special，不会换来更好的整体解
- `D5 final`
  - `target_validation.loss_total = 2.810181`
  - `target_special_eval.delta_loss_total = -0.031687`
  - `zero_e_evt.delta_target_loss_total = 1.462891`
  - `zero_z_art.delta_target_loss_total = 0.137204`

对比 `D4 final`：
- special 更好一点
- 但 validation 更差
- `e_evt` 更差
- `z_art` 也更差

也就是说：
- `D5` 拿到了当前全集里最好的 final special，
- 但它不是更好的主线候选，
- 因为它为了这点 special 收益，继续丢掉了 balance。

### 3. `D4 / D5` 的 late-window 说明 sweet spot 已经很窄
`D4 late window`：
- `step80 = 3.688603 / -0.30717 / 1.315593 / 0.412683`
- `step90 = 3.427096 / -0.343128 / 1.522258 / -0.184007`
- `step100 = 2.729466 / -0.00228 / 1.527013 / 0.199795`

`D5 late window`：
- `step80 = 3.792123 / -0.542106 / 1.497362 / 0.372964`
- `step90 = 3.35247 / -0.22034 / 1.436741 / -0.067098`
- `step100 = 2.810181 / -0.031687 / 1.462891 / 0.137204`

解释：
- `D5` 把 `step80` 的 special 和 `e_evt` 再往前拉了一点，
- 但这股收益没有平顺地留到 final，
- 反而把 final validation 和 `z_art` 一起拖坏了。

先说人话：
- handoff 继续往后拖，不是免费午餐。
- `60` 左右已经很像当前这条线的甜点区间；
- 再推到 `70`，换来的主要是更极端的 special，不是更好的总解。

### 4. 联合 replay 的正式结论
把 `032 / 035 / 039 / 042 / 017 / 018 / 019 / 020 / 021` 一起看：
- `best_final_validation_experiment`
  - 仍是 `EXP-032 final`
- `best_final_e_evt_experiment`
  - 仍是 `EXP-032 final`
- `best_final_special_experiment`
  - 变成了 `EXP-021 final`
  - `2.810181 / -0.031687 / 1.462891 / 0.137204`
- gate replay 里：
  - `non_anchor_joint_beating_count = 0`
  - 仍然没有被打破

这表示：
- 现在已经不是“D 线完全没戏”了，
- 而是：
  - `D4` 已经把 final 拉到非常接近 anchor 的位置
  - `D5` 则进一步证明当前剩下的主要瓶颈是 `z_art`
  - 但还没有任何 non-anchor 能整体打赢 `EXP-032 final`

## 当前结论
- `D4` 是当前最均衡、最值得继续跟进的 `clause_ge4` schedule。
- `D5` 的价值主要是负结论：
  - 它证明继续延后 handoff 会进一步追 special，
  - 但会牺牲 validation 与控制量平衡。
- 当前最合理的下一步，不是再做 `D6 / D7` 横向扫 handoff，
- 而是：
  - 以 `D4` 为新的 schedule 基线，
  - 开始想办法补 `z_art`
  - 或显式约束 late-window 的 `z_art` 保留

## 当前建议
1. `clause_ge4` 线的默认 schedule 基线更新为 `D4`。
2. 不把 `D5` 升为默认方案。
3. 下一轮若继续，优先方向应从“纯 handoff 调度”转向：
   - `D4` 基线上补 `z_art` 保留
   - 或更明确的 dual-control 约束
4. 在没有新证据前，`EXP-032 final` 仍保持 anchor。
