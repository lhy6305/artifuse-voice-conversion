# 222. Stage5 low-activity waveform RMS leakage-strength sidecar 报告

## 背景
- `docs/219_stage5_low_activity_validation12_recheck_report.md`
  已确认:
  - `36/48/60`
    在
    `validation12`
    上的
    核心 low-activity
    指标
    继续塌缩
- `docs/220_stage5_low_activity_smoothness_sidecar_report.md`
  已补出:
  - `mean_sample_delta_peak`
    可作为
    泄漏簇内部
    平滑度 sidecar
- 但上一轮仍缺:
  - 一个更贴近
    “泄漏强度”
    本身的
    波形域指标

## 本轮目标
1. 检查当前
   `validation12`
   low-activity
   原始波形里，
   是否存在
   能稳定区分
   `36/48/60`
   的
   leakage-strength
   指标
2. 若存在，
   就把它接入:
   - low-activity probe
   - checkpoint selection governance sidecar
3. 保持口径克制:
   - 不改主 selector
   - 不改 soft rerank 主权重

## 本轮代码变更

### 1. 修改文件
- `src/v5vc/stage5_low_activity_probe.py`
- `src/v5vc/nores_vocoder_checkpoint_selection.py`
- `src/v5vc/nores_vocoder_low_activity_sensitivity.py`

### 2. 新增指标
- `waveform_rms`
  - 定义:
    - 目标 low-activity
      片段内，
      候选波形的
      raw waveform RMS
  - 解释:
    - 数值越低，
      代表
      低活动段内
      的残留能量越弱，
      更接近
      leakage-strength
      sidecar

### 3. 当前接入方式
- probe json / markdown
  现在会输出:
  - `mean_waveform_rms`
- checkpoint selection
  现在会额外输出:
  - `best_low_activity_leakage_strength_branch`
  - `best_low_activity_leakage_strength_branches`
  - `worst_floor_leakage_strength_ranking`
- sensitivity markdown
  现在会显示
  metric-ready candidate
  的
  `waveform_rms`

## 本轮执行命令

### 1. 语法校验

```powershell
.\python.exe -m py_compile `
  src\v5vc\stage5_low_activity_probe.py `
  src\v5vc\nores_vocoder_checkpoint_selection.py `
  src\v5vc\nores_vocoder_low_activity_sensitivity.py
```

### 2. 重跑 `validation12` low-activity probe

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate36_decodedpitchmatch_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_decodedpitchmatch_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation12_round1_1 `
  --analysis-audio-sources decoded `
  --output-dir reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1 `
  --top-k-windows 12
```

### 3. 用新 probe 重跑 selection / sensitivity

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03 `
  --low-activity-probe reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/stage5_low_activity_fragmentation_probe.json `
  --low-activity-audio-source decoded `
  --low-activity-soft-validation-ratio 1.05

.\python.exe manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1 `
  --weight-step 0.05
```

## 当前结果

### 1. `mean_waveform_rms` 在 branch aggregate 上给出稳定顺序
- `step36 = 0.059632`
- `step48 = 0.038473`
- `step60 = 0.022724`
- `step72 = 0.013488`
- 当前解释:
  - `72`
    整体残留能量最弱
  - 在
    `36/48/60`
    泄漏簇内部，
    也能明确给出:
    - `60 < 48 < 36`

### 2. 记录级顺序也稳定
- 当前
  `validation12`
  的
  `12 / 12`
  条记录上，
  都满足:
  - `step36 > step48`
  - `step48 > step60`
  - `step36 > step60`
- 说明:
  - 这次不是只在
    aggregate
    上偶然成立
  - record 级上也支持
    这条 leakage-strength
    顺序

### 3. selection 现在能显式写出泄漏强度 tie-break
- 当前:
  - `best_low_activity_leakage_strength_branch = step72`
- 对
  `worst_floor_leakage`
  tie group
  (`36/48/60`)
  的排序现在写成:
  - `step60 : 0.022724`
  - `step48 : 0.038473`
  - `step36 : 0.059632`
- 和 smoothness sidecar
  一样，
  当前都支持:
  - `step60 < step48 < step36`

### 4. 主推荐没有被这次 sidecar 展示改写
- 当前
  low-activity soft rerank
  仍然选择:
  - `step72`
- 当前
  fragmentation
  翻盘边界
  也没变化:
  - `fragmentation_weight >= 0.55`
    才会翻到
    `step60`

## 当前解释

### 1. 这次补到的是“泄漏强度 sidecar”，不是新的主规则
- `waveform_rms`
  的价值在于:
  - 当
    `active_fraction / activity_excess / alignment`
    在泄漏簇里
    已经饱和时，
    还能继续区分
    残留能量强弱
- 但它不应直接覆盖:
  - fragmentation
  - alignment
  - activity_excess

### 2. 这次把后续分叉说得更清楚了
- 如果问题是:
  - `72`
    是否太容易
    burst / toggle
  - 仍要看
    fragmentation
    与人工听审
- 如果问题是:
  - `36/48/60`
    里谁的
    leakage-strength
    更弱
  - 当前
    `waveform_rms`
    已经能给出
    清晰顺序

## 当前产物
- probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/`
- selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/`
- sensitivity:
  - `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/`

## 一句话结论
- 当前
  `waveform_rms`
  已经足够作为
  low-activity
  leakage-strength
  sidecar:
  - 它不改写
    `step72`
    仍是当前
    soft rerank
    推荐
  - 但它把
    `36/48/60`
    的泄漏强度顺序
    明确写成了:
    - `step60 < step48 < step36`
