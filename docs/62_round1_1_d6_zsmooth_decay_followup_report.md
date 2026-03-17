# `round1.1 / D6 / z_smooth decay follow-up` 报告

## 目的
- 在 `D4` 已经把 `challenge_proxy_core + structural_clause_ge4` 推到当前最均衡区间之后，
- 做一轮最小机制跟进，
- 验证“late-window 的 `z_art` 瓶颈”是否主要来自 `z_smooth` 约束过硬。

## 实验信息
### D6
- 实验：
  - `EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json`
- 训练输出：
  - `reports/training/offline_mvp_d6_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_exp022/`
- 评估输出：
  - `reports/eval/offline_mvp_ablations_exp022/`
  - `reports/eval/offline_mvp_special_eval_exp022/`
  - `reports/eval/offline_mvp_checkpoint_series_exp022/`
  - `reports/eval/offline_mvp_special_eval_series_exp022/`

### 联合分析
- checkpoint selection：
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_plus_d1_d2_d3_d4_d5_d6/`
- checkpoint gate replay：
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_plus_d1_d2_d3_d4_d5_d6/`

## 机制变更
这轮没有改 sampler，也没有改 secondary axis。

只新增了一个最小 loss 机制：
- `src/v5vc/offline_mvp/losses.py`
  - `build_effective_loss_weights()`
  - `resolve_z_smooth_weight()`
  - `resolve_scalar_weight_schedule()`

含义是：
- 训练现在支持对 `z_smooth` 走 step-aware weight schedule；
- `event_weight_schedule` 也统一走同一套 scalar schedule resolver。

## 配置差异
`D6` 直接继承 `D4` 的 sampler：
- phase1 `step1-20`
  - `priority_ratio = 0.5`
  - primary `challenge_proxy_core`
  - secondary `structural_clause_ge4`
- phase2 `step21-60`
  - `priority_ratio = 0.25`
  - primary only
- `step61+`
  - seeded shuffle

唯一差异在 losses：
- `D4`
  - `z_smooth = 0.1`
  - 固定不变
- `D6`
  - `z_smooth = 0.1`
  - 新增 `z_smooth_weight_schedule`
    - `mode = linear_ramp`
    - `start_step = 61`
    - `end_step = 85`
    - `start_weight = 0.1`
    - `end_weight = 0.02`

## schedule 生效校验
dry-run 和正式训练历史都确认 schedule 确实执行了，不是挂空配置。

关键步位：
- `step60`
  - `effective z_smooth = 0.1`
- `step70`
  - `effective z_smooth = 0.07`
- `step80`
  - `effective z_smooth = 0.03666666666666668`
- `step90`
  - `effective z_smooth = 0.02`
- `step100`
  - `effective z_smooth = 0.02`

先说人话：
- 这轮不是“schedule 没生效”。
- 它是“schedule 生效了，但行为几乎没变”。

## 关键结果
### 1. `D6 final` 与 `D4 final` 基本是数值级平手
- `D6 final`
  - `target_validation.loss_total = 2.728306`
  - `target_special_eval.delta_loss_total = -0.001608`
  - `zero_e_evt.delta_target_loss_total = 1.52269`
  - `zero_z_art.delta_target_loss_total = 0.20107`

对比 `D4 final = 2.729466 / -0.00228 / 1.527013 / 0.199795`：
- validation 只好 `0.00116`
- special 只回退 `0.000672`
- `e_evt` 只回退 `0.004323`
- `z_art` 只回升 `0.001275`

这个量级太小，不能解释成：
- 找到了新的稳定杠杆
- 或已经触到 `z_art` 主瓶颈

### 2. `D6` 没有改写 `D4` 的 late-window 形状
`D6 late window`：
- `step80 = 3.688544 / -0.307189 / 1.315578 / 0.412773`
- `step90 = 3.428308 / -0.344274 / 1.520919 / -0.185088`
- `step100 = 2.728306 / -0.001608 / 1.52269 / 0.20107`

对比 `D4 late window`：
- `step80 = 3.688603 / -0.30717 / 1.315593 / 0.412683`
- `step90 = 3.427096 / -0.343128 / 1.522258 / -0.184007`
- `step100 = 2.729466 / -0.00228 / 1.527013 / 0.199795`

几乎可以直接判成：
- 同一条轨迹形状
- 只发生了极小量级的数值漂移

也就是说：
- late `z_smooth` decay 没有把 `step90` 的负 `z_art` 现象修掉，
- 也没有把 `step80` 的正控制优势更好地留到 final。

### 3. 联合 replay 的大图景完全没变
把 `032 / 035 / 039 / 042 / 017 / 018 / 019 / 020 / 021 / 022` 一起看：
- `best_final_validation_experiment`
  - 仍是 `EXP-032 final`
- `best_final_e_evt_experiment`
  - 仍是 `EXP-032 final`
- `best_final_special_experiment`
  - 仍是 `EXP-021 final`
- gate replay 里：
  - `non_anchor_joint_beating_count = 0`

这表示：
- `D6` 没有把 `D4` 推成新的 anchor，
- 也没有让 gate 获得新的可选点。

## 当前结论
- `D6` 的技术结论是正的：
  - `z_smooth` late decay 机制已成功接入，且 schedule 确实执行。
- 但实验结论是否定的：
  - 这条机制没有带来可解释、可复现的行为级收益。
- 当前证据更支持：
  - `D4` 剩余的 `z_art` 瓶颈，
  - 并不是简单由“late `z_smooth` 权重太高”单独造成。

## 当前建议
1. 不把 `D6` 升为新的默认配置。
2. 不继续优先扩展更多纯 `z_smooth` schedule sweep。
3. `clause_ge4` 线的默认基线仍保持：
   - `D4`
4. 下一轮若继续，优先方向应改为：
   - 更显式的 `z_art` 保留机制
   - 或更明确的 dual-control-preservation 约束
5. 在没有新证据前，`EXP-032 final` 仍保持全局 anchor。
