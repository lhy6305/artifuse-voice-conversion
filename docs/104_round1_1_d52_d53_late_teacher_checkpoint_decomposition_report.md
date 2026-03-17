# `round1.1 / D52-D53 / late teacher checkpoint decomposition on D45 family` 报告

## 目的
- `D50 / D51` 已经说明:
  - 现有 sidecar-pool boundary-local structural family
  - 在 `D45` 路线上基本已经封口
- 因此这轮不再新增监督定义，
  而是按上一轮建议直接转向更强但仍最小的 late teacher family decomposition:
  - `D52 = D33 step10 -> D29 step10`
  - `D53 = D33 step10 -> D29 step10 -> D29 step20`

先说人话:
- 这轮不是再去抠 late gate / late aux。
- 而是在问:
  - `D45` 的 late teacher 会不会只是切得太晚、太硬
  - 如果把 `D29` family 自己拆成更细 checkpoint，
  - 能不能把 `D45` 推成更好的 compromise

## 配置设计
### D52
- 配置:
  - `configs/offline_mvp_train_d52_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29step10_shortpause_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-006-offline-mvp-d52-round1-1-d7-init-phase-teacher-family-handoff-d33step10-to-d29step10-shortpause-20step-calibration`
- 设计:
  - `step1-10`
    - teacher source = `D33 step10`
    - gate = `challenge_proxy_core + short_pause_no_terminal`
    - `fused_hidden_weight = 0.05`
  - `step11-20`
    - teacher source = `D29 step10`
    - gate 保持 `challenge_proxy_core + short_pause_no_terminal`
    - `fused_hidden_weight = 0.0`

### D53
- 配置:
  - `configs/offline_mvp_train_d53_round1_1_d7_init_phase_teacher_family_decomposition_d33step10_d29step10_d29step20_shortpause_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-005-offline-mvp-d53-round1-1-d7-init-phase-teacher-family-decomposition-d33step10-d29step10-d29step20-shortpause-20step-calibration`
- 设计:
  - `step1-10`
    - teacher source = `D33 step10`
    - gate = `challenge_proxy_core + short_pause_no_terminal`
    - `fused_hidden_weight = 0.05`
  - `step11-15`
    - teacher source = `D29 step10`
    - gate 保持 `challenge_proxy_core + short_pause_no_terminal`
  - `step16-20`
    - teacher source = `D29 step20`
    - gate 仍保持 `challenge_proxy_core + short_pause_no_terminal`

## 关键事实
### 1. `D52 / D53 step10` 都精确复刻了 `D45 step10`
- `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`

解释:
- early `D33 step10` anchor 这部分没有被误改。
- 所有差异都只来自 late teacher checkpoint decomposition。

### 2. `D52` 的 `step11` late teacher 切换是真实生效的
- `step11 effective_teacher_consistency.teacher_checkpoint_path`
  - 已切为 `D29 step10`
- `fused_hidden_weight`
  - 已降为 `0.0`

解释:
- 这轮不是“配置写了 `D29 step10`，训练里其实还在用 `D33 step10` 或 `D29 final`”。
- `D52` 的 late teacher source handoff 已真实接入闭环。

### 3. `D53` 的三段式 checkpoint decomposition 也是真实生效的
- `step15 effective_teacher_consistency.teacher_checkpoint_path`
  - 仍为 `D29 step10`
- `step16 effective_teacher_consistency.teacher_checkpoint_path`
  - 已切为 `D29 step20`

解释:
- 这轮不是“虽然写了三段式，但后两段其实没切开”。
- `D53` 的 `D29 step10 -> D29 step20` 渐进 handoff 是真的。

### 4. `D52` 只在 `D45` 附近形成一个 epsilon 级 tradeoff，不是 breakout
- `D52 final = 2.506383 / 0.131541 / 3.201443 / 0.411876`

对比 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`:
- validation 更差 `+0.002628`
- special 更好 `-0.002175`
- `e_evt` 更强 `+0.005134`
- `z_art` 更强 `+0.004643`

解释:
- `D29 step10` late teacher 不是完全没信息量。
- 它确实把 `D45` 稍微往 early compromise 那侧拽回了一点。
- 但这个量级非常小，
  远不到能改写 route policy 的程度。

### 5. `D53` 的三段式 decomposition 没有把 `D52` 再推开
- `D53 final = 2.505593 / 0.132377 / 3.198097 / 0.410493`

对比 `D52 final`:
- validation 略好 `-0.00079`
- special 略差 `+0.000836`
- `e_evt` 略弱 `-0.003346`
- `z_art` 略弱 `-0.001383`

解释:
- 三段式 handoff 的确切进去了，
  但只是在 `D52` 附近做了更小的再平衡。
- 它没有形成比 `D52` 更明显的新前沿，
  更没有把 `D45` 推成新的 default candidate。

### 6. `D52 / D53` 都没有改写当前三锚
- 在包含 `D52 / D53` 的 comparison 中:
  - validation leader 仍是 `D29`
  - default minimax 仍是 `D22`
  - special / `e_evt` / `z_art` leader 仍是 `D33`

解释:
- 这轮更接近:
  - 证明 `late teacher checkpoint decomposition` 确实有微弱调形能力
- 而不是:
  - 发现了新的 route winner

## 当前结论
1. `D52` 说明:
   - 把 `D45` 的 late teacher 从 `D29 step20` 换成 `D29 step10`
   - 会在 `D45` 附近形成一个很小的 special / `e_evt` / `z_art` tradeoff
   - 但量级只到 epsilon 级
2. `D53` 说明:
   - 即使再把 late family 拆成 `D29 step10 -> D29 step20`
   - 也不会自然长出新的 breakout 点
   - 只会在 `D52` / `D45` 附近继续做微小再平衡
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
4. 如果继续沿 teacher family 推进，
   不能再默认“只要再细分几个 late checkpoint，轨迹就会自然突破 `D45`”

## 当前建议
1. 暂停继续做:
   - `D45` 上的 late checkpoint 小步切分
   - `D29 step10 / step20` handoff 时点 sweep
2. 若继续走 teacher 路线，更值得转向:
   - teacher family 与 phase-specific target shape / gate 的更强联动
   - 或真正新的 frame-local formal special supervision
3. 固定交接入口应刷新到 `after D53`:
   - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
