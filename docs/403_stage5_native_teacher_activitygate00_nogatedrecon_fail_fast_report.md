# 403. Stage5 native teacher `activity_gate_weight=0.0 + no gated reconstruction` fail-fast 报告

## 结论
- 这条 “去掉 training-side activity gate 监督，并关闭训练期 predicted gate reconstruction” 的 native teacher 候选也应正式停线。
- 它没有把模型从 buzz 假解里拉出来，真实 `validation3 decoded.wav` 仍是 `3/3 auto_reject_obvious_buzz`。
- 这说明当前主故障不能简单归因于：
  - `activity_gate_weight` 太大
  - 或 `use_predicted_activity_gate` 本身把模型推成了 envelope-following 假解

## 背景
- 这条线的假设是：
  - 当前 template-collapse 可能被 training-side 的 `activity_gate` 监督和 gated reconstruction 放大
- 因此本轮直接做最小否证：
  - `activity_gate_weight = 0.0`
  - `use_predicted_activity_gate = false`
  - 其它主损失保持不变
- 需要强调：
  - export 仍使用当前用户最终会听到的 decode 语义：
    - `use_predicted_activity_gate = true`
    - `predicted_activity_gate_apply_mode = post_ola_envelope`

## 配置与产物
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate00_nogatedrecon_contractv2_normfix_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_activitygate00_nogatedrecon_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_activitygate00_nogatedrecon_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 关键结果
- selected checkpoint：
  - `step = 24`
  - `validation loss_total = 0.766663`
- training summary 明确记录：
  - `activity_gate = 0.0`
  - `use_predicted_activity_gate = false`
- validation3 real decoded：
  - `buzz_reject_summary.auto_reject_count = 3`
  - `buzz_reject_summary.all_records_auto_reject = true`

## 和 corrected baseline 的对照
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_2/nores_vocoder_audio_export.json`
  - `target::chapter3_3_firefly_162`
    - `loss_total = 0.55544`
    - `spectral_centroid_gap_hz = 4999.124195`
    - `spectral_high_band_energy_ratio_gap = 0.338207`

- candidate：
  - `target::chapter3_3_firefly_162`
    - `loss_total = 0.783413`
    - `spectral_centroid_gap_hz = 9184.932004`
    - `spectral_high_band_energy_ratio_gap = 0.578928`
  - `target::chapter3_3_firefly_138`
    - `loss_total = 0.786869`
    - `spectral_centroid_gap_hz = 9159.178629`
    - `spectral_high_band_energy_ratio_gap = 0.527475`
  - `target::chapter3_4_firefly_106`
    - `loss_total = 0.769993`
    - `spectral_centroid_gap_hz = 9282.691285`
    - `spectral_high_band_energy_ratio_gap = 0.536661`

## 解读
- 这条线已经把一个常见误判否掉了：
  - 不是把 `activity_gate_weight` 归零、关掉 training-side gated reconstruction，就能自然摆脱 buzz
- 它相对 `gate_masked_halfsplit_v1` 没那么灾难，但仍然共享同一种失败模式：
  - 高频亮度显著偏高
  - frame template-collapse 持续存在
  - decoded 仍被 obvious-buzz gate 直接否掉
- 所以后续不再继续：
  - `activity_gate_weight` 同层小 sweep
  - `use_predicted_activity_gate` 开关微调
  - “先关掉训练期 gate 再看会不会自然长出人声”的同类路线

## 下一步
- 当前 native teacher 主线应继续上收到：
  - 更根本的 objective / target / contract 语义层
  - 尤其是 noise/periodic target family 与解码含义
- 不再把主要希望放在：
  - `activity_gate` 小权重
  - gated reconstruction 开关
