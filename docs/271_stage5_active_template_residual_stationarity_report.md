# 2026-03-23 Stage5 active-template residual stationarity 报告

## 结论
- 本轮继续沿
  `docs/270`
  的
  active-template breakthrough
  往下走，
  当前已经把 residual hard cases
  和 stationary-risk
  先量化清楚了。
- 当前更准确的结论应写成：
  1. `active_template_excess`
     最简 best combo
     仍是：
     - `template_lambda = 0.25`
     - `zero_jitter_lambda = 0.0`
     - `20 / 24`
  2. 剩下没翻过去的
     只有：
     - `target::chapter3_2_firefly_212`
     - `target::chapter3_2_firefly_155`
  3. 这两条 residual
     并不是因为
     baseline 的
     `active_template_excess`
     特别高
  4. 更像是：
     - target 本身
       更稳态 / 更模板友好
     - 导致 fixed-template oracle
       在这条 metric 上
       几乎吃不到罚

先说人话：
- 这轮更关键的信息
  不是又确认了一次
  `20 / 24`，
- 而是把 residual
  的形状先收紧了：
  - 不是
    candidate 本身
    对 baseline
    出现了普遍误伤
  - 而是剩下那 2 条记录
    更像是
    stationary-friendly residual

## 本轮工程动作

### 1. 给 probe 补了 active-template targeted summary
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增 summary：
  - `active_template_targeted_summary`
- 当前会正式输出：
  - simplest best combo
  - residual losses
  - stationary-risk group summary

## 当前 residual targeted summary

### 1. simplest best combo
- `template_lambda = 0.25`
- `zero_jitter_lambda = 0.0`
- `total_wins = 20 / 24`

### 2. residual records
- `target::chapter3_2_firefly_212`
  - mean margin `0.117139`
  - vs sine oracle `0.098056`
  - vs active oracle `0.136222`
- `target::chapter3_2_firefly_155`
  - mean margin `0.106279`
  - vs sine oracle `0.108622`
  - vs active oracle `0.103936`

## 当前 stationary-risk summary

### 1. residual group
- `residual_mean_aligned_frame_adjacent_cosine = 0.191316`
- `residual_mean_aligned_frame_rms_cv = 0.822725`
- `residual_mean_baseline_active_template_excess = 0.462258`
- `residual_mean_baseline_zero_jitter = 0.032914`

### 2. win group
- `win_mean_aligned_frame_adjacent_cosine = 0.107104`
- `win_mean_aligned_frame_rms_cv = 1.080521`
- `win_mean_baseline_active_template_excess = 0.466354`
- `win_mean_baseline_zero_jitter = 0.141530`

### 3. 这组对照说明什么
- residual 组
  的确更像：
  - adjacent cosine
    更高
  - RMS CV
    更低
  - 也就是
    更稳态 / 更平滑
- 但 residual 组
  的 baseline
  `active_template_excess`
  并没有比 win 组更高：
  - `0.462258`
    vs
    `0.466354`
- 这说明：
  - 当前 residual
    不是因为
    candidate 对 baseline
    的惩罚突然异常变大
  - 更像是：
    - target 更稳态
    - oracle 的
      template-excess
      几乎为零
    - baseline 因此
      仍然翻不过去

## 当前 residual records 的更具体形状

### 1. `target::chapter3_2_firefly_212`
- `aligned_frame_adjacent_cosine_mean = 0.223986`
- `aligned_frame_rms_cv = 0.946428`
- baseline:
  - `weighted_wave_objective = 0.140739`
  - `active_template_excess = 0.462278`
- oracle:
  - `active_template_excess = 0.0`

### 2. `target::chapter3_2_firefly_155`
- `aligned_frame_adjacent_cosine_mean = 0.158646`
- `aligned_frame_rms_cv = 0.699023`
- baseline:
  - `weighted_wave_objective = 0.162713`
  - `active_template_excess = 0.462238`
- oracle:
  - `active_template_excess = 0.0`

这说明：
- 这两条 residual
  的关键不是：
  - baseline template-excess
    特别离谱
- 更像是：
  - oracle 刚好在这两条上
    完全不吃
    `active_template_excess`
    的罚

## 当前判断
- 当前更准确的实验线结论应更新为：
  1. `active_template_excess`
     确实是当前最强 candidate
  2. 当前没有证据表明：
     - 它会对全局
       stationary-ish targets
       造成广泛误伤
  3. 但 residual 组
     确实更偏：
     - stationary-friendly
       subset
  4. 下一步若继续提升，
     问题不该再写成：
     - active-template candidate
       不稳定
     而该写成：
     - 怎么补上
       stationary-friendly residual
       这一小块盲区

## 对下一步的直接含义
1. 下一步最合理的是：
   - 围绕
     `chapter3_2_firefly_155`
     和
     `chapter3_2_firefly_212`
     做 residual-specific
     candidate diagnosis
2. 当前更值得补的方向是：
   - 不改变
     `active_template_excess`
     主轴
   - 只额外寻找：
     - 对 stationary-friendly residual
       有区分度
       但不破坏现有
       `20 / 24`
       的补充项
3. 当前不建议回退去优先做：
   - 否掉
     `active_template_excess`
   - 或重新回到
     directional flux
     主线

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `active_template_targeted_summary`

## 一句话结论
- 当前 `active_template_excess`
  的 residual 已经收紧成：
  - 两条更偏 stationary-friendly 的记录；
- 问题不在于它对 baseline 广泛误伤，
  而在于：
  - 还缺一个能补上
    stationary-friendly residual
    的小补充项。
