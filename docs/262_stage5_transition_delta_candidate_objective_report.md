# 2026-03-23 Stage5 transition-delta candidate-objective 报告

## 结论
- 本轮已经把
  `frame_delta_unit_rms_l1`
  从
  “一个方向上看起来有希望的 sidecar”
  推进到：
  - 可重复的
    candidate-objective
    排序诊断
  - 明确的翻转门槛
- 当前 aggregate 结果显示：
  - 若定义
    `score = weighted_wave_objective + λ * loss_frame_delta_unit_rms_l1`
  - 则：
    - `λ < 0.258`
      时，
      baseline
      还压不过
      `oracle_sine_target_rms`
    - `0.258 <= λ < 0.646`
      时，
      baseline
      已压过
      `oracle_sine_target_rms`，
      但还压不过
      `oracle_active_frame_target_rms`
    - `λ >= 0.646`
      时，
      baseline
      才能同时压过
      两个 fixed-template oracle

先说人话：
- 现在已经能把
  transition-side
  候选约束
  分成两档：
  - 弱翻转区：
    只能挡住比较简单的
    `sine oracle`
  - 稳翻转区：
    连更强的
    `active-frame oracle`
    也能一起挡住

## 背景
- `docs/261`
  已确认：
  - `loss_frame_delta_unit_rms_l1`
    是当前第一类
    把 baseline
    排到两个 oracle 前面的
    transition-side 信号
- 但当时仍缺一个关键问题：
  - 如果真把它并到 objective，
    需要多大权重，
    排序才会开始稳定翻回来

## 本轮补充

### 1. 在 probe 中固化 candidate-objective 诊断
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增：
  - `transition_delta_candidate_objective_rankings`
  - `transition_delta_flip_thresholds_vs_baseline`
- 当前固定诊断口径：
  - `score = weighted_wave_objective + λ * loss_frame_delta_unit_rms_l1`
  - `λ grid = [0.1, 0.25, 0.3, 0.5, 0.75, 1.0]`

### 2. 当前 probe 已可直接输出
- 每个 `λ`
  下三条 variant 的新排序
- baseline
  相对每个 oracle
  的最小翻转门槛

## 关键结果

### 1. `λ = 0.25` 仍属于临界前夜
- 排序：
  1. `oracle_active_frame_target_rms`
  2. `oracle_sine_target_rms`
  3. `baseline_decode_route`
- 但 baseline
  与
  `oracle_sine_target_rms`
  已几乎打平：
  - baseline
    `0.390934`
  - sine oracle
    `0.390828`
- 这说明：
  - `0.25`
    已非常接近
    第一条翻转线，
  - 但还不够稳

### 2. `λ = 0.3 ~ 0.5` 进入弱翻转区
- `λ = 0.3`
  排序：
  1. `oracle_active_frame_target_rms`
  2. `baseline_decode_route`
  3. `oracle_sine_target_rms`
- `λ = 0.5`
  排序：
  1. `oracle_active_frame_target_rms`
  2. `baseline_decode_route`
  3. `oracle_sine_target_rms`
- 这说明：
  - 在这一区间，
    baseline
    已能压过
    `sine oracle`
  - 但还挡不住
    更强的
    `active-frame oracle`

### 3. `λ = 0.75+` 才进入稳翻转区
- `λ = 0.75`
  排序：
  1. `baseline_decode_route`
  2. `oracle_active_frame_target_rms`
  3. `oracle_sine_target_rms`
- `λ = 1.0`
  排序：
  1. `baseline_decode_route`
  2. `oracle_active_frame_target_rms`
  3. `oracle_sine_target_rms`
- 结合翻转门槛：
  - 对
    `oracle_sine_target_rms`
    需：
    - `λ >= 0.258052`
  - 对
    `oracle_active_frame_target_rms`
    需：
    - `λ >= 0.645772`
- 这说明：
  - 若目标是
    “同时压过两个当前已知 fixed-template oracle”，
    当前更像样的候选权重区间应落在：
    - `λ ≈ 0.65+`

## 当前判断
- 当前最值得落盘的新边界是：
  - `frame_delta`
    方向不是“也许有点用”
  - 而是已经能量化成：
    - 弱翻转区：
      `λ ≈ 0.26 ~ 0.65`
    - 稳翻转区：
      `λ >= 0.65`
- 所以后续若继续做
  objective-level
  候选设计，
  当前最合理的两档参考点应是：
  - `λ = 0.3`
    - 看能否先挡住
      较简单的 template oracle
  - `λ = 0.75`
    - 看能否稳定挡住
      已知两类 oracle

## 当前不应误写的地方
- 这不等于：
  - `frame_delta_unit_rms_l1`
    已经足够作为正式训练 loss
- 当前更准确的含义是：
  - 它是目前第一类
    能在 aggregate 排序上
    把 baseline
    往正确方向推回去的
    candidate objective 成分

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `transition_delta_candidate_objective_rankings`
  - `transition_delta_flip_thresholds_vs_baseline`

## 一句话结论
- 当前实验线已经把
  `frame_delta`
  候选从
  “有希望的 sidecar”
  推进到
  “有明确翻转门槛的 candidate objective”；
  下一步若继续做 objective-level 设计，
  最值得先拿来试的两档权重是：
  - `λ ≈ 0.3`
  - `λ ≈ 0.75`
