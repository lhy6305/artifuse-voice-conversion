# 2026-03-26 Stage5 native teacher `fused_hidden_branch_mean_weight=0.25` fail-fast 报告

## 结论
- 这条曾在最小 smoke 上给出第一条较强 fusion-side 正向信号的候选，到了 corrected native-teacher fullsplit24 真 decoded 之后，应正式停线。
- 它不是“参数没生效”的假实验：
  - `fused_hidden_branch_mean_weight = 0.25`
    已真实写进 training summary / checkpoint selection / export 语义链路
  - fullsplit24 训练、checkpoint selection、validation3 真实 `decoded.wav`
    都已跑通
- 但最终结果依然是否定：
  - `validation3`
    仍是 `3/3 auto_reject_obvious_buzz`
  - 相对 corrected native baseline，
    三条样本的：
    - `loss_total`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    都明显更差
- 因此当前可以更硬地说：
  - 现有 fusion-side `loss` 家族里，
    不只是
    `fused_hidden_template / fused_hidden_delta`
    已封口，
    连 smoke 上最像“碰到了正确层级”的
    `fused_hidden_branch_mean_weight = 0.25`
    也不能把 native teacher 拉出当前 template-collapse buzz 假解

## 一、本轮动机
- `docs/300_stage5_contractv2_normfix_fusedhidden_branchmean025_minimal_smoke_report.md`
  曾给出一条值得跟进的 smoke 信号：
  - `loss_fused_hidden_to_branch_mean_unit_rms_l1`
    明显下降
  - `loss_active_template`
    同时下降
  - `waveform / rms_guard`
    在 smoke 上没有明显恶化
- 同时当前 corrected baseline 的 gate-off decoder-structure probe
  继续明确指向：
  - 主病灶仍在 `fusion -> fused_hidden`
  - 绕过当前 fusion 直接喂
    `branch_mean / periodic_hidden / noise_hidden`
    会显著降低 template 化
- 因而这条 fullsplit24 fail-fast 要回答的问题是：
  - smoke 上的正向信号，
    是否意味着
    `fused_hidden_branch_mean_weight = 0.25`
    值得升级成真正的 native teacher 主线候选

## 二、产物目录

### 1. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusedhidden_branchmean025_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusedhidden_branchmean025_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 3. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusedhidden_branchmean025_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

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
- 保持和当前 corrected native baseline 可比的主损失：
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `activity_gate_weight = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- 唯一新增的 fusion-side loss：
  - `fused_hidden_branch_mean_weight = 0.25`
- forward-path 不改：
  - `waveform_decoder_mode = fused_single`
  - `decoder_branch_mean_mix_alpha = 0.0`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = false`

## 四、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.916737`
- `loss_waveform = 0.122746`
- `loss_stft = 0.329765`
- `loss_rms_guard = 0.112912`
- `decoded_to_target_rms_ratio = 0.931677`

### 2. 如何解读
- 这说明：
  - 这条线不是完全静止
  - `fused_hidden_branch_mean_weight`
    已真实参与优化
  - 训练数值也确实收敛到了一个稳定解
- 但和 corrected native baseline 对比，
  这个稳定解明显更差：
  - baseline selected checkpoint
    `loss_total = 0.554104`
  - 当前 candidate
    `loss_total = 0.916737`
- 因而 smoke 上的那条“碰到有效层级”信号，
  并没有转化成 fullsplit24 里的更优 bootstrap objective，
  更没有转化成更好的真实 decoded

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
  - `loss_total = 0.891002`
  - `spectral_centroid_gap_hz = 9019.826955`
  - `spectral_high_band_energy_ratio_gap = 0.65767`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.874278`

### 2. `target::chapter3_3_firefly_138`
- baseline：
  - `loss_total = 0.674103`
  - `spectral_centroid_gap_hz = 4956.085863`
  - `spectral_high_band_energy_ratio_gap = 0.286543`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.041527`
- candidate：
  - `loss_total = 0.882`
  - `spectral_centroid_gap_hz = 8945.445005`
  - `spectral_high_band_energy_ratio_gap = 0.603371`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.877948`

### 3. `target::chapter3_4_firefly_106`
- baseline：
  - `loss_total = 0.607221`
  - `spectral_centroid_gap_hz = 5113.494065`
  - `spectral_high_band_energy_ratio_gap = 0.29865`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.025772`
- candidate：
  - `loss_total = 0.857079`
  - `spectral_centroid_gap_hz = 9036.508367`
  - `spectral_high_band_energy_ratio_gap = 0.611698`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.892341`

## 七、解读
1. 这条线最重要的价值，是把一个仍有“smoke 正向幻觉”的方向正式封口了：
   - `fused_hidden_branch_mean_weight = 0.25`
     在 smoke 上看起来像
     “第一个真正碰到 fusion 有效层级”的候选
   - 但在 corrected native-teacher fullsplit24 真实 decoded 上，
     它仍然共享同一类失败模式
2. 而且它不是“更接近 baseline，但还差一点”：
   - 三条样本的 `loss_total`
     全部明显恶化
   - `spectral_centroid_gap_hz`
     全部从 baseline 约 `5k`
     恶化到约 `8.9k ~ 9.0k`
   - `spectral_high_band_energy_ratio_gap`
     也全部从 baseline 约 `0.29 ~ 0.34`
     恶化到约 `0.60 ~ 0.66`
3. 更关键的是，
   这条线把当前失败模式进一步钉实成：
   - short-time structure
     仍高度 template-collapse
   - 但 frame RMS
     反而重新变成强 envelope-following
   - 也就是同时更亮、
     更硬、
     更贴包络的 harsh buzz
4. 因此当前不能再把这条线解释成：
   - “方向已对，只差 branch_mean 权重 sweep”
   - “smoke 有正向，所以 fullsplit24 只是训练不够久”
5. 当前更合理的口径是：
   - 现有 fusion-side `loss`
     家族已经封口
   - 后续若继续沿
     `fusion -> fused_hidden`
     主线推进，
     必须上收到更强的
     `forward-path structural`
     或 `fusion manifold`
     改路，
     而不是继续叠 penalty

## 八、当前主线判断
- 到这一步，
  corrected native teacher 主线上，
  已经明确否掉：
  - `fused_hidden_template + fused_hidden_delta`
  - `fused_hidden_branch_mean_weight = 0.25`
  - `decoder_branch_mean_mix_alpha = 0.25`
  - `use_decoder_branch_condition_adapter = true`
- 因而当前不再值得继续：
  - fusion-side `loss` 同族扩展
  - `branch_mean_weight`
    小范围 sweep
  - 现有 `fused_single`
    上再叠更多同层 penalty
- 下一步必须继续上收到：
  - 更强的 fusion-path 结构改路
  - 更明确的 `branch_mean` 主通路 / fusion residual handoff
  - 或其它直接改变
    `fusion -> fused_hidden`
    状态流形的候选

## 一句话结论
- `fused_hidden_branch_mean_weight = 0.25`
  这条在 smoke 上最像“碰到正确层级”的 fusion-side loss，
  到 corrected native-teacher fullsplit24 真实 decoded 后，
  仍是 `3/3 auto_reject_obvious_buzz`，
  且相对 baseline 明显更差，
  应正式停线。
