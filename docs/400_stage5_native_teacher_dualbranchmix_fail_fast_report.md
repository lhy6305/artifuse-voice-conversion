# 400. Stage5 native teacher `dual_branch_mix` fail-fast 报告

## 结论
- 我已将 `waveform_decoder_mode = dual_branch_mix` 这条更强的 native teacher 结构候选推进到真实 `validation3 decoded.wav`。
- 结果仍是否定：
  - `3/3 auto_reject_obvious_buzz`
  - 相对 corrected native baseline，三条样本都更差
  - 相对 `branchcondadapter` 这一档，也没有更好
- 因此 `dual_branch_mix` 不应继续扩 horizon，也不应叠同层小修。

## 本轮执行
### 1. 训练
- 命令：
  - `python manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_dualbranchmix_fullsplit24_round1_1 --device cuda:0 --num-steps 24 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260326 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --waveform-decoder-mode dual_branch_mix`
- 训练摘要：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_dualbranchmix_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_dualbranchmix_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 结果：
  - `best_validation = step24`
  - `loss_total = 0.822042`
  - `decoded_to_target_rms_ratio = 0.960273`

### 3. 真实 decoded 导出
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_dualbranchmix_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- 真实音频：
  - `target__chapter3_3_firefly_162__decoded.wav`
  - `target__chapter3_3_firefly_138__decoded.wav`
  - `target__chapter3_4_firefly_106__decoded.wav`

## fail-fast 结果
### 1. 机器门禁
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 相对 corrected baseline，明确更差
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_2/nores_vocoder_audio_export.json`
- candidate：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_dualbranchmix_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### 3. 典型恶化
- `target::chapter3_3_firefly_162`
  - baseline:
    - `loss_total = 0.55544`
    - `spectral_centroid_gap_hz = 4999.124195`
    - `spectral_high_band_energy_ratio_gap = 0.338207`
  - candidate:
    - `loss_total = 0.842867`
    - `spectral_centroid_gap_hz = 7891.148164`
    - `spectral_high_band_energy_ratio_gap = 0.674795`

## 解读
- 这说明把 waveform decoder 从 `fused_single` 直接改成 `dual_branch_mix`，在当前 native teacher contract 下会把输出推向更亮、更高频、更尖的 harsh buzz 区域。
- 它不是“结构没变化所以无效”，而是“结构变化真实生效，但方向错误”。
- 这也意味着，后续更可能有价值的是：
  - 保守 residual 型 decoder
  - 而不是继续做同级别的 branch mixing

## 下一步
- 不继续：
  - `dual_branch_mix` 更长 horizon
  - `dual_branch_mix + 同层小 tweak`
- 下一步改为：
  - 试更保守的 `periodic_plus_noise_residual`
