# 2026-03-23 Stage5 directional flux candidate 否证报告

## 结论
- 本轮继续沿
  `docs/268`
  的
  directional flux
  思路往下走，
  但当前结果已经足够把一个重要误判排掉：
  - naive
    directional flux supervision
    并不是当前最该押注的训练候选
- 更准确地说：
  1. `active-target directional flux cosine`
     这个 sidecar
     aggregate 上仍然更偏向
     fixed-template oracle
  2. `zero-target jitter`
     的确对 baseline 更友好
  3. 但把这两者做成
     candidate objective
     网格后，
     最优点仍只有：
     - `15 / 24`
     - 且最优时
       `direction_lambda = 0.0`
  4. 这说明：
     - 当前 naive directional term
       没有提供额外帮助
     - 真正有效的部分
       只剩
       `zero-target jitter suppression`

先说人话：
- 上一轮已经确认：
  - baseline 的
    flux direction
    更不对
- 但这并不自动等于：
  - 给训练再加一个
    directional flux cosine
    loss
    就会更好
- 当前 probe 反而说明：
  - fixed-template oracle
    在这个 naive directional metric 上
    也更好
  - 所以这条线
    不能直接从
    “现象诊断”
    跳到
    “训练候选”

## 本轮工程动作

### 1. 给 probe 补了 directional sidecars
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增 sidecar：
  - `loss_frame_spectral_flux_direction_cosine_all`
  - `loss_frame_spectral_flux_direction_cosine_active_0p05`
  - `loss_frame_spectral_flux_zero_target_jitter_0p05`

### 2. 给 probe 补了 directional candidate grid
- 当前新增 summary：
  - `directional_flux_candidate_grid_summary`
- 评分口径是：
  - `weighted_wave_objective`
  - `+ λ_direction * active-target directional flux cosine loss`
  - `+ λ_zero * zero-target flux-jitter loss`

## 当前 sidecar 结果

### 1. `active-target directional flux cosine`
aggregate 仍更偏向 oracle
- `oracle_sine_target_rms = 0.946695`
- `oracle_active_frame_target_rms = 0.972199`
- `baseline_decode_route = 1.002153`

这说明：
- 如果把
  `active-target directional flux cosine`
  直接当成 additive loss，
  baseline 在 aggregate 上
  不会被拉到 oracle 前面

### 2. `zero-target jitter`
aggregate 确实更偏向 baseline
- `baseline_decode_route = 0.123427`
- `oracle_active_frame_target_rms = 0.134759`
- `oracle_sine_target_rms = 0.138986`

这说明：
- `zero-target jitter suppression`
  确实捕到了
  一块 oracle 的弱点
- 但它只覆盖：
  - zero-target / plateau
    这条分支

## 当前 directional candidate grid

### 1. 最优点
- `direction_lambda = 0.0`
- `zero_jitter_lambda = 1.0`
- `total_wins = 15 / 24`

这说明：
- directional term
  在最优点里
  实际上被自动退成
  `0`
- 也就是说：
  - 当前 naive directional supervision
    没有给 candidate objective
    带来任何额外收益

### 2. 与现有 best transition combo 对比
- 当前 best transition combo
  仍是：
  - `delta_lambda = 1.5`
  - `flux_lambda = 2.0`
  - `total_wins = 16 / 24`
- directional family
  的最优点
  只有：
  - `15 / 24`

这说明：
- 当前 naive directional candidate
  不仅没超过现有 best combo，
  甚至还更弱

## 当前判断
- 当前更准确的实验线结论应更新为：
  1. “baseline 的 direction 更不对”
     这是有效诊断，
     但不是
     可直接照搬成
     additive training loss
     的充分条件
  2. 当前 naive directional flux cosine
     仍然 template-friendly
  3. 当前真正显露价值的
     只有：
     - zero-target jitter suppression
  4. active-target 部分
     仍缺一个：
     - 不会继续偏向 fixed-template oracle
       的 structure supervision

## 对下一步的直接含义
1. 下一步不建议优先做：
   - 把
     directional flux cosine
     直接写进训练 loss
2. 更合理的下一题应改成：
   - 保留
     zero-target jitter suppression
     这条分支
   - 同时另找一个
     对 active-target 区域
     不那么 template-friendly 的
     structure candidate
3. 当前最自然的方向是：
   - `chapter3_6_firefly_106`
     继续沿
     zero-target jitter
   - `chapter3_3_firefly_162`
     和
     `chapter3_17_firefly_133`
     不再优先押注
     naive directional flux，
     而应改找：
     - 非模板友好的
       active-region structure signal

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `loss_frame_spectral_flux_direction_cosine_all`
  - `loss_frame_spectral_flux_direction_cosine_active_0p05`
  - `loss_frame_spectral_flux_zero_target_jitter_0p05`
  - `directional_flux_candidate_grid_summary`

## 一句话结论
- 当前实验线已经足够否证：
  - naive directional flux supervision
    不是下一步最该押注的候选；
- 下一步更合理的是：
  - 保留
    zero-target jitter
    这条有效支线，
  - 同时另找
    active-target 区域里
    不再偏向 fixed-template oracle 的
    structure supervision
