# 2026-03-23 Stage5 flux alignment directionality 报告

## 结论
- 本轮继续沿
  `docs/267`
  的
  flux-side targeted diagnosis
  往下走，
  给 corrected hard cases
  又补了一层
  `flux_alignment_summary`。
- 当前更深一层的共性已经能正式写成：
  - baseline 并不是单纯因为
    “flux 幅度太大”
    才输给 fixed-template oracle
  - 更准确的是：
    - 在正失败窗口里，
      baseline 和 oracle
      的 flux magnitude
      都明显低于 target
    - 但 oracle 的
      signed flux direction
      明显更接近 target，
      baseline 则接近
      `0` 甚至略负相关

先说人话：
- 这说明当前问题
  不能再理解成：
  - baseline 动得太多
  - 只要再加大一点
    flux L1
    就能修
- 当前更像是：
  - baseline 的 spectral-change
    方向不对
  - oracle 虽然也没有复现 target 的完整 flux 幅度，
    但方向更 coherent，
    所以照样在当前 objective 下赢

## 本轮工程动作

### 1. 给 hard-case breakdown 正式补了 `flux_alignment_summary`
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增字段：
  - `flux_alignment_summary`
- 当前输出的核心量包括：
  - `alignment_label`
  - `dominant_band_label`
  - `baseline_flux_alignment_cosine_mean_positive`
  - `reference_oracle_flux_alignment_cosine_mean_positive`
  - `flux_alignment_cosine_gap_positive`
  - `baseline/reference_oracle_to_target_flux_magnitude_ratio_positive_active_target`
  - `low/mid/high_band_positive_advantage_share`

### 2. 这层 summary 的目的
- 不是只再补一个 band 表，
- 而是把：
  - flux magnitude
  - flux direction coherence
  这两件事拆开看，
  避免继续把
  `flux`
  误读成纯幅度惩罚。

## 当前 corrected hard-case flux alignment

### 1. `target::chapter3_3_firefly_162`
- `alignment_label = low_magnitude_direction_gap`
- `dominant_band = high`
- 关键量化：
  - `baseline_cos = -0.017303`
  - `oracle_cos = 0.337721`
  - `cos_gap = 0.355024`
  - `baseline_flux_ratio_active_target = 0.201196`
  - `oracle_flux_ratio_active_target = 0.112336`
  - `band_share low/mid/high = 0.281861 / 0.332054 / 0.386085`
- 这说明：
  - 即使 baseline
    的 flux magnitude
    还比 oracle 更大，
  - 它仍然输，
    说明这里主导差异
    不是“谁动得更大”，
    而是：
    - oracle 的
      signed flux direction
      更接近 target

### 2. `target::chapter3_17_firefly_133`
- `alignment_label = low_magnitude_direction_gap`
- `dominant_band = high`
- 关键量化：
  - `baseline_cos = -0.010065`
  - `oracle_cos = 0.271186`
  - `cos_gap = 0.281250`
  - `baseline_flux_ratio_active_target = 0.051450`
  - `oracle_flux_ratio_active_target = 0.101296`
  - `band_share low/mid/high = 0.317636 / 0.316518 / 0.365846`
- 这说明：
  - 这条 interior hard case
    的主问题
    也不是窄带噪点
  - 更像是：
    - broadband
      但略偏 high-band
    - 同时 baseline
      的 flux direction
      比 oracle 更不对

### 3. `target::chapter3_6_firefly_106`
- `alignment_label = zero_target_flux_jitter`
- `dominant_band = high`
- 关键量化：
  - `baseline_cos = -0.006861`
  - `oracle_cos = 0.274894`
  - `cos_gap = 0.281754`
  - `baseline_flux_ratio_active_target = 0.061927`
  - `oracle_flux_ratio_active_target = 0.096212`
  - `band_share low/mid/high = 0.231000 / 0.382152 / 0.386848`
- 这说明：
  - 它仍然保留
    plateau / near-zero
    jitter
    这个特殊性
  - 但如果只看 active-target
    正失败窗口，
    它和前两条一样，
    仍存在明显的
    direction gap

## 当前判断
- 当前更准确的实验线结论应更新为：
  1. hard cases
     的 flux failure
     不能再写成：
     - “baseline flux 太大”
  2. 更准确的写法应是：
     - baseline 的
       signed flux direction
       更不接近 target
  3. 当前 corrected hard cases
     都带：
     - mild high-band tilt
     - 但不是
       单一窄带问题
  4. `chapter3_6_firefly_106`
     仍保留：
     - zero-target jitter
       这个单独分支

## 对下一步的直接含义
1. 下一步不建议回退去优先做：
   - 单纯继续加大
     `flux L1`
     权重
2. 更合理的下一题应改成：
   - 继续停留在离线 probe 层，
     直接设计
     signed / directional
     flux-side candidate supervision
3. 当前最自然的拆法是：
   - `chapter3_3_firefly_162`
     - boundary high-motion
       directional flux
   - `chapter3_17_firefly_133`
     - interior high-motion
       directional flux
   - `chapter3_6_firefly_106`
     - zero-target jitter
       suppression

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `flux_alignment_summary`

## 一句话结论
- 当前 corrected hard cases
  的更深一层共性已经收紧成：
  - baseline 输给 oracle，
    主要不是因为
    flux 幅度更大，
    而是因为
    signed flux direction
    更不对；
- 因而下一步应优先转向：
  - directional flux
    supervision
  - 而不是单纯继续抬
    flux L1
