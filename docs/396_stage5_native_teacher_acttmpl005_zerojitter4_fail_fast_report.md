# 2026-03-26 Stage5 native teacher `acttmpl005 + zero_target_flux_jitter=4.0` fail-fast 报告

## 结论
- 这条 `objective-side` 新候选应正式停线。
- 在修正后的 export 语义下，`fullsplit24 -> validation3 real decoded.wav` 仍然是 `3/3 auto_reject_obvious_buzz`。
- 而且相对当前 corrected native baseline，它明显更差，不具备继续扩 horizon 或扫同族小权重的价值。

## 变更内容
- 新增 loss：
  - `frame_spectral_flux_zero_target_jitter_weight`
- 本轮候选配置：
  - `waveform = 0.5`
  - `stft = 0.5`
  - `rms_guard = 0.2`
  - `activity_gate = 0.2`
  - `active_template = 0.05`
  - `frame_spectral_flux_zero_target_jitter = 4.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 代码与接线确认
- 新 loss 已接通到：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 1-step smoke 已确认：
  - `loss_weights.frame_spectral_flux_zero_target_jitter = 4.0`
  - `loss_metrics.loss_frame_spectral_flux_zero_target_jitter_0p05` 非零
- smoke 过程中顺手暴露并修复了两个旧断点：
  - `train-step / training-loop` 的 `multires_stft_short_weight` parser / signature 不完整
  - 新增 `zero_target_flux_jitter` 的 CLI parser / dispatch 尚未补全
- 本轮实验是在修复上述 plumbing 后运行的。

## 训练与导出产物
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint 选择：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 关键结果
- selected checkpoint:
  - `step = 24`
  - `validation loss_total = 1.130953`
- relative to corrected native baseline (`391/394`)：
  - baseline selected checkpoint `loss_total = 0.554104`
  - 当前候选明显更差

### validation3 real decoded
- `buzz_reject_summary.auto_reject_count = 3`
- `buzz_reject_summary.all_records_auto_reject = true`

### 162 对照
- baseline:
  - `loss_total = 0.55544`
  - `spectral_centroid_gap_hz = 4999.124195`
  - `spectral_high_band_energy_ratio_gap = 0.338207`
- candidate:
  - `loss_total = 1.076741`
  - `spectral_centroid_gap_hz = 9045.079383`
  - `spectral_high_band_energy_ratio_gap = 0.718561`

## 判断
- probe 里看起来较强的 `active_template + zero-target flux-jitter` 组合，放到 native teacher fullsplit 真 decoded 上仍然失败。
- 这说明当前问题不能再写成“只是少一个更保守的 frame-structure penalty”。
- 后续不再继续：
  - `zero_target_flux_jitter` 同族小权重 sweep
  - `active_template + zero_target_flux_jitter` 组合微调

## 下一步
- 转去更结构性的 `fusion / fused_hidden / forward-path` 候选。
- 不再继续在同一类 waveform frame objective 上做小修。
