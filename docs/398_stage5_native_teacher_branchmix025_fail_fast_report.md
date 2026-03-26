# 2026-03-26 Stage5 native teacher `decoder_branch_mean_mix_alpha=0.25` fail-fast 报告

## 结论
- 这条轻量 `forward-path structural` 候选也应正式停线。
- 它与 `fused_hidden_t005_d2` 大致同量级，虽然明显好于 `acttmpl005 + zerojitter4`，但真实 `decoded.wav` 仍是 `3/3 auto_reject_obvious_buzz`。
- 因此当前不能再把希望放在“轻量 branch-mean 混合”这一级别的 operating-point 小改路上。

## 背景
- 这条线的依据来自修正后的 decoder-structure probe：
  - `fused_hidden_from_branch_mean`
    是对 decoded template 化影响最大的变体之一
- 与 `fused_hidden_branch_mean_weight` 不同，
  这次试的是显式 forward-path：
  - `decoder_for_waveform = (1 - alpha) * fused_hidden + alpha * branch_mean_hidden`
  - `alpha = 0.25`

## 配置
- `waveform = 0.5`
- `stft = 0.5`
- `rms_guard = 0.2`
- `activity_gate = 0.2`
- `decoder_branch_mean_mix_alpha = 0.25`
- `use_predicted_activity_gate = true`
- `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 产物
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchmix025_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint 选择：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_branchmix025_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_branchmix025_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 关键结果
- selected checkpoint:
  - `step = 24`
  - `validation loss_total = 0.790651`
- relative to corrected native baseline：
  - baseline selected checkpoint `loss_total = 0.554104`
  - 仍明显更差

### validation3 real decoded
- `buzz_reject_summary.auto_reject_count = 3`
- `buzz_reject_summary.all_records_auto_reject = true`

### 162 对照
- baseline:
  - `loss_total = 0.55544`
  - `spectral_centroid_gap_hz = 4999.124195`
  - `spectral_high_band_energy_ratio_gap = 0.338207`
- candidate:
  - `loss_total = 0.804336`
  - `spectral_centroid_gap_hz = 6987.697943`
  - `spectral_high_band_energy_ratio_gap = 0.487147`

## 判断
- 这条结果说明：
  - probe 确实指出了有反应的结构方向
  - 但仅靠轻量 `branch_mean` 混合，还不足以让当前 native teacher route 脱离 buzz 假解
- 所以后续不再继续：
  - `decoder_branch_mean_mix_alpha`
    的小范围 sweep
  - 同级别轻量 operating-point mix 变体

## 下一步
- 当前 native teacher 主线应继续升级到更强的 `forward-path structural` 候选，
  例如真正改变 fusion / branch-conditioned decoder 形态。
- 不再继续叠弱 loss，也不再继续扫轻量 mix 系数。
