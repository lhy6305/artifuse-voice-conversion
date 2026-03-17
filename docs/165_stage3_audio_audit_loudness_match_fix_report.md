# 165. Stage3 audio audit loudness-match 修正报告

## 背景
- 当前 Stage3 人工听审已经进入:
  - `GUI + proxy bundle`
    的人工试听阶段
- 但在实际试听中发现:
  - `teacher_proxy`
  - `student_proxy`
    的总体音量并不一致
- 这会直接干扰主观评估，
  因为人耳会先被
  “谁更响”
  吸引，
  而不只是比较:
  - 节奏
  - 边界
  - 稳定性

## 问题定位
- 问题根因不在 GUI 播放逻辑
- 而在 Stage3 proxy 导出阶段:
  - `teacher_proxy.wav`
  - `student_proxy.wav`
    是分别合成后直接写盘
  - 导出前没有做同记录内的响度对齐

## 修复目标
1. 不改 input 原始音频
2. 只修正:
   - 同一条记录下
     teacher/student
     的总体播放响度偏差
3. 保留每条内部的
   - 停顿
   - 能量轮廓
   - 稳定性变化
4. 让人耳更接近在比较
   - 结构差异
   而不是
   - 全局音量差

## 本轮实现

### 1. 在 proxy 导出公共模块中新增响度匹配 helper
- 文件:
  - `src/v5vc/proxy_audio_export.py`
- 新增:
  - `match_audit_waveform_loudness`
  - `compute_waveform_rms`
  - `rms_to_dbfs`
  - `scale_to_db`

说明:
- 对同一组待比较 wav
  先计算各自 RMS
- 再用几何平均 RMS
  作为 pair-level 目标响度
- 对每条分别缩放到共同目标
- 同时保留:
  - gain cap
  - peak limit
  防止极端放大或写盘削波

### 2. Stage3 导出链默认启用 teacher/student 成对 loudness match
- 文件:
  - `src/v5vc/streaming_student/proxy_audio_export.py`
- 现在每条记录导出前会对:
  - `teacher_proxy`
  - `student_proxy`
    先做响度匹配

### 3. 匹配结果写回导出元数据
- `proxy_audio_export.json`
  新增:
  - `proxy_loudness_matching`
- 每条记录会记录:
  - `rms_dbfs_before`
  - `rms_dbfs_after`
  - `gain_db_requested`
  - `gain_db_applied`
  - `peak_before`
  - `peak_after`

## 重导的正式 bundle
- validation:
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
- special:
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`

使用命令:

```powershell
.\python.exe manage.py export-streaming-student-proxy-audio `
  --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt `
  --split-name target_validation `
  --sample-count 3 `
  --max-audio-sec 4.0 `
  --output-dir reports/audio/streaming_student_proxy_audit_baseline48_step48_v1
```

```powershell
.\python.exe manage.py export-streaming-student-proxy-audio `
  --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt `
  --split-name target_special_eval `
  --sample-count 3 `
  --max-audio-sec 4.0 `
  --output-dir reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1
```

## 验证结果

### 修复前
- validation bundle 中，
  同记录 teacher/student
  曾出现:
  - `+3.835 dB`
  - `+4.151 dB`
  - `+4.704 dB`
    的 RMS 差

### 修复后
- 当前 validation bundle:
  - 3 条记录的
    `teacher vs student delta_db`
    均为:
    - `0.000 dB`
- 当前 special bundle:
  - 3 条记录的
    `teacher vs student delta_db`
    同样均为:
    - `0.000 dB`

## 当前结论
1. 问题根因已确认并修复
2. 当前正式 Stage3 听审 bundle
   已不再带 teacher/student
   的总体音量偏置
3. 后续人工听审
   应以重导后的 bundle 为准
4. 当前 loudness match
   的目的只是减少主观评估偏差，
   不是把 Stage3 proxy
   升级成最终用户试听

## 一句话结论
- Stage3 audio audit 当前已修正
  `teacher_proxy` 与 `student_proxy`
  的音量不一致问题；
  正式试听包已重导，
  现在更适合做结构层面的人工比较。
