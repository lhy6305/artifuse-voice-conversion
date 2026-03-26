# 2026-03-27 Stage5 native teacher `residualshapecond` scale operating-region 收紧报告

## 结论
- 在 `docs/417`
  确认输出侧 `residual-shape` handoff
  首次把 validation3
  拉出 `auto_reject` 之后，
  我继续只收紧这一条 route，
  没有回到别的 family。
- 新增了：
  - `residual_shape_branch_condition_scale`
    全链路透传
  - CLI / checkpoint / export / probe
    全部写回这个参数
- 结果是：
  - `scale = 0.5`
    保住 `3/3 review_required`
    的同时，
    相对 `scale = 1.0`
    进一步压低了
    template-collapse 与 brightness
  - `scale = 0.25`
    同样保住 `3/3 review_required`，
    并重新拿回
    `selected_stable_late_stop = step24`，
    但 heard-path collapse / brightness
    略差于 `0.5`
- 因而当前最佳口径是：
  - `0.5`
    更像当前听审代理指标下的 strongest setting
  - `0.25`
    更像 selector / RMS stability
    更保守的一档
  - 两者都还没修掉
    `envelope-following`

## 一、实现补充
- 新参数：
  - `residual_shape_branch_condition_scale`
- 代码落点：
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
  - `src/v5vc/stage5_speech_emergence_probe.py`
  - `src/v5vc/cli.py`
- 当前它会写回：
  - training summary
  - checkpoint `model_config`
  - export `branch_label`
  - structure probe `decode_runtime`
  - speech-emergence probe `decode_runtime`

## 二、`scale = 0.5`

### 1. 产物
- training：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- structure probe：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_round1_1/stage5_waveform_decoder_structure_probe.md`
- speech-emergence probe：
  - `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale050_round1_1/stage5_speech_emergence_probe.md`

### 2. selector
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.851041`
- `decoded_to_target_rms_ratio = 0.960502`
- `selected_stable_late_stop = null`

### 3. validation3
- `auto_reject_count = 0`
- `review_required_count = 3`
- 三条样本：
  - `162`
    - `decoded_frame_template_cosine_mean = 0.981016`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.908067`
    - `spectral_centroid_gap_hz = 4164.233218`
    - `spectral_high_band_energy_ratio_gap = 0.37631`
  - `138`
    - `decoded_frame_template_cosine_mean = 0.978867`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.900608`
    - `spectral_centroid_gap_hz = 4064.43753`
    - `spectral_high_band_energy_ratio_gap = 0.318682`
  - `106`
    - `decoded_frame_template_cosine_mean = 0.970265`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.909515`
    - `spectral_centroid_gap_hz = 4213.336638`
    - `spectral_high_band_energy_ratio_gap = 0.327931`

### 4. aggregate
- structure probe：
  - `fused_hidden_template_cosine_mean = 0.962972`
  - `waveform_frames_template_cosine_mean = 0.987866`
  - `decoded_frames_template_cosine_mean = 0.975055`
- speech-emergence probe：
  - `decoded_frame_template_cosine_mean = 0.975055`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.892999`
  - `spectral_centroid_gap_hz = 3955.47168`
  - `spectral_high_band_energy_ratio_gap = 0.326294`

## 三、`scale = 0.25`

### 1. 产物
- training：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- structure probe：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_round1_1/stage5_waveform_decoder_structure_probe.md`
- speech-emergence probe：
  - `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_round1_1/stage5_speech_emergence_probe.md`

### 2. selector
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.85184`
- `decoded_to_target_rms_ratio = 0.992803`
- `selected_stable_late_stop = step24`

### 3. validation3
- `auto_reject_count = 0`
- `review_required_count = 3`
- 三条样本：
  - `162`
    - `decoded_frame_template_cosine_mean = 0.981364`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.908384`
    - `spectral_centroid_gap_hz = 4250.343184`
    - `spectral_high_band_energy_ratio_gap = 0.383631`
  - `138`
    - `decoded_frame_template_cosine_mean = 0.979332`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.898847`
    - `spectral_centroid_gap_hz = 4144.882615`
    - `spectral_high_band_energy_ratio_gap = 0.325393`
  - `106`
    - `decoded_frame_template_cosine_mean = 0.970994`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.907293`
    - `spectral_centroid_gap_hz = 4291.474083`
    - `spectral_high_band_energy_ratio_gap = 0.334355`

### 4. aggregate
- structure probe：
  - `fused_hidden_template_cosine_mean = 0.962289`
  - `waveform_frames_template_cosine_mean = 0.987695`
  - `decoded_frames_template_cosine_mean = 0.975636`
- speech-emergence probe：
  - `decoded_frame_template_cosine_mean = 0.975636`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.891069`
  - `spectral_centroid_gap_hz = 4036.778076`
  - `spectral_high_band_energy_ratio_gap = 0.333024`

## 四、三档对照

### 1. 相对 `scale = 1.0`
- `scale = 0.5`
  - 保住 `3/3 review_required`
  - `decoded_frame_template_cosine_mean`
    从 `0.978362`
    降到 `0.975055`
  - `spectral_centroid_gap_hz`
    从 `4218.044922`
    降到 `3955.47168`
  - `spectral_high_band_energy_ratio_gap`
    从 `0.346903`
    降到 `0.326294`
- `scale = 0.25`
  - 也保住 `3/3 review_required`
  - `decoded_frame_template_cosine_mean`
    降到 `0.975636`
  - `spectral_centroid_gap_hz`
    降到 `4036.778076`
  - `spectral_high_band_energy_ratio_gap`
    降到 `0.333024`
  - 同时重新拿回
    `selected_stable_late_stop = step24`

### 2. `0.5` 对 `0.25`
- `0.5`
  更强的地方：
  - 听审代理 collapse 更低：
    - `decoded_frame_template_cosine_mean`
      `0.975055 < 0.975636`
  - brightness 更低：
    - `spectral_centroid_gap_hz`
      `3955.47 < 4036.78`
    - `spectral_high_band_energy_ratio_gap`
      `0.326294 < 0.333024`
- `0.25`
  更强的地方：
  - selector 重新满足：
    - `selected_stable_late_stop = step24`
  - `decoded_to_target_rms_ratio`
    更接近 `1.0`：
    - `0.992803`
      优于
      `0.960502`

### 3. 两者共同没解决的东西
- `decoded_frame_rms_to_aligned_frame_rms_corr`
  仍都稳定在：
  - `~0.89`
- 这说明：
  - 当前优化确实在调
    collapse / brightness operating region
  - 但还没有动到
    `envelope-following`
    这个剩余主病灶

## 五、当前主线判断
1. `branch_mean_contrast + residualshapecond`
   当前已正式从“可尝试候选”
   升格为“应继续保留的主线 route”。
2. 当前最强 heard-path setting
   暂时应写作：
   - `residual_shape_branch_condition_scale = 0.5`
3. 当前最强 selector-side stability setting
   应写作：
   - `residual_shape_branch_condition_scale = 0.25`
4. 下一步不应：
   - 重新回到 hidden-side adapter
   - 也不应把 `scale` 做成无止境 sweep
5. 更合理的下一步应是：
   - 在 `0.25 ~ 0.5`
     这段已成立的 operating region 内，
     直接处理
     `envelope-following`
   - 而不是继续只围绕
     brightness 或 selector 指标
     做单维优化

## 一句话结论
- 输出侧 `residual-shape` handoff
  的 scale 收紧是有效的，
  但当前收益主要是把
  `collapse / brightness / selector`
  三者之间的 operating region
  看清楚了；
  真正还没解决的，
  仍是
  `envelope-following`。
