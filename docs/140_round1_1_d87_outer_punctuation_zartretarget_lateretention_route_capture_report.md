# 140. round1.1 `D87 / outer punctuation z_art-retarget late-retention 200-step` 报告

## 背景
- `D86` 已经说明:
  - outer punctuation + outer-pool `z_art` retarget
    确实能在 `step150` 形成更强的 dual-control 形状
  - 但该形状在 `150 -> 200`
    仍被明显洗掉
- 因此本轮不再换 family，
  也不做新的近邻 sweep，
  只验证一个更直接的问题:
  - 如果把 `z_art_influence_aux`
    的 late window 从短程 ramp
    延长到整个 `200-step`，
    能不能把 `D86 step150` 的形状
    更稳定地保到 final

## 本轮设计
### `D87`
- 配置:
  - `configs/offline_mvp_train_d87_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_lateretention_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration`
- 相对 `D86` 的唯一主改动:
  - `losses.z_art_influence_aux.weight_schedule.end_step`
    - `25 -> 200`
- 保持不变:
  - outer punctuation expansion pool
  - late `D22` teacher
  - strict singleton primary sampler
  - `secondary_sampling -> micro_singleton_anypunct_expansion`
  - `200-step`

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
  - 单实验 `checkpoint_selection(late075)`
  - 单实验 `checkpoint_gate_replay(late075)`
  - `D22 / D33 / D59 / D76 / D85 / D86 / D87`
    联合 `checkpoint_selection(late075)` / `checkpoint_gate_replay(late075)`
  - `D87 step150 synthetic anchor` 物化
  - minimal / full long-horizon route 对照

## 指标口径
- shorthand final 继续记为:
  - `ablation baseline target_validation / special_delta / zero_e_evt / zero_z_art`
- route 判断继续使用:
  - `target_special_eval_model.target_validation.loss_total`

## `D87` final
- shorthand final:
  - `D87 = 2.127392 / 0.230457 / 4.197220 / 2.611827`
- route validation 列:
  - `2.131434`

- `step50 = 2.314084 / 0.184908 / 4.917752 / 2.597331`
- `step100 = 2.213228 / 0.208162 / 4.411053 / 2.554730`
- `step150 = 2.166759 / 0.221860 / 4.497677 / 2.665073`
- `step200 = 2.127392 / 0.230457 / 4.197220 / 2.611827`

### 对 `D86 final` 的直接比较
- `D87 - D86`:
  - validation `-0.002627`
  - special `-0.001113`
  - `zero_e_evt` `+0.250406`
  - `zero_z_art` `+0.086222`

### 对 `D85 final` 的直接比较
- `D87 - D85`:
  - validation `-0.001914`
  - special `-0.000838`
  - `zero_e_evt` `+0.040563`
  - `zero_z_art` `+0.048639`

解释:
- `D87 final` 不是把 `z_art` top floor 从 `D33` 手里抢走。
- 但它相对 `D85 / D86 final`
  已经同时改善了:
  - validation
  - special
  - `e_evt` floor
  - `z_art` floor
- 也就是说，
  late-retention 这次没有把 `step150` 全量保到 final，
  但它确实把一部分 dual-control 形状
  吞进了 final。

## `D87 step150` late-stop 结果
- `D87 step150 - step200`:
  - validation `+0.036557`
  - special `-0.008597`
  - `zero_e_evt` `+0.261090`
  - `zero_z_art` `+0.013879`

解释:
- `D87 step150` 仍然是真实 late-stop option。
- 它没有像目标假设那样
  被完整“吸收到 final”。
- 但相对 `D86`，
  `step150 -> step200` 的回吐已经明显缩小:
  - `zero_z_art` 不再回吐 `+0.109394`
  - 而只剩 `+0.013879`

### 对 `D86 step150` 的直接比较
- `D87 step150 - D86 step150`:
  - validation `+0.011027`
  - special `-0.003590`
  - `zero_e_evt` `+0.144625`
  - `zero_z_art` `-0.006666`

解释:
- `D87 step150` 比 `D86 step150`
  更像:
  - special / `e_evt` 更强
- 但它没有继续扩大 `z_art`；
  `z_art` 反而略低一线。
- 更准确地说，
  `D87` 做到的是:
  - 把 `D86 step150` 的一部分 `e_evt + z_art` 形状
    吞进 final
  - 同时把 `step150` 本身
    推成更强的 family-level special / `e_evt` option

