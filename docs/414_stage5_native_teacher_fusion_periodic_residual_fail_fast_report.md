# 2026-03-26 Stage5 native teacher `fusion_mode = periodic_residual_v1` fail-fast 报告

## 结论
- 这条更偏 `periodic_hidden` 主骨架的 fusion-path 结构候选，
  已完成 corrected native-teacher fullsplit24 真 decoded fail-fast。
- 结果是否定：
  - `validation3`
    仍是 `3/3 auto_reject_obvious_buzz`
  - 相对 corrected native baseline，
    三条样本的：
    - `loss_total`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    仍全部更差
- 更关键的是，
  它还明显差于刚完成的
  `branch_mean_residual_v1`：
  - 高频亮度重新抬升到更坏的一档
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    仍保持强正相关
- 因而当前可以更明确地说：
  - “让 periodic branch 直接当 fusion 主骨架”
    这条 handoff-shape
    不是当前主解法

## 一、背景
- `docs/413`
  已确认：
  - `branch_mean_residual_v1`
    虽然仍失败，
    但已比多数旧候选更接近 corrected baseline
- 同时 gate-off decoder-structure probe
  里，
  `fused_hidden_from_periodic_hidden`
  是比 `branch_mean`
  还更强的去模板化 bypass 之一：
  - `decoded_template = 0.698365`
- 因而本轮要回答的问题是：
  - 如果把 fusion 主骨架进一步前推到
    `periodic_hidden`
    本身，
    并把 noise 只作为受限 residual 引入，
    是否会比 `branch_mean_residual_v1` 更接近可用解

## 二、结构语义
- 新候选：
  - `fusion_mode = periodic_residual_v1`
- 语义：
  - `periodic_hidden`
    作为 fusion 主骨架
  - 用
    `cat(periodic_hidden, noise_hidden, periodic_hidden - noise_hidden)`
    生成 residual context
  - 再经：
    - residual gate
    - residual projection
    生成受限 residual
  - 最终：
    - `fused_hidden = periodic_hidden + gated_residual`
- 初始化保持保守：
  - residual gate bias 为负
  - residual projection 初值为零

## 三、产物目录

### 1. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionperiodicresidual_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionperiodicresidual_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 3. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionperiodicresidual_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

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
- 其它主损失保持 baseline 可比：
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `activity_gate_weight = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- forward-path：
  - `fusion_mode = periodic_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `decoder_branch_mean_mix_alpha = 0.0`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = false`

## 五、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.869297`
- `loss_waveform = 0.123333`
- `loss_stft = 0.341188`
- `loss_rms_guard = 0.104835`
- `decoded_to_target_rms_ratio = 0.941623`

### 2. 如何解读
- 相对 corrected native baseline：
  - baseline selected checkpoint
    `loss_total = 0.554104`
  - current candidate
    `loss_total = 0.869297`
- 相对 `branch_mean_residual_v1`：
  - `0.869297`
    也差于
    `0.834916`
- 因而从 bootstrap objective
  这层，
  它已经没有超过上一条 fusion structural 候选

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

## 七、和 corrected baseline 的对照

### 1. `target::chapter3_3_firefly_162`
- baseline：
  - `loss_total = 0.601405`
  - `spectral_centroid_gap_hz = 5003.986643`
  - `spectral_high_band_energy_ratio_gap = 0.338412`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.170058`
- candidate：
  - `loss_total = 0.895967`
  - `spectral_centroid_gap_hz = 7303.20423`
  - `spectral_high_band_energy_ratio_gap = 0.549204`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.908223`

### 2. `target::chapter3_3_firefly_138`
- baseline：
  - `loss_total = 0.674103`
  - `spectral_centroid_gap_hz = 4956.085863`
  - `spectral_high_band_energy_ratio_gap = 0.286543`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.041527`
- candidate：
  - `loss_total = 0.891105`
  - `spectral_centroid_gap_hz = 7305.078263`
  - `spectral_high_band_energy_ratio_gap = 0.500444`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.894233`

### 3. `target::chapter3_4_firefly_106`
- baseline：
  - `loss_total = 0.607221`
  - `spectral_centroid_gap_hz = 5113.494065`
  - `spectral_high_band_energy_ratio_gap = 0.29865`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.025772`
- candidate：
  - `loss_total = 0.867817`
  - `spectral_centroid_gap_hz = 7477.555458`
  - `spectral_high_band_energy_ratio_gap = 0.512697`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.904302`

## 八、和 `branch_mean_residual_v1` 的对照
- `branch_mean_residual_v1`
  的三条样本大致停在：
  - `spectral_centroid_gap_hz = 5.83k ~ 5.97k`
  - `spectral_high_band_energy_ratio_gap = 0.352 ~ 0.407`
- 当前 `periodic_residual_v1`
  重新恶化到：
  - `spectral_centroid_gap_hz = 7.30k ~ 7.48k`
  - `spectral_high_band_energy_ratio_gap = 0.500 ~ 0.549`
- 这说明：
  - 虽然 direct bypass 里
    `periodic_hidden`
    很能去模板化，
  - 但把它直接抬成 fusion 主骨架后，
    当前 route 更容易滑回
    更亮、更尖的 harsh buzz

## 九、解读
1. 这条线没有证明：
   - `periodic_hidden`
     更接近解法
2. 真实结果恰好相反：
   - 它比
     `branch_mean_residual_v1`
     更差
   - 高频 brightness
     和 high-band 能量
     都明显更坏
3. 同时它和前一条结构候选共享同一个未解模式：
   - `decoded_frame_rms_to_aligned_frame_rms_corr`
     仍然强正相关
   - 也就是：
     即使 template 程度局部有变化，
     系统仍在走
     “贴包络的模板 buzz”
4. 因而当前主线不能再继续朝：
   - `periodic branch`
     直接升格成 fusion 主骨架
   这一方向扩展

## 十、当前主线判断
- 到这一步，
  当前 fusion-path structural 主线上可以更明确地区分两类方向：
  - `branch_mean_residual_v1`
    虽失败，但仍是当前最接近 baseline 的 structural 候选
  - `periodic_residual_v1`
    则说明“更偏 periodic 主骨架”的 handoff-shape 会重新拉高 harsh buzz
- 因而当前下一步不应做：
  - `periodic_residual_v1`
    同族 sweep
  - 更激进的 periodic-dominant fusion 扩展
- 更合理的下一步应是：
  - 留在
    `branch_mean`
    这一侧的 fusion manifold
  - 继续想办法抑制
    envelope-following
    而不是进一步推高 periodic dominance

## 一句话结论
- `fusion_mode = periodic_residual_v1`
  在真实 fullsplit24 上
  不但没有优于 corrected baseline，
  也明显差于
  `branch_mean_residual_v1`，
  应正式停线。
