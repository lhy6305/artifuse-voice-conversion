# 401. Stage5 native teacher 非 recurrent residual decoder family fail-fast 报告

## 结论
- 我已将当前最值得做的三条非 recurrent residual decoder 候选全部推进到真实 `validation3 decoded.wav`：
  - `periodic_plus_noise_residual`
  - `periodic_plus_noise_residual_shape`
  - `periodic_plus_noise_factorized_residual`
- 三条结果全部是否定：
  - 都是 `3/3 auto_reject_obvious_buzz`
  - 都比 corrected native baseline 更差
  - 而且都共享同一种失败模式：
    - frame RMS 继续跟 target envelope
    - 高频能量显著偏高
    - 短时结构继续 template-collapse
- 因此，这整个“非 recurrent residual decoder family”在当前 native teacher contract 下应正式判停。

## 本轮执行
### 1. `periodic_plus_noise_residual`
- 训练：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_periodicnoise_residual_fullsplit24_round1_1`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_periodicnoise_residual_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicnoise_residual_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- 结果：
  - `best_validation step24 loss_total = 0.859222`
  - `3/3 auto_reject_obvious_buzz`

### 2. `periodic_plus_noise_residual_shape`
- 训练：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_periodicnoise_residualshape_fullsplit24_round1_1`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_periodicnoise_residualshape_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicnoise_residualshape_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- 结果：
  - `best_validation step24 loss_total = 0.854511`
  - `3/3 auto_reject_obvious_buzz`

### 3. `periodic_plus_noise_factorized_residual`
- 训练：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_periodicnoise_factorizedresidual_fullsplit24_round1_1`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_periodicnoise_factorizedresidual_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicnoise_factorizedresidual_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- 结果：
  - `best_validation step24 loss_total = 0.857728`
  - `3/3 auto_reject_obvious_buzz`

## 和 corrected baseline 的对照
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_2/nores_vocoder_audio_export.json`
  - `target::chapter3_3_firefly_162`
    - `loss_total = 0.55544`
    - `spectral_centroid_gap_hz = 4999.124195`
    - `spectral_high_band_energy_ratio_gap = 0.338207`

### 1. `periodic_plus_noise_residual`
- `target::chapter3_3_firefly_162`
  - `loss_total = 0.886632`
  - `spectral_centroid_gap_hz = 5861.769978`
  - `spectral_high_band_energy_ratio_gap = 0.720823`

### 2. `periodic_plus_noise_residual_shape`
- `target::chapter3_3_firefly_162`
  - `loss_total = 0.884755`
  - `spectral_centroid_gap_hz = 6201.497063`
  - `spectral_high_band_energy_ratio_gap = 0.716649`

### 3. `periodic_plus_noise_factorized_residual`
- `target::chapter3_3_firefly_162`
  - `loss_total = 0.885108`
  - `spectral_centroid_gap_hz = 6776.60057`
  - `spectral_high_band_energy_ratio_gap = 0.722169`

## 解读
- 这三条线已经把“给当前 native teacher decoder 一个更保守的 noise residual 通道，会不会比 `dual_branch_mix` 更好”这个问题回答清楚了：
  - 不会
- 相比 `dual_branch_mix`：
  - residual family 的 `spectral_centroid_gap_hz` 有时略低
  - 但 `spectral_high_band_energy_ratio_gap` 一直更差，听感风险仍然是同一种 harsh buzz
- 这说明当前主故障不只是“需要更保守的 residual 组合器”，而是更深的：
  - native teacher 当前 contract 下的 noise/periodic 解码语义本身不对
  - 继续在这族 non-recurrent residual decoder 上细修，性价比很低

## 额外说明
- 本轮两次出现 `selection/export` 并行竞态，表现为 export 先于 selection json 落盘启动。
- 这不是模型问题，也不影响最终结论；补跑 export 后结果已完整落盘。

## 下一步
- 不继续：
  - `periodic_plus_noise_residual*` 更长 horizon
  - 这三条线上的同层小 tweak
- 下一步应转去：
  - 更上游的 native teacher objective / target / contract 语义
  - 或重新审视当前 noise branch 的 target family 与解码含义
