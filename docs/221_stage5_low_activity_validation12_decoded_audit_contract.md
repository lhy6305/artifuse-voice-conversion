# 221. Stage5 low-activity `validation12` decoded 听审交付契约

## 背景
- `docs/219_stage5_low_activity_validation12_recheck_report.md`
  已把
  low-activity probe
  扩到:
  - `36/48/60/72`
  且样本扩大到:
  - `validation12`
- `docs/220_stage5_low_activity_smoothness_sidecar_report.md`
  已进一步确认:
  - `36/48/60`
    在核心 low-activity
    指标上塌缩
  - 但
    `mean_sample_delta_peak`
    提供了
    `step60 < step48 < step36`
    的次级平滑度顺序
- `docs/225_stage5_low_activity_governance_fixed_report_materializer_report.md`
  已进一步把
  当前量化治理
  固定成:
  - fixed governance report
  - dual-axis
    (`fragmentation axis`
    vs
    `leakage-strength axis`)

## 本轮目标
1. 把
  `validation12`
   的 high-delta
   低活动窗口
   收成可直接启动的
   GUI bundle
2. 固定:
   - bundle 路径
   - 输出目录
   - 主比较目标
3. 让后续人工复听
   不需要再手工拼路径

## 当前听审对象

### 0. 当前量化治理固定入口
- fixed report:
  - `reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.md`
- 对应 json:
  - `reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.json`
- 当前固定口径:
  - `governance_mode = tradeoff`
  - fragmentation axis
    更偏向:
    - `36/48/60`
      这组
      local-safe
      branch
  - leakage-strength axis
    更偏向:
    - `72`
  - soft rerank
    当前仍选:
    - `72`
- 当前建议顺序:
  - 先看这份
    fixed governance report
  - 再进 GUI
    做人耳复核

### 1. 当前 bundle 目录
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step36/`
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step48/`
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60/`
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72/`

### 2. 当前 session 输出目录
- `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/`

### 3. 当前主比较目标
- 一级问题:
  - `step72`
    在更宽
    `validation12`
    低活动窗口里，
    是否真的更容易出现
    burst / toggle /
    局部毛刺
- 二级问题:
  - 如果因为
    fragmentation
    风险
    需要在
    `36/48/60`
    里找 fallback，
    当前人耳上是否也支持
    量化侧已经给出的:
    - `step60`
      比
      `step48`
      和
      `step36`
      残留更弱、
      也更平滑

## 用户应运行的正式命令

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle `
    reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step36 `
    reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step48 `
    reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60 `
    reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72 `
  --output-dir reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session
```

## 对应脚本入口

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_low_activity_validation12_decoded_audit.ps1
```

- 若只想做启动 smoke，
  可额外传:
  - `-AutoCloseMs 1000`

## 听审完成后的结果物化命令

- 使用条件:
  - GUI session
    已完成
  - 且已导出:
    - `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/audio_audit_review.json`

```powershell
.\python.exe manage.py materialize-stage5-low-activity-audit-result-report `
  --audio-audit-review reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/audio_audit_review.json `
  --governance-report reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.json `
  --output-dir reports/stage_reports/stage5_low_activity_audit_result_validation12_waveformrms_round1_1 `
  --title "stage5 low-activity audit result report - validation12 waveformrms decoded"
```

## 对应结果物化脚本

```powershell
powershell -ExecutionPolicy Bypass -File scripts/materialize_stage5_low_activity_validation12_decoded_audit_result_report.ps1
```

- 当前固定输出目录:
  - `reports/stage_reports/stage5_low_activity_audit_result_validation12_waveformrms_round1_1/`
- 当前目的:
  - 把
    GUI
    导出的
    原始听审结果
    与
    fixed governance report
    自动收成
    一份
    fixed-format
    听审结果报告

## 当前优先试听窗口

### 1. `target::chapter3_6_firefly_106`
- 当前 top window:
  - `0.98s - 1.81s`
- `delta_fragmentation_score = 6.013935`
- 当前最强可疑窗之一

### 2. `target::chapter3_26_firefly_107`
- 当前 top window:
  - `0.65s - 1.20s`
- `delta_fragmentation_score = 5.01555`

### 3. `target::chapter3_29_firefly_113`
- 当前 top window:
  - `1.64s - 2.72s`
- `delta_fragmentation_score = 3.015623`

### 4. `target::chapter3_2_firefly_155`
- 当前 top window:
  - `2.19s - 2.74s`
- `delta_fragmentation_score = 3.012665`

## 具体怎么听

### 1. 先看 `step72` 相对其余三路
- 重点听:
  - 是否出现局部 burst
  - 是否有断续感
  - 是否存在不自然瞬态抖动

### 2. 若确认 `step72` 风险明显，再在 `36/48/60` 内部补听
- 重点看:
  - `step60`
    是否比
    `step48`
    残留更弱、
    也更平滑
  - `step48`
    是否比
    `step36`
    残留更弱、
    也更平滑

### 3. 当前先不要把这轮听审写成
- 整体音色最好
- 最终主 checkpoint
- 成品链路自然度

## 本轮验证

### 1. segmented bundle 已存在
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/`

### 2. 启动脚本已可用
- `scripts/launch_stage5_low_activity_validation12_decoded_audit.ps1`

### 3. 结果物化脚本已可用
- `scripts/materialize_stage5_low_activity_validation12_decoded_audit_result_report.ps1`

### 4. 量化治理 fixed report 已可用
- `reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.md`

### 5. GUI 启动 smoke 已通过

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_low_activity_validation12_decoded_audit.ps1 -AutoCloseMs 1000
```

- 返回:
  - `exit code 0`
- session 目录已生成:
  - `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/`
- 当前已看到:
  - `_segment_cache/`
  - `audio_audit_progress.json`
- 但当前还没有:
  - `audio_audit_review.json`
- 因此:
  - 结果物化命令
    要等
    本轮听审真正完成后
    再运行

## 一句话结论
- 当前 `validation12`
  的 low-activity
  定点复听入口
  已具备:
  - fixed governance report
  - 固定 bundle
  - 固定输出目录
  - 正式命令
  - 脚本入口
  - 听审完成后的
    fixed audit result report
    物化入口
- 后续若要做人耳复核，
  现在可以按
  “先看量化 fixed report，
  再进 GUI 听，
  听完后物化 fixed audit result report”
  的固定顺序执行，
  不需要再手工拼路径或手工恢复双轴结论。
