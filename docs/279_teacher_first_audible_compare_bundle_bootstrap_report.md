# 2026-03-24 teacher-first audible compare bundle 启动报告

## 结论
- 本轮已把
  baseline / candidate
  并排 user-line
  听审入口
  正式落成代码与脚本：
  - CLI:
    `build-offline-mvp-teacher-first-vc-audible-compare-bundle`
  - PowerShell:
    `scripts/run_teacher_first_single_target_audible_compare_bundle.ps1`
- 新 compare bundle
  当前每个 case
  固定只保留一套：
  - `source_input.wav`
  - `target_reference.wav`
  - `smoke_baseline_passthrough.wav`
- 在这套共享正控制旁边，
  再并排导出：
  - `decoded_baseline.wav`
  - `decoded_candidate.wav`
  - 或更一般的
    `decoded_<variant>.wav`
- summary
  当前也已按 variant
  显式列出：
  - `checkpoint_path`
  - `applicability_risk_status`
  - `decoded_listening_audio_path`
  - 以及聚合后的
    `decoded_high_risk_count`

## 本轮代码变更
- `src/v5vc/teacher_first_vc_demo.py`
  - 新增
    `build_teacher_first_vc_audible_compare_bundle(...)`
  - 新增默认 baseline / candidate
    variant
    解析逻辑：
    从两份 Stage5
    dataset-loop summary
    里自动取 checkpoint
  - 新增 compare bundle
    summary json / md
    生成逻辑
  - 新增 variant
    风险状态与试听路径
    字段
  - 对 variant id
    增加稳定去重，
    避免未来 label
    重复时覆盖输出文件
- `src/v5vc/cli.py`
  - 新增正式命令：
    `build-offline-mvp-teacher-first-vc-audible-compare-bundle`
- `scripts/run_teacher_first_single_target_audible_compare_bundle.ps1`
  - 新增默认
    `main_listening / boundary_probe`
    profile
    包装入口

## 默认 variant 契约
- baseline
  默认来源：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_baseline_smoke_round1_2/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- candidate
  默认来源：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_active_template_delta_smoke_round1_2/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- 默认都取：
  - `artifacts.best_checkpoint.checkpoint_path`

## 新 CLI 的当前契约

### 最小输入
- `--input-audio <wav>`
  或
  `--input-spec-jsonl <jsonl>`

### 可选 variant 输入
- `--vocoder-spec-jsonl <jsonl>`
- 每行可包含：
  - `label`
  - 可选
    `variant_id`
  - `checkpoint_path`
    或
    `checkpoint_source_summary_path`
  - 可选
    `checkpoint_source_key`
  - 可选
    `notes`

### 当前主要输出
- `teacher_first_vc_audible_compare_bundle.json`
- `teacher_first_vc_audible_compare_bundle.md`
- `runs/<case_id>/<variant_id>/teacher_first_vc_demo.json`
- `listening/<case_id>/source_input.wav`
- `listening/<case_id>/target_reference.wav`
- `listening/<case_id>/smoke_baseline_passthrough.wav`
- `listening/<case_id>/decoded_<variant>.wav`

### 重要口径
- 每个 case
  只保留一套共享正控制，
  不为每个 variant
  再复制一遍
  source / target / passthrough
- summary
  里每个 variant
  都显式写出：
  - checkpoint
  - 风险标记
  - 试听路径
- 当前命令只在以下情况失败：
  - 正控制音频缺失
  - 任一 variant
    demo run
    失败
- 当前不会因为
  decoded
  仍是
  `high_risk`
  就把 compare bundle
  直接判成命令失败；
  风险会在 summary
  中单独暴露

## 本轮最小 smoke 验证

### 命令
```powershell
$specDir = 'tmp/teacher_first_vc_audible_compare_specs/smoke_manual'
New-Item -ItemType Directory -Force -Path $specDir | Out-Null
$specPath = Join-Path $specDir 'audible_compare_input_specs.jsonl'
$spec = @{
  case_id = 'short_segment_0001'
  input_audio_path = (Resolve-Path 'data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav').Path
  max_audio_sec = 0.15
  notes = @('Short single-case compare smoke for CLI and PowerShell wrapper verification.')
}
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$writer = New-Object System.IO.StreamWriter($specPath, $false, $utf8NoBom)
try {
  $writer.WriteLine(($spec | ConvertTo-Json -Compress -Depth 5))
} finally {
  $writer.Dispose()
}

.\scripts\run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -InputSpecJsonl $specPath `
  -OutputDir tmp/teacher_first_vc_audible_compare_smoke_short `
  -Device cpu `
  -TargetReferenceMaxAudioSec 1.0 `
  -SkipFullPassVerify
```

### 结果
- exit code:
  `0`
- summary:
  - `tmp/teacher_first_vc_audible_compare_smoke_short/teacher_first_vc_audible_compare_bundle.json`
- 关键字段：
  - `case_count = 1`
  - `variant_count = 2`
  - `variant_run_count = 2`
  - `variant_succeeded_count = 2`
  - `positive_controls_ready_count = 1`
  - `variant_decoded_high_risk_count = 2`
  - `all_cases_positive_controls_ready = true`
  - `all_variant_runs_succeeded = true`

### 当前实际落盘的试听目录
- `tmp/teacher_first_vc_audible_compare_smoke_short/listening/001_short_segment_0001/`
- 已写出：
  - `source_input.wav`
  - `target_reference.wav`
  - `smoke_baseline_passthrough.wav`
  - `decoded_baseline.wav`
  - `decoded_candidate.wav`

### 当前 summary 中已实际暴露的 variant 字段
- baseline：
  - `checkpoint_path`：
    `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_baseline_smoke_round1_2/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt`
  - `applicability_risk_status = high_risk`
  - `decoded_listening_audio_path`：
    `tmp/teacher_first_vc_audible_compare_smoke_short/listening/001_short_segment_0001/decoded_baseline.wav`
- candidate：
  - `checkpoint_path`：
    `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_active_template_delta_smoke_round1_2/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt`
  - `applicability_risk_status = high_risk`
  - `decoded_listening_audio_path`：
    `tmp/teacher_first_vc_audible_compare_smoke_short/listening/001_short_segment_0001/decoded_candidate.wav`

## 默认主听 compare 用法

### 默认主听包
```powershell
.\scripts\run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_main_listening_round1_1 `
  -Device cpu `
  -SkipFullPassVerify
```

### 边界 probe 包
```powershell
.\scripts\run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -BundleProfile boundary_probe `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_boundary_probe_round1_1 `
  -Device cpu `
  -SkipFullPassVerify
```

## 当前意义
- 到这一步为止，
  baseline / candidate
  已经可以在
  同一套 source / target / passthrough
  正控制旁边
  直接并排听
- 这样后续人工听审
  不再需要：
  - 手工拼两份独立 smoke
  - 手工核对哪个 decoded
    对应哪个 checkpoint
- 但与此同时，
  本轮最小 smoke
  也再次确认：
  - baseline
    仍是
    `high_risk`
  - candidate
    仍是
    `high_risk`
- 所以当前更准确的阶段表述应是：
  - compare 交付物
    已具备
  - 模型听感
    仍未摆脱 buzz

## 一句话结论
- teacher-first audible compare bundle
  已正式落地并通过最小 smoke；
  当前它把
  baseline / candidate
  并排听审
  变成了可直接交付的固定契约，
  同时继续把
  两条 decoded
  仍是
  `high_risk buzz`
  单独暴露出来。
