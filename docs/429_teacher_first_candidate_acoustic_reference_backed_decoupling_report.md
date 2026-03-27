# 2026-03-27 teacher-first 候选线 acoustic-state reference-backed 去耦 probe 报告

## 结论
- 我没有停在
  `aper / energy = zero`
  这层，
  而是继续补了两类
  reference-backed family override：
  - `reference_mean`
  - `reference_affine_match`
- 当前最关键的新结论是：
  1. `reference_mean`
     能压低一部分
     `activity_corr`，
     但本质上还是在把
     acoustic-state 动态压扁，
     不能算成功去耦
  2. `reference_affine_match`
     反而会把
     `activity_corr`
     与 brightness
     一起抬高，
     同时继续把输出拉离模板
  3. 这说明当前 residual 问题
     不是简单的：
     - 静态均值偏移
     - 静态方差失配
  4. 更准确地说：
     - `aper / energy`
       的时间动态本身
       同时承载着：
       - anti-template 动态
       - envelope-following 耦合
- 因而下一步主线应收敛为：
  - 不再继续做
    静态 reference replacement
    扫描
  - 直接研究如何对
    acoustic-state 的时间动态
    做去耦，
    而不是只改均值/尺度

## 一、代码推进
- `analyze-offline-mvp-teacher-first-vc-waveform-handoff`
  现在已支持：
  - `family=reference_mean`
  - `family=reference_affine_match`
- 它们都复用
  `normalize_scaffold_payload_for_decoder_probe(..., normalization_strategy='none')`
  的统一实现，
  不再走 handoff 私有的
  zero-only 旁路
- 当 override mode
  为 reference-backed 模式时，
  probe 会自动解析
  Stage5 train packages
  并构建 reference feature summary

## 二、probe 目录
- `aper = reference_mean`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_rm/`
- `E_log_rms_norm = reference_mean`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_e_rm/`
- `aper + E_log_rms_norm = reference_mean`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_e_rm/`
- `aper = reference_affine_match`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_aff/`
- `E_log_rms_norm = reference_affine_match`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_e_aff/`
- `aper + E_log_rms_norm = reference_affine_match`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_e_aff/`

## 三、与 baseline / zero 的关键对照
- baseline：
  - `decoded_template = 0.984637`
  - `activity_corr = 0.519889`
  - `centroid = 6510.052734`
  - `high_band = 0.449300`

### 1. `aper`
- `aper = zero`
  - `decoded_template = 0.988699`
  - `activity_corr = 0.217405`
- `aper = reference_mean`
  - `decoded_template = 0.988538`
  - `activity_corr = 0.297761`
- `aper = reference_affine_match`
  - `decoded_template = 0.983265`
  - `activity_corr = 0.535281`
  - `centroid = 6562.902832`
  - `high_band = 0.453626`

读法：
- `reference_mean`
  相比 `zero`
  只是在稍微保住一点
  anti-template，
  但包络相关性回升明显，
  仍然不构成好解
- `reference_affine_match`
  则几乎直接说明：
  - 只要保留
    `aper`
    的时间动态，
    residual envelope-following
    就会重新回来，
    甚至更高

### 2. `E_log_rms_norm`
- `energy = zero`
  - `decoded_template = 0.985994`
  - `activity_corr = 0.476136`
  - `centroid = 6340.537598`
  - `high_band = 0.427833`
- `energy = reference_mean`
  - `decoded_template = 0.987283`
  - `activity_corr = 0.366230`
  - `centroid = 6476.161621`
  - `high_band = 0.448174`
- `energy = reference_affine_match`
  - `decoded_template = 0.981025`
  - `activity_corr = 0.602283`
  - `centroid = 6629.927246`
  - `high_band = 0.458462`

读法：
- `energy`
  的静态 mean replacement
  会压低一部分
  `activity_corr`，
  但会带回更多模板化
- 一旦保留其时间动态
  并只对齐均值/尺度，
  则：
  - `activity_corr`
    反而更高
  - brightness
    也更高

### 3. `aper + energy`
- `aper + energy = zero`
  - `decoded_template = 0.988933`
  - `activity_corr = 0.141311`
- `aper + energy = reference_mean`
  - `decoded_template = 0.990502`
  - `activity_corr = 0.050668`
- `aper + energy = reference_affine_match`
  - `decoded_template = 0.979448`
  - `activity_corr = 0.604880`
  - `centroid = 6700.336426`
  - `high_band = 0.462461`

读法：
- 组合上的对比更直接：
  - `reference_mean`
    是最强的
    `activity_corr`
    压制，
    但也最接近
    “把动态直接抹掉”
  - `reference_affine_match`
    则是最强的
    anti-template 保留，
    但包络跟随和 brightness
    也一起最强

## 四、当前最稳的解释
- 这轮 probe
  已经足够排除：
  - “主要是静态均值错位”
  - “主要是静态尺度错位”
- 当前更稳的解释应写成：
  - `aper / energy`
    的时间变化轨迹
    本身在驱动 residual envelope-following
  - 同一套时间动态
    又在帮助系统脱离模板塌缩
- 所以下一步若要继续推进，
  应优先考虑：
  - 动态去耦
  - 时序形状约束
  - 限制 acoustic-state
    对 activity envelope
    的直接跟随
- 而不是继续：
  - reference mean replacement
  - reference affine replacement
  - 更大规模的静态分布修正

## 一句话结论
- 当前候选线 residual `envelope-following`
  的主问题已经进一步收敛为：
  - acoustic-state
    尤其 `aper / energy`
    的时间动态耦合，
    不是简单的静态分布失配；
  - `reference_mean`
    只能通过压扁动态来缓解，
  - `reference_affine_match`
    则会把这类时间动态重新放大回来。 
