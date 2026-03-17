# `round1.1 / D54-D55 / teacher-family fused-hidden follow-up + gate-target linkage` 报告

## 目的
- `D52 / D53` 已经说明:
  - late teacher checkpoint decomposition 确实有微弱调形能力
  - 但只在 `D45` 附近形成 epsilon 级 tradeoff
- 因此这轮继续沿“teacher family 与 phase-specific target-shape / gate 的更强联动”推进，
  但仍保持纯配置最小改动:
  - `D54 = D52 + late fused-hidden`
  - `D55 = D53 + mid short-pause fused-hidden -> late core-only no-fused linkage`

先说人话:
- `D54` 在问:
  - 如果 `D29 step10` 本身带一点 early-compromise 信息，
  - 那继续保留 fused-hidden target shape，会不会把这点优势放大
- `D55` 在问:
  - 如果再把 late phase 明确切成 `core-only + no fused-hidden`
  - 会不会把中段 tradeoff 收得更干净

## 配置设计
### D54
- 配置:
  - `configs/offline_mvp_train_d54_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29step10_late_fusedhidden_shortpause_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-008-offline-mvp-d54-round1-1-d7-init-phase-teacher-family-handoff-d33step10-to-d29step10-late-fusedhidden-shortpause-20step-calibration`
- 设计:
  - `step1-10`
    - 与 `D52` 相同
    - `D33 step10 + short_pause gate + fused_hidden`
  - `step11-20`
    - teacher source = `D29 step10`
    - gate 仍是 `challenge_proxy_core + short_pause_no_terminal`
    - 但 `fused_hidden_weight` 保持 `0.05`

### D55
- 配置:
  - `configs/offline_mvp_train_d55_round1_1_d7_init_phase_teacher_family_gate_target_linkage_d33step10_d29step10_fused_to_d29step20_core_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-007-offline-mvp-d55-round1-1-d7-init-phase-teacher-family-gate-target-linkage-d33step10-d29step10-fused-to-d29step20-core-20step-calibration`
- 设计:
  - `step1-10`
    - `D33 step10 + short_pause gate + fused_hidden`
  - `step11-15`
    - `D29 step10 + short_pause gate + fused_hidden`
  - `step16-20`
    - `D29 step20 + core-only gate + no fused_hidden`
  - targeted sampling 同步切为:
    - `step1-15 = challenge_proxy_core + short_pause_no_terminal`
    - `step16-20 = challenge_proxy_core`

## 关键事实
### 1. `D54 / D55 step10` 仍精确复刻 `D45 step10`
- `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`

解释:
- early anchor 没被破坏。
- 当前差异全部来自 late/mid-late teacher-family linkage。

### 2. `D54` 的 late fused-hidden 不是挂空配置
- `step11 effective_teacher_consistency.teacher_checkpoint_path`
  - 已切到 `D29 step10`
- 同时:
  - `fused_hidden_weight = 0.05`

解释:
- 这轮不是“仍然只是 `D52`，但配置里多写了一行 fused-hidden”。
- late `D29 step10 + fused_hidden` 确实进了训练。

### 3. `D54` 给出了这组 follow-up 里最好的微小 compromise，但量级仍很小
- `D54 final = 2.505569 / 0.131888 / 3.199683 / 0.412614`

对比 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`:
- validation 更差 `+0.001814`
- special 更好 `-0.001828`
- `e_evt` 更强 `+0.003374`
- `z_art` 更强 `+0.005381`

对比 `D52 final = 2.506383 / 0.131541 / 3.201443 / 0.411876`:
- validation 略好 `-0.000814`
- special 略差 `+0.000347`
- `e_evt` 略弱 `-0.00176`
- `z_art` 略强 `+0.000738`

解释:
- late fused-hidden 在 `D29 step10` 上不是完全没作用。
- 它把 `D52` 向更低 validation / 更高 `z_art` 的方向轻推了一点。
- 但整体仍只是在 `D45 / D52` 附近做小数点后三位级别的再平衡。

### 4. `D55` 的更强 phase-specific gate-target linkage 也是真实生效的
- `step16 effective_teacher_consistency.teacher_checkpoint_path`
  - 已切到 `D29 step20`
- `step16 fused_hidden_weight = 0.0`
- `step16` 的 late teacher gate 也已缩回:
  - `pool_memberships = ["challenge_proxy_core"]`
- dry-run 已确认:
  - targeted sampling `phase_priority_record_counts = 19 -> 16`

解释:
- 这轮不是“更强 linkage 其实没接上”。
- `D55` 的 teacher / gate / sampler 三者联动切换都是真的。

### 5. 但 `D55` 只是把 `D54` 的微弱收益又回吐掉了
- `D55 final = 2.506311 / 0.133216 / 3.190822 / 0.405426`

对比 `D54 final`:
- validation 更差 `+0.000742`
- special 更差 `+0.001328`
- `e_evt` 更弱 `-0.008861`
- `z_art` 更弱 `-0.007188`

解释:
- 这说明:
  - 把 mid/late phase 再做成更强的 gate-target linkage
  - 并没有把 `D54` 收敛成更好的 final
- 更像是:
  - 把 `D54` 那点 epsilon 级收益重新抹平

### 6. `D55` 被 `D54` 直接压住，当前 route 仍未改写
- 在 `D54 / D55` 这组里:
  - `D54` 已经整体优于 `D55`
- 在全局 comparison 中:
  - validation leader 仍是 `D29`
  - default minimax 仍是 `D22`
  - special / `e_evt` / `z_art` leader 仍是 `D33`

解释:
- 这轮能得到的最强结论不是“发现新 route”。
- 而是:
  - `late fused-hidden` 在 `D29 step10` 上还有一点点微调空间
  - 但再继续加更强的 phase linkage，并不会自然突破当前三锚

## 当前结论
1. `D54` 说明:
   - `D29 step10` 晚段如果继续保留 `fused_hidden`
   - 会在 `D45 / D52` 附近形成一个新的 epsilon 级 compromise
   - 但量级仍远不足以改写 route policy
2. `D55` 说明:
   - 更强的 phase-specific gate-target linkage
   - 在当前 teacher family 下不会进一步放大 `D54` 的收益
   - 反而会把它回吐成更弱点
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做:
   - `D29 step10` late fused-hidden 小 weight sweep
   - `D55` 这种 mid/late gate-target linkage 时点小排列
2. 若继续走 teacher 路线，更值得转向:
   - 真正新的 frame-local formal special supervision
   - 或更强的 teacher family + supervision 联合定义，而不是只调 phase 排布
3. 固定交接入口应刷新到 `after D55`:
   - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
