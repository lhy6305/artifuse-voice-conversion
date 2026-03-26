# 2026-03-26 Stage5 native teacher `branch_mean_contrast_residual_v1 + decoder_branch_condition_adapter` fail-fast 报告

## 结论
- 我把当前最强的 fusion backbone
  `fusion_mode = branch_mean_contrast_residual_v1`
  与现成的 decoder 交互补丁
  `use_decoder_branch_condition_adapter = true`
  组合起来，
  跑完了 corrected native-teacher fullsplit24 真 decoded fail-fast。
- 结果是否定：
  - `validation3`
    仍是 `3/3 auto_reject_obvious_buzz`
  - 相对仅用
    `branch_mean_contrast_residual_v1`
    的上一条 strongest candidate，
    它没有打掉
    `template-collapse + envelope-following`
  - 同时还把原本已经压下来的 brightness
    重新抬坏了一截
- 因而当前可以正式排除：
  - “在 `branch_mean_contrast` backbone 上，
    直接把 branch-conditioned hidden adapter
    重新插回 decoder”
    这条路径

## 一、背景
- `docs/415`
  已确认：
  - `branch_mean_contrast_residual_v1`
    是当前最强的 fusion structural 候选
  - 它已显著压下：
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
  - 但仍没有摆脱：
    - `template-collapse`
    - `envelope-following`
- 因而本轮要回答的问题是：
  - 是否能在不破坏其低亮度 operating region 的前提下，
    通过 decoder hidden 条件 adapter，
    把 branch-side 动态重新送进 waveform handoff，
    从而打掉剩余 collapse

## 二、结构语义
- backbone 保持：
  - `fusion_mode = branch_mean_contrast_residual_v1`
- 新增 decoder 侧补丁：
  - `use_decoder_branch_condition_adapter = true`
- 语义：
  - 保留
    `branch_mean + normalized contrast residual`
    的 fused hidden
  - 再用
    `cat(fused_hidden, periodic_hidden, noise_hidden)`
    生成 branch-conditioned decoder delta
  - 通过 gate
    受限地加回 decoder hidden
- 初始化仍是保守的：
  - adapter gate bias 为负
  - 三路 condition projection 初值为零

## 三、产物目录

### 1. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_branchcond_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_branchcond_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 3. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_branchcond_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### 4. gate-off structure probe
- `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_branchcond_round1_1/stage5_waveform_decoder_structure_probe.md`

## 四、训练口径
- 数据集：
  - `offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1`
- runtime：
  - `device = cuda:0`
- 训练预算：
  - `num_steps = 24`
  - `packages_per_step = 4`
  - `validation_interval = 12`
  - `checkpoint_interval = 12`
  - `sampler_mode = shuffle`
  - `seed = 20260326`
  - `deterministic = true`
- 主损失保持 baseline 可比：
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `activity_gate_weight = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- forward-path：
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_decoder_branch_condition_adapter = true`
  - `use_residual_shape_branch_condition_adapter = false`

## 五、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.839584`
- `loss_waveform = 0.124865`
- `loss_stft = 0.304858`
- `loss_rms_guard = 0.102743`
- `decoded_to_target_rms_ratio = 0.949945`

### 2. 如何解读
- 相对 `docs/415`
  的纯 `branch_mean_contrast`：
  - `loss_total`
    从 `0.826456`
    变差到
    `0.839584`
  - `decoded_to_target_rms_ratio`
    也从更接近 1.0 的
    `0.988113`
    恶化到
    `0.949945`
- 更关键的是：
  - 这次 `selected_stable_late_stop = null`
  - 说明它连上一条已经拿到的 selector-side 稳定性也丢掉了

## 六、validation3 真实 decoded 结果

### 1. buzz gate 汇总
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 三条记录
- `target::chapter3_3_firefly_162`
- `target::chapter3_3_firefly_138`
- `target::chapter3_4_firefly_106`

## 七、和 `docs/415` 的 strongest candidate 对照

