# 164. Stage3 audio audit GUI smoke test 与人工听审启动报告

## 目的
- 确认新接入的 GUI
  不是只停留在:
  - `--help`
  - 参数解析
- 而是真能:
  - 打开窗口
  - 读取当前 Stage3 bundle
  - 写出进度文件
- 同时把当前人工听审阶段的入口固定下来

## 本轮 smoke test

### 1. 预加载 Stage3 bundle 启动测试
- 执行:

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/audio/streaming_student_proxy_audit_baseline48_step48_v1 `
           reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1 `
  --output-dir reports/audio/audio_audit_gui_stage3_baseline48_session `
  --auto-close-ms 800
```

- 结果:
  - GUI 成功启动并自动关闭
  - 已写出:
    - `reports/audio/audio_audit_gui_stage3_baseline48_session/audio_audit_progress.json`

### 2. 续接恢复测试
- 执行:

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --output-dir reports/audio/audio_audit_gui_stage3_baseline48_session `
  --auto-close-ms 800
```

- 结果:
  - GUI 可仅凭已有 progress 文件重新恢复 bundle 列表
  - 重新关闭后，
    `audio_audit_progress.json`
    仍保留原 bundle 引用

## 当前已确认的工程事实
1. `launch-audio-audit-gui`
   的正式入口已可用
2. GUI 可读取当前 Stage3 的:
   - validation bundle
   - special bundle
3. GUI 已能为当前会话写出正式 progress 文件
4. GUI 已具备最小“关掉再开继续做”的续接能力

## 当前人工听审会话目录
- 当前建议正式使用:
  - `reports/audio/audio_audit_gui_stage3_baseline48_session/`

该目录当前用于保存:
- `audio_audit_progress.json`
- 后续人工导出的:
  - `audio_audit_review.json`
  - `audio_audit_review.md`

## 当前人工听审阶段说明
- 当前已经进入:
  - GUI 测试通过后的人工听审阶段
- 但“人工听审”本身仍需要用户实际试听
- 助手当前能完成的是:
  - 工具接线
  - bundle 预加载
  - 记录格式固定
  - 会话目录准备
- 助手不能替代:
  - 人耳主观判断

## 当前推荐听审对象
- `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
- `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`

## 当前推荐听法
- 优先按:
  - `input.wav`
  - `teacher_proxy.wav`
  - `student_proxy.wav`
  的顺序比较
- 重点听:
  - 停顿
  - 边界
  - 能量起伏
  - 稳定性
- 不把当前结果解释成:
  - 最终音质
  - 最终 speaker identity

## 一句话结论
- Stage3 audio audit GUI
  已完成真实启动与续接 smoke test，
  当前项目已经正式进入
  `GUI + proxy bundle`
  的人工听审阶段。

