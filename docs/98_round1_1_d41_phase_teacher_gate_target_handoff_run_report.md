# `round1.1 / D41 / phase-specific teacher gate-target handoff` 报告

## 目的
- `D38 / D39 / D40` 已经证明:
  - 仅靠 sampler handoff
  - 或 sampler handoff + teacher off
  还不足以把 `D33 step10` 收敛成新的 final joint winner
- 但那轮还没验证一个更强的假设:
  - 如果不仅改 sampler
  - 还显式让 `teacher_consistency` 自己按 phase 切换:
    - 早段保留 `short_pause` gate + fused-hidden target shape
    - 晚段退到 `core-only` gate + `event/z_art` target shape
  会不会比 `D38 / D40` 更有信息量

所以本轮只做一个最小但更强的 follow-up:
- `D41 = early broad teacher gate + fused_hidden`
- `late core-only teacher gate + no fused_hidden`

## 代码与配置
### 新增训练能力
- `src/v5vc/train_entry.py`
  - `teacher_consistency` 新增 `schedule_phases`
  - 支持按 step 覆盖:
    - `pool_memberships`
    - `weight`
    - `event_weight`
    - `z_art_weight`
    - `acoustic_weight`
    - `fused_hidden_weight`
  - 训练计划汇总里也会落出标准化的 `schedule_phases`

### D41
- 配置:
  - `configs/offline_mvp_train_d41_round1_1_d7_init_d10_teacher_consistency_phase_teacher_gate_target_handoff_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-058-offline-mvp-d41-round1-1-d7-init-d10-teacher-consistency-phase-teacher-gate-target-handoff-fused-hidden-20step-calibration`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - `step1-10`
    - sampler priority = `challenge_proxy_core + short_pause_no_terminal`
    - teacher gate = `challenge_proxy_core + short_pause_no_terminal`
    - `teacher_consistency.fused_hidden_weight = 0.05`
  - `step11-20`
    - sampler priority = `challenge_proxy_core`
    - teacher gate = `challenge_proxy_core`
    - `teacher_consistency.fused_hidden_weight = 0.0`

## 关键事实
### 1. `teacher_consistency.schedule_phases` 不是挂空配置
- dry-run 训练计划已记录:
  - `step1-10 = broad gate + fused_hidden`
  - `step11-20 = core-only + no fused_hidden`
- `step10` 日志中的 `effective_teacher_consistency` 仍为:
  - `pool_memberships = ["challenge_proxy_core", "short_pause_no_terminal"]`
  - `fused_hidden_weight = 0.05`
- `step11` 日志中的 `effective_teacher_consistency` 已切为:
  - `pool_memberships = ["challenge_proxy_core"]`
  - `fused_hidden_weight = 0.0`

解释:
- 这轮不是“phase-specific teacher 其实没生效”。
- teacher 自身的 gate 和 target shape 确实在 `step11` 成功切换了。

### 2. `D41 step10` 仍精确复刻了 `D33 step10`
- `D41 step10 special_eval = 2.621019 / 0.081505`
- `D41 step10 ablation = 3.224344 / 0.46347`
- 与 `D33 step10` 完全一致

解释:
- 更强的 phase-specific teacher 机制并没有破坏早段 special checkpoint。
- 它同样能把轨迹准确带到已知的 `D33 step10`。

### 3. 但 `D41 final` 仍然只回到了 `D38 / D40` 一类中间点
- `D41 final = 2.493233 / 0.163597 / 3.088342 / 0.435649`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.049039`
- special 更差 `+0.023596`
- `e_evt` 更弱 `-0.210693`
- `z_art` 略弱 `-0.003287`

对比 `D38 final = 2.494434 / 0.161978 / 3.096622 / 0.436892`:
- validation 仅略好 `-0.001201`
- special 略差 `+0.001619`
- `e_evt` 略弱 `-0.00828`
- `z_art` 略弱 `-0.001243`

对比 `D40 final = 2.492335 / 0.160804 / 3.102396 / 0.431034`:
- validation 略差 `+0.000898`
- special 略差 `+0.002793`
- `e_evt` 略弱 `-0.014054`
- `z_art` 略强 `+0.004615`

解释:
- `D41` 不是完全重放 `D38 / D40` 的同一个数字点，
- 但它仍然只回到了同一类中间盆地。
- 更明确地说:
  - phase-specific teacher gate/target handoff
  - 没有把 `D33 step10` 稳定落成新的 minimax 或新的 final joint winner

### 4. checkpoint / special series 同样没有给出“只是 final 选坏了”的借口
- `step10 = 2.621019 / 0.081505 / 3.224344 / 0.46347`
- `step20 = 2.493233 / 0.163597 / 3.088342 / 0.435649`

解释:
- `step10` 依然是更极端的 special-only checkpoint
- `step20` 才是这轮真正落地的 final
- 而 `step20` 的形状已经回到和 `D38 / D40` 很接近的中间点

### 5. route-context comparison 没有改写当前三锚
- 在 `D22 / D29 / D33 / D38 / D39 / D40 / D41` comparison 中:
  - validation leader 仍是 `D29`
  - default minimax 仍是 `D22`
  - special / `e_evt` / `z_art` leader 仍是 `D33`

解释:
- `D41` 没有改写当前 route
- 但它提供了一个更强的负结果:
  - 不是“teacher phase 没有切”
  - 而是“即使明确切了，同一 teacher family 仍不够”

## 当前结论
1. `teacher_consistency.schedule_phases` 已经真实接入代码和训练闭环。
2. `D41` 证明:
   - 更明确的 phase-specific teacher gate / target shape
   - 仍然不足以把 `D33 step10` 稳定收敛成新的 final winner。
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做“同一 `D10 teacher` 下的 phase-specific gate / weight / target-shape 小变体”。
2. 若继续推进 teacher 路线，更值得试:
   - phase-specific teacher checkpoint / teacher source
   - 而不是继续只改同一 teacher 的 mask 和 target 权重
3. 或者回到更强的 target-side supervision / gate 级重构，
   不再优先押注同一条 teacher family 的 phase 排布。
