# 211. Stage5 低活动段 decoded 听审窗口重建与部分人耳反馈记录

## 背景
- `docs/210_stage5_low_activity_fragmentation_decoded_audio_audit_kickoff_and_operator_contract.md`
  已把
  Stage5
  低活动段专项复核
  收成正式听审入口
- 但用户实际开听后给出直接反馈:
  - 当前切片太短
  - 几乎没有足够判断因素
  - 更合适的窗口应是:
    - 单条约
      `2s - 3s`
    - 并且前后保留约
      `200ms`
      静音/低活动上下文，
      以免瞬态被截断

## 用户本轮反馈

### 1. 对旧切片的直接评价
- 旧版 probe
  导出的可疑片段
  更接近:
  - 原低活动段本体
  - 加少量 padding
- 这对算法诊断够用，
  但对人耳判断不够

### 2. 当前已听结果边界
- 用户本轮只试听了:
  - 前两条
- 当前唯一可安全写下的主观结论是:
  - `step72`
    比
    `step60`
    更尊重原音频音量变化
- 同时在这两条里:
  - `step72`
    未出现毛刺现象

### 3. 结论约束
- 因此截至本轮，
  不能再把
  decoded
  定点听审
  写成:
  - `step72`
    已被人耳确认在低活动段更容易毛刺
- 更准确的表述应改成:
  - probe
    仍把
    `step72`
    标成更可疑
  - 但当前已完成的人耳复核
    还不足以支持
    “`step72` 已确认更差”

## 本轮代码修正

### 1. 修改文件
- `src/v5vc/stage5_low_activity_probe.py`
- `src/v5vc/cli.py`

### 2. 具体改动
- 将导出窗口默认最小上下文
  从:
  - `0.08s`
  调整为:
  - `0.2s`
- 新增正式 CLI 参数:
  - `--min-audit-window-sec`
  - `--max-audit-window-sec`
- 当前默认:
  - `window_padding_sec = 0.2`
  - `min_audit_window_sec = 2.4`
  - `max_audit_window_sec = 3.0`
- 导出逻辑改为:
  - 先保证低活动段前后至少各留
    `200ms`
  - 若原可疑窗过短，
    再向两侧扩成
    约 `2.4s`
    听审窗
  - 若原始音频边界不允许，
    则保留可获得的最大窗口

### 3. 导出 manifest 补充信息
- 当前 segmented bundle
  除原始 segment 范围外，
  还会写出:
  - `clip_start_sec`
  - `clip_end_sec`
  - `clip_duration_sec`
- 方便后续 GUI / 文档
  明确看到
  真正用于听审的窗口

### 4. GUI 主听 bundle 过滤
- 当前生成
  `audio_audit_bundles/`
  时，
  会优先剔除:
  - 实际听审窗仍短于
    `2.0s`
    的贴边样本
- 这些样本不会从
  probe summary
  里消失，
  但默认不再占用
  GUI
  主听位

## 本轮重跑命令

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 `
  --analysis-audio-sources decoded audit_proxy `
  --output-dir reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource `
  --top-k-windows 6
```

## 本轮验证

### 1. 语法校验

```powershell
.\python.exe -m py_compile src\v5vc\cli.py src\v5vc\stage5_low_activity_probe.py
```

### 2. probe 重跑
- 已通过
- 正式目录已重建:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/`

### 3. GUI 脚本 smoke

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_low_activity_fragmentation_decoded_audit.ps1 -AutoCloseMs 1000
```

- 已通过

## 当前输出变化

### 1. 当前 decoded 主窗口已扩成长窗
- 例如:
  - `target::chapter3_22_firefly_114`
    的可听窗口
    现已变为:
    - `0.188662s - 2.588662s`
    - 总长 `2.4s`
- `target::chapter3_3_firefly_213`
  的可听窗口
  现为:
  - `1.970068s - 4.370068s`
  - 总长 `2.4s`
- `target::chapter3_4_firefly_106`
  的优先窗口
  现为:
  - `6.126077s - 8.526077s`
  - 总长 `2.4s`

### 2. 边界情况
- 若低活动段本身靠近音频起点或终点，
  实际导出窗仍可能短于
  `2.4s`
- 例如:
  - `target::chapter3_3_firefly_162`
    的若干片段
    本身就贴近样本边界，
    当前最长也只有约
    `0.61s`
- 这类样本的人耳信息量仍然有限，
  当前已默认从
  GUI
  主听 bundle
  中降级

## 当前对后续听审的影响
1. 先前那批过短切片，
   不再适合继续作为
   低活动段毛刺结论的主依据
2. 现在应优先基于
   重建后的 decoded segmented bundle
   继续听:
   - `target::chapter3_22_firefly_114`
   - `target::chapter3_3_firefly_213`
   - `target::chapter3_4_firefly_106`
3. 当前人耳侧可以明确保留的部分发现只有:
   - `step72`
     更尊重原音频音量变化
4. 在用户完成更多条目的定点复核前，
   低活动段是否真的存在
   `step72`
   特有毛刺，
   仍应保持开放判断

## 一句话结论
- 本轮不是继续扩大结论，
  而是先把听审材料修正到可判断的长度。
- 当前正式 bundle
  已按
  `2.4s`
  左右的听审窗重建，
  同时把已有的人耳反馈边界明确收紧为:
  - `step72`
    更尊重原音量变化，
    但前两条里
    暂未听到其毛刺现象。
