# 2026-03-21 Stage5 no-res 门槛验收听审启动报告

## 结论
- 当前实验线不再继续开
  `postenv` /
  training apply-mode /
  clean-only
  这类低信息量小题。
- 已把下一步正式接成：
  - `Stage5 no-res milestone acceptance`
- 当前使用的正式听审入口是：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1/`
- 当前正式脚本入口是：
  - `scripts/launch_stage5_nores_milestone_acceptance_audit.ps1`
- 当前 GUI
  已不再沿用旧的分支对比字段，
  而是正式切成：
  - `milestone_acceptance`
    评审模式

## 为什么现在要切到这一步
- `docs/247_stage5_experiment_line_next_question_assessment_report.md`
  已确认：
  - 最近几条实验子线都已阶段性收口
- `docs/248_stage5_original_design_milestone_review_report.md`
  已确认：
  - 真正还没被正式回答的，
    不是局部 decode 参数，
    而是：
    - 当前 no-res route
      是否已达到
      “可懂、稳定、基本自然”

## 本轮采用的验收资产

### 1. 当前 best route
- bundle:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1/`
- 当前口径：
  - `step72`
  - `decode_gate_smooth3`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`
  - `listening_audio_source = decoded`

### 2. 当前样本面
- `sample_count = 12`
- 记录包括：
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_2_firefly_212`
  - `target::chapter3_29_firefly_113`
  - `target::chapter3_3_firefly_174`
  - `target::chapter3_20_firefly_133`
  - `target::chapter3_2_firefly_163`
  - `target::chapter3_6_firefly_106`
  - `target::chapter3_2_firefly_155`
  - `target::chapter3_3_firefly_245`
  - `target::chapter3_26_firefly_107`
  - `target::chapter3_17_firefly_133`
  - `target::chapter3_4_firefly_106`

## 当前正式运行命令

```powershell
$env:PYTHONPATH = "src"
.\python.exe -m v5vc.audio_audit_gui `
  --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1 `
  --output-dir reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session `
  --review-mode milestone_acceptance
```

## 对应脚本入口

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_nores_milestone_acceptance_audit.ps1
```

- 若只做启动 smoke，
  可额外传：
  - `-AutoCloseMs 1000`

## 当前听审输出目录
- `reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session/`

## 这轮听什么

### 1. 这轮不是分支排名
- 当前 GUI
  只加载一条当前 best route bundle
- 当前评分字段固定为：
  - `intelligibility`
  - `stability`
  - `basic_naturalness`
  - `milestone_verdict`
- 要回答的是：
  - 它自己是否已经达到
    Stage5 no-res
    的阶段门槛
- 不是：
  - `step72`
    对
    `step96`
  - 或
    `smooth3`
    对
    `postenv`
    的对比题

### 2. 当前主判断维度
- 可懂性
  - 语音内容是否大体能听清，
    是否频繁糊成难辨识片段
- 稳定性
  - 是否存在明显破音、
    持续 buzzing、
    句内大起伏、
    边界碎裂
- 基本自然度
  - 虽然不要求 final vocoder 级别，
    但至少不能长期停留在
    “只能当技术信号，
    不像正常语音”

### 3. 当前辅助判断维度
- 与
  `aligned_target.wav`
  对照时，
  关注：
  - 句尾是否收得住
  - 停顿是否自然
  - 节奏和连续性是否明显崩坏

### 4. 当前不要误判的地方
- `aligned_target.wav`
  是当前 bootstrap objective
  的对齐参考，
  不是最终用户线 source-to-target
  闭环产物
- `decoded.wav`
  是当前最接近可听成品的
  Stage5 no-res
  导出音频，
  但仍不是
  final MRSTFT /
  adversarial vocoder

## 本轮工程动作
- 新增脚本：
  - `scripts/launch_stage5_nores_milestone_acceptance_audit.ps1`
- 作用：
  - 固定 milestone acceptance
    使用的 bundle 和输出目录
  - 固定
    `milestone_acceptance`
    评审模式
  - 避免下次接班时又退回到：
    - 继续开局部 tweak
    - 或重新猜应该听哪一包

## 验证
- 已执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_nores_milestone_acceptance_audit.ps1 -AutoCloseMs 1000
```

- 预期通过标准：
  - 命令退出成功
  - 目录
    `reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session/`
    已生成
  - 至少看到：
    - `audio_audit_progress.json`
  - 且其中
    `review_mode = milestone_acceptance`
  - 且单条记录字段为：
    - `intelligibility`
    - `stability`
    - `basic_naturalness`
    - `milestone_verdict`

## 听完后怎么物化结果
### 1. 当前正式结果物化脚本
- `scripts/materialize_stage5_nores_milestone_acceptance_result_report.ps1`

### 2. 对应底层命令
```powershell
$env:PYTHONPATH = "src"
.\python.exe -m v5vc.stage5_nores_milestone_acceptance_report `
  --audio-audit-review reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session/audio_audit_review.json `
  --output-dir reports/stage_reports/stage5_nores_milestone_acceptance_result_round1_1 `
  --title "stage5 no-res milestone acceptance report - step72 smooth3 postenv validation12 decoded"
```

### 3. 当前固定输出目录
- `reports/stage_reports/stage5_nores_milestone_acceptance_result_round1_1/`

## 下一步
1. 若用户继续实验线，
   优先参考：
   - `docs/253_stage5_nores_milestone_acceptance_partial_human_audit_fail_report.md`
2. 若后续还要补齐 GUI
   导出的正式
   `audio_audit_review.json`，
   再运行：
   - `powershell -ExecutionPolicy Bypass -File scripts/materialize_stage5_nores_milestone_acceptance_result_report.ps1`
3. 当前在新的 root-cause
   题被明确前，
   不再继续这轮 milestone acceptance
   的逐条穷举听审
4. 在新的调查方向明确前，
   不再重开当前局部 tweak
   小题

## 一句话结论
- 当前实验线已经从
  “下一题应该做什么”
  推进到
  “Stage5 no-res 门槛验收现在就能启动”；
  下次接班应优先接这轮正式听审，
  而不是回去继续扫旧局部参数。
