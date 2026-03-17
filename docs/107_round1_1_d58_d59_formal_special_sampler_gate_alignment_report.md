# `round1.1 / D58-D59 / formal special sampler-gate alignment` 报告

## 目的
- `D56 / D57` 已说明:
  - `formal_special_clause_shape_aux` 工程上已经接通
  - 但 late exposure 太稀疏，几乎只在个别 step 命中
- 这轮不再改 aux 公式，也不再扫 role / weight 小排列
- 目标改成更硬的 `sampler / gate` 对齐:
  - 先把真正会给当前 `D57` formal aux 出梯度的 cohort 显式筛出来
  - 再看“稳定命中以后” final 轨迹到底会不会改写 route

先说人话:
- 这轮不是继续调教法。
- 是先把喂到嘴里的样本固定住。
- 这样能把“命中率问题”和“监督本身有没有杠杆”拆开。

## 代码与配置
### 新增代码能力
- `src/v5vc/offline_mvp/data.py`
  - `targeted_sampling` 新增 `required_within_special_duration_ceiling`
- `src/v5vc/offline_mvp/losses.py`
  - `build_special_supervision_sample_weights / mask`
    新增:
    - `min_clause_count`
    - `min_pause_boundary_count`
    - `min_terminal_boundary_count`
    - `required_within_special_duration_ceiling`
- `src/v5vc/train_entry.py`
  - 新字段已进入:
    - targeted sampling summary / schedule phase summary
    - teacher consistency runtime / effective summary

### D58
- 配置:
  - `configs/offline_mvp_train_d58_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_gate_late_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-011-offline-mvp-d58-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-gate-late-20step-calibration`
- 设计:
  - 基线沿 `D57`
  - late targeted sampling 从原来的 `19` 条 `core + short_pause` 候选
    收紧到 3 条显式 `priority_record_ids`
  - 这 3 条都满足:
    - `short_pause_no_terminal`
    - `clause_count >= 2`
    - `within_special_duration_ceiling = true`
    - `utterance_structure_type = other`
  - `formal_special_clause_shape_aux` 的 sample gate 也同步收紧到同一 cohort

### D59
- 配置:
  - `configs/offline_mvp_train_d59_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-012-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-20step-calibration`
- 设计:
  - 完全继承 `D58`
  - 只再把 late `teacher_consistency` gate 也收紧到同一 cohort

## 关键事实
### 1. 这次不是“感觉更准了”，而是 priority cohort 真的从 19 条收紧到了 3 条
- `D58 / D59 dry-run`
  - `phase_priority_record_counts = 19 -> 3`
- late phase 显式固定为:
  - `target::chapter3_2_firefly_191`
  - `target::chapter3_3_firefly_125`
  - `target::chapter3_3_firefly_148`

解释:
- 这说明:
  - sampler 已不再被 `short_pause_no_terminal` 的大量单 clause 样本稀释
  - late batch 里会稳定包含真正能激活当前 formal aux 的 3 条样本

### 2. `D58 / D59 step10` 仍精确复刻旧 anchor
- `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`

解释:
- early anchor 仍完全没被破坏。
- 当前差异全部来自 late sampler / gate alignment。

### 3. `D58` 已经把 formal aux 的 late hit 从“偶发”推成了“step11-20 全覆盖”
- `D58 step11-20`
  - `loss_formal_special_clause_shape_aux` 全部非零
  - 范围约为 `0.032209 -> 0.030982`
- 同时每个 late batch 都稳定带着那 3 条目标样本

解释:
- `D56 / D57` 那个“只有少数 late step 真命中”的问题，这轮已经工程上解决了。
- 这次不能再把结果解释成“只是没喂到样本”。

### 4. `D59` 的 teacher gate 也确实在 late phase 全程命中了同一 cohort
- `D59 step11-20`
  - `effective_teacher_consistency.pool_memberships = ['short_pause_no_terminal']`
  - `min_clause_count = 2`
  - `required_within_special_duration_ceiling = true`
- `loss_teacher_consistency`
  - 从 `step11 = 0.12287`
  - 降到 `step20 = 0.018237`

解释:
- 这说明:
  - 不是只有 sampler / formal aux 对齐了
  - 连 teacher pull 也已经被锁到同一批样本上

### 5. 但 final 依然没有往 special route 走，反而稳定滑向 validation-first compromise
- `D58 final = 2.480056 / 0.171798 / 2.994445 / 0.374825`
- `D59 final = 2.480048 / 0.171791 / 2.994481 / 0.374835`

对比 `D57 final = 2.505587 / 0.131861 / 3.199882 / 0.41264`:
- validation 明显更低
- 但 special 明显更差
- `e_evt / z_art` 也明显更弱

解释:
- 这次已经不是稀疏 exposure 问题。
- 是这条被稳定放大的 cohort，本身就更像 validation-first 方向，而不是 special-first 方向。

### 6. `D59` 几乎精确复刻 `D58`
- `D59` 相比 `D58`
  - validation 略好 `-0.000008`
  - special 略好 `-0.000007`
  - `e_evt` 略强 `+0.000036`
  - `z_art` 略差 `+0.00001`

解释:
- 当 sampler 和 formal gate 已经把这 3 条样本稳定喂满以后，
  再把 teacher gate 也对齐，并没有带来新的 regime。
- `D59` 只是 `D58` 的 epsilon 级重放。

### 7. final validation / special slice 上，formal aux 仍回到 0
- `D58 / D59`
  - final validation `loss_formal_special_clause_shape_aux = 0.0`
  - final special_eval `loss_formal_special_clause_shape_aux = 0.0`

解释:
- 一个合理推断是:
  - 当前 3 条训练 cohort 与 final special slice 的覆盖关系仍然太弱
  - 所以即使训练期命中稳定，final special behavior 也没有被直接拉动

### 8. 当前 route 仍未改写
- latest comparison 已扩到 `25` 个实验
- leaders 仍是:
  - `D29 = validation`
  - `D22 = default_minimax`
  - `D33 = special / e_evt / z_art`

## 当前结论
1. `D58 / D59` 已经把 `formal special` 这条线的 late exposure 问题工程上解决了:
   - late priority cohort `19 -> 3`
   - `step11-20` formal aux 全程非零
   - `D59` 的 teacher gate 也全程对齐同一 cohort
2. 但结果说明:
   - 这个被稳定放大的短样本 cohort
   - 会把轨迹推向更强 validation
   - 而不是推向更强 special / `e_evt` / `z_art`
3. 所以这轮最重要的结论不是“formal special 终于突破了”
   - 而是:
   - 当前这 3 条 `short_pause_no_terminal + clause>=2 + duration_ceiling` cohort
   - 不是我们要的 special-route 杠杆
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 保留这轮 sampler / gate 过滤能力代码，但不要继续优先做:
   - 同一 3 条样本的 priority ratio sweep
   - `D58 / D59` 的 teacher gate 小微调
   - 同一 short-pause cohort 的再细分 handoff
2. 若继续走 formal special supervision，更值得转向:
   - 与 final special slice 更接近的新 cohort 定义
   - 或能直接覆盖 special/no-text slice 的 frame-local supervision
3. 固定交接入口应刷新到 `after D59`:
   - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
   - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
