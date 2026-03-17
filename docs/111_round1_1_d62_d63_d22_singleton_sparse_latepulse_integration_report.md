# 111. round1.1 `D62-D63 / D22 backbone singleton sparse late-pulse integration` 报告

## 背景
- 在 `D60 / D61` 已确认 `singleton sparse proxy` principle 本身有效之后，
  当前问题转成:
  - 能否把这条 principle 接到更强 validation backbone(`D22`) 上，
  - 同时保住 `D22` 的 minimax 地位，
  - 而不是继续停留在 `D60` 的 validation tax。
- 为此本轮先后做了两条 `D22 backbone` 集成线:
  - `D62`: `D22 + step21-30 singleton late pulse`
  - `D63`: 在 `D62` 基础上再把 `teacher_consistency` late phase 对齐到 singleton strict cohort

## 实验设计
### `D62`
- 配置:
  - `configs/offline_mvp_train_d62_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_30step_smallscale_seeded_shuffle.json`
- 设计要点:
  - backbone 保持 `D22`
  - `step1-20`:
    - `teacher_consistency = challenge_proxy_core`
    - `targeted_sampling = challenge_proxy_core`
  - `step21-30`:
    - `targeted_sampling -> micro_pause_none_singleton_strict`
    - 打开 `singleton_sparse_proxy_aux`
    - `teacher_consistency` 仍保持 `challenge_proxy_core`

### `D63`
- 配置:
  - `configs/offline_mvp_train_d63_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_teacheraligned_30step_smallscale_seeded_shuffle.json`
- 设计要点:
  - 与 `D62` 唯一原则差异:
    - `step21-30 teacher_consistency`
      也切到 `micro_pause_none_singleton_strict`
    - 并附加:
      - `required_within_special_duration_ceiling = true`
      - `required_utterance_structure_types = ["other"]`
      - `required_final_terminal_types = ["none"]`

## 结果
### final
- `D22 = 2.444194 / 0.140001 / 3.299035 / 0.438936`
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D62 = 2.42375 / 0.234048 / 2.603584 / 0.316145`
- `D63 = 2.42375 / 0.234048 / 2.603584 / 0.316145`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

### `D62` checkpoint trajectory
- `step10 = 2.592379 / 0.174415 / 2.891888 / 0.414234`
- `step20 = 2.51054 / 0.162702 / 2.988662 / 0.397983`
- `step30 = 2.42375 / 0.234048 / 2.603584 / 0.316145`

### `D63` 与 `D62` 的直接比较
- `D63 final` 与 `D62 final` 四项完全一致
- `D63 checkpoint series` 与 `D62 checkpoint series` 三个检查点完全一致
- 两者训练 `step1-30 loss_total` 轨迹逐点一致
- 两者 `step21-30 loss_singleton_sparse_proxy_aux` 逐点一致:
  - `0.353602 / 0.355703 / 0.335321 / 0.351439 / 0.327014 / 0.333778 / 0.344203 / 0.35263 / 0.350737 / 0.326509`

## 解释
- `D62` 说明:
  - 把 singleton sparse late pulse 直接接到 `D22 backbone`
  - 不会形成更强 minimax anchor
  - 反而会把 final trajectory 继续压向:
    - 更低 validation
    - 但明显更差的 special / `e_evt` / `z_art`
- 更具体地说，相对当前 route anchor `D22`:
  - validation 改善 `-0.020444`
  - 但 special 恶化 `+0.094047`
  - `zero_e_evt` 下滑 `-0.695451`
  - `zero_z_art` 下滑 `-0.122791`
- `D63` 进一步说明:
  - 把 late `teacher_consistency` 也对齐到 singleton strict cohort
  - 在这条 `D22 + late pulse` family 上仍然是近似 no-op
  - 当前坏轨迹不能简单解释成:
    - `core-only teacher` 与 singleton late sampler 的相位错配

先说人话:
- `D60` 证明了 principle 是对的。
- `D62` 证明了把这条 principle 硬接到 `D22` 后半段，形状不对。
- `D63` 又证明这不是“teacher late gate 没跟上”这么简单。

## route 结论
- 新 selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d62_d63_default_minimax/`
- 结果仍为:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`
- 新 final comparison:
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_d62_d63_default_minimax/`
- `D62 / D63` 都没有进入当前正式 handoff 的可替换区间

## 当前阶段正式结论
1. `singleton sparse proxy` principle 仍然有效，但当前有效集成形状不在 `D22 backbone + late pulse` 这条线上。
2. `D22 + singleton late pulse` family 暂停继续追加预算。
3. `teacher-aligned late gate` 在这条 family 上也是 no-op，不值得继续做同轴小排列。
4. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 下一步
- 若继续削减 singleton principle 的 validation tax，优先回到:
  - `D60` 这一类已被验证有效的 post-`D59` backbone
  - 再做更短、更弱或 checkpoint-selected 的 late tail
- 不再优先做:
  - `D22 backbone` 上的 singleton late pulse 变体
  - 同 family 的 late teacher gate 微调
