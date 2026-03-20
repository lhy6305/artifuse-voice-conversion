# 226. Stage5 low-activity `validation12` 听审契约与 governance report 联动报告

## 背景
- `docs/221_stage5_low_activity_validation12_decoded_audit_contract.md`
  已把
  `validation12`
  decoded
  low-activity
  听审入口
  固定下来
- `docs/225_stage5_low_activity_governance_fixed_report_materializer_report.md`
  已进一步提供:
  - fixed governance report
  - 固定 report 命令
  - 固定 `stage_reports`
    输出目录
- 但上一轮仍缺:
  - 听审交付文档
    自身
    还没有显式挂上
    fixed governance report
  - 启动脚本
    也还指向
    旧的
    pre-waveformrms
    bundle 目录

## 本轮目标
1. 把
   `validation12`
   decoded
   听审契约
   切到最新
   `waveformrms`
   bundle
2. 把
   fixed governance report
   显式接进
   听审交付文档
3. 固定当前执行顺序:
   - 先看
     fixed governance report
   - 再进 GUI

## 本轮变更

### 1. 修改文件
- `docs/221_stage5_low_activity_validation12_decoded_audit_contract.md`
- `scripts/launch_stage5_low_activity_validation12_decoded_audit.ps1`

### 2. 当前合同新增内容
- 新增:
  - 当前量化治理固定入口
  - fixed governance report 路径
  - 当前固定口径
    (`tradeoff`)
  - 执行顺序说明

### 3. 当前脚本切换到最新 bundle
- 旧路径:
  - `...decoded_validation12_round1_1/...`
- 新路径:
  - `...decoded_validation12_waveformrms_round1_1/...`

## 当前固定入口

### 1. fixed governance report
- `reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.md`

### 2. 听审脚本
- `scripts/launch_stage5_low_activity_validation12_decoded_audit.ps1`

### 3. session 输出目录
- `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/`

## 当前执行顺序
1. 先看:
   - fixed governance report
2. 再运行:
   - 听审脚本
3. 听审时默认按双轴理解:
   - fragmentation axis
   - leakage-strength axis

## 本轮验证

### 1. GUI smoke

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_low_activity_validation12_decoded_audit.ps1 -AutoCloseMs 1000
```

- 返回:
  - `exit code 0`

### 2. 当前说明
- 这说明:
  - 更新后的脚本
    仍可正常启动 GUI
  - 最新
    `waveformrms`
    bundle
    没有破坏
    听审交付入口

## 当前结果

### 1. 听审契约不再只是“怎么开 GUI”
- 现在它也会直接告诉使用者:
  - 先看哪份
    fixed governance report
  - 当前量化治理
    为什么是
    `tradeoff`

### 2. 当前量化与人工听审已经挂到同一交付链
- 量化侧:
  - fixed governance report
- 人工侧:
  - fixed audit contract
  - fixed launch script
- 因此后续接班时，
  不再需要自己补一句:
  - “先理解量化，再去听”

## 一句话结论
- 当前
  `validation12`
  decoded
  听审交付
  已经从:
  - 纯 GUI 启动契约
  升级为:
  - fixed governance report
    + fixed audit contract
    + fixed launch script
    的联动入口。
