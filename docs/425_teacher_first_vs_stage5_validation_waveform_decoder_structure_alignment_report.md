# 2026-03-27 teacher-first 与 Stage5 validation3 waveform decoder structure 对照报告

## 结论
- 在 user-line 三条 pure buzz 样本跑完
  decoder structure probe
  之后，
  我又用同 checkpoint
  在 validation3 package
  上补跑了同口径的
  gate-off structure probe：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_validation3_gateoff_round1_1/`
- 当前最关键的新结论是：
  - user-line
    与 validation package
    在结构层面的响应形状仍然高度一致：
    - baseline 都是
      `collapse_not_localized_to_waveform_decoder`
    - `fused_hidden_frame_mean`
      都几乎不改变输出
    - branch bypass
      都会立刻显著脱离 baseline 模板区，
      但同时冲进更亮、更高频的非稳态
- 因而当前不能把 bypass 响应解释成：
  - user-line 特有结构失真
  - user-line 特有 decoder 死亡
- 更准确的主线应是：
  - 这是当前 checkpoint-native
    的
    `fusion / decoder input manifold`
    问题，
    user-line 与 validation
    只是两种观测面

## 一、对照对象

### 1. user-line
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp/`
- 样本：
  - `segment_0001_0000020110_0000021640`
  - `segment_0061_0000300400_0000300910`
  - `peak_011_0002370615_top_peak`

### 2. Stage5 validation
- 目录：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_validation3_gateoff_round1_1/`
- 命令：
```powershell
.\python.exe manage.py analyze-stage5-nores-waveform-decoder-structure `
  --output-dir reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_validation3_gateoff_round1_1 `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --split-name validation `
  --sample-count 3 `
  --device cpu `
  --disable-predicted-activity-gate `
  --predicted-activity-gate-apply-mode post_ola_envelope
```

## 二、baseline 对照

### user-line
- `fused_hidden_template_cosine_mean = 0.994928`
- `waveform_frames_template_cosine_mean = 0.999597`
- `decoded_frames_template_cosine_mean = 0.993580`
- `diagnosis = collapse_not_localized_to_waveform_decoder`

### validation
- `fused_hidden_template_cosine_mean = 0.991694`
- `waveform_frames_template_cosine_mean = 0.999516`
- `decoded_frames_template_cosine_mean = 0.994831`
- `diagnosis = collapse_not_localized_to_waveform_decoder`

读法：
- 两边 baseline
  都不是
  “decoder 单点才第一次把系统推坏”
- 两边都是：
  - `fused_hidden`
    已经非常模板化
  - `waveform_frames`
    只是再补一小步

## 三、`fused_hidden_frame_mean` 对照

### user-line
- `waveform_mean_abs_delta_vs_baseline = 0.007526`
- `decoded_template = 0.995503`

### validation
- `waveform_mean_abs_delta_vs_baseline = 0.007795`
- `decoded_template = 0.997201`

读法：
- 两边几乎同形：
  - baseline 的
    `fused_hidden`
    都已经接近常模板
  - 再压成 frame mean
    几乎不会带来新变化

## 四、branch bypass 对照

### `fused_hidden_from_periodic_hidden`
- user-line：
  - `decoded_template = 0.859604`
  - `waveform_delta = 0.332345`
  - `centroid = 12240.174805`
  - `high_band = 0.851884`
- validation：
  - `decoded_template = 0.727802`
  - `waveform_delta = 0.324736`
  - `centroid = 11030.297852`
  - `high_band = 0.824120`

### `fused_hidden_from_noise_hidden`
- user-line：
  - `decoded_template = 0.915412`
  - `waveform_delta = 0.315547`
  - `centroid = 10667.417969`
  - `high_band = 0.808060`
- validation：
  - `decoded_template = 0.810333`
  - `waveform_delta = 0.320238`
  - `centroid = 10936.583008`
  - `high_band = 0.873918`

### `fused_hidden_from_branch_mean`
- user-line：
  - `decoded_template = 0.901776`
  - `waveform_delta = 0.328595`
  - `centroid = 11467.301758`
  - `high_band = 0.820298`
- validation：
  - `decoded_template = 0.791456`
  - `waveform_delta = 0.333161`
  - `centroid = 10708.041992`
  - `high_band = 0.837725`

读法：
- 两边都满足同一组结构性事实：
  1. branch bypass
     会立刻让输出大幅偏离 baseline
  2. 这种偏离不是轻微修复，
     而是显著脱离当前模板区
  3. 但输出同时会冲进更亮、更高频的非稳态

## 五、当前主线应该怎么收紧
1. 不能把 user-line 继续优先写成：
   - 特有 gate 问题
   - 特有 decoder 死亡
   - 特有结构 mismatch
2. 当前更准确的表述应是：
   - 同一个 checkpoint
     在 native validation
     与 user-line
     上都表现出同类结构响应
   - fusion 先把系统压进坏 manifold
   - decoder 对 branch dynamics
     仍有响应，
     但当前工作区已经偏到高频非稳态
3. 因而下一步应优先追：
   - `branch_mean -> fused_hidden`
     为什么被压成当前坏 manifold
   - 以及
     `decoder_hidden -> waveform_frame_logits`
     为什么只会在这块坏 manifold
     周围稳定收敛

## 一句话结论
- user-line 与 validation3 的 decoder structure probe 方向一致：
  baseline 都不是 decoder-first collapse，
  `fused_hidden_frame_mean` 都几乎无效，
  branch bypass 都会显著脱模但落入高频非稳态；
  当前主病灶应继续优先定位在
  `fusion / decoder input manifold`，
  而不是 user-line 特有故障。 
