# 196. Stage5 audio audit GUI bundle integration 报告

## 背景
- `docs/195_stage5_waveform_step72_audio_export_bootstrap_report.md`
  已让 Stage5 waveform route
  拥有:
  - `aligned_target.wav`
  - `decoded.wav`
  的正式导出链路
- 但现有人工听审 GUI
  默认只认:
  - `proxy_audio_export.json`
- 而本轮 Stage5 导出最初只写:
  - `nores_vocoder_audio_export.json`
- 这意味着:
  - 产物已经能导出
  - 但还不能直接接入
    现有听审工作流

## 本轮目标
1. 让 Stage5 导出目录
   直接成为
   `audio_audit_gui.py`
   可消费的试听包
2. 不破坏已有
   Stage3 / proxy
   听审工作流
3. 给旧的 Stage5 导出目录
   保留最小回退兼容

## 本轮代码落地

### 1. `src/v5vc/nores_vocoder_audio_export.py`
- 在保留
  `nores_vocoder_audio_export.json/.md`
  的同时，
  新增同步输出:
  - `proxy_audio_export.json`
  - `proxy_audio_export.md`
- 新增:
  - `branch_label`
- 当前默认把 Stage5 导出记录
  映射为 GUI 可识别字段:
  - `audio_path = target_audio_path`
  - `input_audio_path = aligned_target_audio_path`
  - `proxy_audio_path = decoded_audio_path`
- 这样同一个导出目录
  既保留 Stage5 自己的详细指标，
  又能直接复用现有 GUI

### 2. `src/v5vc/audio_audit_gui.py`
- `resolve_manifest_path(...)`
  现在对目录优先查找:
  - `proxy_audio_export.json`
  - `nores_vocoder_audio_export.json`
- 也就是说:
  - 新 bundle
    直接走标准
    `proxy_audio_export.json`
  - 旧 bundle
    即使还没重导，
    也能回退读取
    `nores_vocoder_audio_export.json`
- `load_manifests(...)`
  现在也能兼容 Stage5 记录字段:
  - `target_audio_path`
  - `aligned_target_audio_path`
  - `decoded_audio_path`

## 实际验证

### 1. 重新导出 Stage5 `step72` validation bundle

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_baseline96_deterministic_round1_1/nores_vocoder_checkpoint_selection.json --selection-target stable_late_stop --split-name validation --sample-count 6 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1
```

- 当前导出目录已同时包含:
  - `nores_vocoder_audio_export.json`
  - `nores_vocoder_audio_export.md`
  - `proxy_audio_export.json`
  - `proxy_audio_export.md`
- 当前生成的
  `branch_label` 为:
  - `stage5_stable_late_stop_step72`

### 2. GUI smoke: 新标准 bundle 入口

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1 --output-dir reports/audio/audio_audit_gui_stage5_step72_session --auto-close-ms 1000
```

- 命令返回:
  - `exit code 0`
- 自动生成:
  - `reports/audio/audio_audit_gui_stage5_step72_session/audio_audit_progress.json`
- 其中记录的加载清单为:
  - `.../proxy_audio_export.json`

### 3. GUI smoke: 旧 Stage5 manifest 回退入口

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1/nores_vocoder_audio_export.json --output-dir reports/audio/audio_audit_gui_stage5_step72_legacy_manifest_session --auto-close-ms 1000
```

- 命令返回:
  - `exit code 0`
- 自动生成:
  - `reports/audio/audio_audit_gui_stage5_step72_legacy_manifest_session/audio_audit_progress.json`
- 其中记录的加载清单为:
  - `.../nores_vocoder_audio_export.json`

## 当前判断

### 1. Stage5 `step72` 已正式接入现有人工听审 GUI
- 现在不是只有
  “能导 wav”
- 而是已经具备:
  - 可直接加载 bundle
  - 可保存 GUI 进度
  - 可导出后续听审 review

### 2. 这轮应该优先做听审，不该再继续 brute-force 拉 horizon
- 原因不是训练已经完美，
  而是:
  - checkpoint 选择
  - 音频导出
  - GUI bundle 接入
  三段链路
  已经闭环
- 现在最缺的
  不再是更多 step，
  而是:
  - 听感证据
  - 问题归因

### 3. 兼容层必须双边做，不能只改 GUI 或只改 exporter
- 只改 GUI:
  - 新 bundle 仍不符合既有契约
- 只改 exporter:
  - 旧 Stage5 导出目录
    仍然无法直接打开
- 本轮同时做两边，
  才避免:
  - 旧产物失效
  - 新产物继续分叉

## 当前产物
- Stage5 听审 bundle:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1`
- GUI session:
  - `reports/audio/audio_audit_gui_stage5_step72_session/`
- GUI legacy-manifest session:
  - `reports/audio/audio_audit_gui_stage5_step72_legacy_manifest_session/`

## 下一步建议
1. 直接用:
   - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1`
   启动人工听审
2. 若下一轮需要比较
   `step72`
   和
   `step96`
   或其他 objective，
   保持复用同一
   `proxy_audio_export`
   契约
3. 听审记录默认落到:
   - `reports/audio/audio_audit_gui_stage5_*_session/`
   不再手工散落

## 一句话结论
- Stage5 waveform route
  现在已经从
  “能导出 `aligned_target.wav / decoded.wav`”
  推进到
  “可直接进入现有 audio audit GUI
  做人工听审并保存进度”，
  且新旧 Stage5 manifest
  都已具备兼容入口。
