# 2026-03-21 用户线 inference-side 归一化试验报告

## 结论
- 本轮继续沿用户线方向推进，
  没有改训练。
- 当前已完成
  inference-side
  最小归一化试验，
  结论是：
  - 只改固定 conditioning
    没有实质作用
  - 只做
    `q01/q99`
    分位裁剪
    也几乎没有作用
  - 做更强的
    `reference_affine_match`
    后，
    一部分门控/幅度指标
    确实更接近训练内分布，
    但高频异常仍没有被真正拉回
- 当前更准确的工程判断是：
  - 简单的一阶分布匹配
    还不足以把用户线输出拉回健康音色区
  - 所以短期内不应假设：
    - “加一个简单 inference 归一化”
      就能直接修好 buzzing

## 本轮新增能力

### 1. decoder behavior probe 新增归一化策略
- CLI：
  - `analyze-offline-mvp-teacher-first-vc-decoder-behavior`
- 新增参数：
  - `--normalization-strategy`

### 2. 当前支持的策略
- `none`
- `conditioning_reference_mean`
- `reference_q01_q99_clip`
- `reference_affine_match`
- `conditioning_reference_mean_plus_reference_q01_q99_clip`

## 试验对象
- `segment_0001_0000020110_0000021640.wav`
- `segment_0061_0000300400_0000300910.wav`
- `peak_011_0002370615_top_peak.wav`

## 本轮结果

### 1. `conditioning_reference_mean` 基本无变化
- 这轮 smoke
  显示：
  - `alpha`
  - `s_spk_target`
  - `s_geom_target`
  的参考均值替换
    对 decoded 结果几乎没有影响
- 更准确的解释是：
  - 当前固定 target conditioning
    很可能本来就已经与训练参考常量接近
  - 当前主问题不主要在这几个固定常量

### 2. `reference_q01_q99_clip` 几乎无变化
- triplet probe
  结果几乎与基线重合：
  - 常规 segment
    `HF=0.479510 -> 0.479510`
  - 高静音 case
    `HF=0.477566 -> 0.477566`
  - peak case
    `HF=0.477874 -> 0.477877`
- 说明：
  - 当前问题不是简单的：
    - 某些通道落到参考分位区间外
    - 然后 clamp 一下就能修回去

### 3. `reference_affine_match` 有部分改善，但没触及核心高频异常
- 常规 segment：
  - `outside_q01_q99_fraction`
    从
    `0.666667`
    降到
    `0.238095`
  - `abs_z_median`
    从
    `2.617021`
    降到
    `0.126182`
  - 但
    `HF`
    仍是
    `0.477256`
- peak case：
  - `outside_q01_q99_fraction`
    从
    `0.476190`
    降到
    `0.333333`
  - `abs_z_median`
    从
    `2.875917`
    降到
    `1.109710`
  - 但
    `HF`
    仍是
    `0.476869`
- 高静音 case：
  - 没有改善，
    反而：
    - `centroid`
      升到
      `3432.93`
    - `bandwidth`
      升到
      `5373.09`
    - `HF`
      仍是
      `0.478953`

## 当前解释
- `reference_affine_match`
  能把：
  - gate mean/std
  - gate active fraction
  - waveform RMS
  - 一部分中低阶统计
  往训练内分布拉近
- 但它不能把：
  - `decoded_spectral_high_band_energy_ratio`
  - `decoded_spectral_rolloff95_hz`
  - `decoded_spectral_centroid_hz`
  真正拉回正常范围
- 这说明：
  - 当前 buzzing
    不是简单的一阶通道分布失配
  - 更像是：
    user-line
    当前控制语义
    与 Stage5 checkpoint
    学到的可用映射关系
    本身就不兼容

## 当前建议的下一步
1. 当前不建议把
   `reference_affine_match`
   直接升格为正式用户线默认，
   因为它没有真正解决高频异常。
2. 若继续用户线，
   下一题应优先转向：
   - 更结构化的 control 替换试验
   - 例如只替换
     `z_art`
     或只替换
     `event_probs`
     family
   - 明确哪一族动态控制
     最可能触发失配
3. 在这之前，
   当前最小 runtime
   仍应保留
   `applicability_risk`
   告警口径，
   不当作质量已通过的成品入口

## 一句话结论
- 本轮已经把
  “简单 inference 归一化能不能救回用户线 buzzing”
  这个问题压实了一步；
  当前答案更接近：
  - 不能靠简单常量回拉、
    分位裁剪、
    或一阶 affine 匹配
    直接修好，
  - 下一步要去定位
    到底是哪一族动态控制
    触发了 Stage5 checkpoint
    的适用性失配。
