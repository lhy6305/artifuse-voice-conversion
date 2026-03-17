# 163. Stage3 audio audit GUI bootstrap 报告

## 背景
- `docs/161_stage3_proxy_audio_export_bootstrap_report.md`
  已让 Stage3 拥有:
  - `input.wav`
  - `teacher_proxy.wav`
  - `student_proxy.wav`
  的正式导出链路
- 但如果继续完全靠手工切文件夹试听，
  后续人工 gate 记录会越来越散
- 因此需要把新写到一半的
  `audio_audit_gui.py`
  补成正式可接手的听审工具入口

## 本轮目标
1. 把 GUI 从独立脚本
   补到正式项目入口
2. 修掉影响真实听审流程的 GUI 工作流缺口
3. 让 Stage3 bundle
   可以直接进入 GUI 测试与人工听审阶段

## 本轮实际完成

### 1. 新增正式命令入口
- 新增:
  - `launch-audio-audit-gui`
- 接入位置:
  - `src/v5vc/cli.py`

### 2. GUI 当前支持的正式参数
- `--bundle`
  - 预加载一个或多个 bundle 目录
  - 或 `proxy_audio_export.json`
- `--output-dir`
  - 指定进度与 review 导出目录
- `--auto-close-ms`
  - 供 GUI smoke test 使用
  - 在指定毫秒后自动关闭窗口

### 3. 本轮修正的 GUI 工作流问题
- 修正了筛选列表后
  `current_index`
  可能失效的问题
- 现在改变 filter 时，
  会先保存当前记录状态，
  再刷新当前记录显示
- GUI 现在支持:
  - 仅凭 `output_dir` 中已有的
    `audio_audit_progress.json`
    自动恢复上次 bundle 列表
- GUI 左侧记录列表的汇总信息
  现在会显示:
  - bundle 数
  - record 总数
  - completed 数
  - 当前 filter 可见数量

## 当前正式启动方式

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/audio/streaming_student_proxy_audit_baseline48_step48_v1 `
           reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1 `
  --output-dir reports/audio/audio_audit_gui_stage3_baseline48_session
```

## 当前输出约定
- 进度文件:
  - `audio_audit_progress.json`
- 导出 review:
  - `audio_audit_review.json`
  - `audio_audit_review.md`

## 当前结论
1. GUI 现在不再只是仓库里的孤立脚本
2. 它已经具备正式启动入口
3. 也已经具备继续上次听审会话的最小能力
4. 当前已可以把 Stage3 proxy bundle
   正式推进到 GUI 听审阶段

## 一句话结论
- Stage3 的人工听审工具链
  现在已经从
  “独立 Tk 脚本草稿”
  升级为
  “带正式 CLI 入口、可续接进度的 GUI 工作流”