## 联合 late-stop replay 结果
- `D22 / D33 / D59 / D76 / D85 / D86 / D87`
  的 late-stop aggregate 为:
  - `mean_delta_vs_final_validation = +0.020441`
  - `mean_delta_vs_final_special = -0.005673`
  - `mean_delta_vs_final_e_evt = +0.119741`
  - `mean_delta_vs_final_z_art = +0.023462`

解释:
- 加入 `D87` 后，
  这组 late-stop aggregate 仍然保持:
  - `special` 正收益
  - `e_evt` 正收益
  - `z_art` 正收益
- 但它没有再把 late-stop layer
  推成一个新的强制 final 替代制度；
  更像是在把 checkpoint-option 层的优势
  向 final route 靠近。

## synthetic anchor route 结果
### 1. minimal family
集合:
- `D22 / D33 / D59 / D76 / D85 / D85step150 / D86 / D86step150 / D87 / D87step150`

结果:
- validation = `D76`
- special = `D87 step150`
- `zero_e_evt = D87 step150`
- `zero_z_art = D33`
- `default_minimax = D87`
- `budget_to_special_anchor = 0.060055`

解释:
- `D87 step150` 取代了:
  - `D85 step150` 的 minimal-family special 位置
  - `D86 step150` 的 minimal-family `zero_e_evt` 位置
- 更关键的是:
  - `D87 final`
    把 minimal-family 的 `default/minimax`
    从 `D33`
    正式改写成了自己

### 2. full long-horizon
集合:
- `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83 / D85 / D85step150 / D86 / D86step150 / D87 / D87step150`

结果:
- validation = `D76`
- special = `D82`
- `zero_e_evt = D87 step150`
- `zero_z_art = D33`
- `default_minimax = D87`
- `budget_to_special_anchor = 0.040968`

解释:
- `D87 final` 没有改写:
  - validation
  - special
  - `zero_z_art`
- 但它已经正式改写:
  - `default/minimax`
- 同时:
  - `D87 step150`
    把 checkpoint-option 层的 `zero_e_evt`
    继续前推到自己

## 当前阶段正式判断
1. `D87 final` 没有把 `z_art` top floor 从 `D33` 手里拿走。
2. 但 `D87 final` 已经把 long-horizon 的正式 `default/minimax`
   从 `D33` 改写成自己。
3. `D87 step150` 仍是有效 checkpoint-option，
   并且现在是:
   - minimal-family 的 `special + zero_e_evt` leader
   - full long-horizon 的 `zero_e_evt` leader
4. 更准确的制度写法应变成:
   - validation = `D76`
   - special = `D82`
   - `zero_e_evt checkpoint-option = D87 step150`
   - `zero_z_art = D33`
   - `default_minimax = D87`

## 收口判断
- 这轮单主线实验已经回答了前一阶段的核心问题:
  - 能不能把 `D86 step150` 的 late-window 形状
    至少部分保到 final，
    并形成制度级 final-route 影响
- 结论是:
  - 可以，且影响已经进入正式 `default/minimax`
- 因此:
  - 离线 MVP 验证环节已经具备收口条件
- 若没有额外外部约束，
  当前更合理的下一步不是继续扩训练分支，
  而是:
  - 冻结当前 route 口径
  - 输出 final handoff / stage report
  - 结束这一段 offline MVP validation

## 产物
- 配置:
  - `configs/offline_mvp_train_d87_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_lateretention_200step_smallscale_seeded_shuffle.json`
- 训练 / 评估:
  - `reports/training/offline_mvp/EXP-20260316-043.train_plan.json`
  - `reports/eval/offline_mvp_ablations_d87_exp20260316_043/`
  - `reports/eval/offline_mvp_special_eval_d87_exp20260316_043/`
  - `reports/eval/offline_mvp_checkpoint_series_d87_exp20260316_043/`
  - `reports/eval/offline_mvp_special_eval_series_d87_exp20260316_043/`
- checkpoint review:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_d87_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_d87_late075/`
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_d85_d86_d87_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_d85_d86_d87_late075/`
- synthetic anchor:
  - `reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.checkpoint-step150-anchor.metrics.json`
- route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_d86_d86step150_d87_d87step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_d86_d86step150_d87_d87step150_default_minimax/`
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_d86_d86step150_d87_d87step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_d86_d86step150_d87_d87step150_default_minimax/`
