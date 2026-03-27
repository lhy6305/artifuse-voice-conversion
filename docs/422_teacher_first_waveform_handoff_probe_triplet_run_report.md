# 2026-03-27 teacher-first 固定三样本 waveform handoff probe 运行报告

## 结论
- 我已经直接跑完固定三条
  pure buzz
  user-line 样本的
  waveform handoff probe：
  - 输出目录：
    `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe/`
- 结果很一致，
  当前最关键的判断是：
  - 坏相位不是
    `tanh`
    才新引入
  - 也不是
    `pre_ola / post_ola gate`
    才第一次把系统推坏
  - 更准确地说：
    - `waveform_frame_logits`
      已经几乎完全模板化
    - `waveform_frames`
      只是把这个坏工作区
      原样保留了下来
    - gate
      主要再把它和输入包络
      更强地绑在一起
- 因而后续 decode-side 主线应收紧为：
  - 暂停继续优先怀疑
    `gate / OLA`
  - 优先定位
    `waveform_frames`
    之前的
    handoff / projector collapse

## 一、命令
```powershell
.\python.exe manage.py analyze-offline-mvp-teacher-first-vc-waveform-handoff `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --input-audio data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav `
  --input-audio data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe `
  --device cpu `
  --chunk-ms 33.333333
```

## 二、主要产物
- 汇总：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe/teacher_first_vc_waveform_handoff_probe.json`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe/teacher_first_vc_waveform_handoff_probe.md`
- 每个 case：
  - `decoded.wav`
  - `waveform_handoff_probe/waveform_frame_logits_stitched.wav`
  - `waveform_handoff_probe/waveform_frames_stitched.wav`
  - `waveform_handoff_probe/decoded_no_gate.wav`
  - `waveform_handoff_probe/decoded_pre_ola_gate.wav`
  - `waveform_handoff_probe/decoded_post_ola_gate.wav`
  - `waveform_handoff_probe/teacher_first_vc_waveform_handoff_tensors.pt`

## 三、aggregate 结果

### 1. stage 侧
- `waveform_frame_logits_template_cosine_mean = 0.999641`
- `waveform_frames_template_cosine_mean = 0.999597`
- `logits_to_frames_template_cosine_gap = -0.000044`
- `waveform_frame_logits_adjacent_cosine_mean = 0.999987`
- `waveform_frames_adjacent_cosine_mean = 0.999986`
- `waveform_frame_logits_fraction_abs_ge_1 = 0.068172`

### 2. route 侧
- `decoded_no_gate`
  - `decoded_frame_template_cosine_mean = 0.99358`
  - `predicted_activity_to_decoded_frame_rms_corr = -0.049617`
  - `decoded_spectral_centroid_hz = 6852.941895`
  - `decoded_spectral_high_band_energy_ratio = 0.391782`
- `decoded_pre_ola_gate`
  - `decoded_frame_template_cosine_mean = 0.988782`
  - `predicted_activity_to_decoded_frame_rms_corr = 0.989237`
  - `decoded_spectral_centroid_hz = 6786.922363`
  - `decoded_spectral_high_band_energy_ratio = 0.387961`
- `decoded_post_ola_gate`
  - `decoded_frame_template_cosine_mean = 0.990762`
  - `predicted_activity_to_decoded_frame_rms_corr = 0.989282`
  - `decoded_spectral_centroid_hz = 6778.623047`
  - `decoded_spectral_high_band_energy_ratio = 0.387314`

### 3. probe diagnosis
- `likely_failure_already_present_by_frames_before_gate = true`
- `pre_ola_vs_no_gate_template_delta = -0.004798`
- `post_ola_vs_no_gate_template_delta = -0.002818`
- `post_ola_vs_no_gate_high_band_delta = -0.004468`
- `post_ola_vs_no_gate_centroid_hz_delta = -74.318848`

## 四、三条样本逐条读法

### 1. `segment_0001_0000020110_0000021640`
- stage：
  - `waveform_frame_logits_template_cosine_mean = 0.999496`
  - `waveform_frames_template_cosine_mean = 0.999436`
- route：
  - `decoded_no_gate`
    template `0.994681`
  - `decoded_post_ola_gate`
    template `0.992243`
- 解读：
  - gate 没把它明显再推坏，
    只是把 RMS
    改成更强地跟 predicted activity 走

### 2. `segment_0061_0000300400_0000300910`
- stage：
  - `waveform_frame_logits_template_cosine_mean = 0.999642`
  - `waveform_frames_template_cosine_mean = 0.999595`
- route：
  - `decoded_no_gate`
    centroid `6962.67 Hz`
    high_band `0.395736`
  - `decoded_post_ola_gate`
    centroid `6797.32 Hz`
    high_band `0.385441`
- 解读：
  - 这是三条里
    gate 介入后
    brightness 回落最明显的一条，
    但即使不加 gate
    本体也已经是坏 buzz

### 3. `peak_011_0002370615_top_peak`
- stage：
  - `waveform_frame_logits_template_cosine_mean = 0.999784`
  - `waveform_frames_template_cosine_mean = 0.999759`
- route：
  - `decoded_no_gate`
    template `0.995898`
  - `decoded_post_ola_gate`
    template `0.99477`
- 解读：
  - 连 peak case
    也没有出现
    “gate off 明显正常、gate on 才坏”
    的分叉

## 五、工程判断
- 这批结果最重要的不是：
  - `pre_ola`
    还是
    `post_ola`
    略好一点
- 而是：
  - `logits`
    已经接近固定模板
  - `frames`
    继续保持这个固定模板
  - `decoded_no_gate`
    已经是高 centroid /
    高 high-band /
    高 template 的坏波形
- 所以当前更准确的分层结论应是：
  1. `gate`
     主要负责把坏模板
     更强地贴到输入包络
  2. 但坏模板本身
     不是 gate 才创造出来的
  3. 真正更上游的病灶
     在：
     - `waveform_frame_logits`
     - `waveform_frames`
     - 或它们之前的 projector / handoff source

## 六、对下一步的影响
1. 不再优先继续做：
   - `pre_overlap_add` vs `post_ola_envelope`
   - gate smoothing / floor
   - OLA 语义微调
2. 后续若继续 decode-side，
   应优先看：
   - 为什么 user-line scaffold
     会把同一个 Stage5 checkpoint
     直接推入
     `waveform_frame_logits`
     的固定模板区
   - 也就是：
     - handoff source
     - projector operating region
     - checkpoint 对 user-line control payload
       的适用性边界
3. 这条 probe
   现在应作为固定回归基线保留；
   后续任何 decoder-side 修复，
   都应先和这组三样本做同口径对照，
   看它是否真的把坏相位从
   `logits / frames`
   层往前拉开。

## 一句话结论
- 固定三条 pure buzz 样本的 waveform handoff probe 已经证明：
  当前 user-line 坏相位主要不是 gate 语义层新引入，
  而是在 `waveform_frame_logits / waveform_frames` 附近就已经形成了固定模板化坏解。 
