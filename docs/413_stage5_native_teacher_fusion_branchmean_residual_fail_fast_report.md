# 2026-03-26 Stage5 native teacher `fusion_mode = branch_mean_residual_v1` fail-fast 报告

## 结论
- 这条更强的 fusion-path 结构候选已经完成 corrected native-teacher fullsplit24 真 decoded fail-fast。
- 结果仍是否定：
  - `validation3`
    仍是 `3/3 auto_reject_obvious_buzz`
  - 相对 corrected native baseline，
    三条样本的：
    - `loss_total`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    仍全部更差
- 但它和此前多数 fusion-side / decoder-side 候选不同：
  - 这次恶化幅度明显更小
  - 它确实比
    `fused_hidden_branch_mean_weight = 0.25`
    和多条旧结构候选更接近 baseline
- 因而当前更准确的结论不是：
  - “fusion-path structural 也全死了”
- 而是：
  - `branch_mean_residual_v1`
    这一个具体结构还不够，
    但当前主线仍应留在
    `fusion -> fused_hidden`
    结构改路，
    不回到 penalty sweep

## 一、背景
- 到 `docs/411`
  为止，
  corrected native-teacher 主线上，
  现有 fusion-side `loss`
  家族已经基本封口：
  - `fused_hidden_template + fused_hidden_delta`
  - `fused_hidden_branch_mean_weight = 0.25`
- 同时
  `docs/410`
  的 gate-off decoder-structure probe
  继续给出：
  - 主病灶仍在
    `fusion -> fused_hidden`
- 因而本轮不再做 loss 微扫，
  而是直接实现并推进：
  - `fusion_mode = branch_mean_residual_v1`
- 这条结构的语义是：
  - `branch_mean_hidden`
    作为 fusion 主通路
  - fusion 只学习 residual

## 二、产物目录

### 1. bootstrap 与 smoke
- `docs/412_stage5_fusion_branchmean_residual_v1_bootstrap_and_smoke_report.md`

### 2. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeanresidual_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 3. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeanresidual_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 4. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeanresidual_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 三、训练口径
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
- 结构变化：
  - `fusion_mode = branch_mean_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `decoder_branch_mean_mix_alpha = 0.0`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = false`

## 四、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.834916`
- `loss_waveform = 0.121895`
- `loss_stft = 0.307907`
- `loss_rms_guard = 0.108`
- `decoded_to_target_rms_ratio = 0.934293`

### 2. 如何解读
- 它明显优于：
  - `fused_hidden_branch_mean_weight = 0.25`
    的 `loss_total = 0.916737`
- 也说明：
  - 这次结构改动不是假生效
  - 它确实把训练 objective
    拉到比上一条 fusion-side loss
    更合理的位置
- 但相对 corrected native baseline，
  仍然明显更差：
  - baseline selected checkpoint
    `loss_total = 0.554104`
  - current candidate
    `loss_total = 0.834916`

## 五、validation3 真实 decoded 结果

### 1. buzz gate 汇总
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 三条记录
- `target::chapter3_3_firefly_162`
- `target::chapter3_3_firefly_138`
- `target::chapter3_4_firefly_106`

## 六、和 corrected baseline 的对照

### 1. `target::chapter3_3_firefly_162`
- baseline：
  - `loss_total = 0.601405`
  - `spectral_centroid_gap_hz = 5003.986643`
  - `spectral_high_band_energy_ratio_gap = 0.338412`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.170058`
- candidate：
  - `loss_total = 0.859618`
  - `spectral_centroid_gap_hz = 5909.613318`
  - `spectral_high_band_energy_ratio_gap = 0.406588`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.89945`

### 2. `target::chapter3_3_firefly_138`
- baseline：
  - `loss_total = 0.674103`
  - `spectral_centroid_gap_hz = 4956.085863`
  - `spectral_high_band_energy_ratio_gap = 0.286543`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.041527`
- candidate：
  - `loss_total = 0.859596`
  - `spectral_centroid_gap_hz = 5829.424703`
  - `spectral_high_band_energy_ratio_gap = 0.352675`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.886634`

### 3. `target::chapter3_4_firefly_106`
- baseline：
  - `loss_total = 0.607221`
  - `spectral_centroid_gap_hz = 5113.494065`
  - `spectral_high_band_energy_ratio_gap = 0.29865`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.025772`
- candidate：
  - `loss_total = 0.835028`
  - `spectral_centroid_gap_hz = 5973.414242`
  - `spectral_high_band_energy_ratio_gap = 0.364229`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.899456`

## 七、解读
1. 这条候选没有赢：
   - 三条样本仍全部
     `auto_reject_obvious_buzz`
   - 三条样本相对 baseline
     仍全部更差
2. 但它也没有像许多前序候选那样
   把系统直接推向
   `9k~10k` 级别的 centroid gap
   或 `0.6+` 的 high-band gap
3. 相反，
   这次恶化幅度收敛到了：
   - centroid gap
     约 `+0.86k ~ +0.91k`
   - high-band gap
     约 `+0.054 ~ +0.068`
4. 这说明两件事同时成立：
   - `branch_mean`
     作为 fusion 主底座
     确实比先前几条结构 / loss 候选更合理
   - 但当前 `branch_mean + residual`
     这一个具体 handoff 形态，
     仍不足以把系统拉出当前
     template-collapse + envelope-following
     假解
5. 更关键的未解问题仍然是：
   - 虽然频谱亮度 gap 缩小了，
     但 `decoded_frame_rms_to_aligned_frame_rms_corr`
     又重新回到强正相关
   - 也就是：
     结构被拉近了，
     但仍没有摆脱
     “贴包络的模板 buzz”

## 八、当前主线判断
- 当前不应把这条结果写成：
  - `fusion-path structural`
    也应整体停线
- 更准确的口径是：
  - 现有 penalty 家族已封口
  - 第一条更强的 fusion-path structural 候选
    也已给出真实 fail-fast
  - 它仍失败，
    但比许多前序候选更接近 baseline
- 因而当前下一步应保持在：
  - `fusion -> fused_hidden`
    结构改路主线
- 但不继续：
  - `branch_mean_residual_v1`
    的 horizon 扩展
  - 或把它直接升级成同族 sweep
- 若继续，
  更合理的是：
  - 继续做更强的 fusion manifold / handoff-shape 候选
  - 而不是回到 penalty 或 decoder-only 小修

## 一句话结论
- `fusion_mode = branch_mean_residual_v1`
  是目前第一条在真实 fullsplit24 上
  明显比多数旧候选更接近 baseline 的 fusion-path 结构改路，
  但它仍然 `3/3 auto_reject_obvious_buzz`，
  仍不足以晋级为当前主解法。
