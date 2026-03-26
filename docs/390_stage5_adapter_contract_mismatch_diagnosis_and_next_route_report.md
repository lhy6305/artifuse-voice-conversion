# 390. Stage5 adapter 合同错位诊断与下一步路线报告

## 结论
- 上一轮 `student_control_packet -> Stage5 decoded.wav` 的 fail-fast 结论仍成立，但这次把失败层级进一步定准了。
- 当前用于真实 decoded smoke 的 best Stage5 checkpoint，本质上是旧 `contractv2_normfix` 路线：
  - `source_scaffold_version = offline_teacher_vocoder_input_scaffold_v2`
  - noise branch 前 8 维语义家族是 `event_probs`
- 所以它不是“显式 `e_evt` consumer” checkpoint。
- 更关键的是：
  - 当前 student route 的主要偏移不在 periodic branch
  - 而在 noise branch 前 8 维 event family 的分布错位
- 但这条错位也不是 adapter 命名问题：
  - 在当前 `vuvbalancedgate48` candidate 上，`e_evt == legacy_event_probs`
  - 所以把 adapter 从 `e_evt` 切到 `legacy_event_probs`，不会改变 decoded 结果
- 因此下一步不该继续修 Stage5 adapter，也不该继续围绕 `e_evt vs legacy_event_probs` 改字段名。
- 更值钱的下一步已经收敛为：
  - 回到 Stage3 generation-side
  - 直接处理前 8 维 event family 的维度分布失衡

## 一、关键代码与合同事实

### 1. 当前 best Stage5 checkpoint 是旧 `v2/event_probs` 承接层
- 核对文件：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/packages/validation/target__chapter3_3_firefly_162/scaffold/teacher_vocoder_input_scaffold.pt`
- 结论：
  - `scaffold_version = offline_teacher_vocoder_input_scaffold_v2`
  - `noise_feature_semantics = ['event_probs', 'aper', 'vuv', 'E_log_rms_norm', 'alpha', 's_spk_target', 's_geom_target']`

### 2. 当前 candidate 上 `e_evt` 和 `legacy_event_probs` 实际相同
- 核对文件：
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate48_sample8_round1_1/records/target__chapter3_3_firefly_162.pt`
- 结论：
  - `mae = 0.0`
  - `cos = 1.0`
- 所以：
  - 对这版 candidate 来说，adapter 的 `noise_event_family = e_evt` 或 `legacy_event_probs` 只是语义标签不同
  - 不是实际张量不同

## 二、真实 decoded 对照

### 1. 三条可比 route
- student + current adapter：
  - `reports/runtime/streaming_student_stage5_audio_export_vuvbalancedgate48_smoke_round1_1/nores_vocoder_audio_export.json`
- student + legacy_event_probs-compatible adapter：
  - `reports/runtime/streaming_student_stage5_audio_export_vuvbalancedgate48_legacyevent_smoke_round1_1/nores_vocoder_audio_export.json`
- native teacher package + same checkpoint + same decode settings：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_162_postenv_compare_round1_1/nores_vocoder_audio_export.json`

### 2. 结果
- 三者都仍是：
  - `auto_reject_obvious_buzz`
- 但 student route 比 native teacher 稍差：
  - student:
    - `spectral_centroid_gap_hz = 5228.478641`
    - `high_band_gap = 0.365601`
    - `loss_total = 0.656386`
  - native teacher:
    - `spectral_centroid_gap_hz = 4999.124195`
    - `high_band_gap = 0.338207`
    - `loss_total = 0.516165`
- 说明：
  - 当前 Stage5 checkpoint 对该样本本来就不健康
  - 但 student packet 仍额外带来可量化退化

## 三、合同错位具体在哪

### 1. 8-sample contract compare
- 产物：
  - `reports/runtime/streaming_student_stage5_adapter_contract_compare_sample8_round1_1.json`
- 聚合结论：
  - periodic branch 基本对齐：
    - `z_art mean_cos = 0.99443`
  - noise / named-control 偏移更明显：
    - `event_presence_proxy mean_mae = 0.33637`
    - `f0_hz_log_norm mean_mae = 0.24269`
    - `vuv mean_mae = 0.21240`
    - `energy_proxy mean_mae = 0.27161`
- 当前最稳定的偏移不是“完全乱掉”，而是：
  - `event_presence_proxy` 系统性偏高
  - `energy_proxy` 系统性偏低
  - `f0 / vuv` 也偏，但没有 noise first-8 那么集中

### 2. 前 8 维 event family 的方向性错误已经很清楚
- teacher validation 全局均值：
  - `[0.594572, 0.282445, 0.204368, 0.551651, 0.195895, 0.496151, 0.462723, 0.598186]`
- student current packet 在 sample-8 上的均值：
  - `[0.041066, 0.032219, 0.061042, 0.925210, 0.468143, 0.016917, 0.016770, 0.221371]`
- 这说明当前 student 的 event family 不是“整体偏一点”，而是：
  - `dim0-2` 过低
  - `dim3-4` 过高
  - `dim5-7` 过低
- 大白话说：
  - 它在过度押注一小部分 voiced/aper-like 维度
  - 同时把其它结构维度压塌了

## 四、单样本 root-cause probe

### 1. 产物
- `reports/runtime/streaming_student_stage5_adapter_rootcause_probe_162_round1_1.json`

### 2. 结论
- 把 student 的 periodic branch 全替成 teacher：
  - 几乎没改善
- 把 student 的 noise branch 全替成 teacher：
  - 结果基本收敛到 native teacher baseline
- 只替换 student 的 noise 前 8 维：
  - 也能把结果显著拉向 teacher baseline
- 所以当前最强结论是：
  - 问题主病灶在 noise branch 前 8 维 event family
  - 不在 periodic branch
  - 更不在 `z_art` 单独一项

## 五、全局 affine 校准 probe

### 1. 便宜 probe 结果
- 我对 student 的 noise 前 8 维做了向 teacher validation 全局分布靠拢的 in-memory affine / mean-shift probe。
- 结果：
  - `centroid_gap_hz` 和 `high_band_gap` 有部分改善
  - 但仍然 `auto_reject_obvious_buzz`

### 2. 解释
- 这说明：
  - 方向打中了
  - 但单纯 adapter 侧分布校准不够
- 所以下一步不应继续修 adapter 公式，
  而要回到 Stage3 generation-side 真正修 event family 本体

## 六、下一步
- 正式停掉：
  - `e_evt vs legacy_event_probs` adapter 名义切换
  - 当前 minimal adapter 的继续微调
- 下一条主线应改为：
  - Stage3 event-family 维度分布校准
  - 重点是前 8 维：
    - 抑制 `dim3-4` 过强
    - 拉起 `dim0-2` 与 `dim5-7`
- 换句话说：
  - 下一步不是修 Stage5
  - 而是修 Stage3 生成出的 noise/event contract
