# 2026-03-27 teacher-first output-head high-band 对比听审包与音频打分入口报告

## 结论
- 针对 `docs/441_stage5_output_head_headstruct_high_band_candidate_breakthrough_report.md`
  的新主候选，
  本轮已经把正式人工听审入口落成到磁盘：
  - compare bundle：
    `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/`
  - 听审主目录：
    `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/listening/`
  - GUI 输出目录：
    `reports/audio/audio_audit_gui_outputhead_highband_vs_strongest_round1_1/`
- 本轮主对比目标已固定为：
  - 旧 strongest native candidate
  - 对比
  - 新 `output_head_high_band_bhb01`
- compare bundle
  已完成：
  - `case_count = 3`
  - `variant_count = 2`
  - `variant_runs_succeeded = 6 / 6`
  - `positive_controls_ready = 3 / 3`
- GUI
  也已完成一次可启动 smoke，
  但要注意：
  - `launch-audio-audit-gui`
    对这类 bundle
    不能只传目录，
    要传：
    `teacher_first_vc_audible_compare_bundle.json`

## 一、正式听审对象

### 1. baseline
- variant id：
  `strongest_native_candidate`
- checkpoint：
  `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`

### 2. candidate
- variant id：
  `output_head_high_band_bhb01`
- checkpoint：
  `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bhb01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`

### 3. decode 口径
- 两路都固定为：
  - predicted activity gate `on`
  - apply mode `post_ola_envelope`
  - normalization `none`

## 二、固定听审样本
- `001_segment_0001`
  - `data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav`
- `002_segment_0061`
  - `data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav`
- `003_peak_011`
  - `data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav`

## 三、当前已落盘的正式入口

### 1. bundle 生成命令
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -InputSpecJsonl tmp/teacher_first_output_head_highband_compare_specs/input_specs_round1_1.jsonl `
  -VocoderSpecJsonl tmp/teacher_first_output_head_highband_compare_specs/vocoder_specs_round1_1.jsonl `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1 `
  -Device cuda `
  -SkipFullPassVerify
```

### 2. GUI 启动命令
```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/teacher_first_vc_audible_compare_bundle.json `
  --output-dir reports/audio/audio_audit_gui_outputhead_highband_vs_strongest_round1_1
```

### 3. 直接听 wav 的目录
- `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/listening/`

### 4. GUI 结果输出目录
- `reports/audio/audio_audit_gui_outputhead_highband_vs_strongest_round1_1/`

## 四、本轮听审重点
- 第一优先：
  `output_head_high_band_bhb01`
  是否比旧 strongest
  明显更少
  “亮、尖、刺、纯 buzz”
- 第二优先：
  在 `segment_0061`
  这种高静音占比样本上，
  门后是否更稳，
  是否减少边界漏声和尖锐残响
- 第三优先：
  在 `peak_011`
  上，
  是否开始出现更接近人声的结构感，
  而不只是把亮度压暗
- 本轮不要把判断重点放在：
  - “是否已经完全转正”
  上；
  当前更关键的是：
  - 相对旧 strongest
    有没有形成稳定、可听的主观改善

## 五、当前量化侧对听审的支撑
- 三条样本上，
  `output_head_high_band_bhb01`
  都比旧 strongest
  更暗一些，
  而且下降幅度不是只出现在单条样本：
  - `001_segment_0001`
    - centroid：
      `6475.924298 -> 4296.370313`
    - high_band：
      `0.447577 -> 0.218496`
  - `002_segment_0061`
    - centroid：
      `6432.026358 -> 5427.835514`
    - high_band：
      `0.440972 -> 0.309665`
  - `003_peak_011`
    - centroid：
      `6612.378657 -> 4689.932082`
    - high_band：
      `0.459648 -> 0.249593`
- 但当前两路
  仍都被
  `teacher_first_runtime_risk_v2_reference_relative`
  标成：
  - `high_risk`
- 因而这轮人工听审的意义是：
  - 判断它是不是第一次从“明显更亮更刺的坏样本”
    收敛成“值得继续治理的相对更好样本”
  - 而不是让旧 heuristic
    代替主观结论

## 六、交付物清单
- compare bundle summary：
  `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/teacher_first_vc_audible_compare_bundle.json`
- compare bundle markdown：
  `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/teacher_first_vc_audible_compare_bundle.md`
- 输入规格：
  `tmp/teacher_first_output_head_highband_compare_specs/input_specs_round1_1.jsonl`
- variant 规格：
  `tmp/teacher_first_output_head_highband_compare_specs/vocoder_specs_round1_1.jsonl`

## 一句话结论
- `441` 的新 high-band 候选已经被整理成可直接听的正式 compare bundle，旧 strongest vs 新 `bhb01` 的主观对比入口、GUI 启动命令和结果输出目录都已固定，下一步可以直接做人工听审，不需要再手工拼路径。
