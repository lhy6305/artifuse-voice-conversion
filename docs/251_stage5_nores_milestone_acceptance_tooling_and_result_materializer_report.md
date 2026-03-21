# 2026-03-21 Stage5 no-res 门槛验收模式与结果物化入口补齐报告

## 结论
- 当前
  `Stage5 no-res milestone acceptance`
  已不再借用旧的分支对比评分字段，
  而是拥有：
  - 专用 GUI 评审模式
  - 专用结果物化模块
  - 专用结果物化脚本
- 这次补的是：
  - 让门槛验收“对题”
  - 以及让听审后结果能正式落盘
- 不是：
  - 重开新的 decode / training
    实验

## 背景
- `docs/249_stage5_nores_milestone_acceptance_audit_kickoff_report.md`
  已把实验线下一题切到：
  - 当前 best route
    的绝对门槛验收
- 但进一步核对后发现：
  - 旧
    `audio_audit_gui`
    默认字段仍是：
    - `best_rhythm`
    - `best_boundary`
    - `most_stable`
    - `overall_pick`
  - 这更适合：
    - 多分支比较
  - 不适合：
    - 单 bundle
      的 no-res 门槛验收

## 本轮代码动作

### 1. `audio_audit_gui` 新增评审模式
- 文件：
  - `src/v5vc/audio_audit_gui.py`
- 当前新增：
  - `--review-mode milestone_acceptance`

### 2. 门槛验收模式的评分字段
- `intelligibility`
- `stability`
- `basic_naturalness`
- `milestone_verdict`

### 3. 留空语义已与旧模式分离
- 旧的 comparative 模式：
  - 完成且可比较时，
    留空按
    `打平`
    解释
- 新的 milestone_acceptance 模式：
  - 不再自动把留空解释成
    `打平`
  - 门槛字段必须显式填写

### 4. 新增结果物化模块
- 文件：
  - `src/v5vc/stage5_nores_milestone_acceptance_report.py`
- 当前功能：
  - 读取
    `audio_audit_review.json`
  - 读取对应 bundle manifest
  - 物化：
    - `stage5_nores_milestone_acceptance_report.json`
    - `stage5_nores_milestone_acceptance_report.md`

### 5. 新增模板与脚本
- 模板：
  - `reports/templates/stage5_nores_milestone_acceptance_report_template.md`
- 启动脚本：
  - `scripts/launch_stage5_nores_milestone_acceptance_audit.ps1`
- 结果物化脚本：
  - `scripts/materialize_stage5_nores_milestone_acceptance_result_report.ps1`

## 当前正式入口

### 1. 门槛验收启动脚本
```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_nores_milestone_acceptance_audit.ps1
```

### 2. 门槛验收结果物化脚本
```powershell
powershell -ExecutionPolicy Bypass -File scripts/materialize_stage5_nores_milestone_acceptance_result_report.ps1
```

## 本轮验证

### 1. 语法检查
```powershell
.\python.exe -m py_compile src\v5vc\audio_audit_gui.py src\v5vc\stage5_nores_milestone_acceptance_report.py
```

- 结果：
  - exit code `0`

### 2. 新模式帮助文本
```powershell
$env:PYTHONPATH = "src"
.\python.exe -m v5vc.audio_audit_gui --help
.\python.exe -m v5vc.stage5_nores_milestone_acceptance_report --help
```

- 结果：
  - 新模式
    `milestone_acceptance`
    已出现在 GUI 帮助文本中
  - 结果物化模块帮助文本可正常显示

### 3. 启动脚本 smoke
```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_nores_milestone_acceptance_audit.ps1 -AutoCloseMs 1000
```

- 结果：
  - exit code `0`
  - `reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session/audio_audit_progress.json`
    已刷新
  - 当前已确认：
    - `review_mode = milestone_acceptance`
    - 单条记录字段为：
      - `intelligibility`
      - `stability`
      - `basic_naturalness`
      - `milestone_verdict`

## 当前意义

### 1. 门槛验收问题终于和工具字段对齐
- 以前：
  - 能听
  - 但字段还是
    “谁更好”
- 现在：
  - 问题就是
    “当前 best route
    到底过没过门槛”
  - 字段也直接对应：
    - 可懂性
    - 稳定性
    - 基本自然度
    - 阶段结论

### 2. 听审完成后不再只剩原始 `audio_audit_review.json`
- 当前已经有：
  - 固定结果物化脚本
  - 固定输出目录
  - 固定 markdown 模板
- 后续只要真正导出
  `audio_audit_review.json`，
  就能直接物化成正式结果报告

## 下一步
1. 当前先完成这轮
   milestone acceptance
   的人工听审
2. 听完后立即运行：
   - `scripts/materialize_stage5_nores_milestone_acceptance_result_report.ps1`
3. 再根据 fixed report
   和单条备注，
   写正式门槛结论文档

## 一句话结论
- 当前实验线的
  `Stage5 no-res`
  门槛验收
  已从：
  - “能启动 GUI”
  推进到：
  - “字段对题，
     且听完后能一键物化正式结果”。
