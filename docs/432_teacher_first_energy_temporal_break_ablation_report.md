# 2026-03-27 teacher-first energy temporal-break 单项消融报告

## 结论
- 在 source-vs-reference probe
  已经把上游重点收窄到
  `energy / aper*energy`
  之后，
  我补了最小必要的单项对照：
  - `E_log_rms_norm = time_roll_half`
  - `E_log_rms_norm = time_shuffle`
- 当前结论是：
  1. 单独打断
     `energy`
     的时间对齐，
     确实能稳定压低
     residual `activity_corr`
  2. 但它明显不如
     `aper = time_shuffle`
     强
  3. 更不如
     `aper + energy = time_shuffle`
     这组组合
- 因而当前优先级应写成：
  - `energy`
    是稳定的上游异常杠杆
  - 但最终 residual EF
    不是它单独承载，
    仍然需要和
    `aper`
    联动处理

## 一、probe 目录
- `energy = time_roll_half`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_e_rh/`
- `energy = time_shuffle`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_e_shuf/`

## 二、关键对照
- baseline：
  - `decoded_template = 0.984637`
  - `activity_corr = 0.519889`
- `energy = time_roll_half`
  - `decoded_template = 0.983817`
  - `activity_corr = 0.426418`
  - `centroid = 6449.605469`
  - `high_band = 0.442062`
- `energy = time_shuffle`
  - `decoded_template = 0.983387`
  - `activity_corr = 0.367678`
  - `centroid = 6487.275391`
  - `high_band = 0.446802`
- `aper = time_shuffle`
  - `decoded_template = 0.983125`
  - `activity_corr = 0.259761`
- `aper + energy = time_shuffle`
  - `decoded_template = 0.981053`
  - `activity_corr = 0.101686`

## 三、读法
- `energy`
  单独做时间打断，
  说明它确实不是无关项：
  - `activity_corr`
    能从
    `0.519889`
    压到
    `0.426418 / 0.367678`
- 但这个收益仍明显弱于：
  - `aper = time_shuffle`
    的
    `0.259761`
- 也远弱于：
  - `aper + energy = time_shuffle`
    的
    `0.101686`

这说明：
- `energy`
  是当前最稳定的
  上游 envelope 对齐异常项
- 但最终可听残差
  不是只靠
  `energy`
  一条路在推
- `aper`
  仍是更强的下游
  residual EF 承载项
- 两者联动时，
  才是当前最接近
  有效去耦的方向

## 一句话结论
- 下一步若做训练/结构改动，
  可以把
  `energy`
  作为优先的上游对齐约束入口，
  但不能把它误当成唯一故障项；
  当前最有希望的方向仍是
  `aper + energy`
  联动去耦。 
