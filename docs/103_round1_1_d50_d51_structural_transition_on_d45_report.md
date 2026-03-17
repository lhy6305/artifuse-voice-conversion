# `round1.1 / D50-D51 / structural transition supervision on D45 family` 报告

## 目的
- `D48 / D49` 已经说明:
  - `D45` 路线上的 late teacher softweight 不起杠杆
  - late-only punctuation supervision 只有极轻微 tradeoff
- 因此这轮继续沿“更强的 formal special supervision”方向走，
  但优先选现成能力里最小的 boundary-local 方案:
  - 把历史上已经实现过的 `structural_clause_transition_aux`
  - 挂到 `D45 = D33 step10 -> D29 final` 这条 teacher-family 路线上

这轮分成两步:
- `D50 = D45 + late-only structural_clause_transition_aux`
- `D51 = D50 + late structural secondary slot`

先说人话:
- `D50` 是在问:
  - 如果只把这条 boundary-local supervision 放上去，
    它本身有没有杠杆
- `D51` 是在问:
  - 如果 `D50` 只是吃不到样本，
    那补一口最小 late structural exposure 后会不会变好

## 配置设计
### D50
- 配置:
  - `configs/offline_mvp_train_d50_round1_1_d7_init_phase_teacher_family_structural_transition_late_only_d33step10_to_d29_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-003-offline-mvp-d50-round1-1-d7-init-phase-teacher-family-structural-transition-late-only-d33step10-to-d29-20step-calibration`
- 设计:
  - teacher family 完全保持 `D45`
  - sampler 完全保持 `D45`
  - 新增:
    - `structural_clause_transition_aux.pool_memberships = ["structural_clause_ge4"]`
    - `weight = 0.18`
    - `weight_schedule = step11 -> step15 linear ramp`

### D51
- 配置:
  - `configs/offline_mvp_train_d51_round1_1_d7_init_phase_teacher_family_structural_transition_late_secondary_d33step10_to_d29_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-004-offline-mvp-d51-round1-1-d7-init-phase-teacher-family-structural-transition-late-secondary-d33step10-to-d29-20step-calibration`
- 设计:
  - 保持 `D50` 的 aux
  - 保持 `D45` 的 teacher family
  - 只把 late sampler 改成:
    - `priority_ratio = 0.5`
    - primary 仍是 `challenge_proxy_core + short_pause_no_terminal`
    - `secondary_sampling.max_slots = 1`
    - `secondary_sampling.priority_pool_memberships = ["structural_clause_ge4"]`

## 关键事实
### 1. `D50 step10` 精确复刻 `D45 step10`
- `D50 step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
- 与 `D45 step10` 完全一致

解释:
- 这说明:
  - early phase 没被误改
  - 当前观察到的差异都只来自 late structural supervision

### 2. `D50` 的 late structural aux 不是挂空，但 final 仍精确复刻 `D45`
- 训练日志里:
  - `step14 loss_structural_clause_transition_aux = 0.182235`
- 说明新 aux 确实在 late phase 命中过目标 batch
- 但结果:
  - `D50 final = 2.503763 / 0.133735 / 3.196203 / 0.407221`
- 对比 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
  - 仍是数值级重合

解释:
- 这说明:
  - 把 boundary-local structural transition supervision 直接挂到 `D45`
  - 本身不足以形成新杠杆
- 现在这条线给出的口径更接近:
  - 机制有机会命中
  - 但单次命中对 `D45` 的终点几乎没有推动力

### 3. `D51` 明确补足了 late structural exposure，而且轨迹确实被改动了
- dry-run 已确认:
  - late `phase_priority_record_count = 204`
- 训练日志里 late phase 多次出现非零:
  - `step12 loss_structural_clause_transition_aux = 0.128683`
  - `step19 = 0.166892`
  - `step20 = 0.194475`

解释:
- `D51` 不是“secondary slot 看起来加了，其实没进去 batch”。
- 它在 late phase 已经稳定地把 structural supervision 拖进训练。

### 4. 但 `D51` 的最终形状还是 validation-first 滑移，不是新的 compromise
- `D51 final = 2.493466 / 0.148358 / 3.130833 / 0.403129`
- 对比 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`

相对 `D45`:
- validation 改善 `-0.010289`
- special 退化 `+0.014642`
- `e_evt` 退化 `-0.065476`
- `z_art` 退化 `-0.004104`

解释:
- 这不是 `D45` 上的“更强 special supervision 带来更好平衡”。
- 更像是:
  - 一旦补足 late structural exposure
  - 轨迹又会沿熟悉的方向往 validation-first 滑
  - 同时回吐一部分 special / control

## 当前结论
1. `D50` 说明:
   - `D45 + late-only structural_clause_transition_aux`
   - 本身没有形成新杠杆
2. `D51` 说明:
   - 即使补最小 late structural exposure
   - 这条 boundary-local family 在 `D45` 路线上也没有长成更好 compromise
   - 只会把轨迹再次推向 validation-first
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
4. `D45` 仍是 post-D41 family 里最值得引用的 compromise 点；
   `D50 / D51` 都没有改写这一点

## 当前建议
1. 暂停继续做 `D45` 上的 `structural_clause_transition_aux` 小变体:
   - 纯 weight sweep
   - 纯 late secondary slot sweep
   - 纯 phase step 位 sweep
2. 若继续推进，不该再继续拿现有 sidecar-pool 的 boundary-local family 做微调；
   更值得转向:
   - 更强的 late teacher family decomposition
   - 或真正新的 frame-local formal special supervision 定义
3. 固定交接入口已刷新到 `after D51`:
   - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
