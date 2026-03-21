# 2026-03-21 `teacher-first / single-target` 多输入 smoke 与 PowerShell 包装脚本报告

## 结论
- 当前终端用户线已在
  `3`
  类真实输入上完成附加 smoke，
  三次均成功导出：
  - `decoded.wav`
  - `teacher_first_vc_demo.json`
  - `teacher_first_vc_demo.md`
  - 中间 contract / scaffold
- 同时已补一条正式 PowerShell 包装脚本：
  - `scripts/run_teacher_first_single_target_vc_demo.ps1`
- 当前最重要的新工程结论不是“质量已经定型”，
  而是：
  - 这条最小闭环入口在不同输入形态上继续保持可运行
  - 并且用户侧默认入口现在不必再手写完整 `manage.py` 命令

## 本轮目标
1. 继续验证当前
   `run-offline-mvp-teacher-first-vc-demo`
   是否只是在单一样本上偶然跑通
2. 补一个更接近终端用户使用方式的正式脚本入口
3. 避免重复复用固定 output dir
   导致旧结果被覆盖

## 本轮 smoke

### 1. 原始长录音前 2 秒截断
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_ly65_raw.wav `
  --output-dir tmp/teacher_first_vc_demo_smoke_raw2s `
  --max-audio-sec 2.0 `
  --device cpu
```

- exit code:
  `0`
- summary 关键字段：
  - `decoded_audio_sec = 1.998333`
  - `decoded_waveform_rms = 0.046524`
  - `branch_label = stage5_best_validation_step72__decode_gate_smooth3`

### 2. 常规 source segment
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --output-dir tmp/teacher_first_vc_demo_smoke_segment1 `
  --device cpu
```

- exit code:
  `0`
- summary 关键字段：
  - `decoded_audio_sec = 1.528333`
  - `decoded_waveform_rms = 0.085918`
  - `branch_label = stage5_best_validation_step72__decode_gate_smooth3`

### 3. peak 片段
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav `
  --output-dir tmp/teacher_first_vc_demo_smoke_peak11 `
  --device cpu
```

- exit code:
  `0`
- summary 关键字段：
  - `decoded_audio_sec = 1.398333`
  - `decoded_waveform_rms = 0.130412`
  - `branch_label = stage5_best_validation_step72__decode_gate_smooth3`

## 新增脚本

### 1. 文件
- `scripts/run_teacher_first_single_target_vc_demo.ps1`

### 2. 设计目标
- 只要求用户显式提供：
  - `-InputAudio`
- 其余默认继续沿当前正式用户线口径：
  - Stage5 `best_validation`
  - `step72`
  - `predicted activity gate smoothing = 3`
  - apply mode = `post_ola_envelope`

### 3. 当前能力
- 若未显式提供
  `-OutputDir`，
  脚本会自动创建：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_runs/<input_stem>_<timestamp>/`
- 脚本当前默认显式传：
  - `--chunk-ms 33.333333`
  以保持不同输入采样率下的默认时间窗基本一致
- 可选参数：
  - `-Device`
  - `-MaxAudioSec`
  - `-ChunkMs`
  - `-UsePostEnv`
  - `-NoSaveIntermediates`
  - `-SkipFullPassVerify`

### 4. 为什么要自动生成输出目录
- 当前底层 CLI
  会先 reset output directory
- 所以如果包装脚本继续默认写死某个固定路径，
  用户重复运行时会直接覆盖上一轮产物
- 这对：
  - 多轮对比
  - 问题复现
  - 听感回查
  都不友好

### 5. 为什么脚本默认要显式传 `chunk-ms`
- 当前 teacher runtime
  若未显式给
  `chunk_samples/chunk_ms`，
  会退回 sample-based 默认
- 这在常见输入上接近
  `33.33ms`，
  但一旦输入采样率变化，
  相同 sample 数就会对应到不同时间窗
- 所以终端用户包装脚本当前默认固定传：
  - `33.333333ms`
  避免非默认采样率把 runtime 边界悄悄放大

## 包装脚本 smoke

### 命令
```powershell
.\scripts\run_teacher_first_single_target_vc_demo.ps1 `
  -InputAudio data_prep/round1/source_segments/segments/segment_0002_0000023770_0000024280.wav `
  -Device cpu `
  -NoSaveIntermediates
```

### 结果
- exit code:
  `0`
- 自动生成输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_runs/segment_0002_0000023770_0000024280_20260321_152543/`
- 已导出：
  - `decoded.wav`
  - `teacher_first_vc_demo.json`
  - `teacher_first_vc_demo.md`
- 未保留中间：
  - `teacher_contract`
  - `teacher_vocoder_input_scaffold`
- summary 关键字段：
  - `decoded_audio_sec = 0.508333`
  - `decoded_waveform_rms = 0.030339`
  - `save_intermediates = false`

## 当前边界
- 本轮只验证了：
  - 多输入形态下是否能稳定跑通
  - 包装脚本是否能收敛终端用户调用面
- 本轮还没有验证：
  - 静音占比极高输入
  - 非默认 sample rate
  - `postenv`
    分支的人耳优劣
  - 最终产品级质量

## 补充边界 smoke

### 1. 高静音输入
```powershell
.\scripts\run_teacher_first_single_target_vc_demo.ps1 `
  -InputAudio data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav `
  -Device cpu `
  -NoSaveIntermediates
