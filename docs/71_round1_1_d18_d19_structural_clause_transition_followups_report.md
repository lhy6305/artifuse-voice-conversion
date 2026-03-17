# `round1.1 / D18+D19 / structural_clause_transition follow-ups` 报告

## 目的
- 在 `D17` 证明 sample-level structural profile 无法改写 `D7` 轨迹后，
- 继续验证更高分辨率的 boundary-local 结构监督是否值得推进。
- 本轮聚焦 `structural_clause_ge4` 上的 late-only `structural_clause_transition_aux`。

## 代码与配置
### 新增代码
- `src/v5vc/offline_mvp/losses.py`
  - 新增 `structural_clause_transition_aux`
  - 复用 clause-transition 边界目标，但通过 `target_special_supervision.pool_memberships` 只作用于 `structural_clause_ge4`
- 同步更新:
  - `src/v5vc/train_entry.py`
  - `src/v5vc/special_eval.py`
  - `src/v5vc/ablation_eval.py`
  - `src/v5vc/special_eval_series.py`

### D18
- 实验:
  - `EXP-20260315-035-offline-mvp-d18-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-transition-late-only-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d18_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_transition_late_only_smallscale_100_seeded_shuffle.json`
- 核心变化:
  - 保留 `D7` sampler 与 `z_art_influence_aux`
  - 新增 `structural_clause_transition_aux.pool_memberships = ["structural_clause_ge4"]`
  - `weight = 0.18`
  - `weight_schedule = step61-80 linear ramp to 0.18`

### D19
- 实验:
  - `EXP-20260315-036-offline-mvp-d19-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-transition-late-only-late-clause-tail-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d19_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_transition_late_only_late_clause_tail_smallscale_100_seeded_shuffle.json`
- 相对 `D18` 的唯一额外变化:
  - 在 `step61-100` 新增 `priority_ratio = 0.125`
  - `priority_pool_memberships = ["structural_clause_ge4"]`
  - 用显式 late clause tail 强制增加 `structural_clause_ge4` 曝光

## 关键结果
### 1. `D18` 不是挂空配置，但只形成 `D7` 近似重跑
- `D18 step90` 训练日志:
  - `loss_structural_clause_transition_aux = 0.126826`
  - effective `weight = 0.18`
- 说明新 aux 在 late window 确实命中过一次目标 batch
- 但 `D18 final`:
  - `target_validation.loss_total = 2.729923`
  - `target_special_eval.delta_loss_total = -0.002973`
  - `zero_e_evt.delta_target_loss_total = 3.490768`
  - `zero_z_art.delta_target_loss_total = 0.599433`
- 对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - 几乎是数值级重合
- `D18 late-window` 也近似重合:
  - `step80 = 3.68858 / -0.306975 / 2.65965 / 1.084377`
  - `step90 = 3.42724 / -0.3432 / 2.807716 / 0.509011`
  - `step100 = 2.729923 / -0.002973 / 3.490768 / 0.599433`

### 2. `D18` 的真正问题不是“方向错了”，而是 late 曝光不稳定
- `D18 step80`:
  - `loss_structural_clause_transition_aux = 0.0`
- `D18 step90`:
  - `loss_structural_clause_transition_aux = 0.126826`
- `D18 step100`:
  - `loss_structural_clause_transition_aux = 0.0`
- 这说明:
  - 新 aux 能生效
  - 但在原始 `D7` sampler 上，late window 并不会稳定持续吃到 `structural_clause_ge4`
- 所以仅凭 `D18` 还不能下“这个 family 完全没杠杆”的最强结论

### 3. `D19` 明确强制 late structural exposure，但结果更差
- `D19 train_plan` 已确认:
  - `phase_priority_record_counts` 末段新增 `priority_record_count = 185`
  - 整体训练时长从 `D18` 的 `17.357207s` 增到 `44.900339s`
- 这说明:
  - `step61-100` 的 `structural_clause_ge4` late tail 不是挂空
  - 训练流程确实被迫更多经过 structural pool
- 但 `D19 final`:
  - `target_validation.loss_total = 2.84661`
  - `target_special_eval.delta_loss_total = 0.219234`
  - `zero_e_evt.delta_target_loss_total = 2.363735`
  - `zero_z_art.delta_target_loss_total = 0.441742`
- 对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - validation 变差
  - final special 直接翻正
  - `e_evt / z_art` 都明显回落

### 4. `D19` 给出了比 `D18` 更硬的负证据
- `D19 late-window`:
  - `step80 = 3.918003 / -0.278947 / 1.734595 / 0.737025`
  - `step90 = 3.418923 / -0.069672 / 2.527362 / 0.458825`
  - `step100 = 2.84661 / 0.219234 / 2.363735 / 0.441742`
- 解释:
  - 即使强行把 `structural_clause_ge4` 拖进 late phase，
  - 也没有让 boundary-local structural target 形成新的主线解，
  - 反而把 final 推向更差的 validation / special / control 平衡

## 当前结论
- `structural_clause_transition_aux` 工程上是成立的。
- `D18` 说明它可以命中 late structural batch，但不足以把 `D7` 推出原有轨迹。
- `D19` 进一步说明，即使显式强制 late structural exposure，这条 family 也不会自动变成新杠杆，反而更可能推坏 final。

## 当前建议
1. 保留 `structural_clause_transition_aux` 代码，但不继续优先扩展这条 family。
2. 不把 `D18 / D19` 升为默认方案。
3. 暂不继续优先做:
   - `structural_clause_transition_aux` 纯 weight sweep
   - `structural_clause_transition_aux` 纯启动步位 sweep
   - `structural_clause_ge4` 纯 late-tail sweep
4. 当前若继续推进“新目标形状 / 更强监督变化”，应转向:
   - 更高层级的 supervision-definition 跳变
   - 或不同的 phase / training decomposition
   - 而不是继续在现有 sidecar-pool 上做 boundary-local 小变体
