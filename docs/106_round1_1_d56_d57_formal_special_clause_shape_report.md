# `round1.1 / D56-D57 / formal special clause-shape aux` 报告

## 目的
- `D54 / D55` 已说明:
  - teacher family / gate-target linkage 这条线只剩 epsilon 级再平衡
  - 继续抠 phase 排布的小排列，不太可能自然突破当前 route
- 因此这轮转向真正新的 `frame-local formal special supervision`:
  - 直接复用 `target_weak_event_hints` 里的 `clause_spans / clause_transition`
  - 再叠加 `target_special_supervision` 的 pool-level sample gate
- 设计成一个新的 `formal_special_clause_shape_aux`:
  - 不看 sample-level mean profile
  - 只在命中的 special 样本上约束 clause body 与 clause end 的 frame-local event shape

先说人话:
- 这轮不是再做 `D54` 的 teacher 小扫。
- 是第一次把 `formal special` 监督真落到 `clause-span` frame map 上。

## 代码与配置
### 新增代码
- `src/v5vc/offline_mvp/losses.py`
  - 新增 `formal_special_clause_shape_aux`
  - 用 `clause_role_strengths + clause_transition_strengths + target_special_supervision`
    做 pool-gated clause body / boundary / post-boundary 监督
- 同步更新:
  - `src/v5vc/train_entry.py`
  - `src/v5vc/special_eval.py`
  - `src/v5vc/ablation_eval.py`
  - `src/v5vc/special_eval_series.py`

### D56
- 配置:
  - `configs/offline_mvp_train_d56_round1_1_d7_init_d54_formal_special_clause_shape_finalsingle_late_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-009-offline-mvp-d56-round1-1-d7-init-d54-formal-special-clause-shape-finalsingle-late-20step-calibration`
- 设计:
  - 基线完全复用 `D54`
  - 只新增:
    - `formal_special_clause_shape_aux`
    - late-only `weight_schedule = step11-15 -> 0.08`
    - role 只看 `single + final`

### D57
- 配置:
  - `configs/offline_mvp_train_d57_round1_1_d7_init_d54_formal_special_clause_shape_middle_late_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-010-offline-mvp-d57-round1-1-d7-init-d54-formal-special-clause-shape-middle-late-20step-calibration`
- 设计:
  - 同样以 `D54` 为基线
  - 在 `D56` 基础上:
    - 把 `middle` role 一起纳入
    - 对 `other / multi_terminal / none` 给一点 sample weighting 倾斜
    - late-only `weight_schedule = step11-16 -> 0.1`

## 关键事实
### 1. 新 aux 工程上是真实接通的，不是空配置
- `D56 dry-run step0`
  - `loss_formal_special_clause_shape_aux = 0.02187`
  - 但 effective `weight = 0.0`
- `D57 dry-run step0`
  - `loss_formal_special_clause_shape_aux = 0.025937`
  - 但 effective `weight = 0.0`

解释:
- 这说明:
  - 新 frame-local clause-shape loss 已经能真正读取 `clause_spans / clause_transition`
  - 同时 early anchor 没被提前污染

### 2. `D56 / D57 step10` 仍精确复刻 `D45 / D54 step10`
- `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`

解释:
- early anchor 依旧没被破坏。
- 当前差异全部来自 late-only formal special supervision。

### 3. late window 里新 aux 也确实命中过，不是“只在 dry-run 有值”
- `D56 step15`
  - `formal_special_clause_shape_aux.weight = 0.08`
  - `loss_formal_special_clause_shape_aux = 0.031738`
- `D57 step15`
  - `formal_special_clause_shape_aux.weight = 0.08`
  - `loss_formal_special_clause_shape_aux = 0.036294`

解释:
- 这轮不是“新 aux 只在 config 里写了，实际 late batch 没吃到”。
- 它在 late phase 确实真实参与过优化。

### 4. 但它只在极少数 late batch 命中，final slice 上基本完全消失
- `D56 / D57` 的 training log 显示:
  - late 非零命中主要集中在 `step15`
  - `step16-20` 很快又回到 `0.0`
- final validation / final special_eval 都是:
  - `loss_formal_special_clause_shape_aux = 0.0`

解释:
- 这意味着:
  - 新 supervision 不是完全没用
  - 但它没有稳定渗透成 final behavior 的持续杠杆
- 更像是:
  - 在少数命中的 batch 上给了局部 nudging
  - 最终仍没改写主轨迹

### 5. `D56` 只是在 `D54` 附近形成万分位级 tradeoff
- `D56 final = 2.505586 / 0.131862 / 3.19987 / 0.412639`

对比 `D54 final = 2.505569 / 0.131888 / 3.199683 / 0.412614`:
- validation 更差 `+0.000017`
- special 更好 `-0.000026`
- `e_evt` 更强 `+0.000187`
- `z_art` 更强 `+0.000025`

解释:
- 这不是 breakout。
- 这是围绕 `D54` 的万分位级重新分配。

### 6. `D57` 把 `middle` clause 也纳进来后，仍只是 `D56` 的近似数值重放
- `D57 final = 2.505587 / 0.131861 / 3.199882 / 0.41264`

对比 `D56 final`:
- validation 更差 `+0.000001`
- special 更好 `-0.000001`
- `e_evt` 更强 `+0.000012`
- `z_art` 更强 `+0.000001`

解释:
- `middle` role 扩展没有把轨迹推到新的 regime。
- 只是在当前精度下给出一个几乎不可分辨的数值重放。

### 7. 当前 route 仍未改写
- 全局 comparison 现在已含 `23` 个实验
- leaders 仍是:
  - `D29 = validation`
  - `D22 = default_minimax`
  - `D33 = special / e_evt / z_art`

解释:
- `D56 / D57` 给出的最强结论不是“发现了新 route”
- 而是:
  - frame-local formal special supervision 这第一版已经工程打通
  - 但当前这版 clause-shape 定义仍只产生局部、稀疏、不可持续的 late 扰动

## 当前结论
1. `formal_special_clause_shape_aux` 工程上是成立的:
   - 能真实消费 `clause_spans / clause_transition`
   - late phase 也确实命中过 batch
2. 但 `D56 / D57` 说明:
   - 当前这版 clause body + clause end frame-local special supervision
   - 还不足以改写 `D54` 轨迹
   - 只在 `D54` 附近形成万分位级 tradeoff
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 保留 `formal_special_clause_shape_aux` 代码，但不要继续优先做:
   - `D56 / D57` 的小 weight sweep
   - `single/final/middle` 小排列
   - 同一套 pool gate 的细粒度时点调整
2. 若继续走 formal special supervision，更值得转向:
   - 更稳定命中的 frame-local target 定义
   - 或让 sampler / gate 明确为这类 clause-shape supervision 保证 late exposure
3. 固定交接入口应刷新到 `after D57`:
   - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
