# 2026-03-23 Stage5 active-template candidate breakthrough 报告

## 结论
- 本轮继续沿
  `docs/269`
  的
  “找一个 active-target 区域里
  不再偏向 fixed-template oracle 的
  structure candidate”
  往下走，
  当前已经出现第一条真正像样的突破：
  - `loss_active_frame_template_excess_relu_0p02`
- 这条 candidate
  的意义不是：
  - 又找到一个 aggregate 上
    看起来更好的 sidecar
- 而是：
  - 它在 candidate grid
    上第一次把 baseline
    稳定推到了
    `20 / 24`
  - 并且
    最简口径里，
    连 `zero-target jitter`
    都不是必须项

先说人话：
- 前一轮已经否证了：
  - naive directional flux
    不能直接转成训练候选
- 这一轮的区别在于：
  - `active-template excess`
    直接抓住了
    fixed-template oracle
    最根本的弱点：
    - 在 active 区域里，
      它比真实 target
      更“模板化”
- 当前 baseline
  虽然整体也很模板化，
  但还没有 oracle
  夸张到那个程度，
  所以这条 loss
  第一次把 baseline
  推到了 oracle 前面

## 本轮工程动作

### 1. 给 probe 补了 active-template sidecar
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增字段：
  - `loss_active_frame_template_excess_relu_0p02`
- 定义口径：
  - 先做
    per-frame mean / RMS
    normalization
  - 以首帧为 reference
  - 只在
    `aligned_frame_rms >= 0.02`
    的 active frames
    上，
    计算：
    - `relu(decoded_template_cosine - aligned_template_cosine)`

### 2. 给 probe 补了 active-template candidate grid
- 当前新增 summary：
  - `active_template_candidate_grid_summary`
- 评分口径是：
  - `weighted_wave_objective`
  - `+ λ_template * loss_active_frame_template_excess_relu_0p02`
  - `+ λ_zero * loss_frame_spectral_flux_zero_target_jitter_0p05`

## 当前 sidecar 结果

### 1. `loss_active_frame_template_excess_relu_0p02`
aggregate 已明显偏向 baseline
- `baseline_decode_route = 0.465671`
- `oracle_active_frame_target_rms = 0.611023`
- `oracle_sine_target_rms = 0.669643`

这说明：
- 它和前面那些
  directional / logspec
  候选不同，
  不再天然偏向
  fixed-template oracle

## 当前 active-template candidate grid

### 1. 最简有效点
- `template_lambda = 0.25`
- `zero_jitter_lambda = 0.0`
- `total_wins = 20 / 24`

这说明：
- 这轮突破
  不依赖
  `zero-target jitter`
  才成立
- active-target 区域的
  anti-template signal
  本身就已经足够强

### 2. 另一条强点
- `template_lambda = 0.1`
- `zero_jitter_lambda = 4.0`
- `total_wins = 20 / 24`

这说明：
- `zero-target jitter`
  仍然可以当 side branch
  一起工作
- 但这轮真正起主导作用的，
  已经不是它，
  而是
  `active_template_excess`

### 3. 与现有 best transition combo 对比
- 旧 best transition combo：
  - `delta_lambda = 1.5`
  - `flux_lambda = 2.0`
  - `total_wins = 16 / 24`
- 当前 active-template candidate：
  - `20 / 24`

这说明：
- 当前 active-template family
  明确超过了
  之前的 transition combo family

## 当前 residual losses

### 1. 对 `oracle_sine_target_rms`
仍然没翻过去的记录
- `target::chapter3_2_firefly_155`
  - `margin = 0.108622`
- `target::chapter3_2_firefly_212`
  - `margin = 0.098056`

### 2. 对 `oracle_active_frame_target_rms`
仍然没翻过去的记录
- `target::chapter3_2_firefly_212`
  - `margin = 0.136222`
- `target::chapter3_2_firefly_155`
  - `margin = 0.103936`

这说明：
- 之前那 3 条 corrected hard cases
  已经不再是主阻塞
- 当前新的 residual hard cases
  已经收紧成：
  - `chapter3_2_firefly_155`
  - `chapter3_2_firefly_212`

## 当前判断
- 当前更准确的实验线结论应更新为：
  1. active-target 区域里，
     真正有效的
     non-template-friendly signal
     已经出现：
     - `active_template_excess`
  2. “baseline direction 更不对”
     仍然是有效诊断，
     但并不是最优训练候选
  3. 当前最值得继续推进的候选家族，
     应从：
     - transition / directional flux
     改成：
     - active-template anti-collapse
       supervision

## 对下一步的直接含义
1. 下一步最合理的是：
   - 围绕
     `chapter3_2_firefly_155`
     和
     `chapter3_2_firefly_212`
     做新的 residual targeted diagnosis
2. 同时应优先验证：
   - `active_template_excess`
     为什么能翻掉旧 hard cases
   - 它会不会误伤
     genuinely stationary / vowel-heavy
     target
3. 当前不建议回退去优先做：
   - naive directional flux
   - 继续只扫
     transition-side
     权重

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `loss_active_frame_template_excess_relu_0p02`
  - `active_template_candidate_grid_summary`

## 一句话结论
- 当前实验线已经拿到第一条真正超过旧 best combo 的 active-region 候选：
  - `loss_active_frame_template_excess_relu_0p02`
- 它把 candidate objective
  直接推到了
  `20 / 24`，
  并把 residual hard cases
  收紧成了
  `chapter3_2_firefly_155`
  和
  `chapter3_2_firefly_212`。
