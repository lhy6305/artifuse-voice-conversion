# 162. Stage3 上下文恢复与 GUI 接管报告

## 目的
- 在上次对话因上下文过长中断后，
  把当前工作状态重新对齐到磁盘文档。
- 明确:
  - 当前正式主线是什么
  - 本轮实际已经完成到哪里
  - 新写到一半的 GUI 现在处于什么状态

## 本轮恢复时按顺序读取的入口
1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `docs/144_next_phase_development_handoff.md`
5. `docs/161_stage3_proxy_audio_export_bootstrap_report.md`
6. `initial_design.md`
7. `initial_design_judg.md`

## 当前正式主线

### 1. offline MVP 主线已经收口
- `docs/144_next_phase_development_handoff.md`
  的阶段切换结论仍成立:
  - 主要时间不再投入旧的 offline MVP 近邻实验补洞
  - 当前主线已转入 Stage3 / streaming student

### 2. 当前 Stage3 默认 best checkpoint
- 仍是:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
- 该结论来自:
  - `docs/160_stage3_baseline48_vs_eventprior025_full_validation_report.md`

### 3. 当前最新正式能力
- 已新增并跑通:
  - `export-streaming-student-proxy-audio`
- 已导出两组正式试听包:
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
- 当前试听包仍只解释为:
  - 结构代理试听
  - 不是最终 vocoder / 最终音质试听

## 本轮代码恢复结论

### 1. 已完成且已落盘的部分
- `src/v5vc/streaming_student/proxy_audio_export.py`
  已实现 Stage3 proxy audio 导出逻辑
- `src/v5vc/cli.py`
  已接入:
  - `export-streaming-student-proxy-audio`
- `src/v5vc/streaming_student/__init__.py`
  已导出该入口
- `docs/161_stage3_proxy_audio_export_bootstrap_report.md`
  已记录命令、产物和边界

### 2. 本轮新发现的 GUI 状态
- 工作区里新增了:
  - `src/v5vc/audio_audit_gui.py`
- 该文件当前状态是:
  - 可以被 `.\python.exe src/v5vc/audio_audit_gui.py --help` 正常解析
  - 可以识别当前 `proxy_audio_export.json` 格式
  - 可以识别 Stage3 bundle 中的:
    - `teacher_proxy`
    - `student_proxy`
  - 可以导出:
    - `audio_audit_progress.json`
    - `audio_audit_review.json`
    - `audio_audit_review.md`

### 3. GUI 当前还没收口的部分
- 目前没有接到:
  - `manage.py`
  - `src/v5vc/cli.py`
  的正式命令入口
- 当前没有任何正式文档
  说明它的使用方式、预期工作流和输出位置
- 当前也没有发现已生成的 GUI 导出目录:
  - `reports/audio/audio_audit_gui_exports/`
- 这说明:
  - GUI 更像是“已写出首版独立脚本”
  - 但还没有完成正式集成、正式交接和实际使用验证

## 当前最接近真实中断点的判断
- 上次中断前，
  `proxy audio` 导出主线已经完成并落盘。
- 新增 GUI 已经写出一个可运行的独立 Tkinter 脚本，
  但还没完成:
  - CLI 集成
  - 文档交接
  - 正式运行产物留档
- 所以当前更准确的状态不是:
  - “GUI 完全没开始”
- 而是:
  - “GUI scaffold 已写出，但正式工作流还没闭环”

## 当前若要手动启动 GUI
- 当前只能直接运行独立脚本，例如:

```powershell
.\python.exe src\v5vc\audio_audit_gui.py `
  --bundle reports/audio/streaming_student_proxy_audit_baseline48_step48_v1 `
           reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1
```

说明:
- 这不是 `manage.py` 子命令
- 也不是当前文档里已经正式登记过的标准入口

## 恢复后的下一步建议
1. 若目标是继续推进听审流程，
   下一步优先补:
   - GUI 的正式入口
   - GUI 使用文档
   - 一次真实导出与回写样例
2. 若目标只是先完成当前阶段判定，
   也可以先不动 GUI，
   直接人工试听现有两个 Stage3 bundle
3. 在没有新听审记录前，
   当前正式口径仍保持:
   - Stage3 已具备试听导出链
   - 但还没有完成新一轮正式人工 gate 结论

## 一句话结论
- 当前项目主线已经推进到
  `Stage3 proxy audio human-review gate`；
  `proxy audio` 导出链已正式完成，
  但新写的 `audio_audit_gui.py`
  仍处于“独立脚本已成形、正式集成未完成”的状态。
