# 394. Stage5 export 语义修正后的最小回补重跑确认报告

## 结论
- 最小回补重跑已完成：
  - native teacher baseline `validation3`
  - `acttmpl005_delta6` candidate `validation3`
- 旧结论没有被推翻，而是被修正后再次确认：
  - native teacher baseline 仍然是 `3/3 auto_reject_obvious_buzz`
  - `acttmpl005_delta6` candidate 仍然是 `3/3 auto_reject_obvious_buzz`
  - 而且 candidate 相对 baseline 仍明显更差
- 因此：
  - `docs/391_stage5_native_teacher_buzz_recheck_and_physiology_data_assessment.md`
  - `docs/392_stage5_native_teacher_acttmpl005_delta6_fail_fast_report.md`
  现在都可以恢复为当前主线可引用结论
- `393` 的影响评估本身仍成立，但其中关于 `391 -> 392` “尚待确认”的部分现在已经关闭。

## 一、回补重跑内容

### 1. native teacher baseline
- 新导出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_2`
- 关键文件：
  - `nores_vocoder_audio_export.json`

### 2. `acttmpl005_delta6` candidate
- 新导出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_acttmpl005_delta6_fullsplit24_validation3_round1_2`
- 关键文件：
  - `nores_vocoder_audio_export.json`

## 二、baseline 回补结果

### 1. buzz gate
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 当前新口径下的关键事实
- `waveform_decode.use_predicted_activity_gate = true`
- `waveform_decode.predicted_activity_gate_apply_mode = post_ola_envelope`
- `loss_metrics_semantics` 已明确写出：
  - metric 权重来自 checkpoint training summary
  - `activity_gate_weight = 0.2`
  - `active_template_weight = 0.0`
  - `frame_delta_weight = 0.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
  - `exactly_matches_decoded_audio = false`

### 3. 三条样本仍是同一类 native buzz
- `target::chapter3_3_firefly_162`
  - `loss_total = 0.55544`
  - `spectral_centroid_gap_hz = 4999.124195`
  - `spectral_high_band_energy_ratio_gap = 0.338207`
- `target::chapter3_3_firefly_138`
  - `loss_total = 0.595536`
  - `spectral_centroid_gap_hz = 4886.46595`
  - `spectral_high_band_energy_ratio_gap = 0.28214`
- `target::chapter3_4_firefly_106`
  - `loss_total = 0.540066`
  - `spectral_centroid_gap_hz = 4982.211332`
  - `spectral_high_band_energy_ratio_gap = 0.291194`

## 三、candidate 回补结果

### 1. buzz gate
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 当前新口径下的关键事实
- `waveform_decode.use_predicted_activity_gate = true`
- `waveform_decode.predicted_activity_gate_apply_mode = post_ola_envelope`
- `loss_metrics_semantics` 已明确写出：
  - metric 权重来自 candidate checkpoint training summary
  - `activity_gate_weight = 0.2`
  - `active_template_weight = 0.05`
  - `frame_delta_weight = 6.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
  - `exactly_matches_decoded_audio = false`

### 3. candidate 仍比 baseline 更差
- `target::chapter3_3_firefly_162`
  - baseline:
    - `loss_total = 0.55544`
    - `spectral_centroid_gap_hz = 4999.124195`
    - `spectral_high_band_energy_ratio_gap = 0.338207`
  - candidate:
    - `loss_total = 6.754951`
    - `spectral_centroid_gap_hz = 10629.966157`
    - `spectral_high_band_energy_ratio_gap = 0.623384`
- `target::chapter3_3_firefly_138`
  - baseline:
    - `0.595536`
    - `4886.46595`
    - `0.28214`
  - candidate:
    - `6.358903`
    - `10545.355771`
    - `0.568219`
- `target::chapter3_4_firefly_106`
  - baseline:
    - `0.540066`
    - `4982.211332`
    - `0.291194`
  - candidate:
    - `6.749262`
    - `10599.423992`
    - `0.57489`

## 四、这次回补改变了什么
- 改变的是：
  - 现在这两份结论已明确建立在修正后的 export 语义之上
  - 不再依赖旧版默认值或旧版 metric 继承逻辑
- 没改变的是：
  - native teacher baseline 本身仍然明显 buzz
  - `acttmpl005_delta6` 仍然是更差的失败候选

## 五、对当前主线的影响
- `391` 的主结论现在恢复为正式可用：
  - native teacher 路线自己已经在真实 `decoded.wav` 上稳定 obvious buzz
- `392` 的主结论现在恢复为正式可用：
  - `acttmpl005_delta6` 这条 native teacher objective 组合应正式停线
- 因此下一轮可以恢复新实验，但范围仍保持：
  - `native teacher buzz` 主线
  - 不恢复 student 蒸馏
  - 不引入新模态
