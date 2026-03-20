# 225. Stage5 low-activity governance 固定报告物化入口报告

## 背景
- `docs/224_stage5_low_activity_dual_axis_governance_template_integration_report.md`
  已把
  dual-axis
  governance
  接进:
  - probe
  - checkpoint selection
- 但上一轮仍有一个实际缺口:
  - 当前双轴口径
    虽然已经存在于
    probe / selection
    产物里
  - 但还没有像
    `route_handoff -> handoff_document -> stage_report`
    那样，
    有一条
    fixed-format
    的正式汇报入口

## 本轮目标
1. 为
   Stage5 low-activity
   governance
   新增
   固定格式
   report
   物化命令
2. 让后续新的
   low-activity family
   可以复用同一入口，
   不必再手工从
   selection json
   提炼双轴结论
3. 用当前三套关键 selection
   产物完成真实物化验证

## 本轮代码变更

### 1. 新增文件
- `src/v5vc/stage5_low_activity_governance_report.py`
- `reports/templates/stage5_low_activity_governance_report_template.md`

### 2. 修改文件
- `src/v5vc/cli.py`

### 3. 新增正式命令
- `materialize-stage5-low-activity-governance-report`

### 4. 当前命令输入输出
- 输入:
  - `--checkpoint-selection`
    - 已带
      `low_activity_probe_analysis`
      与
      `governance_template`
      的
      `nores_vocoder_checkpoint_selection.json`
- 输出:
  - `stage5_low_activity_governance_report.json`
  - `stage5_low_activity_governance_report.md`

## 当前固定报告内容
- `governance_mode`
- `executive_status`
- `fragmentation_axis`
- `leakage_strength_axis`
- `cross_axis_note`
- `soft_rerank` 快照
- `top_windows`
- `source_artifacts`

## 本轮验证

### 1. 语法校验

```powershell
.\python.exe -m py_compile `
  src\v5vc\stage5_low_activity_governance_report.py `
  src\v5vc\cli.py `
  src\v5vc\stage5_low_activity_probe.py `
  src\v5vc\nores_vocoder_checkpoint_selection.py
```

### 2. 真实物化命令

```powershell
.\python.exe manage.py materialize-stage5-low-activity-governance-report `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1 `
  --title "stage5 low-activity governance report - validation12 waveformrms"

.\python.exe manage.py materialize-stage5-low-activity-governance-report `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/stage_reports/stage5_low_activity_governance_6record_waveformrms_round1_1 `
  --title "stage5 low-activity governance report - 6record waveformrms"

.\python.exe manage.py materialize-stage5-low-activity-governance-report `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/stage_reports/stage5_low_activity_governance_60_vs_72_waveformrms_round1_1 `
  --title "stage5 low-activity governance report - 60vs72 waveformrms"
```

## 当前结果

### 1. 当前已经形成 Stage5 low-activity 的 fixed-format report 入口
- 现在不再只能看:
  - probe markdown
  - selection markdown
  - 原始 json
- 也可以直接看:
  - fixed governance report

### 2. fixed report 的核心价值
- 它会直接把:
  - governance mode
  - fragmentation axis
  - leakage-strength axis
  - cross-axis note
  - soft rerank 当前指向
  固定写成一份独立报告
- 所以:
  - 后续 family
    若继续沿
    low-activity governance
    扩展，
    现在已经有了
    可复用的正式汇报入口

### 3. 当前三份正式产物
- `reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/`
- `reports/stage_reports/stage5_low_activity_governance_6record_waveformrms_round1_1/`
- `reports/stage_reports/stage5_low_activity_governance_60_vs_72_waveformrms_round1_1/`

## 当前解释

### 1. 这一步不是新增治理逻辑
- 没有改:
  - fragmentation 规则
  - leakage-strength 规则
  - soft rerank 规则
- 改的是:
  - 如何把现有双轴治理
    物化成固定格式报告

### 2. 这一步的工程意义
- 现在 Stage5
  low-activity
  这条线，
  已经不只是:
  - 若干专项报告
  - 若干 selection 产物
- 而是也具备了:
  - 固定格式报告入口
  - 固定模板
  - 固定输出目录结构

## 一句话结论
- 当前
  Stage5 low-activity
  governance
  已经从:
  - 双轴模板化产物
  再推进到:
  - 固定格式 report 物化入口
- 后续若扩新的
  low-activity family，
  现在可以直接复用
  `materialize-stage5-low-activity-governance-report`
  做正式汇报。
