# `round1.1 / D48-D49 / late target-shape softweight + punctuation supervision` 报告

## 目的
- `D46 / D47` 已经证明:
  - 在 `D45` 这条 teacher-family 路线里
  - 继续只靠 late filter 收紧
  - 只会把轨迹往 validation-first 方向推
- 因此这轮改做两条更小、但更贴近当前判断的 follow-up:
  - `D48 = 不缩 late sample set，只把 late teacher pull 做成 soft target-shape weighting`
  - `D49 = 不改 teacher family，只给 late phase 叠一个 formal-special-facing 的 punctuation supervision`

先说人话:
- 这轮不是又去抠同一条 late filter 阈值。
- 而是在验证:
  - `D45` 缺的到底是不是“更聪明的 late teacher 权重”
  - 或“更明确但仍很轻的 formal special 对齐监督”

## 配置设计
### D48
- 配置:
  - `configs/offline_mvp_train_d48_round1_1_d7_init_phase_teacher_family_softweight_handoff_d33step10_to_d29_late_targetshape_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-002-offline-mvp-d48-round1-1-d7-init-phase-teacher-family-softweight-handoff-d33step10-to-d29-late-targetshape-20step-calibration`
- 设计:
  - `step1-10`
    - 与 `D45` 完全一致
    - `D33 step10 teacher + short_pause gate + fused_hidden`
  - `step11-20`
    - 仍用 `D29 final teacher`
    - 仍用 `challenge_proxy_core + short_pause_no_terminal`
    - 但 teacher consistency 新增 soft sample weighting:
      - `base_sample_weight = 0.35`
      - `proximity_weight_scale = 1.0`
      - `final_terminal_type_weight_overrides = {"none": 0.2}`
      - `utterance_structure_type_weight_overrides = {"other": 0.15, "nonverbal": 0.15}`

### D49
- 配置:
  - `configs/offline_mvp_train_d49_round1_1_d7_init_phase_teacher_family_punctuation_aux_handoff_d33step10_to_d29_late_only_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-001-offline-mvp-d49-round1-1-d7-init-phase-teacher-family-punctuation-aux-handoff-d33step10-to-d29-late-only-20step-calibration`
- 设计:
  - teacher family 保持 `D45`
  - sampler 保持 `D45`
  - 新增 `punctuation_profile_aux`
    - `weight = 0.2`
    - `weight_schedule = step11 -> step15 linear ramp to 0.2`

## 代码补充
- `src/v5vc/offline_mvp/losses.py`
  - 新增 `build_special_supervision_sample_weights`
  - `teacher_consistency` 现在可以用 soft sample weighting，而不是只有二值 sample mask
  - `punctuation_profile_aux` 正式支持 `weight_schedule`
- `src/v5vc/train_entry.py`
  - `teacher_consistency` 新增配置透传:
    - `base_sample_weight`
    - `proximity_weight_scale`
    - `final_terminal_type_weight_overrides`
    - `utterance_structure_type_weight_overrides`

## 关键事实
### 1. `D48` 不是挂空配置，但 final 精确复刻 `D45`
- `step11-20` 的 `effective_teacher_consistency` 已明确切到:
  - `base_sample_weight = 0.35`
  - `proximity_weight_scale = 1.0`
  - `final_terminal_type_weight_overrides = {"none": 0.2}`
  - `utterance_structure_type_weight_overrides = {"other": 0.15, "nonverbal": 0.15}`
- 但结果:
  - `D48 step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
  - `D48 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`

这与 `D45`:
- `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
- `final = 2.503755 / 0.133716 / 3.196309 / 0.407233`

在当前精度下完全一致。

解释:
- 这说明:
  - late teacher softweight 机制已经真实接入
  - 但它没有形成新的优化杠杆
- 当前 `D45` 缺的，不像是“把 late teacher 样本按 proximity 再加权一点”。

### 2. `D49` 的 punctuation supervision 确实在 late/final 激活了
- 训练日志已确认:
  - `step10 effective punctuation weight = 0.0`
  - `step11 effective punctuation weight = 0.0`
  - `step12 effective punctuation weight = 0.05`
  - `step15 effective punctuation weight = 0.2`
  - `step20 effective punctuation weight = 0.2`
- final:
  - validation `loss_punctuation_profile_aux = 0.017141`
  - special `loss_punctuation_profile_aux = 0.002731`
  - `delta_loss_punctuation_profile_aux = -0.01441`

解释:
- 这轮不是“punctuation aux 又挂空”。
- 它在 validation 和 special 上都真实命中了。

### 3. 但 `D49` 只给出一个非常轻微的 validation-for-special 交换
- `D49 final = 2.507186 / 0.130834 / 3.196306 / 0.407234`
- 对比 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`

相对 `D45`:
- validation 变差 `+0.003431`
- special 略好 `-0.002882`
- `e_evt` 基本不变 `-0.000003`
- `z_art` 基本不变 `+0.000001`

解释:
- 这说明:
  - `D49` 不是完全没信息
  - 它确实稍微把 final 往 formal special 拉了一点
- 但这个变化太小:
  - 没有改善 control
  - 也没有改变 route 结论

### 4. `D49 step10` 没有严格复刻 `D45 step10`，但差异来自极小数值扰动，不是 because late punct 已提前生效
- `D49 step10 = 2.58238 / 0.158166 / 2.971409 / 0.420419`
- 相比 `D45 step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
  - 只有 validation / special 出现极小偏移
- 同时日志已显示:
  - `step10 punctuation weight = 0.0`
  - `step11 punctuation weight = 0.0`

解释:
- 所以这里不应解释成:
  - punctuation aux 早于计划介入
- 更合理的口径是:
  - 当前 20-step seeded-shuffle 小实验本身存在极小数值漂移
  - 但核心判断仍由 final 结果决定

## 当前结论
1. `D48` 证明:
   - 在 `D45` 路线上
   - 只把 late teacher pull 改成 proximity / none / structure 的 soft weighting
   - 不足以形成新的行为杠杆
2. `D49` 证明:
   - late-only `punctuation_profile_aux` 的确能真实激活
   - 但它只换来一个极轻微的 validation-for-special tradeoff
   - 并没有改善 `e_evt / z_art`
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
4. 在 `post-D45` family 里:
   - `D45` 仍是最值得引用的 compromise 点
   - `D48` 是精确重放
   - `D49` 是极轻微但不改局的旁支

## 当前建议
1. 暂停继续做 `D45` 上的:
   - late teacher softweight 小变体
   - late punctuation-profile 小变体
2. 若继续沿 `D45` 路线推进，下一步不该还是 utterance-level profile 或 soft weighting；
   更值得考虑:
   - 更强的 late teacher family decomposition
   - 或 frame-local / boundary-local 的 formal special supervision
3. 固定交接入口已刷新到 `after D49`:
   - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
