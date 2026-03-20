# 219. Stage5 low-activity `validation12` 扩样复核报告

## 背景
- `docs/218_stage5_low_activity_probe_4way_expansion_report.md`
  已把
  low-activity probe
  扩到
  `36/48/60/72`
- 但那一轮仍只覆盖:
  - `6`
    条定点记录
- 当时最重要的发现是:
  - `36/48/60`
    在当前低活动切片上
    核心指标几乎完全塌缩

## 本轮目标
1. 不再停留在
   `6-record`
   结论
2. 用更宽的
   `validation12`
   子集复核:
   - `36/48/60`
     的塌缩
     是否仍存在
3. 把更宽样本的 probe
   再接回:
   - selection
   - sensitivity
   看当前
   `step72`
   推荐是否仍成立

## 本轮执行命令

### 1. 导出四个 `validation12` bundle

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt `
  --split-name validation `
  --sample-count 12 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate36_decodedpitchmatch_validation12_round1_1 `
  --listening-audio-source decoded_pitch_matched `
  --pitch-match-reference aligned_target `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate

.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt `
  --split-name validation `
  --sample-count 12 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_decodedpitchmatch_validation12_round1_1 `
  --listening-audio-source decoded_pitch_matched `
  --pitch-match-reference aligned_target `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate

.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step60.pt `
  --split-name validation `
  --sample-count 12 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation12_round1_1 `
  --listening-audio-source decoded_pitch_matched `
  --pitch-match-reference aligned_target `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate

.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt `
  --split-name validation `
  --sample-count 12 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation12_round1_1 `
  --listening-audio-source decoded_pitch_matched `
  --pitch-match-reference aligned_target `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate
```

### 2. 跑更宽样本 low-activity probe

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate36_decodedpitchmatch_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_decodedpitchmatch_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation12_round1_1 `
  --analysis-audio-sources decoded `
  --output-dir reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_round1_1 `
  --top-k-windows 12
```

### 3. 用 `validation12` probe 重跑 selection / sensitivity

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03 `
  --low-activity-probe reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_round1_1/stage5_low_activity_fragmentation_probe.json `
  --low-activity-audio-source decoded `
  --low-activity-soft-validation-ratio 1.05

.\python.exe manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_round1_1 `
  --weight-step 0.05
```

## 当前结果

### 1. `36/48/60` 的塌缩在 `validation12` 上仍然存在
- decoded aggregate:
  - `step36`
    - `mean_fragmentation_score = 0.0`
    - `mean_active_fraction = 1.0`
    - `mean_activity_alignment_mae = 0.980059`
    - `mean_activity_excess_mean = 0.980059`
  - `step48`
    - 与上面四项完全相同
  - `step60`
    - 与上面四项完全相同
- 说明:
  - 这已经不是
    前一轮
    `6-record`
    的偶然现象

### 2. `step72` 的优势与风险在更宽样本上反而更清楚
- `mean_fragmentation_score = 1.497705`
- `mean_active_fraction = 0.395834`
- `mean_activity_alignment_mae = 0.513092`
- `mean_activity_excess_mean = 0.513092`
- 解释:
  - `step72`
    的局部 burst 风险
    更明显了
  - 但它对
    target
    低活动轨迹的跟随
    也更明显优于
    `36/48/60`

### 3. 更宽样本下，soft rerank 结论仍不变
- 当前默认:
  - `soft_validation_ratio = 1.05`
  - 权重
    `0.35 / 0.35 / 0.2 / 0.1`
- 推荐仍然是:
  - `step72`
- ratio sweep:
  - `1.110966`
    纳入
    `step48`
  - `1.259344`
    纳入
    `step36`
  - 但 selected
    仍都为
    `step72`

### 4. 翻盘边界仍然没变
- `fragmentation_weight`
  仍需到:
  - `0.55`
  以上，
  结果才翻到
  `step60`

## 当前解释

### 1. 现在可以把“塌缩”从观察升级为更可靠的阶段性事实
- 当前至少在:
  - `6-record`
  - `validation12`
  两轮上都看到:
  - `36/48/60`
    的核心 low-activity
    指标完全重合
- 这意味着:
  - 当前 probe
    对这三步的区分度
    确实很弱

### 2. 当前更合理的下一步已经更清楚
- 优先不是:
  - 继续调
    soft rerank
    权重
- 而是:
  - 扩大记录覆盖
  - 引入更能区分
    “持续满活动残留”
    之间细微差别
    的指标
  - 或者专门找
    `36 -> 48 -> 60`
    的低活动变化开始出现
    分歧的窗口类型

## 当前产物
- `validation12` probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_round1_1/`
- `validation12` selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_round1_1/`
- `validation12` sensitivity:
  - `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_round1_1/`

## 一句话结论
- 用更宽的
  `validation12`
  子集复核后，
  当前结论没有反转，
  反而更稳了:
  - `step72`
    仍是当前 low-activity
    soft rerank
    推荐
  - 但更关键的是，
    `36/48/60`
    的核心 low-activity
    指标塌缩
    不是小样本偶然，
    后续应优先补样本与指标分辨率。