```

- exit code:
  `0`
- 说明：
  - 该输入按快速静音统计，
    `silence_frac_abs512 = 0.9623`
  - 属于当前 source segments
    中近乎极端高静音样本
- summary 关键字段：
  - `decoded_audio_sec = 0.508333`
  - `decoded_waveform_rms = 0.027804`
  - `save_intermediates = false`

### 2. `postenv` 包装脚本 smoke
```powershell
.\scripts\run_teacher_first_single_target_vc_demo.ps1 `
  -InputAudio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  -Device cpu `
  -UsePostEnv `
  -NoSaveIntermediates
```

- exit code:
  `0`
- summary 关键字段：
  - `decoded_audio_sec = 1.528333`
  - `decoded_waveform_rms = 0.08585`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`
  - `branch_label = stage5_best_validation_step72__decode_gate_smooth3_postenv`

### 3. 非默认采样率 `16kHz` 输入
```powershell
.\scripts\run_teacher_first_single_target_vc_demo.ps1 `
  -InputAudio tmp/teacher_first_vc_demo_inputs/segment_0001_0000020110_0000021640_16k.wav `
  -Device cpu `
  -NoSaveIntermediates
```

- exit code:
  `0`
- 临时输入来源：
  - 由
    `data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav`
    重采样到
    `16kHz`
  - 路径：
    `tmp/teacher_first_vc_demo_inputs/segment_0001_0000020110_0000021640_16k.wav`
- summary 关键字段：
  - `decoded_audio_sec = 1.525`
  - `decoded_waveform_rms = 0.085248`
  - `chunk_samples = 533`
  - `chunk_ms = 33.3125`

## 当前新增判断
- 当前终端用户包装脚本已经覆盖：
  - 常规 segment
  - peak 片段
  - 高静音片段
  - `postenv`
    显式切换
  - `16kHz`
    非默认采样率输入
- 当前看到的结果是：
  - 这些边界都不是立刻阻断运行的 blocker
  - 非默认采样率也已能稳定导出
  - 包装脚本层的
    `chunk-ms`
    固定策略
    已把一个潜在时序漂移风险先压住

## 下一步建议
1. 继续补：
   - 高静音输入 smoke
   - `postenv`
     包装脚本 smoke
   - 非默认 sample rate 输入 smoke
2. 若都稳定，
   再考虑把用户线 summary
   的失败分层做得更明确

## 一句话结论
- 当前终端用户线已经从
  “单条 CLI 能跑”
  进一步推进到：
  - 多输入 smoke 继续稳定
  - 终端用户可直接调用的 PowerShell 包装脚本已具备
  - 默认也避免了重复运行时覆盖旧结果的问题

## 2026-03-21 补充：用户线 summary 已补齐失败分层与流水线状态
### 当前结论
- `teacher_first_vc_demo.json/.md`
  不再只写：
  - `stage`
  - `error_type`
  - `error_message`
- 现在还会显式写出：
  - `pipeline.layers`
  - 当前停在哪个
    `layer`
  - 当前停在哪个
    `stage`
  - 对应的
    `diagnostic_summary`
  - `likely_causes`
  - `recommended_actions`
- 用户线失败口径现在可直接区分：
  - `teacher_runtime`
  - `teacher_contract`
  - `teacher_vocoder_input_scaffold`
  - `vocoder_checkpoint`
  - `waveform_reconstruction`

### 本轮验证
#### 1. 故意失败验证：缺失输入音频
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio tmp/does_not_exist.wav `
  --output-dir tmp/teacher_first_vc_demo_failure_missing_input `
  --device cpu
```

- 结果：
  - 命令按预期失败
  - 但仍成功写出：
    - `tmp/teacher_first_vc_demo_failure_missing_input/teacher_first_vc_demo.json`
    - `tmp/teacher_first_vc_demo_failure_missing_input/teacher_first_vc_demo.md`
- summary 关键字段：
  - `pipeline.current_stage = input_audio_load`
  - `failure.layer = teacher_runtime`
  - `failure.stage_label = Load input audio`
  - `failure.diagnostic_summary = The input audio could not be read into the teacher runtime.`

#### 2. 短成功 smoke：确认成功态也会写全流水线
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --output-dir tmp/teacher_first_vc_demo_success_short `
  --max-audio-sec 0.1 `
  --device cpu `
  --no-save-intermediates `
  --skip-full-pass-verify
```

- 结果：
  - exit code `0`
- summary 关键字段：
  - `decoded_audio_sec = 0.098333`
  - `pipeline.current_stage = null`
  - `pipeline.skipped_stages = ["teacher_runtime_verification"]`
  - `pipeline.layers[*].status`
    全部为
    `succeeded`

### 当前意义
- 终端用户线现在不仅能跑通，
  还更接近“可排障入口”：
  即使用户命令失败，
  也能直接看 summary 判断：
  - 是输入/teacher runtime 问题
  - 是 conditioning / contract 问题
  - 是 scaffold 问题
  - 还是 Stage5 checkpoint / waveform reconstruction 问题

### 下一步建议
1. 补一轮更贴近真实用户误用的失败演练：
   - 错 calibration asset
   - 错 vocoder checkpoint
2. 再决定是否把
   `recommended_actions`
   进一步压缩成更终端用户化的中文提示