### 1. `target::chapter3_3_firefly_162`
- pure `branch_mean_contrast`：
  - `loss_total = 0.837276`
  - `spectral_centroid_gap_hz = 1090.175877`
  - `spectral_high_band_energy_ratio_gap = 0.066059`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.905581`
- current combo：
  - `loss_total = 0.868894`
  - `spectral_centroid_gap_hz = 2941.823362`
  - `spectral_high_band_energy_ratio_gap = 0.517938`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.902476`

### 2. `target::chapter3_3_firefly_138`
- pure `branch_mean_contrast`：
  - `loss_total = 0.860457`
  - `spectral_centroid_gap_hz = 987.320155`
  - `spectral_high_band_energy_ratio_gap = 0.010965`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.891924`
- current combo：
  - `loss_total = 0.864439`
  - `spectral_centroid_gap_hz = 2876.771138`
  - `spectral_high_band_energy_ratio_gap = 0.466191`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.895426`

### 3. `target::chapter3_4_firefly_106`
- pure `branch_mean_contrast`：
  - `loss_total = 0.814991`
  - `spectral_centroid_gap_hz = 1086.298302`
  - `spectral_high_band_energy_ratio_gap = 0.0203`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.902094`
- current combo：
  - `loss_total = 0.835902`
  - `spectral_centroid_gap_hz = 2960.925213`
  - `spectral_high_band_energy_ratio_gap = 0.472312`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.904096`

## 八、关键信号变化
1. 这条组合没有改善剩余主故障：
   - `decoded_frame_template_cosine_mean`
     仍在
     `0.98958 ~ 0.993478`
   - `decoded_frame_rms_to_aligned_frame_rms_corr`
     仍稳定在
     `0.895 ~ 0.904`
2. 但它确实把 brightness 重新抬坏了：
   - `spectral_centroid_gap_hz`
     从 `~1.0k`
     回升到 `~2.9k`
   - `spectral_high_band_energy_ratio_gap`
     从 `0.01 ~ 0.07`
     回升到 `0.47 ~ 0.52`
3. 也就是说：
   - 它没有换来更少的 collapse
   - 只换来了更多的 brightness

## 九、structure probe 结果
- baseline collapse summary：
  - `fused_hidden_template_cosine_mean = 0.971562`
  - `waveform_frames_template_cosine_mean = 0.995827`
  - `decoded_frames_template_cosine_mean = 0.989991`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`
- 相对 `docs/415`
  的纯 `branch_mean_contrast`：
  - `fused_hidden_template`
    基本持平：
    - `0.972359 -> 0.971562`
  - 但 `waveform_frames_template`
    进一步恶化：
    - `0.99219 -> 0.995827`
  - `fused_to_waveform_template_gap`
    也扩大：
    - `0.019831 -> 0.024265`
- 这说明：
  - combo 方案并没有把 fusion 本体做坏很多
  - 真正变差的是：
    decoder-side hidden conditioning
    把已经较好的 fused_hidden
    又推向了更模板化的 frame projector operating region

## 十、解读
1. 当前可以把这条解释得更具体：
   - `branch_mean_contrast`
     这个 fusion backbone
     是有用的
   - 但直接把
     `branch-conditioned hidden delta`
     再插回 decoder hidden，
     不是有用的修复
2. 它的失败方式也很清楚：
   - 没打掉 envelope-following
   - 没打掉 template-collapse
   - 却明显抬回了 brightness
3. 所以下一步不应继续：
   - `branch_mean_contrast + branchcondadapter`
     horizon
   - 同族 hidden-side decoder adapter 小变体
4. 更合理的后续方向应是：
   - 保留
     `branch_mean_contrast`
     这条 backbone
   - 但不要再直接改 decoder hidden
   - 如果还要把 branch-side dynamics 重新引入 waveform，
     应改成更保守的
     frame-space / residual-shape
     交互方式，
     而不是 hidden-side adapter

## 一句话结论
- `branch_mean_contrast_residual_v1 + decoder_branch_condition_adapter`
  既没有解决剩余的 collapse，
  也破坏了上一条 strongest candidate
  的低亮度优势，
  应正式停线。
