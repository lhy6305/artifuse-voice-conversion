# 2026-03-24 Stage5 active-template + frame-delta candidate 报告

## 结论
- 本轮把
  `active_template_excess`
  后面叠
  `frame_delta`
  的候选家族
  正式接进了
  `stage5_waveform_objective_collapse_probe`。
- 当前 probe
  已确认：
  - `weighted_wave_objective`
  - `+ lambda_template * loss_active_frame_template_excess_relu_0p02`
  - `+ lambda_delta * loss_frame_delta_unit_rms_l1`
  这条家族
  可以把当前
  `12 records x 2 oracle matchups`
  直接推到：
  - `24 / 24`
- 但更准确的阶段结论不是：
  - 已经找到
    “active-template 主轴 + 小补丁”
    的训练候选
- 而是：
  - `frame_delta`
    确实能补掉
    `stationary-friendly residual blind spot`
  - 但在当前标度下，
    真正把 probe 打满的点
    已经明显是
    `delta-dominated`
    regime

先说人话：
- 这轮的正面结论是：
  `active_template_excess`
  不是死路，
  residual blind spot
  确实能被
  `frame_delta`
  补上
- 但负面约束同样重要：
  现在还不能把这件事
  写成
  “只要再补一个很小的 delta 项，
  就能直接进训练”

## 本轮工程动作

### 1. probe 新增 active-template + delta candidate grid
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 新增输出：
  - `active_template_delta_candidate_grid_summary`
  - `active_template_delta_targeted_summary`
- 当前评分口径：
  - `weighted_wave_objective`
  - `+ lambda_template * loss_active_frame_template_excess_relu_0p02`
  - `+ lambda_delta * loss_frame_delta_unit_rms_l1`

### 2. 实际复跑正式 probe
- 继续沿用
  `docs/259`
  的固定命令口径：
  - same checkpoint selection
  - same validation-12 record set
  - same predicted activity gate
  - same objective weights
- 运行产物继续写回：
  - [stage5_waveform_objective_collapse_probe.md](F:/proj_dev/tmp/workdir4/reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/stage5_waveform_objective_collapse_probe.md)
  - [stage5_waveform_objective_collapse_probe.json](F:/proj_dev/tmp/workdir4/reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/stage5_waveform_objective_collapse_probe.json)

## 关键结果

### 1. 当前 best point 已达到 24 / 24
- 当前最优点：
  - `template_lambda = 0.05`
  - `delta_lambda = 8.0`
  - `total_wins = 24 / 24`
- 两类 oracle
  都被完全压过：
  - vs `oracle_sine_target_rms`
    - `12 / 12`
    - `mean_margin = -0.112115`
    - `max_margin = -0.050571`
  - vs `oracle_active_frame_target_rms`
    - `12 / 12`
    - `mean_margin = -0.114148`
    - `max_margin = -0.012593`

### 2. 更温和的点已经非常接近，但仍留一个 residual
- 当前最简的
  `23 / 24`
  点之一：
  - `template_lambda = 0.1`
  - `delta_lambda = 4.0`
- 此时唯一 residual：
  - `oracle_active_frame_target_rms`
  - `target::chapter3_2_firefly_212`
  - `margin = 0.038701`
- 另一条之前的 residual：
  - `target::chapter3_2_firefly_155`
  已经被收掉

### 3. 真正把 24 / 24 打满的，并不是“template 主导 + delta 小修正”
- aggregate 上，
  `24 / 24`
  最优点的项分解是：

#### baseline
- `weighted_wave_objective = 0.150852`
- `template_term = 0.05 * 0.465671 = 0.023284`
- `delta_term = 8.0 * 0.960329 = 7.682632`
- total:
  - `7.856768`

#### oracle_sine_target_rms
- `weighted_wave_objective = 0.147455`
- `template_term = 0.05 * 0.669643 = 0.033482`
- `delta_term = 8.0 * 0.973493 = 7.787944`
- total:
  - `7.968881`

#### oracle_active_frame_target_rms
- `weighted_wave_objective = 0.141467`
- `template_term = 0.05 * 0.611023 = 0.030551`
- `delta_term = 8.0 * 0.974862 = 7.798896`
- total:
  - `7.970914`

直接结论：
- 当前 best point
  虽然名义上属于
  `active_template + delta`
  家族，
  但数值主导项
  已经明显是：
  - `frame_delta`

## 与上一轮 active-template 结果的关系

### 1. 正面更新
- 上一轮
  `active_template_excess`
  单项最佳：
  - `template_lambda = 0.25`
  - `zero_jitter_lambda = 0.0`
  - `20 / 24`
- 当前说明：
  - `stationary-friendly residual blind spot`
    不是 active-template 主轴本身失效
  - 而是它还需要
    一类额外结构项
  - `frame_delta`
    是目前最有效的补项候选

### 2. 负面约束
- 当前还不能把结论写成：
  - “active-template 已经够了，
    只要加一点 delta”
- 更准确的说法是：
  - 当前 probe 上
    最终封顶解
    要求很大的
    `delta_lambda`
  - 这更像：
    - delta 在接管排序
  - 还不是：
    - template 主轴下的轻量 residual repair

## 与试听包的关系
- 当前试听路径
  的确就是：
  - [offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1)
- 你已经回听并确认：
  - 除 `aligned_target`
    之外，
    其余仍是
    与原方案一致的 buzz
- 这与本轮结论并不冲突：
  - 当前所有进展
    仍然只是
    offline probe
    上的 candidate-objective
    诊断
  - 还没有任何新的训练结果
    或新 checkpoint
  - 所以现有试听包
    理应继续反映
    原 baseline decode route

## 对下一步的直接含义
1. 当前不该直接把
   `template=0.05, delta=8.0`
   写进训练，
   因为这更像
   `delta-dominated`
   排序解，
   不是稳健的轻量补项。
2. 下一步更合理的是：
   - 继续停留在 offline probe 层
   - 设计更“只补 residual blind spot、
     不让 delta 接管主轴”的 candidate 形式
3. 当前还应继续保留
   试听约束：
   - 没有新的训练产物前，
     不要把 probe 分数改善
     误写成可听质量进展

## 一句话结论
- `active_template + frame_delta`
  已经能把当前 probe
  打到 `24 / 24`，
  但这一步更像
  “证明 residual blind spot
  可以被 delta 收掉”，
  还不能直接等同于
  一个可放心写进训练的
  轻量新 objective。
