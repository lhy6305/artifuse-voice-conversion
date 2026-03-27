# 2026-03-27 teacher-first 用户线 waveform handoff probe 启动与 smoke 报告

## 结论
- 已新增正式命令：
  - `analyze-offline-mvp-teacher-first-vc-waveform-handoff`
- 这条 probe
  不是训练包内分布用的
  `Stage5 waveform handoff probe`
  换皮，
  而是：
  - 专门面向
    teacher-first / single-target
    user-line case
  - 在同一条输入上
    把
    `decoder_hidden -> waveform_frame_logits -> waveform_frames -> decoded_no_gate / decoded_pre_ola_gate / decoded_post_ola_gate`
    串起来看
- 现在每个 case
  都会额外导出：
  - `waveform_frame_logits_stitched.wav`
  - `waveform_frames_stitched.wav`
  - `decoded_no_gate.wav`
  - `decoded_pre_ola_gate.wav`
  - `decoded_post_ola_gate.wav`
  - `teacher_first_vc_waveform_handoff_tensors.pt`
- 单样本 smoke
  已通过，
  且当前 smoke 的定性读法是：
  - `logits -> frames`
    的 collapse gap
    近乎为零
  - gate on/off
    主要在改包络相关性，
    并没有把频谱或模板性
    朝更坏方向再推一大截
  - 因而这条 smoke
    初步支持：
    - 当前坏相位
      更像在
      `waveform_frames`
      之前就已形成，
      而不是 export-side gate
      才新引入

## 一、为什么要补这条 probe
- 之前用户线已经确认：
  - 那组三条固定样本
    主观上仍是 pure buzz
- 但后续如果继续修 decoder-side，
  仅靠：
  - `decoded.wav`
  - 或单独切换
    gate on/off
    再听
  很难稳定回答：
  - 坏是从
    `logits`
    就开始，
  - 还是
    `tanh`
    才模板化，
  - 还是
    `OLA / gate`
    才放大
- 因而需要一个正式、固定口径的
  handoff probe，
  后续每修一层
  都能直接做同口径前后对照。

## 二、本次代码落点
- `src/v5vc/cli.py`
  - 新增命令：
    - `analyze-offline-mvp-teacher-first-vc-waveform-handoff`
- `src/v5vc/teacher_first_vc_demo.py`
  - 新增：
    - user-line waveform handoff probe 主流程
    - per-case stage 指标汇总
    - staged audio 导出
    - route aggregate / diagnosis markdown
  - 同时补了一个兼容修复：
    - `export_teacher_contract_with_stage_tracking`
      现在会继续透传
      `teacher_e_evt`
      相关新增参数，
      避免 probe
      在 teacher-contract 阶段提前报错

## 三、命令用法

### 1. 基本命令
```powershell
.\python.exe manage.py analyze-offline-mvp-teacher-first-vc-waveform-handoff `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --input-audio data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav `
  --input-audio data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe `
  --device cpu `
  --chunk-ms 33.333333
```

### 2. 主要输出
- 根目录：
  - `teacher_first_vc_waveform_handoff_probe.json`
  - `teacher_first_vc_waveform_handoff_probe.md`
- 每个 case 目录：
  - `decoded.wav`
  - `teacher_first_vc_demo.json`
  - `teacher_contract/`
  - `teacher_vocoder_input_scaffold/`
  - `waveform_handoff_probe/`
- `waveform_handoff_probe/`
  下额外包含：
  - `waveform_frame_logits_stitched.wav`
  - `waveform_frames_stitched.wav`
  - `decoded_no_gate.wav`
  - `decoded_pre_ola_gate.wav`
  - `decoded_post_ola_gate.wav`
  - `teacher_first_vc_waveform_handoff_tensors.pt`

## 四、单样本 smoke

### 1. 命令
```powershell
.\python.exe manage.py analyze-offline-mvp-teacher-first-vc-waveform-handoff `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --output-dir reports/runtime/teacher_first_vc_waveform_handoff_probe_smoke_20260327 `
  --device cpu `
  --max-audio-sec 1.0 `
  --chunk-ms 33.333333
```

### 2. 关键产物
- `reports/runtime/teacher_first_vc_waveform_handoff_probe_smoke_20260327/teacher_first_vc_waveform_handoff_probe.json`
- `reports/runtime/teacher_first_vc_waveform_handoff_probe_smoke_20260327/teacher_first_vc_waveform_handoff_probe.md`
- `reports/runtime/teacher_first_vc_waveform_handoff_probe_smoke_20260327/cases/001_segment_0001_0000020110_0000021640/waveform_handoff_probe/`

### 3. smoke 读法
- `diagnosis`
  - `logits_to_frames_template_cosine_gap = -0.00005`
  - `logits_to_frames_adjacent_cosine_gap = -0.000001`
  - `likely_failure_already_present_by_frames_before_gate = true`
- route 对比：
  - `decoded_no_gate`
    - `decoded_frame_template_cosine_mean = 0.993645`
    - `decoded_spectral_high_band_energy_ratio = 0.384545`
  - `decoded_pre_ola_gate`
    - `decoded_frame_template_cosine_mean = 0.988343`
    - `predicted_activity_to_decoded_frame_rms_corr = 0.988074`
  - `decoded_post_ola_gate`
    - `decoded_frame_template_cosine_mean = 0.991045`
    - `predicted_activity_to_decoded_frame_rms_corr = 0.988119`
- 解释：
  - `no_gate`
    已经很坏，
    说明问题不是“只有 gate 打开才出现”
  - `pre_ola / post_ola`
    主要把帧级 RMS
    强行拉回 predicted activity，
    但没有额外造成
    一个数量级的 brightness 跳变
  - 因而当前这条 smoke
    更像是在回答：
    - 先怀疑
      `frames` 之前的 collapse，
      不要先把锅扣给 export-side gate

## 五、下一步
1. 直接用这条 probe
   跑那组三条
   已确认 pure buzz
   的固定 user-line 样本。
2. 后续任何 decode-side 修复，
   默认都保留同一批 case、
   同一命令、
   同一输出目录结构做前后对照。
3. 若后续某版首次出现：
   - `logits -> frames`
     gap 明显扩大，
   - 或 `no_gate`
     明显好于
     `pre/post_ola`
   再把根因进一步收缩到：
   - `tanh`
   - 或
     `OLA / gate`
     语义层。

## 一句话结论
- 用户线现在已经有了正式的
  waveform handoff probe；
  它能把
  `logits / frames / no_gate / pre_ola / post_ola`
  用统一口径一次性导出来，
  后续可以直接拿固定 pure buzz 三样本
  做层级定位和修复回归。
