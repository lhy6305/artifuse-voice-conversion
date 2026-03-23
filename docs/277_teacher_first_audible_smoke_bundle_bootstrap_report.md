# 2026-03-24 teacher-first audible smoke bundle 启动报告

## 结论
- 本轮已把
  “不是只导出一个 `decoded.wav`，
  而是带可听正控制的 smoke”
  正式落成代码与脚本：
  - CLI:
    `build-offline-mvp-teacher-first-vc-audible-smoke-bundle`
  - PowerShell:
    `scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1`
- 新 bundle
  当前每个 case
  固定导出：
  - `source_input.wav`
  - `target_reference.wav`
  - `smoke_baseline_passthrough.wav`
  - `decoded_experimental.wav`
- 这样当前就算
  experimental decoded
  仍是 buzz，
  smoke bundle
  本身也已经是
  真正能听的交付物，
  不再只有失败音频。

## 本轮代码变更
- `src/v5vc/teacher_first_vc_demo.py`
  - 新增
    `build_teacher_first_vc_audible_smoke_bundle(...)`
  - 新增默认 target reference
    解析逻辑：
    从 calibration asset
    的
    `selected_record_ids`
    和
    `source_records_path`
    里自动取第一条可用目标音频
  - 新增正控制音频物化与
    audible smoke summary
    生成逻辑
- `src/v5vc/cli.py`
  - 新增正式命令：
    `build-offline-mvp-teacher-first-vc-audible-smoke-bundle`
- `scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1`
  - 新增默认 triplet
    case
    的 PowerShell 包装入口

## 新 CLI 的当前契约

### 最小输入
- `--input-audio <wav>`
  或
  `--input-spec-jsonl <jsonl>`

### 当前主要输出
- `teacher_first_vc_audible_smoke_bundle.json`
- `teacher_first_vc_audible_smoke_bundle.md`
- `runs/<case_id>/teacher_first_vc_demo.json`
- `listening/<case_id>/source_input.wav`
- `listening/<case_id>/target_reference.wav`
- `listening/<case_id>/smoke_baseline_passthrough.wav`
- `listening/<case_id>/decoded_experimental.wav`

### 重要口径
- summary
  里明确拆开：
  - pipeline 是否成功
  - positive controls
    是否齐全
  - decoded
    是否存在
  - decoded
    是否仍命中
    high-risk buzz
- 当前命令只在以下情况失败：
  - demo pipeline
    本身失败
  - 正控制音频缺失
- 当前不会因为
  decoded
  仍是
  `high_risk`
  就把整个 audible smoke
  判成命令失败

## 本轮 smoke 验证

### 命令
```powershell
$env:PYTHONPATH='src'
.\python.exe manage.py build-offline-mvp-teacher-first-vc-audible-smoke-bundle `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --output-dir tmp/teacher_first_vc_audible_smoke_short `
  --device cpu `
  --max-audio-sec-default 0.15 `
  --target-reference-max-audio-sec 1.0 `
  --no-save-intermediates `
  --skip-full-pass-verify
```

### 结果
- exit code:
  `0`
- summary:
  - `tmp/teacher_first_vc_audible_smoke_short/teacher_first_vc_audible_smoke_bundle.json`
- 关键字段：
  - `case_count = 1`
  - `pipeline_succeeded_count = 1`
  - `positive_controls_ready_count = 1`
  - `decoded_present_count = 1`
  - `decoded_high_risk_count = 1`
  - `all_cases_pipeline_succeeded = true`
  - `all_cases_positive_controls_ready = true`

### 当前物化出的共享 target reference
- 来源：
  - calibration asset
    第一条选中记录
    `target::chapter3_20_firefly_112`
- 共享文件：
  - `tmp/teacher_first_vc_audible_smoke_short/listening/_shared_target_reference.wav`
- 本轮限制：
  - `target_reference_max_audio_sec = 1.0`

### 当前 case 试听目录
- `tmp/teacher_first_vc_audible_smoke_short/listening/001_segment_0001_0000020110_0000021640/`
- 已写出：
  - `source_input.wav`
  - `target_reference.wav`
  - `smoke_baseline_passthrough.wav`
  - `decoded_experimental.wav`

## 包装脚本 smoke

### 命令
```powershell
.\scripts\run_teacher_first_single_target_audible_smoke_bundle.ps1 `
  -InputSpecJsonl tmp/teacher_first_vc_audible_smoke_short/audible_smoke_input_specs.jsonl `
  -OutputDir tmp/teacher_first_vc_audible_smoke_script_short `
  -Device cpu `
  -TargetReferenceMaxAudioSec 1.0 `
  -SkipFullPassVerify
```

### 结果
- exit code:
  `0`
- 控制台关键输出：
  - `teacher-first audible smoke cases = 1`
  - `positive controls ready = 1/1`
  - `decoded high-risk count = 1`
  - `teacher-first audible smoke ok = True`
- 说明：
  - PowerShell
    包装层
    已完成一次真实 smoke，
    当前不是只停留在 CLI
    级代码存在

## 默认 triplet audible smoke

### 命令
```powershell
.\scripts\run_teacher_first_single_target_audible_smoke_bundle.ps1 `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_triplet_round1_1 `
  -Device cpu `
  -TargetReferenceMaxAudioSec 1.0 `
  -SkipFullPassVerify
```

### 结果
- exit code:
  `0`
- summary:
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_triplet_round1_1/teacher_first_vc_audible_smoke_bundle.json`
- 关键字段：
  - `case_count = 3`
  - `pipeline_succeeded_count = 3`
  - `positive_controls_ready_count = 3`
  - `decoded_present_count = 3`
  - `decoded_high_risk_count = 3`
- 当前主听目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_triplet_round1_1/listening/`

### 当前意义
- 到这一步为止，
  默认 triplet
  也已经具备：
  - 真可听正控制
  - 固定 target reference
  - 当前 experimental decoded
  - 每 case
    对应的完整 run summary
- 所以后续人工试听
  已可直接从这份 bundle
  开始，
  不需要再手工拼音频

## 当前意义
- 这条新入口已经把 smoke
  从：
  - “只证明命令能写出一个 wav”
  推进到：
  - “先保证 bundle 里有真能听的正控制，
     再单独汇报 experimental decoded
     仍是不是 buzz”
- 这样后续无论是脚本级 smoke
  还是人工试听，
  都不会再落回
  “整包只有一条失败 buzz”
  的交付状态

## 下一步建议
1. 直接用
   `scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1`
   跑默认 triplet
2. 若后续要做
   baseline / candidate
   并排 source-driven
   听审，
   优先在这条 audible smoke
   bundle
   之上扩分支维度，
   不要再回到
   只有 `decoded.wav`
   的旧契约

## 一句话结论
- 新的 audible smoke bundle
  已经正式落地并通过最小 smoke；
  当前它先保证
  smoke 交付物本身“真能听”，
  同时把 experimental decoded
  是否仍是 buzz
  单独暴露出来。
