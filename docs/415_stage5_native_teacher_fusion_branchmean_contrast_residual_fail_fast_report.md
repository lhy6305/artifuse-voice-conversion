# 2026-03-26 Stage5 native teacher `fusion_mode = branch_mean_contrast_residual_v1` fail-fast 报告

## 结论
- 这条更收敛到 `branch_mean` 主骨架、同时只让 contrast residual 参与 fusion 的结构候选，
  已完成 corrected native-teacher fullsplit24 真 decoded fail-fast。
- 结果仍是否定：
  - `validation3` 仍是 `3/3 auto_reject_obvious_buzz`
  - 当前仍没有摆脱 `template-collapse + envelope-following`
- 但它也是当前最强、最有信息量的 fusion structural 候选：
  - 高频 harsh-buzz 明显被压下来了
  - 相对 corrected baseline，
    `spectral_centroid_gap_hz`
    从约 `5.0k`
    下降到约 `1.0k`
  - `spectral_high_band_energy_ratio_gap`
    从约 `0.29 ~ 0.34`
    下降到约 `0.01 ~ 0.07`
  - checkpoint selector 还第一次给出了
    `selected_stable_late_stop = step24`
- 因而当前更准确的口径不是：
  - “fusion structural 也已经整体封口”
- 而是：
  - `branch_mean` 侧的 contrast-only residual
    已经打中了 brightness 症状
  - 但剩余主故障已经收缩成：
    `decoder-side template projector / envelope-following`

## 一、背景
- `docs/413`
  已确认：
  - `branch_mean_residual_v1`
    虽仍失败，
    但比多数旧候选更接近 corrected baseline
- `docs/414`
  又确认：
  - 更偏 `periodic_hidden` 主骨架的
    `periodic_residual_v1`
    会把系统重新拉回更亮、更尖的 harsh buzz
- 同时 gate-off structure probe 进一步说明：
  - 当前主线应继续留在
    `branch_mean`
    一侧
  - 但需要减少把共模幅度/包络直接送进 fusion residual
- 因而本轮要回答的问题是：
  - 如果 fusion 主骨架固定为
    `branch_mean_hidden`
  - residual 只看经归一化后的
    `branch_difference_hidden`
  - 是否能在不重新拉高 brightness 的前提下，
    继续压低 template-collapse

## 二、结构语义
- 新候选：
  - `fusion_mode = branch_mean_contrast_residual_v1`
- 语义：
  - `branch_mean_hidden`
    作为 fusion 主骨架
  - `branch_difference_hidden`
    先做 `LayerNorm`
    去掉共模幅度后，
    再进入：
    - contrast gate
    - contrast projection
  - 最终：
    - `fused_hidden = branch_mean_hidden + gated_contrast_residual`
- 初始化保持保守：
  - gate bias 为负
  - residual projection 初值为零

## 三、产物目录

### 1. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 3. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### 4. gate-off structure probe
- `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_round1_1/stage5_waveform_decoder_structure_probe.md`

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
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `decoder_branch_mean_mix_alpha = 0.0`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = false`

## 五、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.826456`
- `loss_waveform = 0.125706`
- `loss_stft = 0.285491`
- `loss_rms_guard = 0.099272`
- `decoded_to_target_rms_ratio = 0.988113`

### 2. selector 侧新增信号
- `selected_stable_late_stop = step24`
- `late_candidates.step24.qualifies_as_stable_late_stop = true`
- pairwise review：
  - `improved_count = 66`
  - `worsened_count = 0`

### 3. 如何解读
- 相对 corrected native baseline：
  - baseline selected checkpoint
    `loss_total = 0.554104`
  - current candidate
    `loss_total = 0.826456`
- 相对 `branch_mean_residual_v1`：
  - `0.826456`
    略优于
    `0.834916`
- 也即：
  - 它还没有转正，
    但已经是当前最强的 fusion structural objective 信号

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
  - `loss_total = 0.837276`
  - `spectral_centroid_gap_hz = 1090.175877`
  - `spectral_high_band_energy_ratio_gap = 0.066059`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.905581`

### 2. `target::chapter3_3_firefly_138`
- baseline：
  - `loss_total = 0.674103`
  - `spectral_centroid_gap_hz = 4956.085863`
  - `spectral_high_band_energy_ratio_gap = 0.286543`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.041527`
