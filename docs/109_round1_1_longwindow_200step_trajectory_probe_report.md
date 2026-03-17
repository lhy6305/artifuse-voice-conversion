# `round1.1 / 200step long-window trajectory probe` 报告

## 目的
- `post-D59` 诊断已经说明:
  - `D56-D59` 的主要矛盾不是“命中率还差一点”
  - 而是 proxy principle mismatch
- 但还有一个独立问题没有正式落盘:
  - 当前 `20/30 step` quick-screen 终点，是否截断了关键 late dynamics
  - 如果把代表路线拉到更长窗口，route 会不会被改写
- 这轮不再扩新教法，先做最小长窗观测:
  - `D22` 代表当前 `default_minimax`
  - `D33` 代表当前 `special / e_evt / z_art`
  - `D59` 代表当前已被怀疑原则错位的 formal-special 线

先说人话:
- 这轮不是要立刻换默认冠军。
- 是要先看 200 step 以后，这几条线到底会往哪边滑。
- 免得把 quick-screen 的截断点误当成真正终点。

## 配置与实验
### D22 / default-minimax probe
- 配置:
  - `configs/offline_mvp_train_d22_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_smallscale_200_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration`

### D33 / special-control probe
- 配置:
  - `configs/offline_mvp_train_d33_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_fused_hidden_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration`

### D59 / formal-special probe
- 配置:
  - `configs/offline_mvp_train_d59_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_teacher_gate_late_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration`

### 通用执行
- 三条线均完成:
  - `200 step` 正式训练
  - final `special_eval`
  - final `ablation_eval`
  - `checkpoint_series`
  - `special_eval_series(step50/100/150/200)`
- 额外产出:
  - 六实验 mixed-horizon `route_selection`
  - 六实验 final comparison

## 关键事实
### 1. `200 step` 成本很低，适合作为 trajectory probe
- `D22` 训练耗时约 `19.55s`
- `D33` 训练耗时约 `17.35s`
- `D59` 训练耗时约 `17.14s`

解释:
- 这说明长窗探针不是重成本动作。
- 后续若只给少数代表路线补长窗，工程代价是可控的。

### 2. 三条线在 `50 -> 100 -> 150 -> 200` 都持续往 validation-first 滑，没有出现 late special 回摆
- `D22`
  - validation: `2.358588 -> 2.251363 -> 2.16706 -> 2.125622`
  - special delta: `0.177657 -> 0.210452 -> 0.230214 -> 0.238578`
  - `zero_e_evt`: `2.773641 -> 2.135677 -> 1.960466 -> 1.864222`
- `D33`
  - validation: `2.372053 -> 2.249853 -> 2.168489 -> 2.122699`
  - special delta: `0.184745 -> 0.203847 -> 0.229425 -> 0.239846`
  - `zero_e_evt`: `2.874014 -> 2.354133 -> 2.032546 -> 1.9703`
- `D59`
  - validation: `2.329353 -> 2.208258 -> 2.146063 -> 2.126544`
  - special delta: `0.198428 -> 0.22892 -> 0.252575 -> 0.258922`
  - `zero_e_evt`: `2.590052 -> 2.069441 -> 1.971437 -> 1.927875`

解释:
- 这轮没有看到“前面只是太短，所以 special 没来得及起来”。
- 相反，late dynamics 很明确:
  - validation 持续变好
  - special 持续变差
  - `e_evt` 持续变弱

### 3. `D22` 和 `D33` 到 `step200` 基本收敛成同一类 validation-first 终点
- `D33 step200`
  - `2.122699 / 0.239846 / 1.9703 / 0.710849`
- `D22 step200`
  - `2.125622 / 0.238578 / 1.864222 / 0.669467`
- 相对 `D33 step200`
  - `D22` validation 仅差 `+0.002923`
  - special 略好 `-0.001268`
  - `e_evt` 略弱 `-0.106078`
  - `z_art` 略弱 `-0.041382`

