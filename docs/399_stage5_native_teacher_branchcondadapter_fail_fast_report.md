# 399. Stage5 native teacher `branchcondadapter` fail-fast 报告

## 结论
- 我已将 `use_decoder_branch_condition_adapter = true` 这条 native teacher 结构候选推进到真实 `validation3 decoded.wav`。
- 结果是否定：
  - `3/3 auto_reject_obvious_buzz`
  - 相对当前 corrected native baseline，三条样本都更差
- 因此这条 `fused_single + branchcondadapter` 路线应正式停线，不再扩 horizon，也不再叠同层小权重。

## 本轮执行
### 1. 训练
- 命令：
  - `python manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchcondadapter_fullsplit24_round1_1 --device cuda:0 --num-steps 24 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260326 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --use-decoder-branch-condition-adapter`
- 训练摘要：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_branchcondadapter_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_branchcondadapter_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 结果：
  - `best_validation = step24`
  - `loss_total = 0.807557`
  - `decoded_to_target_rms_ratio = 0.969662`

### 3. 真实 decoded 导出
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_branchcondadapter_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
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
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_branchcondadapter_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### 3. 典型恶化
- `target::chapter3_3_firefly_162`
  - baseline:
    - `loss_total = 0.55544`
    - `spectral_centroid_gap_hz = 4999.124195`
    - `spectral_high_band_energy_ratio_gap = 0.338207`
  - candidate:
    - `loss_total = 0.825819`
    - `spectral_centroid_gap_hz = 5888.521452`
    - `spectral_high_band_energy_ratio_gap = 0.621765`

## 解读
- 这说明单独把 `fused_hidden / branch_mean_hidden / difference` 做成非线性条件 adapter，并不足以把当前 native teacher 路线从 template-collapse 式 buzz 中拉出来。
- 相比前两条轻量候选：
  - 它比 `acttmpl005_zerojitter4` 好
  - 但仍差于 corrected baseline
  - 也没有优于 `fusedhidden_t005_d2 / branchmix025` 这一档
- 因而它只说明“病灶确实在 decoder 条件结构附近”，但这版结构修复还不够强。

## 下一步
- 不继续：
  - `branchcondadapter` 更长 horizon
  - 在 `fused_single` 上叠更多同层小 penalty
- 下一步改为：
  - 试更强的 native teacher `waveform decoder mode` 结构候选
  - 优先 `dual_branch_mix`