- candidate：
  - `loss_total = 0.860457`
  - `spectral_centroid_gap_hz = 987.320155`
  - `spectral_high_band_energy_ratio_gap = 0.010965`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.891924`

### 3. `target::chapter3_4_firefly_106`
- baseline：
  - `loss_total = 0.607221`
  - `spectral_centroid_gap_hz = 5113.494065`
  - `spectral_high_band_energy_ratio_gap = 0.29865`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.025772`
- candidate：
  - `loss_total = 0.814991`
  - `spectral_centroid_gap_hz = 1086.298302`
  - `spectral_high_band_energy_ratio_gap = 0.0203`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.902094`

## 八、关键信号变化
1. 亮度症状明显被压下来了：
   - `spectral_centroid_gap_hz`
     不再是 `~5k`
     那一档 harsh buzz
   - `spectral_high_band_energy_ratio_gap`
     也不再是
     `0.28 ~ 0.34`
     那一档
2. 但 collapse 并没有被解除：
   - 三条样本仍全部
     `auto_reject_obvious_buzz`
   - `decoded_frame_template_cosine_mean`
     仍在
     `0.988694 ~ 0.991182`
3. 包络跟随反而仍非常强：
   - `decoded_frame_rms_to_aligned_frame_rms_corr`
     变成
     `0.891924 ~ 0.905581`
4. 因而当前失败语义已从：
   - “高频亮尖 harsh buzz”
   收缩为：
   - “没那么亮，但仍然高度模板化、强贴包络”

## 九、structure probe 结果
- baseline collapse summary：
  - `fused_hidden_template_cosine_mean = 0.972359`
  - `waveform_frames_template_cosine_mean = 0.99219`
  - `decoded_frames_template_cosine_mean = 0.989687`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`
- variant impact ranking 显示：
  - `fused_hidden_from_branch_mean`
    对 waveform 的改变量只有
    `0.008046`
  - `fused_hidden_from_periodic_hidden`
    和
    `fused_hidden_from_noise_hidden`
    仍会造成更大改动：
    - `0.086417`
    - `0.092543`
- 这说明：
  - 当前 learned fused_hidden
    已经很贴近
    `branch_mean`
    主骨架
  - fusion 侧 brightness 问题基本被压住
  - 但 waveform decoder
    仍会把一个相对没那么差的
    `fused_hidden`
    再推向模板化输出

## 十、解读
1. 这条线不是失败得“没有信息量”
2. 相反，它第一次把当前主病灶重新分层了：
   - brightness / harsh-buzz
     已显著缓解
   - 剩下的主故障是
     `template-collapse + envelope-following`
3. 这意味着：
   - 下一步不该再把主精力放在
     `high-band restraint`
     或
     `periodic dominance`
   - 而应直接处理：
     - decoder-side template projector
     - branch dynamics 如何重新进入 waveform handoff

## 十一、当前主线判断
- 到这一步，
  当前 fusion-path structural 主线上已经可以更明确地区分：
  - `periodic_residual_v1`
    这一侧会重新拉高 brightness
  - `branch_mean_contrast_residual_v1`
    这一侧能压住 brightness，
    但还不能打穿 collapse
- 因而当前下一步不应做：
  - 回到 `periodic-dominant`
    方向
  - 围绕 brightness 再做小修
- 更合理的下一步应是：
  - 保持
    `branch_mean_contrast`
    这一侧的 fusion backbone
  - 直接改
    decoder interaction / handoff-shape
  - 目标是破掉
    envelope-following
    和 decoder-side template projector

## 一句话结论
- `fusion_mode = branch_mean_contrast_residual_v1`
  虽然仍然 `3/3 auto_reject_obvious_buzz`，
  但它是当前第一条真正压下 harsh-brightness 的 fusion structural 候选；
  剩余主故障已经收缩到
  `template-collapse + envelope-following`，
  后续应继续留在这条 branch_mean-side handoff 主线。
