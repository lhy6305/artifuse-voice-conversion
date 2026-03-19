# 209. Stage5 低活动段 probe 跨音源跟进与 GUI 定点复核包报告

## 背景
- `docs/208_stage5_low_activity_fragmentation_probe_cli_bootstrap_report.md`
  已把
  Stage5
  低活动段 fragmentation probe
  接入正式 CLI
- 但上一轮还停在:
  - `decoded_pitch_matched`
    单音源诊断
- 真正更有信息量的下一步应是:
  1. 看
     `decoded`
     与
     `audit_proxy`
     上的结论是否一致
  2. 把
     `top_windows`
     直接转成
     GUI
     可听的定点复核包，
     避免人工拼路径

## 本轮目标
1. 继续运行
   low-activity probe，
   覆盖:
   - `decoded`
   - `audit_proxy`
2. 明确
   当前 bundle
   的
   `listening`
   是否是独立音源
3. 让
   probe
   输出可以直接接到
   `launch-audio-audit-gui`

## 当前事实核对

### 1. `listening` 不是新的独立音源
- 当前 bundle manifest
  中:
  - `listening_audio_source = decoded_pitch_matched`
  - `listening_audio_path = ...decoded_pitch_matched.wav`
- 也就是说，
  在当前这批 bundle 上
  再单跑
  `listening`
  不会提供新信息，
  只是重复
  `decoded_pitch_matched`
  口径

### 2. 当前更有信息量的音源
- 本轮实际补跑:
  - `decoded`
  - `audit_proxy`

## 本轮代码变更

### 1. probe 自动导出 GUI bundle manifest
- 修改文件:
  - `src/v5vc/stage5_low_activity_probe.py`
- 当前每次 probe
  在导出:
  - `stage5_low_activity_fragmentation_probe.json`
  - `clips/`
  之外，
  还会新增:
  - `audio_audit_bundles/<source>/<branch>/proxy_audio_export.json`
- 这些 manifest
  可直接被:
  - `launch-audio-audit-gui`
    读取

### 2. 当前导出的 segmented audit bundle 结构
- 每条记录对应:
  - 一个
    `top_window`
    片段
- 输入参考:
  - `aligned_target.wav`
- 候选音频:
  - 对应 branch 的
    片段 wav
- 同时保留:
  - 原始 `record_id`
  - `segment_index`
  - `segment_start_sec`
  - `segment_end_sec`
  - `delta_fragmentation_score`
  - `worst_branch`
  - `best_branch`

## 本轮命令

### 1. 跨音源 probe

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 `
  --analysis-audio-sources decoded audit_proxy `
  --output-dir tmp/stage5_low_activity_fragmentation_probe_multisource `
  --top-k-windows 6
```

### 2. GUI smoke

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle `
    tmp/stage5_low_activity_fragmentation_probe_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60 `
    tmp/stage5_low_activity_fragmentation_probe_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72 `
  --output-dir tmp/stage5_low_activity_fragmentation_gui_smoke_decoded `
  --auto-close-ms 1000
```

## 验证

### 1. 语法校验
- 已通过:

```powershell
.\python.exe -m py_compile src\v5vc\stage5_low_activity_probe.py src\v5vc\cli.py
```

### 2. 跨音源 probe
- 已通过，
  输出目录:
  - `tmp/stage5_low_activity_fragmentation_probe_multisource/`
- 当前已生成:
  - `stage5_low_activity_fragmentation_probe.json`
  - `stage5_low_activity_fragmentation_probe.md`
  - `clips/decoded/`
  - `clips/audit_proxy/`
  - `audio_audit_bundles/decoded/`
  - `audio_audit_bundles/audit_proxy/`

### 3. GUI smoke
- 已通过，
  输出目录:
  - `tmp/stage5_low_activity_fragmentation_gui_smoke_decoded/`
- 当前已看到:
  - `audio_audit_progress.json`
  - `_segment_cache/`
- 说明:
  - 新生成的 segmented bundle
    确实能被 GUI 正常读取

## 当前结果

### 1. `decoded` 口径
- aggregate:
  - `step60`
    `mean_fragmentation_score = 0.0`
  - `step72`
    `mean_fragmentation_score = 1.222465`
- top window:
  - `target::chapter3_22_firefly_114`
    `0.98s - 1.80s`
    区间，
    `step72`
    明显更差，
    `delta_fragmentation_score = 9.022783`

### 2. `audit_proxy` 口径
- aggregate:
  - `step60`
    `mean_fragmentation_score = 0.812467`
  - `step72`
    `mean_fragmentation_score = 0.689215`
- 当前 top windows
  反而更偏向:
  - `step60`
    更差

### 3. 当前解释
- `decoded`
  与
  `audit_proxy`
  没有给出同向结论
- 这意味着:
  - 低频 audit proxy
    可以作为排查辅助，
    但不能直接代替
    真正 decoded
    口径
- 当前更可信的主结论仍应优先参考:
  - `decoded`
  - `decoded_pitch_matched`
  - 以及对应的人耳定点复核

先说人话:
- 这轮结果说明，
  代理听感和真实 decoded
  不是一回事。
- 如果只看
  `audit_proxy`，
  很容易把判断方向看反。
- 所以后面应该把
  `decoded`
  的可疑窗口
  直接送进 GUI，
  做定点听审，
  而不是拿
  low-frequency proxy
  直接做最终裁决。

## 当前可直接使用的复核入口

### 1. decoded 定点复核 bundle
- `tmp/stage5_low_activity_fragmentation_probe_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60/`
- `tmp/stage5_low_activity_fragmentation_probe_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72/`

### 2. audit_proxy 对照 bundle
- `tmp/stage5_low_activity_fragmentation_probe_multisource/audio_audit_bundles/audit_proxy/offline_mvp_nores_vocoder_dataset_loop_step60/`
- `tmp/stage5_low_activity_fragmentation_probe_multisource/audio_audit_bundles/audit_proxy/offline_mvp_nores_vocoder_dataset_loop_step72/`

## 下一步建议
1. 默认先听:
   - `decoded`
   这组 segmented bundle，
   优先复核:
   - `target::chapter3_22_firefly_114`
   - `target::chapter3_3_firefly_213`
   - `target::chapter3_4_firefly_106`
2. `audit_proxy`
   继续只保留为:
   - 技术对照口径
   不把它直接当作
   主听结论
3. 后续若把该 probe
   接进
   checkpoint governance，
   默认优先接:
   - `decoded`
   - `decoded_pitch_matched`
   侧指标

## 一句话结论
- 本轮把
  Stage5
  低活动段 probe
  又往前推进了一步:
  - 不仅补齐了
    `decoded / audit_proxy`
    跨音源对照，
  - 还把
    `top_windows`
    自动转成了
    GUI
    可直接打开的 segmented audit bundle
- 当前最重要的工程结论是:
  - `audit_proxy`
    不能替代
    `decoded`
    结论，
    后续定点复核应默认围绕
    `decoded`
    片段开展。
