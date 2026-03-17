# `round1.1 / D23 / teacher-consistency relaxed-gate follow-up` 报告

## 目的
- 在 `D22 = D7 init + D10 teacher` 已经证明 teacher-consistency family 有真实信号之后，
- 验证“把 teacher gate 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + challenge_proxy_relaxed`”
  是否能够进一步保住 formal special 与 `z_art`，
- 同时不牺牲 `D22` 已经拿到的强 validation / `e_evt`。

## 配置与实验
- 配置:
  - `configs/offline_mvp_train_d23_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_smallscale_30_seeded_shuffle.json`
- 正式实验:
  - `EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - `teacher_consistency.pool_memberships = ["challenge_proxy_core", "challenge_proxy_relaxed"]`
  - 其余 consolidation 机制与 `D22` 保持一致

备注:
- 本轮评估链的正式记录以 `EXP-...040` 为准。
- 早先一次手工假定 experiment id 的试跑产物不纳入正式结论。

## 关键结果
### 1. broadened teacher gate 确实接上了，但没有形成新的行为层级
- `D23 step1`
  - `loss_teacher_consistency = 0.029021`
- `D23 step10`
  - `loss_teacher_consistency = 0.078484`
  - `loss_teacher_event_consistency = 0.035911`
  - `loss_teacher_z_art_consistency = 0.042574`
- `D23 step30`
  - `loss_teacher_consistency = 0.387194`
  - `loss_teacher_event_consistency = 0.213799`
  - `loss_teacher_z_art_consistency = 0.173395`

解释:
- 这轮不是“relaxed gate 没生效”。
- broadened gate 在整个 30-step consolidation 里都持续 active。

### 2. `D23 final` 基本数值级复刻 `D22 final`
- `D23 final`
  - `target_validation.loss_total = 2.442024`
  - `target_special_eval.delta_loss_total = 0.142199`
  - `zero_e_evt.delta_target_loss_total = 3.289808`
  - `zero_z_art.delta_target_loss_total = 0.43533`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 仅略好 `-0.00217`
- final special 略差 `+0.002198`
- `e_evt` 略弱 `-0.009227`
- `z_art` 略弱 `-0.003606`

解释:
- `challenge_proxy_relaxed` 并没有把 `D22` 推到一个新的 Pareto 点。
- 更接近事实的描述是:
  - 它只是在 `D22` 附近做了一个极小幅抖动，
  - 没有产生新的 joint winner。

### 3. late-window 也没有给出“只是 final 选坏了”的借口
- `D23 step10 = 2.592393 / 0.135164 / 3.053715 / 0.419647`
- `D23 step20 = 2.471498 / 0.174403 / 3.042276 / 0.401863`
- `D23 step30 = 2.442024 / 0.142199 / 3.289808 / 0.43533`

解释:
- `step10` 虽然 special 比 final 稍好，
  但 validation 明显更差，且控制也没有形成新优势。
- `step20` validation 更强，但 special 进一步变差。
- 这说明 `D23` 不存在一个明显优于 `D22` 的隐藏 checkpoint。

### 4. 当前更准确的诊断，不再是“gate 太窄”，而是“`challenge_proxy_relaxed` 这层扩展不够有信息增益”
- `D21 / D22` 给出的诊断是:
  - 当前窄 gate 可能太窄
- `D23` 则补上了新的负证据:
  - 把 gate 直接扩到 `challenge_proxy_relaxed`
  - 并没有明显改善 formal special 或 `z_art`

这说明:
- teacher-consistency 大方向仍可保留
- 但“只做更宽的 challenge-adjacent coverage”并不自动等于更好的 teacher gate
- `challenge_proxy_relaxed` 这层扩展当前信息增益很低

## 当前结论
- `D23` 不值得升为默认方案。
- `D23` 也没有打赢 `D22`。
- 当前 teacher-consistency family 的有效结论更新为:
  - `D22` 仍是这一 family 里最有价值的点
  - `challenge_proxy_core -> challenge_proxy_core + challenge_proxy_relaxed` 的 coverage 扩展没有形成新杠杆

## 当前建议
1. 保留 `teacher_consistency` 能力，不回退代码。
2. 不把 `D23` 升为默认方案。
3. 暂不继续优先做:
   - `challenge_proxy_relaxed` 方向的更多 weight sweep
   - `challenge_proxy_relaxed` 方向的更多 coverage 扩展
4. 若继续沿 teacher-consistency family 推进，下一步更值得试:
   - 更有结构差异的 teacher gate
   - 例如 `challenge_proxy_core + short_pause_no_terminal`
   - 或直接改变蒸馏目标形状，而不是继续平铺更宽的 challenge-relaxed coverage
5. `D22` 暂时保持 teacher-consistency family 主参考点。

