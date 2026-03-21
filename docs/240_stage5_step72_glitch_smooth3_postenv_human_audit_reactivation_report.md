# 2026-03-21 Stage5 `step72__decode_gate_smooth3_postenv` focused human audit 重新激活报告

## 结论
- 当前实验线仍停在：
  - `step72__decode_gate_smooth3`
    vs
    `step72__decode_gate_smooth3_postenv`
    的 focused human audit
- 本轮不是新增 probe，
  而是把已失效的听审入口恢复成：
  - 可自动重建 bundle
  - 可再次启动 GUI
  - 可继续由用户接手听审
- 当前正式听审脚本已恢复可用：
  - `scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1`

## 背景
- `docs/236_stage5_step72_decode_gate_smooth3_postenv_validation_report.md`
  已把：
  - `step72__decode_gate_smooth3_postenv`
    固化为下一轮待审主分支
- 但本轮检查发现：
  - 正式 session
    目录
    `reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session/`
    中只剩：
    - `audio_audit_progress.json`
  - 对应的 decoded audit bundles
    一度不存在，
    导致 GUI 无法按原脚本启动

## 当前问题

### 1. 当前失效点
- 原脚本会直接调用：
  - `launch-audio-audit-gui`
- 但启动时解析：
  - `reports/audio/stage5_s72_glitch_s3_postenv_v12_probe/audio_audit_bundles/decoded/...`
  失败
- 报错本质是：
  - manifest/bundle
    路径缺失
  - 不是 GUI 主程序本身损坏

### 2. 当前更准确的状态
- 这条线此前只能说：
  - session 曾经启动过
- 不能说：
  - 现在仍可直接继续听审

## 本轮代码修正

### 1. 修改文件
- `scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1`

### 2. 当前新增行为
- 启动前先检查：
  - `offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3`
  - `offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3_postenv`
  两路 decoded bundle
  是否存在
- 若缺失，
  自动执行：

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1 `
  --analysis-audio-sources decoded `
  --output-dir reports/audio/stage5_s72_glitch_s3_postenv_v12_probe
```

- 重建完 bundle
  后，
  再继续启动 GUI

## 当前正式听审入口

### 1. 脚本入口
```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1
```

### 2. smoke 命令
```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1 -AutoCloseMs 1000
```

### 3. 正式 session 输出目录
- `reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session/`

### 4. 当前 bundle 根目录
- `reports/audio/stage5_s72_glitch_s3_postenv_v12_probe/audio_audit_bundles/decoded/`

## 本轮验证

### 1. 脚本级 smoke
- 命令：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1 -AutoCloseMs 1000
```

- 结果：
  - exit code `0`
  - 启动时自动输出：
    - `Missing decoded audit bundles. Rebuilding them from the Stage5 export manifests...`

### 2. bundle 恢复结果
- 当前已恢复：
  - `.../audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3/proxy_audio_export.json`
  - `.../audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3_postenv/proxy_audio_export.json`

### 3. session 当前状态
- 正式 session
  目录当前仍可见：
  - `audio_audit_progress.json`
- 当前仍未生成：
  - `audio_audit_review.json`
- 所以这条线现在应视为：
  - 听审入口已恢复
  - 人工结论仍未完成

## 当前主对比目标
- `step72__decode_gate_smooth3`
  vs
  `step72__decode_gate_smooth3_postenv`

## 当前试听重点
1. 局部边界毛刺是否继续减少
2. 清辅音渐变与呼吸声是否更平滑
3. 低活动段 leakage 是否没有明显回升
4. 整体听感是否比当前默认
   `smooth3`
   更稳定

## 当前操作建议
1. 直接运行正式脚本入口
2. 听审完成后，
   在：
   - `reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session/`
   留下：
   - `audio_audit_review.json`
   - `audio_audit_review.md`
3. 在拿到正式 review
   前，
   不把
   `postenv`
   写成新的默认 apply mode

## 一句话结论
- 当前实验线没有新增新实验，
  而是把已经失效的
  `postenv`
  focused human audit
  启动入口恢复成了
  “缺 bundle 也能自愈重建并重新启动 GUI”
  的可接班状态；
  下一棒仍然是用户完成正式听审，
  而不是继续扩 probe。
