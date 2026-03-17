# 169. Stage3 上下文恢复续接与 `proxytemporal50` 听审启动报告

## 目的
- 在再次发生上下文中断后，
  用磁盘文档、代码和产物
  重新确认当前真实停点
- 避免把当前主线
  错误回退成:
  - “GUI 还没正式接入”
  - 或
  - “还停在 baseline48 首轮听审”
- 把
  `proxytemporal50`
  的下一轮正式人工复听入口
  固定下来

## 本轮恢复时实际读取与核对范围
1. `docs/00_context_bootstrap.md`
2. `docs/144_next_phase_development_handoff.md`
3. `docs/162_stage3_context_restore_and_gui_takeover_report.md`
4. `docs/163_stage3_audio_audit_gui_bootstrap_report.md`
5. `docs/164_stage3_audio_audit_gui_smoke_test_and_human_review_kickoff_report.md`
6. `docs/165_stage3_audio_audit_loudness_match_fix_report.md`
7. `docs/166_stage3_proxy_pitch_alignment_and_applicability_check_report.md`
8. `docs/167_stage3_proxy_audio_human_review_round1_report.md`
9. `docs/168_stage3_proxy_stability_probe_and_temporal_supervision_report.md`
10. `docs/01_project_overview_and_plan.md`
11. `docs/02_pitfalls_log.md`
12. 代码与入口:
   - `manage.py`
   - `src/v5vc/cli.py`
   - `src/v5vc/audio_audit_gui.py`
   - `src/v5vc/streaming_student/losses.py`
   - `src/v5vc/streaming_student/proxy_acoustic.py`
   - `src/v5vc/streaming_student/proxy_audio_export.py`

## 当前真实状态复原结论

### 1. GUI 集成问题已经不是当前阻塞
- `launch-audio-audit-gui`
  已经正式接入:
  - `src/v5vc/cli.py`
  - `manage.py`
- baseline48 的 GUI 会话、
  smoke test、
  首轮人工听审
  都已经正式落盘

### 2. 当前最新正式主线停在:
- `docs/168_stage3_proxy_stability_probe_and_temporal_supervision_report.md`

也就是:
- baseline48 首轮听审
  已确认
  `student`
  的主要剩余问题
  是:
  - 毛刺
  - 瞬态不稳
  - 稳定性偏弱
- 随后已新增:
  - `teacher_proxy_acoustic`
  - `teacher_proxy_temporal`
    两类附加监督
- 当前更值得继续复听的候选
  不是:
  - `proxyacoustic020`
  而是:
  - `proxytemporal50`

### 3. 当前工作树状态
- `git status --short`
  为空
- 说明仓库在本轮恢复开始时
  是干净状态，
  没有未提交代码残留

## 本轮新确认的产物状态

### 1. `proxytemporal50` 试听包已经存在
- validation:
  - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1/`
- special:
  - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1/`

### 2. 之前还没有对应的正式 GUI 会话目录
- 已存在:
  - `reports/audio/audio_audit_gui_stage3_baseline48_session/`
- 但本轮恢复前
  未看到:
  - `reports/audio/audio_audit_gui_stage3_proxytemporal50_session/`

这意味着:
- 候选 bundle
  已经导出，
- 但下一轮人工复听
  还没有固定正式会话入口

## 本轮实际补做的工作

### 1. 已为 `proxytemporal50` 创建正式 GUI 会话
- 执行:

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1 `
           reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1 `
  --output-dir reports/audio/audio_audit_gui_stage3_proxytemporal50_session `
  --auto-close-ms 800
```

### 2. smoke test 结果
- GUI 成功启动并自动关闭
- 已写出:
  - `reports/audio/audio_audit_gui_stage3_proxytemporal50_session/audio_audit_progress.json`

### 3. 当前会话状态
- 当前新会话
  已记录:
  - 两个 `proxy_audio_export.json`
    manifest
- 当前 `current_index = 0`
- 当前已有第 1 条记录的初始 review state
  但尚未形成任何正式人工结论

## 当前建议如何继续

### 推荐正式启动命令

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --output-dir reports/audio/audio_audit_gui_stage3_proxytemporal50_session
```

说明:
- 由于 progress 文件已存在，
  当前不必重复手填 bundle 路径
- 直接用 `--output-dir`
  就能恢复本轮候选复听会话

### 本轮复听应聚焦的问题
1. 只问:
   - `proxytemporal50 step12`
     相比 baseline48，
     是否更稳
2. 重点听:
   - 毛刺感
   - 瞬态抖动
   - 能量忽大忽小
3. 不把当前 proxy
   用来判断:
   - 音节级结构
   - 可懂度
   - 最终音质

## 当前一句话交接
- 这次恢复后确认:
  当前真正的下一步
  不是继续补 GUI，
  也不是回到 baseline48 首轮听审，
  而是直接进入
  `proxytemporal50`
  的正式人工复听；
  对应 GUI 会话目录
  现在已经建立并可直接续接。
