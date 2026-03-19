# 208. Stage5 低活动段 fragmentation probe 正式 CLI 接入报告

## 背景
- `docs/207_stage5_decodedpitchmatch_human_audit_and_gui_segmentation_followup_report.md`
  已确认当前更值钱的下一步不是继续泛化式盲听，
  而是补一条:
  - 低活动段 /
    非音节段 /
    breath-like
    区间的
    fragmentation
    诊断口径
- 当前仓库里已出现:
  - `src/v5vc/stage5_low_activity_probe.py`
  这份专项分析模块
- 但在本轮接班前，
  它还没有:
  - 正式 CLI 入口
  - 运行验证
  - 正式报告

## 本轮目标
1. 把
   `stage5_low_activity_probe`
   接入
   `src/v5vc/cli.py`
   正式命令入口
2. 直接用现有
   `activitygate60 vs 72`
   decoded-pitchmatch bundle
   做一次 smoke
3. 把当前输出口径和初步观察落盘

## 本轮代码变更

### 1. 新增正式命令入口
- 修改文件:
  - `src/v5vc/cli.py`
- 新命令:
  - `analyze-stage5-low-activity-fragments`
- 当前暴露参数包括:
  - `--bundle`
  - `--output-dir`
  - `--analysis-audio-sources`
  - `--target-activity-threshold`
  - `--candidate-activity-threshold`
  - `--min-low-activity-frames`
  - `--top-k-windows`
  - `--window-padding-sec`

### 2. 修复 WAV 读取 warning
- 修改文件:
  - `src/v5vc/stage5_low_activity_probe.py`
- 原先对
  `torch.frombuffer(raw, ...)`
  直接传
  `bytes`
  时，
  会触发:
  - non-writable buffer warning
- 当前改为:
  - `torch.frombuffer(bytearray(raw), ...)`
- 这样后续批量诊断时，
  stderr
  不会再被无效 warning 污染

## 本轮 smoke 命令

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 `
  --analysis-audio-sources decoded_pitch_matched `
  --output-dir tmp/stage5_low_activity_fragmentation_probe_smoke `
  --top-k-windows 4
```

## 验证

### 1. 语法校验
- 已通过:

```powershell
.\python.exe -m py_compile src\v5vc\cli.py src\v5vc\stage5_low_activity_probe.py
```

### 2. 真实 bundle smoke
- 已通过，
  输出目录:
  - `tmp/stage5_low_activity_fragmentation_probe_smoke/`
- 关键产物:
  - `stage5_low_activity_fragmentation_probe.json`
  - `stage5_low_activity_fragmentation_probe.md`
  - `clips/`
    下的逐片段导出 wav

## 当前 smoke 结果

### 1. 当前比较对象
- bundle:
  - `activitygate60`
  - `activitygate72`
- audio source:
  - `decoded_pitch_matched`
- 共享记录数:
  - `6`

### 2. 当前 aggregate
- `step60`
  - `mean_fragmentation_score = 0.21466`
- `step72`
  - `mean_fragmentation_score = 1.214996`

### 3. 当前 top windows
- `target::chapter3_22_firefly_114`
  的
  `0.98s - 1.80s`
  片段，
  当前 probe
  判为:
  - `step72`
    明显更差
- 但也存在
  `target::chapter3_4_firefly_106`
  的若干片段，
  当前 probe
  判为:
  - `step60`
    更差

先说人话:
- 这条 probe
  没有把结果写成
  “72 全面更差”
  或
  “60 全面更差”
- 它给出的更像是:
  - 在低活动段，
    `72`
    确实存在更明显的
    毛刺 / 断续
    可疑窗口
  - 但问题不是
    单边绝对垄断，
    `60`
    也有自己更差的片段
- 这和
  `docs/207`
  里的人耳结论
  是一致的:
  - 不是宣布赢家，
    而是把排查口径
    从
    “整体验收”
    推进到
    “低活动瞬态专项复核”

## 当前边界
- 当前只是:
  - bundle-level
    诊断与片段导出
- 还不是:
  - 自动 checkpoint ranking
  - 或最终质量裁决器
- 当前默认更适合用于:
  - 给人工听审提供
    可疑片段入口
  - 给后续治理实验提供
    结构化对照证据

## 下一步建议
1. 用同一命令
   再补跑:
   - `listening`
   - `audit_proxy`
   两种音源，
   看问题是:
   - decode 侧更明显
   - 还是跨音源都成立
2. 从
   `top_windows`
   里挑
   `chapter3_22_firefly_114`
   与
   `chapter3_4_firefly_106`
   这类片段，
   回到 GUI
   做定点听审
3. 若后续要做
   checkpoint governance，
   可以把该 probe
   先作为:
   - 辅助诊断口径
   而不是直接硬编码成
   唯一评分标准

## 一句话结论
- 本轮已把
  Stage5
  低活动段 fragmentation probe
  从
  “单文件草稿”
  升级为:
  - 可通过
    `manage.py`
    直接调用的正式 CLI
- 并已用
  `activitygate60 vs 72`
  的 decoded-pitchmatch bundle
  跑通 smoke，
  初步结果与上一轮人耳判断一致:
  - 问题的重点不是简单换默认点，
    而是把低活动段毛刺/断续
    作为专项治理口径正式建立起来。