解释:
- quick-screen 阶段里那种更清楚的 `D22 vs D33` route 分工，
  到 `step200` 已经被明显压扁了。
- 长窗 final point 更像“同一类 validation-first compromise 的细微变体”，
  不再像一个好的 balanced-route 选点。

### 4. `D59` 拉到 `200 step` 也没有自我修复
- `D59 step200`
  - `2.126544 / 0.258922 / 1.927875 / 0.311379`
- 相对 `D33 step200`
  - validation 仅差 `+0.003845`
  - special 更差 `+0.019076`
  - `e_evt` 更弱 `-0.042425`
  - `z_art` 明显更弱 `-0.39947`

解释:
- 这说明:
  - `D59` 不是“窗口还不够长”
  - 而是原则本身仍不对路
- 所以继续给 `D59` 同 family 拉更长步数，不像高信息量下一手。

### 5. mixed-horizon route selector 会直接塌成 `validation_strict`
- 在旧锚点:
  - `D22(30step)`
  - `D29(20step)`
  - `D33(20step)`
- 与新长窗:
  - `D22(200step)`
  - `D33(200step)`
  - `D59(200step)`
- 六实验混合比较下，selector 给出:
  - `selected_policy = validation_strict`
  - `selected_anchor = D33(200step)`
  - `budget_to_minimax_anchor = 0.321495`

解释:
- 这不应被解读成“官方 route 应立刻刷新到 D33-200”。
- 真正说明的是:
  - 旧 `20/30 step` quick-screen anchor
  - 和 `200 step` trajectory probe final
  - 不能直接放进同一个 `default_minimax` selector 里混选
- 否则 validation 预算会被 horizon 差异直接吞掉，语义塌成纯 validation 选路。

## 当前结论
1. `200 step` 已经证明:
   - 当前 quick-screen 并没有错过一个 late special breakout
   - late dynamics 的主方向反而是持续 validation-first
2. `D59` 在长窗下仍然不给翻盘证据:
   - 它依旧更像原则错位的负结果封口
   - 不是应继续加步数挖掘的主线
3. `D22 / D33` 到 `step200` 的 final 点明显收敛:
   - 长窗更适合做 trajectory probe
   - 不适合直接拿 final point 替换当前 balanced handoff anchor
4. 当前固定 handoff / stage-report 不应直接刷新到这批 `200 step` final:
   - 这批结果是“长窗观测结论”
   - 不是“新的正式默认 route”

## 当前建议
1. 继续保留当前 `20/30 step` anchor 体系作为:
   - quick screen
   - 正式 handoff / stage-report 默认入口
2. 后续实验制度改成两段式更合理:
   - 先用 quick-screen 看方向
   - 再只给少数代表路线补 `200 step` trajectory probe
3. 若继续推进 `post-D59` 新方向，
   优先在 quick-screen 里先验证:
   - `clause-free singleton sparse-frame supervision`
   - 或更贴近 `micro_pause_none_singleton_strict` 的新 proxy principle
4. 若后续还要做长窗选点，
   优先考虑:
   - matched-horizon comparison
   - 或 checkpoint-selected late stop
   - 不再把 `20/30 step` final 和 `200 step` final 直接混进同一个默认 selector

## 产物
- `reports/training/offline_mvp_d22_200step_exp013/`
- `reports/training/offline_mvp_d33_200step_exp015/`
- `reports/training/offline_mvp_d59_200step_exp014/`
- `reports/eval/offline_mvp_checkpoint_series_d22_200step_exp013/`
- `reports/eval/offline_mvp_checkpoint_series_d33_200step_exp015/`
- `reports/eval/offline_mvp_checkpoint_series_d59_200step_exp014/`
- `reports/eval/offline_mvp_special_eval_series_d22_200step_exp013/`
- `reports/eval/offline_mvp_special_eval_series_d33_200step_exp015/`
- `reports/eval/offline_mvp_special_eval_series_d59_200step_exp014/`
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d29_d33_d59_default_minimax/`
- `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d29_d33_d59_default_minimax/`
