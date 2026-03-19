# 206. Stage5 decoded pitch-match listening contract 报告

## 背景
- `docs/204_stage5_decoded_primary_listening_contract_report.md`
  已把 Stage5
  人工听评口径
  从:
  - 默认主听
    `audit_proxy.wav`
  切到:
  - 默认主听
    `decoded.wav`
- 但本轮继续推进时，
  用户明确反馈:
  - 上一轮
    `decoded.wav`
    听评已取消
  - 原因是
    当前音调 / 频率感过高，
    会引起心理不适

这说明:
- 之前把主听入口
  切回
  `decoded.wav`
  的方向本身没错，
  因为它更接近成品语音
- 但当前 raw `decoded`
  还不适合
  直接拿去做人耳主比较

## 本轮目标
1. 恢复可执行的人耳听评入口
2. 把当前 raw `decoded`
   的绝对音高偏移
   从听评主问题里剥离出去
3. 不把这种 listening-only
   修正误写成
   “模型已经学会正确 F0”

## 问题复核

### 1. 当前 `activitygate72` bundle 上的 raw `decoded` 确实存在系统性偏高
- 用当前
  `6`
  条 validation 记录，
  对:
  - `aligned_target.wav`
  - `decoded.wav`
  做
  `librosa.pyin`
  中位 voiced F0
  复核
- 观察到:
  - 多条
    `decoded`
    的中位 voiced F0
    近似锁在:
    - `275.460405 Hz`
- 相对目标的
  aggregate:
  - median ratio
    约为:
    - `0.896792`
  - 等价于:
    - 约 `-1.9`
      semitones

### 2. 这类问题已经不是“听起来有点怪”，而是会直接阻断人工听评
- 当听者已经因为
  绝对音高
  产生明显不适时，
  后续关于:
  - 动态
  - 边界
  - 可接受度
  的判断
  都会被带偏

先说人话:
- 现在不是
  “它虽然高一点，
   但还是勉强能听”
- 而是
  “高到已经影响你继续做比较”

## 本轮代码落地

### 1. `src/v5vc/nores_vocoder_audio_export.py`
- 新增可选输出:
  - `decoded_pitch_matched.wav`
- 当前做法:
  - 对每条记录分别估计:
    - `decoded.wav`
      的中位 voiced F0
    - `aligned_target.wav`
      的中位 voiced F0
  - 计算两者的
    semitone 偏移
  - 用全局 pitch shift
    把 `decoded.wav`
    拉到与
    `aligned_target.wav`
    同一音高量级，
    保持时长不变
- 同时把以下信息
  写入 manifest:
  - `decoded_pitch_matched_audio_path`
  - `pitch_match_metrics`
  - summary 级
    `pitch_match`

### 2. `src/v5vc/cli.py`
- 为
  `export-offline-mvp-nores-vocoder-audio`
  新增:
  - `--pitch-match-reference`
  - `--pitch-match-fmin-hz`
  - `--pitch-match-fmax-hz`
  - `--pitch-match-max-semitones`
- `--listening-audio-source`
  现支持:
  - `decoded`
  - `decoded_pitch_matched`
  - `audit_proxy`

### 3. `src/v5vc/audio_audit_gui.py`
- GUI
  现在也能识别:
  - `decoded_pitch_matched`
  作为主听源

## 本轮导出与验证

### 1. 单条 smoke
- 导出目录:
  - `tmp/stage5_decoded_pitchmatch_smoke/`
- GUI smoke 输出:
  - `tmp/stage5_decoded_pitchmatch_gui_smoke/`

其中
  `target::chapter3_22_firefly_114`
  的 pitch-match
  记录为:
- `decoded_median_f0_hz = 275.460405`
- `reference_median_f0_hz = 184.912782`
- `applied_semitones = -6.9`
- `status = applied`

并且复核后，
  `decoded_pitch_matched.wav`
  的中位 voiced F0
  已与目标对齐到:
- `184.912782 Hz`

### 2. 当前主线双 bundle 已重导
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1/`
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1/`

两者当前都记录:
- `listening_audio_source = decoded_pitch_matched`
- `pitch_match.reference = aligned_target`

aggregate
  shift 统计:
- `median applied semitones = -1.9`
- `mean applied semitones = -2.458321`
- `median applied ratio = 0.896792`

### 3. 新 GUI session 已 smoke
- 输出目录:
  - `reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_decodedpitchmatch_session/`

### 4. 对应脚本入口

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_audio_audit_activitygate60_vs_72_decoded_pitchmatch.ps1
```

## 当前契约

### 1. 当前主听源
- `decoded_pitch_matched.wav`

### 2. 当前技术排查源
- `decoded.wav`

### 3. 当前诊断源
- `audit_proxy.wav`

## 适用边界

### 1. 适合拿来判断的内容
- 边界是否顺
- 动态是否更自然
- 整体可接受度
- `60`
  对
  `72`
  的相对听感差异

### 2. 不适合拿来判断的内容
- 原始模型输出
  是否已经学会
  正确音高
- 绝对 pitch fidelity
- 最终成品链路的
  原生可听形态

## 当前判断

### 1. 这一步是必要的“听评解阻”，不是模型结论升级
- 它解决的是:
  - 听评被绝对音高偏差
    阻断
- 它没有证明:
  - Stage5 raw decoded
    已经修好 pitch

### 2. 当前最合理的人工听评入口应改为 pitch-matched decoded
- 因为它比
  `audit_proxy.wav`
  更接近正常语音
- 又比 raw `decoded.wav`
  更不容易因高音刺激
  直接带偏判断

## 一句话结论
- 当前 Stage5
  人工听评的可执行主入口
  应更新为
  `decoded_pitch_matched.wav`；
  这是为了把
  raw `decoded.wav`
  的绝对音高偏移
  从听评主问题里剥离出去，
  恢复可做的人耳比较，
  但不代表模型原始输出
  已经解决 pitch 问题。
