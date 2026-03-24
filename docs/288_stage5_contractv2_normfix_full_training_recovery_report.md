# 2026-03-24 Stage5 `contractv2_normfix` full training 恢复报告

## 结论
- 本轮已把
  consumer-side
  热修真正落到正式实验：
  - full-split package
    重导完成
  - 正式
    `72-step`
    no-res baseline
    重训完成
  - checkpoint review /
    selection /
    validation audio export /
    teacher-first smoke
    均已完成
- 当前关键结果是：
  - `contractv2_normfix`
    `best_validation = 0.554104`
  - 已优于旧主线
    `0.564671`
  - 也明显优于原始
    `contract_v2`
    首轮
    `0.658881`

## 一、full-split package 重导

### 命令
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1 `
  --device cpu
```

### 结果
- output：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/`
- 耗时：
  - `duration_sec = 1071.587694`
- package 数量：
  - `train = 592`
  - `validation = 66`
  - `total = 658`

## 二、正式重训

### 命令
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1 `
  --device cuda `
  --num-steps 72 `
  --packages-per-step 4 `
  --validation-interval 12 `
  --checkpoint-interval 12 `
  --sampler-mode shuffle `
  --seed 20260318 `
  --deterministic `
  --activity-gate-weight 0.2 `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode pre_overlap_add
```

### 结果
- output：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/`
- 耗时：
  - `duration_sec = 256.877605`
- best checkpoint：
  - `step72`
  - `loss_total = 0.554104`

### 与前两条主线对比
- 旧主线：
  - `0.564671`
- 原始
  `contract_v2`：
  - `0.658881`
- 本轮
  `contractv2_normfix`：
  - `0.554104`
- 因此：
  - 相比原始
    `contract_v2`
    改善
    `-0.104777`
  - 相比旧主线
    改善
    `-0.010567`

## 三、checkpoint review 与 selection

### review
- output：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/`
- 总体 review：
  - `step12 -> step72`
    `66/66 improved`
  - `average_delta_loss_total = -0.42379`

### selection
- output：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/`
- 当前结果：
  - `best_validation_checkpoint = step72`
  - `best_rms_checkpoint = step12`
  - `selected_stable_late_stop = null`

### 当前解释
- 当前并不是
  “selection 工具坏了”
- 而是：
  - `step72`
    虽然 validation
    最优，
    但
    `pairwise worsened_ratio = 0.363636`
    高于
    `0.2`
  - 同时
    `rms_ratio_deviation = 0.090012`
    也高于
    `0.03`
- 所以当前正确写法是：
  - `step72`
    是 best validation
  - 但还不是 stable late stop

## 四、validation audio export

### 命令
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 6 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_bestval_validation6_round1_1
```

### 结果
- 已导出：
  - `6`
    条 validation
    听审资产
- output：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_bestval_validation6_round1_1/`

## 五、teacher-first source-to-target smoke

### 命令
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_bestval_round1_1 `
  --device cuda `
  --max-audio-sec 3.0 `
  --vocoder-checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation
```

### 结果
- output：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_bestval_round1_1/`
- pipeline：
  - `status = succeeded`
  - `decoded_audio_exists = true`
  - `decoded_audio_sec = 2.998639`
- 当前风险仍是：
  - `applicability_risk = high_risk`
  - `spectral_centroid = 6004.709495 Hz`
  - `high_band_energy_ratio = 0.352201`

### 与上一轮原始 `contract_v2` demo 对比
- 上一轮原始
  `contract_v2`
  demo：
  - `spectral_centroid = 6187.811 Hz`
  - `high_band_energy_ratio = 0.895873`
- 本轮
  `contractv2_normfix`
  demo：
  - `spectral_centroid = 6004.709 Hz`
  - `high_band_energy_ratio = 0.352201`
- 当前解释：
  - 高频塌穿风险
    明显下降
  - 但还没下降到
    当前 user-line
    的安全区

## 六、当前判断
1. consumer-side
   热修
   已经被正式训练结果验证为有效，
   不再只是“方向上可能对”
2. 当前实验线状态已从：
   - `contract_v2`
     首轮正式训练落后旧主线
   转为：
   - `contractv2_normfix`
     数值略优于旧主线，
     但 checkpoint 治理
     与 user-line
     风险仍未转正
3. 当前真正下一问不再是：
   - `contract_v2`
     能不能站住
4. 而是：
   - 数值回升
     是否对应主观听感改善
   - 为什么 user-line
     仍保留
     `high_risk`

## 七、下一步
1. 围绕：
   - 旧主线
   - 原始 `contract_v2`
   - `contractv2_normfix`
   做 validation
   音频并排听审
2. 保持当前治理判断：
   - `step72`
     是 best validation
   - 但不是 stable late stop
3. 若听感也确认改善，
   再继续追：
   - user-line
     remaining high-risk
   - decode / out-of-distribution
     适配

## 一句话结论
- `contractv2_normfix`
  已完成正式 full-split
  重导与 `72-step`
  重训，
  数值上已略优于旧 baseline；
  但当前仍需通过听审确认主观改善，
  且 user-line
  依然处于
  `high_risk`
  诊断态。
