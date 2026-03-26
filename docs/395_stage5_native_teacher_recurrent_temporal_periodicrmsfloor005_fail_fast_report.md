# 395. Stage5 native teacher `recurrent + temporal + periodic_rms_floor=0.05` fullsplit24 fail-fast 报告

## 结论
- 已完成一条新的 native teacher 最小结构候选：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `periodic_waveform_frame_delta_weight = 0.25`
  - `periodic_waveform_frame_adjacent_cosine_weight = 0.01`
  - `periodic_waveform_frame_rms_floor_weight = 0.05`
- 这条线在训练 summary 上看起来不是完全静止：
  - `validation step24 loss_waveform = 0.121032`
  - `loss_stft = 0.330765`
  - `decoded_to_target_rms_ratio = 0.928559`
- 但真实 `decoded.wav` fail-fast 结果是否定的，而且比当前 native teacher baseline 更差：
  - `validation3` 导出仍是 `3/3 auto_reject_obvious_buzz`
  - 三条样本的 `spectral_centroid_gap_hz`
    从 baseline 的约 `4.9~5.0k`
    恶化到约 `9.3~9.5k`
  - `spectral_high_band_energy_ratio_gap`
    也从 baseline 的约 `0.28~0.34`
    恶化到约 `0.76~0.81`
- 因此这条 `recurrent + periodic_rms_floor=0.05` 路线应正式停线：
  - 不扩 horizon
  - 不导试听包
  - 不再把“adjacent cosine 可能更低”当成继续投资的理由

## 一、实验目录

### 1. 训练
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_recurrent_temporal_periodicrmsfloor005_fullsplit24_round1_1/`

### 2. checkpoint 选择
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_recurrent_temporal_periodicrmsfloor005_fullsplit24_round1_1/`

### 3. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_recurrent_temporal_periodicrmsfloor005_fullsplit24_validation3_round1_1/`

## 二、运行口径
- 数据集：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 共同保留：
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `activity_gate_weight = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- 新候选：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `periodic_waveform_frame_delta_weight = 0.25`
  - `periodic_waveform_frame_adjacent_cosine_weight = 0.01`
  - `periodic_waveform_frame_rms_floor_weight = 0.05`
- 训练预算：
  - `num_steps = 24`
  - `packages_per_step = 4`
  - `validation_interval = 12`
  - `checkpoint_interval = 12`
  - `seed = 20260326`
  - `deterministic = true`

## 三、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 4.404278`
- `loss_waveform = 0.121032`
- `loss_stft = 0.330765`
- `loss_rms_guard = 0.112212`
- `decoded_to_target_rms_ratio = 0.928559`

### 2. 如何解读这组训练数值
1. 这组数字说明：
   - 这不是“完全没学到东西”的假实验
   - `recurrent + temporal + local periodic RMS floor`
     确实在改动训练动力学
2. 但它没有自动转化成更好的真实 decoded：
   - 训练 summary 的局部改善
   - 不足以抵消 decode 后的高频 harsh buzz 恶化

## 四、真实 decoded fail-fast 结果

### 1. buzz gate 汇总
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 相对当前 native baseline 的逐条对照

#### `target::chapter3_3_firefly_162`
- baseline:
  - `loss_total = 0.55544`
  - `spectral_centroid_gap_hz = 4999.124195`
  - `spectral_high_band_energy_ratio_gap = 0.338207`
  - `decoded_frame_template_cosine_mean = 0.989028`
  - `decoded_frame_adjacent_cosine_mean = 0.991827`
- candidate:
  - `loss_total = 0.890892`
  - `spectral_centroid_gap_hz = 9362.216389`
  - `spectral_high_band_energy_ratio_gap = 0.807327`
  - `decoded_frame_template_cosine_mean = 0.989385`
  - `decoded_frame_adjacent_cosine_mean = 0.992649`

#### `target::chapter3_3_firefly_138`
- baseline:
  - `loss_total = 0.595536`
  - `spectral_centroid_gap_hz = 4886.46595`
  - `spectral_high_band_energy_ratio_gap = 0.28214`
  - `decoded_frame_template_cosine_mean = 0.995464`
  - `decoded_frame_adjacent_cosine_mean = 0.998852`
- candidate:
  - `loss_total = 0.882451`
  - `spectral_centroid_gap_hz = 9345.363039`
  - `spectral_high_band_energy_ratio_gap = 0.758295`
  - `decoded_frame_template_cosine_mean = 0.993015`
  - `decoded_frame_adjacent_cosine_mean = 0.998525`

#### `target::chapter3_4_firefly_106`
- baseline:
  - `loss_total = 0.540066`
  - `spectral_centroid_gap_hz = 4982.211332`
  - `spectral_high_band_energy_ratio_gap = 0.291194`
  - `decoded_frame_template_cosine_mean = 0.993396`
  - `decoded_frame_adjacent_cosine_mean = 0.999483`
- candidate:
  - `loss_total = 0.858843`
  - `spectral_centroid_gap_hz = 9489.160026`
  - `spectral_high_band_energy_ratio_gap = 0.770757`
  - `decoded_frame_template_cosine_mean = 0.992315`
  - `decoded_frame_adjacent_cosine_mean = 0.999036`

### 3. decoded 侧的关键信号
1. 三条样本都不是“结构更好但还差一点”：
   - 高频亮度指标显著恶化
   - buzz gate 直接给出 `auto_reject_obvious_buzz`
2. `template / adjacent cosine`
   即便局部有轻微波动，
   也完全不够抵消亮度恶化
3. 当前更准确的判断是：
   - `recurrent + temporal`
     的训练侧优势
     在这版 fullsplit native teacher 上被 decode-side harsh buzz 放大问题覆盖了

## 五、与历史路线的关系
1. 这条线不是全新的盲试：
   - 它承接了
     `docs/307_stage5_contractv2_normfix_recurrent_temporal_followup_report.md`
     里“`recurrent + explicit temporal loss` 最接近有效信号”的历史判断
2. 但本轮给出了更高等级的反证：
   - 放到当前 native teacher fullsplit24
   - 再看真实 `decoded.wav`
   - 这条线不是“值得继续打磨”，而是“已应停线”
3. 因而当前不应再把旧 smoke 上的
   `adjacent cosine` 改善
   外推成这条分支仍有主线价值

## 六、当前判断
1. `recurrent + temporal + local periodic RMS floor`
   不是当前 native teacher buzz 的解法
2. 当前主故障并不是：
   - “还没把 RMS 稍微锚住”
3. 更像是：
   - 这类 recurrent-temporal 结构在当前 fullsplit teacher 线上
     会把 decoded 推向更亮、更尖的 harsh buzz
4. 所以下一步不应继续：
   - 扫 `periodic_waveform_frame_rms_floor_weight`
   - 再叠 `high_band_excess`
   - 或继续在同一 recurrent 分支上补小修

## 七、下一步建议
1. 先把这条 `recurrent` 路线正式封口
2. 然后用修正后的 native teacher Stage5 probes
   重看当前 baseline 的 buzz 根因
3. 下一条训练候选必须满足：
   - 相对当前正式 baseline 更保守
   - 不重复历史上已被 decoded 或听审判死的 recurrent/fusion-side 同层微调
   - 若通过最小 fail-fast，再尽快导出真实 `decoded.wav`

## 一句话结论
- `recurrent + temporal + periodic_rms_floor=0.05`
  这条 native teacher 候选在真实 `decoded.wav` 上明确更差，
  应正式停线；后续先回到修正后的 baseline probe，
  再决定下一条更保守的 native teacher 候选。
