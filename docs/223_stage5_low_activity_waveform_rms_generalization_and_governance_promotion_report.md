# 223. Stage5 low-activity waveform RMS 泛化复核与 governance 升级报告

## 背景
- `docs/222_stage5_low_activity_waveform_rms_leakage_strength_sidecar_report.md`
  已证明:
  - 在
    `validation12`
    的
    `decoded`
    四候选 low-activity
    probe
    上，
    `mean_waveform_rms`
    能稳定区分
    `36/48/60`
    的
    leakage-strength
- 但上一轮仍缺:
  - 这条指标
    是否只在
    当前
    `validation12/decoded`
    视角下成立
  - 是否值得升级为
    后续 family
    的通用 sidecar

## 本轮目标
1. 回到更早的
   `6-record`
   四候选 probe，
   检查
   `waveform_rms`
   是否仍稳定
2. 回到更早的
   `60 vs 72`
   multisource probe，
   检查它在:
   - `decoded`
   - `decoded_pitch_matched`
   - `audit_proxy`
   上是否仍有一致解释
3. 若证据足够，
   就把
   `waveform_rms`
   正式提升为:
   - 通用 low-activity
     leakage-strength sidecar

## 本轮执行命令

### 1. 重跑 `6-record` 四候选 probe

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate36_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 `
  --analysis-audio-sources decoded `
  --output-dir reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_waveformrms_round1_1 `
  --top-k-windows 8
```

### 2. 重跑 `60 vs 72` multisource probe

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 `
  --analysis-audio-sources decoded decoded_pitch_matched audit_proxy `
  --output-dir reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource_waveformrms_round1_1 `
  --top-k-windows 6
```

### 3. 生成对应 selection / sensitivity 资产

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03 `
  --low-activity-probe reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_waveformrms_round1_1/stage5_low_activity_fragmentation_probe.json `
  --low-activity-audio-source decoded `
  --low-activity-soft-validation-ratio 1.05

.\python.exe manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1 `
  --weight-step 0.05

.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03 `
  --low-activity-probe reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource_waveformrms_round1_1/stage5_low_activity_fragmentation_probe.json `
  --low-activity-audio-source decoded `
  --low-activity-soft-validation-ratio 1.05

.\python.exe manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1 `
  --weight-step 0.05
```

## 当前结果

### 1. `6-record` 四候选上，`waveform_rms` 仍稳定
- aggregate:
  - `step36 = 0.061624`
  - `step48 = 0.04151`
  - `step60 = 0.026557`
  - `step72 = 0.017769`
- `6 / 6`
  条记录都满足:
  - `36 > 48`
  - `48 > 60`
  - `36 > 60`
- 说明:
  - 它不是
    `validation12`
    扩样后
    才偶然长出来的
    新排序

### 2. `60 vs 72` multisource 上，`waveform_rms` 也保持一致解释
- `decoded`:
  - `step60 = 0.026557`
  - `step72 = 0.017769`
- `decoded_pitch_matched`:
  - `step60 = 0.022232`
  - `step72 = 0.015944`
- `audit_proxy`:
  - `step60 = 0.015009`
  - `step72 = 0.01324`
- 当前
  `6 / 6`
  条记录上，
  三个音源都满足:
  - `step60 > step72`
- 说明:
  - 无论音源是
    raw decoded
    还是 pitch-matched
    或低频 proxy，
    `waveform_rms`
    都在表达同一个方向:
    - `72`
      的 residual leakage strength
      更弱

### 3. 但它和 fragmentation 不是同一件事
- 在
  `decoded`
  与
  `decoded_pitch_matched`
  上:
  - fragmentation
    仍明显更支持:
    - `step60`
      比
      `step72`
      更安全
- 在
  `audit_proxy`
  上:
  - fragmentation
    甚至方向相反，
    更偏向:
    - `step72`
      更安全
- 但
  `waveform_rms`
  三个音源
  都保持:
  - `step72`
    leakage-strength
    更弱
- 这说明:
  - `waveform_rms`
    的泛化稳定性
    很强
  - 但它表达的是:
    - residual energy strength
  - 不是:
    - burst / toggle / fragmentation
      风险

### 4. 重新生成的 governance 资产没有改写主推荐
- `6-record` 四候选 selection:
  - soft rerank
    仍选择:
    - `step72`
  - `worst_floor_leakage_strength_ranking`
    写成:
    - `step60 < step48 < step36`
- `60 vs 72` selection:
  - soft rerank
    仍选择:
    - `step72`
  - summary line
    现在显式包含:
    - `best_leakage_strength = step72`

## 当前判断

### 1. 现在可以把 `waveform_rms` 升级为通用 sidecar
- 当前至少已经在以下场景都成立:
  - `6-record` 四候选
  - `validation12` 四候选
  - `60 vs 72`
    的
    `decoded`
  - `60 vs 72`
    的
    `decoded_pitch_matched`
  - `60 vs 72`
    的
    `audit_proxy`
- 所以当前更合理的制度口径是:
  - `waveform_rms`
    可作为
    后续 low-activity family
    的通用
    leakage-strength sidecar

### 2. 但升级范围只到 sidecar，不到主规则
- 原因不是
  它不稳定
- 恰恰相反，
  是因为它太稳定地在表达
  一件更窄的事:
  - residual leakage strength
- 所以它适合:
  - branch aggregate 展示
  - tie group 内部排序
  - fallback cluster
    的 leakage-strength
    对照
- 但不适合直接替代:
  - fragmentation
  - alignment
  - activity_excess

## 当前产物
- `6-record` probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_waveformrms_round1_1/`
- `6-record` selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1/`
- `6-record` sensitivity:
  - `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1/`
- `60 vs 72` multisource probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource_waveformrms_round1_1/`
- `60 vs 72` selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1/`
- `60 vs 72` sensitivity:
  - `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1/`

## 一句话结论
- 当前
  `waveform_rms`
  已经不只是
  `validation12`
  的局部技巧，
  而是可以正式升级为:
  - 通用 low-activity
    leakage-strength sidecar
- 但升级边界必须写死:
  - 它表达的是
    residual leakage strength，
  - 不是 fragmentation
    或主治理裁决器。
