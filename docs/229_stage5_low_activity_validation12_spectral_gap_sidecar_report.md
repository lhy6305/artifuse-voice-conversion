# 229. Stage5 low-activity `validation12` target-relative spectral gap sidecar 报告

## 背景
- `docs/228_stage5_low_activity_validation12_manual_human_audit_summary_report.md`
  已记录:
  - 人耳侧
    明确支持
    `72`
    作为四者中的
    临时最佳锚点
  - 但同时也指出:
    `72`
    在某些
    清辅音渐变 /
    呼吸声
    节点上
    仍有明显毛刺
- 用户还额外观察到:
  - 从
    `36 -> 72`
  - 听起来
    没那么刺耳
    且频谱感受
    更合理
- 当前问题是:
  - 如果直接用
    绝对高频能量 /
    绝对 centroid
    去解释这条观察，
    很容易被
    `36`
    更重的
    底噪污染

## 本轮目标
1. 不再补一份
   纯文字结论
2. 直接把
   这条听感
   推成
   可复用的
   定量 sidecar
3. 要求该 sidecar
   能与当前
   low-activity
   双轴治理并存，
   但不改写
   主 selector
   硬规则

## 本轮代码变更

### 1. 修改文件
- `src/v5vc/stage5_low_activity_probe.py`
- `src/v5vc/nores_vocoder_checkpoint_selection.py`
- `src/v5vc/stage5_low_activity_governance_report.py`
- `reports/templates/stage5_low_activity_governance_report_template.md`

### 2. 新增的 sidecar 定义
- 当前新增的是:
  - target-relative spectral shape gap
- 具体比较:
  - spectral centroid gap
  - spectral bandwidth gap
  - rolloff95 gap
  - high-frequency energy ratio gap
- 解释口径:
  - 都是在
    target low-activity
    同一片段里，
    把 candidate
    与
    aligned_target
    做相对比较
  - gap 越小，
    代表 decoded
    的频谱形状
    越接近 target
  - 这更适合表达:
    - 没那么刺耳
    - 谱形漂移更小
  - 而不是误把
    高底噪
    直接当成
    “更宽频带”

## 本轮执行命令

### 1. 重跑 `validation12` probe

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

### 2. 重跑 selection

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
```

### 3. 重物化 governance report

```powershell
.\python.exe manage.py materialize-stage5-low-activity-governance-report `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1 `
  --title "stage5 low-activity governance report - validation12 waveformrms"
```

## 当前结果

### 1. `72` 在四个 spectral gap sidecar 上全部最优
- probe aggregate:
  - `step36`
    - `mean_spectral_centroid_gap_hz = 5705.951591`
    - `mean_spectral_bandwidth_gap_hz = 6602.175148`
    - `mean_spectral_rolloff95_gap_hz = 18277.849564`
    - `mean_spectral_hf_ratio_gap = 0.250365`
  - `step48`
    - `4000.611142`
    - `5825.074156`
    - `18267.961055`
    - `0.143962`
  - `step60`
    - `3110.906248`
    - `5094.677794`
    - `18267.961055`
    - `0.106407`
  - `step72`
    - `1986.924605`
    - `3771.858196`
    - `18221.306057`
    - `0.074798`
- 这四条都是:
  - `36 > 48 > 60 > 72`
  - 也就是
    `72`
    与 target
    的频谱形状偏差最小

### 2. 这条 sidecar 定量支持“72 没那么刺耳”的主观结论
- 严格说，
  这里量化到的是:
  - target-relative
    spectral-shape drift
    更小
- 当前推断是:
  - 这与用户听到的
    “没那么刺耳”
    一致
- 这里是
  从量化到听感的推断，
  不是直接量到了
  “刺耳感” 本身

### 3. 当前主治理结论没有反转，反而更稳
- fragmentation axis
  仍然提醒:
  - `72`
    存在局部 burst /
    glitch 风险
- leakage-strength axis
  仍然支持:
  - `72`
    底噪 / 残留最弱
- 新增 spectral sidecar
  进一步支持:
  - `72`
    的频谱形状
    最接近 target
- 所以当前正式口径应继续保持:
  - `72`
    是最合适的临时锚点
  - 下一步该打的是
    `72`
    的局部毛刺，
    不是回头替
    `36/48`
    洗白

## 当前影响

### 1. 当前已经不需要再为“是否继续以 `72` 为锚点”反复停留
- quant
  与 human
  当前已经同向:
  - 低底噪
  - 更接近 target 的谱形
  - forced choice
    仍选
    `72`

### 2. 当前最该继续推进的是 `72` 的毛刺打点
- 当前 top windows
  仍然集中在:
  - `target::chapter3_6_firefly_106`
  - `target::chapter3_26_firefly_107`
  - `target::chapter3_29_firefly_113`
- 后续更合理的工程动作是:
  - 继续围绕这些窗口
    打
    清辅音渐变 /
    呼吸声
    的 glitch 抑制

## 当前产物
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/`
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/`
- `reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/`

## 一句话结论
- 当前新增的
  target-relative spectral gap sidecar
  已把
  `validation12`
  上
  “`72` 虽仍有局部毛刺，
  但整体更不刺耳、更适合继续做临时锚点”
  这件事补成了定量支持，
  所以下一步应直接转向
  `72`
  的局部 glitch 压制。
