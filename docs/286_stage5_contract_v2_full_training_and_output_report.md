# 2026-03-24 Stage5 `contract_v2` full training 与产物落盘报告

## 结论
- 本轮已完成：
  - 扩覆盖 source acoustic state
    审计
  - `contract_v2`
    full-split dataset package
    导出
  - 正式 no-res baseline
    训练
  - checkpoint review
  - checkpoint selection
  - validation audio export
  - teacher-first source-to-target
    smoke 恢复
- 但当前不能宣称：
  - `contract_v2`
    已优于旧主线
- 因为本轮
  `best_validation loss_total = 0.658881`，
  仍明显落后于旧
  `gate72 deterministic`
  baseline
  的
  `0.564671`。

## 一、训练前最后核验

### 1. 扩覆盖 source acoustic audit
- 已执行：
```powershell
.\python.exe manage.py audit-source-acoustic-state `
  --output-dir reports/runtime/source_acoustic_state_audit_readiness_round1_1 `
  --max-audio-sec 6.0 `
  --input-audio `
    data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
    data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_132.wav `
    data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav `
    data_convert/dataset_firefly_raw/chapter3_22_firefly_105.wav `
    data_convert/dataset_firefly_raw/chapter3_17_firefly_143.wav `
    data_convert/dataset_firefly_raw/archive_firefly_5.wav `
    data_convert/dataset_firefly_raw/chapter3_3_firefly_162.wav `
    data_convert/dataset_firefly_raw/chapter3_3_firefly_114.wav `
    data_convert/dataset_firefly_raw/chapter3_6_firefly_106.wav
```
- aggregate：
  - `mean_voiced_ratio = 0.686053`
  - `mean_nonzero_f0_ratio = 0.686053`
  - `mean_f0_p90_hz_nonzero = 366.739877`
  - `mean_high_f0_ratio_ge_400hz = 0.077416`
  - `warning_case_count = 3`
- warning
  样例：
  - `chapter3_17_firefly_143`
  - `archive_firefly_5`
  - `chapter3_6_firefly_106`
- 当前解释：
  - 这轮校准已经足够支撑正式训练启动
  - 但高 `f0_p90`
    边界仍值得后续单独追

## 二、full-split `v2` dataset package 导出

### 1. 首次 full export
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_round1_1 `
  --device cpu
```
- 结果：
  - `train_packages = 592`
  - `validation_packages = 66`
  - `total = 658`
  - `duration_sec = 935.744984`

### 2. 当前 package 一致性
- 当前 summary
  已显式写出：
  - train / validation
    都只有：
    `offline_mvp_nores_vocoder_train_targets_v2`
  - train / validation
    都只有：
    `offline_teacher_vocoder_input_scaffold_v2`
  - train / validation
    都只有：
    - `periodic_input_dim = 36`
    - `noise_input_dim = 36`
    - `harmonic_target_dim = 32`
    - `noise_target_dim = 32`
  - `versions_consistent = true`
  - `dims_consistent = true`

### 3. `--skip-existing` 复用
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_round1_1 `
  --device cpu `
  --skip-existing
```
- 结果：
  - `duration_sec = 3.840896`
- 当前结论：
  - `v2`
    首次导出明显比旧版更慢，
    但复用态仍然很便宜，
    不会阻塞后续迭代。

## 三、正式训练

### 命令
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1 `
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

### 训练结果
- runtime：
  - `device = cuda:0`
  - `GPU = NVIDIA GeForce RTX 3060 Laptop GPU`
- 总耗时：
  - `duration_sec = 245.251286`
- best checkpoint：
  - `step72`
  - `loss_total = 0.658881`
- 关键中间点：
  - `step12 = 0.986235`
  - `step24 = 0.818536`
  - `step36 = 0.734092`
  - `step48 = 0.689489`
  - `step60 = 0.669387`
  - `step72 = 0.658881`

### 与旧主线比较
- 旧：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/`
  - `best_validation = 0.564671`
- 新：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/`
  - `best_validation = 0.658881`
- delta：
  - `+0.094210`
- 因此当前结论不是：
  - `contract_v2`
    训练失败了
- 而是：
  - 训练与产物链都成立，
    但第一轮正式重训的数值结果
    暂未胜过旧 baseline

## 四、checkpoint 后处理

### 1. review
- 已执行：
```powershell
.\python.exe manage.py review-offline-mvp-nores-vocoder-checkpoints `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1 `
  --top-k 10
```
- 结果显示：
  - `step12 -> 24 -> 36 -> 48 -> 60 -> 72`
    每次 pairwise
    都是：
    `66/66 improved`
  - 这说明当前 checkpoint
    改善是 broad-based，
    不是少数样本带动

### 2. selection
- 已执行：
```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03
```
- 结果：
  - `best_validation = step72`
  - `best_rms = step48`
  - `selected_stable_late_stop = null`
- 原因：
  - 晚窗候选虽然持续改善，
    但
    `step60 / step72`
    的
    `rms_ratio_deviation`
    分别为：
    - `0.058748`
    - `0.085782`
  - 都没进当前
    `0.03`
    硬阈值

## 五、最小音频产物

### 1. validation audio export
- 已执行：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 6 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_bestval_validation6_round1_1
```
- 已导出
  `6`
  条 validation
  试听资产：
  - `aligned_target.wav`
  - `decoded.wav`
  - `audit_proxy.wav`
- 当前产物目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_bestval_validation6_round1_1/`

### 2. teacher-first source-to-target smoke
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_parallel107_bestval_round1_1 `
  --device cuda `
  --max-audio-sec 3.0 `
  --vocoder-checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation
```
- 结果：
  - `status = succeeded`
  - `decoded_audio_exists = true`
  - `decoded_audio_sec = 2.998639`
- 说明：
  - 之前
    `vocoder_checkpoint_load`
    的主阻塞已被这轮新 checkpoint
    真正解除
- 但当前 applicability risk
  仍是：
  - `high_risk`
  - `spectral_centroid = 6187.811 Hz`
  - `high_band_energy_ratio = 0.895873`
- 所以当前只能写成：
  - end-to-end path
    已打通
  - 但用户线音质仍是
    诊断态，
    不能宣称已转正

### 3. 默认 self-check 已恢复
- 已将
  `teacher_first_vc_demo`
  默认 checkpoint selection
  切到这轮新的
  `contract_v2`
  selection
- 已执行：
```powershell
.\scripts\self_check_teacher_first_single_target_vc_demo.ps1 `
  -OutputDir tmp/teacher_first_vc_demo_self_check_contractv2_parallel107 `
  -MaxAudioSec 0.1
```
- 结果：
  - `7/7 passed`

## 六、当前判断
1. 这轮已经完成了完整的
   `contract_v2`
   训练闭环，
   不再存在
   “还没开始正式重训”
   的问题。
2. 当前真正的下一问已经变成：
   - 为什么
     `contract_v2`
     第一轮正式训练
     比旧 baseline
     更差
3. 当前答案很可能不在：
   - package plumbing
   - checkpoint selection
   - source-to-target path
     是否可跑
4. 而在：
   - `v2-core`
     字段质量
   - 训练目标与新字段的耦合方式
   - decode / user-line
     风险仍偏高

## 一句话结论
- `contract_v2`
  的第一轮正式 no-res baseline
  已完整训练并产生产物；
  端到端 source-to-target
  路径也已恢复成功。
- 但当前数值与可听风险都表明：
  这轮训练回答的是
  “v2 方案已能被正式执行”，
  不是
  “v2 已经胜出并可直接升格”。
