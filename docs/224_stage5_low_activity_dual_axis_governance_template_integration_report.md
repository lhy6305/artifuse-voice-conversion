# 224. Stage5 low-activity 双轴 governance 模板接入报告

## 背景
- `docs/223_stage5_low_activity_waveform_rms_generalization_and_governance_promotion_report.md`
  已确认:
  - `waveform_rms`
    可以升为
    通用
    low-activity
    leakage-strength sidecar
- 但上一轮正式产物里，
  这两条轴
  仍然主要散落在:
  - 单行 summary
  - branch aggregates
  - tie-break 小节
- 这会带来一个实际问题:
  - 明明制度上已经是
    双轴治理
  - 但产物读起来，
    仍容易被误读成
    “一行里选一个 winner”

## 本轮目标
1. 把
   low-activity
   governance
   正式收成固定模板
2. 让 probe
   和 selection
   都默认输出:
   - fragmentation axis
   - leakage-strength axis
   - cross-axis note
3. 把
   “双轴 tradeoff，
   不强压单 winner”
   变成产物级默认口径

## 本轮代码变更

### 1. 修改文件
- `src/v5vc/stage5_low_activity_probe.py`
- `src/v5vc/nores_vocoder_checkpoint_selection.py`

### 2. 当前新增模板字段
- probe output
  现在每个
  `analysis_source`
  都会新增:
  - `governance_template`
- selection output
  的
  `low_activity_probe_analysis`
  现在也会新增:
  - `governance_template`

### 3. 当前模板结构
- `mode`
  - `convergent`
  - `partial_overlap`
  - `tradeoff`
- `fragmentation_axis`
  - `best_fragmentation_branches`
  - `best_alignment_branches`
  - `best_quietness_branches`
  - `note`
- `leakage_strength_axis`
  - `best_leakage_strength_branches`
  - `worst_floor_leakage_branches`
  - `worst_floor_leakage_strength_ranking`
  - `worst_floor_leakage_smoothness_ranking`
  - `note`
- `cross_axis_note`

## 本轮验证

### 1. 语法校验

```powershell
.\python.exe -m py_compile `
  src\v5vc\stage5_low_activity_probe.py `
  src\v5vc\nores_vocoder_checkpoint_selection.py
```

### 2. 重跑关键产物
- `validation12`
  四候选 probe
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/`
- `6-record`
  四候选 probe
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_waveformrms_round1_1/`
- `60 vs 72`
  multisource probe
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource_waveformrms_round1_1/`
- 对应 selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_waveformrms_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_waveformrms_round1_1/`

## 当前结果

### 1. probe markdown 现在直接写出双轴模板
- 例如
  `validation12`
  四候选
  `decoded`
  probe
  现在会固定输出:
  - `mode=tradeoff`
  - `fragmentation_axis`
  - `leakage_strength_axis`
  - `cross_axis_note`
- 这意味着:
  - 不看 selection
    也能在 probe
    本体里直接看到
    双轴口径

### 2. selection markdown 现在也固定写出同一套模板
- 当前
  low-activity governance
  区块
  不再只是
  一行压缩 summary
- 现在会同时写出:
  - fragment 轴
  - leakage-strength 轴
  - cross-axis note
- 所以阅读 selection
  时，
  不再需要自己从
  branch aggregate
  里倒推
  “现在到底是同向还是 tradeoff”

### 3. 当前最关键的制度效果
- 在
  `validation12`
  四候选上，
  现在产物会明确写出:
  - `mode = tradeoff`
  - fragmentation axis
    更偏向:
    - `36/48/60`
      这组
      local-safe
      branch
  - leakage-strength axis
    更偏向:
    - `72`
- 也就是说，
  产物本身已经在提醒:
  - 这是双轴 tradeoff，
    不是单 winner

## 当前解释

### 1. 这次改的是“表达制度”，不是“选择规则”
- 没有改:
  - 主 selector
  - soft rerank 权重
  - fragmentation 定义
  - leakage-strength 定义
- 改的是:
  - 产物默认怎么把
    这两条轴写清楚

### 2. 这一步的价值
- 以前要靠读者自己理解:
  - `fragmentation`
    是一条轴
  - `waveform_rms`
    是另一条轴
- 现在模板里已经写死:
  - 分开报告
  - 明确当前是
    `convergent`
    还是
    `tradeoff`

## 一句话结论
- 当前
  Stage5 low-activity
  governance
  已从
  “双轴概念”
  升级为
  “双轴模板化产物”:
  - probe
    和
    selection
    都会默认把
    fragmentation
    与
    leakage-strength
    分开写清楚，
  - 不再默认把它们压成
    单一 winner。
