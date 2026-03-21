# 2026-03-20 Stage5 `step72__decode_gate_smooth3_postenv` 扩样验证与待审主分支固化报告

## 结论
- 当前 `postenv` 方向在 `validation3` 与 `validation12` 上都保持与先导观察同向。
- 相比当前默认导出主线
  `step72__decode_gate_smooth3`，
  `step72__decode_gate_smooth3_postenv`
  在 `validation12` aggregate 上同时改善：
  - fragmentation
  - alignment
  - waveform RMS leakage
  - sample delta peak
  - spectral centroid / bandwidth / HF ratio gap
- 当前只有
  `spectral_rolloff95_gap_hz`
  小幅变差，
  且 `top windows`
  中只有
  `1 / 12`
  个窗口判给旧分支，
  其余
  `11 / 12`
  都支持
  `postenv`。
- 因此当前最合理的工程动作不是立即改写全局默认，
  而是：
  1. 把
     `step72__decode_gate_smooth3_postenv`
     固化为下一轮待审主分支
  2. 补齐
     `validation12`
     GUI 听审入口
  3. 待人耳复核不反转后，
     再决定是否升级为新的默认 decode-side apply mode

## 背景
- `docs/235_stage5_step72_decode_gate_smooth3_default_promotion_report.md`
  已将
  `smooth3`
  固化为当前 Stage5 默认 decode-side 设置。
- 但当前代码中新增了第二层 export-side 对照：
  - `predicted_activity_gate_apply_mode = pre_overlap_add`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`
- 当前假设是：
  在保持
  `smooth3`
  不变的前提下，
  将 gate gain 从逐帧 frame 内预乘，
  改为 OLA 后包络乘法，
  可能进一步减少边界跳变，
  同时不把 leakage 拉回去。

## 本轮代码变更
- `src/v5vc/offline_vocoder_training.py`
  - `reconstruct_waveform_from_frames(...)`
    新增
    `frame_gain_apply_mode`
  - 支持：
    - `pre_overlap_add`
    - `post_ola_envelope`
- `src/v5vc/nores_vocoder_audio_export.py`
  - 新增
    `normalize_predicted_activity_gate_apply_mode(...)`
  - export manifest / notes / branch label
    全部写入 apply mode
  - `post_ola_envelope`
    分支自动追加：
    - `__decode_gate_smooth3_postenv`
- `src/v5vc/cli.py`
  - `export-offline-mvp-nores-vocoder-audio`
    新增：
    - `--predicted-activity-gate-apply-mode`

## 本轮产物

### 1. validation3 先导 probe
- export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation3_round1_1/`
- probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_postenv_validation3_round1_1/`

### 2. validation12 扩样 probe
- baseline smooth3 export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1/`
- postenv export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1/`
- probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_postenv_validation12_round1_1/`

## 结果

### 1. `validation3` 先导结果已同向支持 `postenv`
- branch aggregate:
  - `smooth3`
    - `mean_fragmentation_score = 1.543622`
    - `mean_waveform_rms = 0.014492`
    - `mean_sample_delta_peak = 0.077360`
    - `mean_activity_alignment_mae = 0.574888`
  - `smooth3_postenv`
    - `1.376959`
    - `0.013942`
    - `0.069730`
    - `0.570868`
- `top windows`
  统计：
  - `postenv` 最优：
    `9 / 12`
  - `postenv` 最差：
    `3 / 12`
- 这
  `3`
  个逆向窗口里，
  有
  `2`
  个只是 utterance 起点极短窗口，
  `delta_fragmentation_score`
  量级仅
  `1e-5 ~ 1e-4`，
  没有形成真正反转。

### 2. `validation12` 扩样后仍然同向
- `smooth3`
  aggregate:
  - `mean_fragmentation_score = 1.196807`
  - `mean_activity_alignment_mae = 0.550197`
  - `mean_waveform_rms = 0.014613`
  - `mean_sample_delta_peak = 0.079572`
  - `mean_spectral_centroid_gap_hz = 2063.073882`
  - `mean_spectral_bandwidth_gap_hz = 3881.181621`
  - `mean_spectral_rolloff95_gap_hz = 18094.181108`
  - `mean_spectral_hf_ratio_gap = 0.077030`
- `smooth3_postenv`
  aggregate:
  - `1.155091`
  - `0.548987`
  - `0.014128`
  - `0.071058`
  - `1876.026962`
  - `3662.607611`
  - `18259.938702`
  - `0.065086`
- 即：
  - fragmentation
    `-0.041716`
  - alignment MAE
    `-0.001210`
  - waveform RMS
    `-0.000485`
  - sample delta peak
    `-0.008514`
  - centroid gap
    `-187.046920 Hz`
  - bandwidth gap
    `-218.574010 Hz`
  - HF ratio gap
    `-0.011944`
  - 只有
    `rolloff95 gap`
    `+165.757594 Hz`
    小幅变差

### 3. `validation12 top windows` 没有反转
- `postenv` 最优：
  `11 / 12`
- `postenv` 最差：
  `1 / 12`
- 唯一逆向窗口：
  - `target::chapter3_26_firefly_107`
  - `segment_index = 0`
  - `delta_fragmentation_score = 0.001226`
- 这说明：
  当前不是“少数大窗口换来 aggregate 假改善”，
  而是绝大多数重点窗口仍支持
  `postenv`。

## 当前判断
- 当前量化证据已经足够把
  `step72__decode_gate_smooth3_postenv`
  固化成下一轮待审主分支。
- 但它还没有经过 focused human audit，
  所以当前不应直接把
  `post_ola_envelope`
  升成新的全局默认 apply mode。
- 更准确的口径应是：
  - 当前默认 decode 仍是
    `smooth3`
  - 当前待审主分支改为
    `smooth3_postenv`

## GUI 听审交付

### 1. 听审脚本
- `scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1`

### 2. 对应 CLI 命令
```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle `
  reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_postenv_validation12_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3 `
  reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_postenv_validation12_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3_postenv `
  --output-dir `
  reports/audio/audio_audit_gui_stage5_step72_glitch_smooth3_postenv_validation12_session
```

### 3. 本轮主对比目标
- `step72__decode_gate_smooth3`
  vs
  `step72__decode_gate_smooth3_postenv`

### 4. 本轮试听重点
- 局部边界毛刺是否继续减少
- 清辅音渐变与呼吸声是否更平滑
- 低活动段 leakage 是否没有明显回升
- 整体听感是否比当前默认
  `smooth3`
  更稳定

## 一句话结论
- `postenv`
  在
  `validation3`
  和
  `validation12`
  上都继续同向优于当前
  `smooth3`
  主线，
  所以下一棒应该进入
  `smooth3_postenv`
  的 focused human audit，
  而不是停留在代码里但没有正式交付入口。
