# 2026-03-27 teacher-first 三条 pure buzz 样本 waveform decoder structure probe 报告

## 结论
- 我已在 user-line 固定三条 pure buzz 样本上，
  补跑新的
  `analyze-offline-mvp-teacher-first-vc-waveform-decoder-structure`
  结构探针：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp/`
- 当前最关键的新结论是：
  1. user-line baseline 下，
     `fused_hidden -> waveform_frames`
     确实还会再模板化一点，
     但量级不大：
     - `fused_hidden_template_cosine_mean = 0.994928`
     - `waveform_frames_template_cosine_mean = 0.999597`
     - 自动诊断仍是
       `collapse_not_localized_to_waveform_decoder`
  2. `fused_hidden_frame_mean`
     对最终波形几乎没有影响：
     - `waveform_mean_abs_delta_vs_baseline = 0.007526`
  3. 一旦直接用
     `periodic / noise / branch_mean`
     旁路 fusion，
     输出会立刻明显脱离当前模板区：
     - `decoded_template`
       从 baseline 的 `0.993580`
       降到
       `0.859604 / 0.915412 / 0.901776`
  4. 但这些 bypass
     不是自然变成 speech，
     而是掉进
     更亮、更尖、更高频
     的非稳态区：
     - centroid
       上冲到
       `10667 ~ 12240 Hz`
     - high-band ratio
       上冲到
       `0.808 ~ 0.852`

## 一、probe 入口
- 命令：
```powershell
.\python.exe manage.py analyze-offline-mvp-teacher-first-vc-waveform-decoder-structure `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --input-audio data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav `
  --input-audio data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp `
  --device cpu `
  --chunk-ms 33.333333
```
- 默认 decode 语义：
  - `use_predicted_activity_gate = false`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`
- 也就是：
  - 先把 gate 从主读法里拿掉，
    直接看 decoder 结构路径本身

## 二、baseline 结构摘要
- `fused_hidden_template_cosine_mean = 0.994928`
- `waveform_frames_template_cosine_mean = 0.999597`
- `decoded_frames_template_cosine_mean = 0.993580`
- `fused_hidden_adjacent_cosine_mean = 0.999900`
- `waveform_frames_adjacent_cosine_mean = 0.999986`
- `fused_to_waveform_template_cosine_gap = 0.004669`
- `fused_to_waveform_adjacent_cosine_gap = 0.000086`
- 自动诊断：
  - `collapse_not_localized_to_waveform_decoder`

这说明：
- user-line 上，
  decoder route
  会继续把当前坏 manifold
  往固定模板方向推一点，
  但第一大坍缩点
  仍不在 decoder 单点内部

## 三、关键变换结果

### 1. `fused_hidden_frame_mean` 几乎不改变输出
- `waveform_mean_abs_delta_vs_baseline = 0.007526`
- `decoded_template`
  - `0.993580 -> 0.995503`

这说明：
- user-line baseline 的
  `fused_hidden`
  本身已经非常接近常模板，
  再压成 frame mean
  也不会明显更坏

### 2. branch bypass 会立刻明显脱离当前模板区

#### `fused_hidden_from_periodic_hidden`
- `waveform_mean_abs_delta_vs_baseline = 0.332345`
- `decoded_template`
  - `0.993580 -> 0.859604`
- `waveform_template`
  - `0.999597 -> 0.882346`

#### `fused_hidden_from_noise_hidden`
- `waveform_mean_abs_delta_vs_baseline = 0.315547`
- `decoded_template`
  - `0.993580 -> 0.915412`
- `waveform_template`
  - `0.999597 -> 0.925074`

#### `fused_hidden_from_branch_mean`
- `waveform_mean_abs_delta_vs_baseline = 0.328595`
- `decoded_template`
  - `0.993580 -> 0.901776`
- `waveform_template`
  - `0.999597 -> 0.917534`

这说明：
- 当前 decoder
  并不是
  “无论输入什么都只会吐同一个 buzz”
- 它对 branch-side hidden dynamics
  仍然有响应

### 3. 但 bypass 响应落到高频非稳态区

#### `fused_hidden_from_periodic_hidden`
- `decoded_spectral_centroid_hz = 12240.174805`
- `decoded_spectral_high_band_energy_ratio = 0.851884`

#### `fused_hidden_from_noise_hidden`
- `decoded_spectral_centroid_hz = 10667.417969`
- `decoded_spectral_high_band_energy_ratio = 0.808060`

#### `fused_hidden_from_branch_mean`
- `decoded_spectral_centroid_hz = 11467.301758`
- `decoded_spectral_high_band_energy_ratio = 0.820298`

这说明：
- 绕开当前 fusion
  确实能让输出离开 baseline 的
  固定模板区
- 但不会自然落回语音区，
  而是会冲进更亮、更刺、更高频的
  非稳态区域

## 四、当前应如何解释
1. user-line 上的第一大坍缩点，
   仍应优先放在：
   - `branch_mean -> fused_hidden`
   - 以及随后的
     decoder input operating region
2. 不能把当前问题写成：
   - 只是 gate 才新引入了坏解
   - 或 decoder 自身已经完全死到只会输出常模板
3. 更准确的说法是：
   - fusion 先把系统压进坏 manifold
   - decoder 再围绕这块坏 manifold
     学到一个稳定的高模板 buzz 解
   - 一旦强行喂回 branch dynamics，
     decoder 会响应，
     但会落到另一种高频非稳态

## 一句话结论
- user-line 三条 pure buzz 样本上，
  `fused_hidden_frame_mean` 几乎无影响，
  而 branch bypass 会立刻让输出大幅脱离 baseline 模板区；
  因而当前主病灶仍应优先定位在
  `fusion / decoder input manifold`，
  不是 gate，
  也不是“decoder 已完全失去响应能力”。 
