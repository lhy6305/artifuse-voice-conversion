# 227. Stage5 low-activity 听审结果 fixed report 入口补齐报告

## 背景
- `docs/225_stage5_low_activity_governance_fixed_report_materializer_report.md`
  已把
  Stage5 low-activity
  的量化治理
  固定成:
  - fixed governance report
- `docs/226_stage5_low_activity_validation12_audit_contract_governance_integration_report.md`
  已把
  `validation12`
  听审契约
  固定成:
  - 先看
    governance report
  - 再进
    GUI
- 但上一轮仍缺:
  - 听审完成后，
    如何把
    `audio_audit_review.json`
    与
    fixed governance report
    自动合成
    一份正式结果报告

## 本轮目标
1. 把
   Stage5 low-activity
   的
   human audit result
   也接成
   fixed-format report
2. 为
   `validation12`
   听审链路
   固定:
   - 结果物化命令
   - 结果物化脚本
   - 固定输出目录
3. 用已有
   `windowed_v2 decoded 60vs72`
   听审结果
   做一次真实物化验证，
   避免只停留在
   `--help`
   层面

## 本轮变更

### 1. 新增文件
- `docs/227_stage5_low_activity_audit_result_fixed_report_bootstrap_report.md`
- `scripts/materialize_stage5_low_activity_validation12_decoded_audit_result_report.ps1`

### 2. 修改文件
- `docs/221_stage5_low_activity_validation12_decoded_audit_contract.md`

### 3. 复用的既有代码入口
- `src/v5vc/stage5_low_activity_audit_result_report.py`
- `reports/templates/stage5_low_activity_audit_result_report_template.md`
- `materialize-stage5-low-activity-audit-result-report`

## 当前固定入口

### 1. `validation12` 听审结果物化命令

```powershell
.\python.exe manage.py materialize-stage5-low-activity-audit-result-report `
  --audio-audit-review reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/audio_audit_review.json `
  --governance-report reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.json `
  --output-dir reports/stage_reports/stage5_low_activity_audit_result_validation12_waveformrms_round1_1 `
  --title "stage5 low-activity audit result report - validation12 waveformrms decoded"
```

### 2. `validation12` 对应脚本

```powershell
powershell -ExecutionPolicy Bypass -File scripts/materialize_stage5_low_activity_validation12_decoded_audit_result_report.ps1
```

### 3. 当前固定输出目录
- `reports/stage_reports/stage5_low_activity_audit_result_validation12_waveformrms_round1_1/`

## 本轮真实验证

### 1. 当前为什么没直接物化 `validation12`
- 当前
  `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/`
  里
  只有:
  - `audio_audit_progress.json`
- 还没有:
  - `audio_audit_review.json`
- 所以当前不能把
  `validation12`
  写成
  “听审结果已物化”

### 2. 改用已完成的匹配 session 做真实物化

```powershell
.\python.exe manage.py materialize-stage5-low-activity-audit-result-report `
  --audio-audit-review reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session_windowed_v2/audio_audit_review.json `
  --governance-report reports/stage_reports/stage5_low_activity_governance_60_vs_72_waveformrms_round1_1/stage5_low_activity_governance_report.json `
  --output-dir reports/stage_reports/stage5_low_activity_audit_result_windowedv2_60_vs_72_decoded_round1_1 `
  --title "stage5 low-activity audit result report - windowed_v2 decoded 60vs72"
```

### 3. 当前真实物化结果
- 产物目录:
  - `reports/stage_reports/stage5_low_activity_audit_result_windowedv2_60_vs_72_decoded_round1_1/`
- 当前 fixed report 明确写出:
  - `governance_mode = tradeoff`
  - comparable
    `3 / 4`
  - overall_pick
    聚合为:
    - `step60 = 1`
    - `step72 = 1`
    - `打平 = 1`
  - cross-axis readout:
    - `split_across_axes`

## 当前结果

### 1. Stage5 low-activity 现在不只量化侧有 fixed report
- 当前人工听审侧
  也已经有:
  - fixed-format result report
  - 固定模板
  - 固定命令

### 2. `validation12` 听审契约已经补成三段式
- 先看:
  - fixed governance report
- 再运行:
  - GUI 听审脚本
- 听完后再运行:
  - fixed audit result report
    物化脚本

### 3. 当前边界仍要写清楚
- 这一步
  没有补完
  `validation12`
  的人工听审本身
- 只是把:
  - 听完之后
    应该如何固定汇报
  这条链
  先补齐

## 一句话结论
- 当前
  Stage5 low-activity
  已经从:
  - fixed governance report
    + fixed audit contract
  再往前补成:
  - fixed audit result report
    入口
- 所以今后只要
  `validation12`
  GUI
  真正产出
  `audio_audit_review.json`，
  就可以直接物化成
  正式结果报告，
  不必再手工读
  review json
  和
  governance report
  自己拼总结。
