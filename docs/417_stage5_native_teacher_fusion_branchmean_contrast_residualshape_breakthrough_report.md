# 2026-03-26 Stage5 native teacher `branch_mean_contrast_residual_v1 + residualshapecond` 首次脱离 auto-reject 报告

## 结论
- 我先修正了一个实现事实：
  - 旧 `fused_single` 路径里，
    `use_residual_shape_branch_condition_adapter`
    之前并没有真正作用到
    `waveform_frame_logits`
  - 同时 structure probe
    也没有忠实复现这条路径
- 在把这条输出侧 handoff 真正接通后，
  corrected native-teacher fullsplit24
  第一次从：
  - `3/3 auto_reject_obvious_buzz`
  进入到：
  - `3/3 review_required`
  - `auto_reject_count = 0`
- 这不是成功，
  但它是当前 Stage5 native-teacher 主线上
  第一条真正保住“非 auto-reject”的结构候选。

## 一、这轮实际修了什么
- 代码改动：
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
- 新的真实语义是：
  - backbone 仍是
    `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = true`
  - residual-shape delta
    直接加到
    `waveform_frame_logits`
    上，
    不再只是 residual decoder family
    的旧残留接线

## 二、产物目录

### 1. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 3. validation3 真实 decoded
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### 4. structure probe
- `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_round1_1/stage5_waveform_decoder_structure_probe.md`

### 5. speech-emergence probe
- `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_round1_1/stage5_speech_emergence_probe.md`

## 三、训练与 selector
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.850578`
- `loss_waveform = 0.12429`
- `loss_stft = 0.329022`
- `loss_rms_guard = 0.097807`
- `decoded_to_target_rms_ratio = 0.967419`
- `selected_stable_late_stop = null`

### 如何解读
- 相对 `docs/415`
  的纯 `branch_mean_contrast`：
  - objective 没有更好
  - selector 也丢掉了
    `selected_stable_late_stop = step24`
- 但这轮的价值不在 selector，
  而在真实听审路由首次跨过了 conservative auto-reject gate。

## 四、validation3 真实 decoded

### 1. buzz gate
- `record_count = 3`
- `auto_reject_count = 0`
- `review_required_count = 3`
- `all_records_auto_reject = false`

### 2. 三条记录
- `target::chapter3_3_firefly_162`
  - `decoded_frame_template_cosine_mean = 0.982943`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.909131`
  - `spectral_centroid_gap_hz = 4436.175238`
  - `spectral_high_band_energy_ratio_gap = 0.397825`
- `target::chapter3_3_firefly_138`
  - `decoded_frame_template_cosine_mean = 0.981688`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.900045`
  - `spectral_centroid_gap_hz = 4320.663971`
  - `spectral_high_band_energy_ratio_gap = 0.339005`
- `target::chapter3_4_firefly_106`
  - `decoded_frame_template_cosine_mean = 0.974411`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.908863`
  - `spectral_centroid_gap_hz = 4461.012525`
  - `spectral_high_band_energy_ratio_gap = 0.347602`

## 五、probe 读数

### 1. structure probe
- baseline collapse summary：
  - `fused_hidden_template_cosine_mean = 0.964166`
  - `waveform_frames_template_cosine_mean = 0.988993`
  - `decoded_frames_template_cosine_mean = 0.978362`
  - `fused_to_waveform_template_cosine_gap = 0.024827`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`
- 相对 `docs/415`
  的纯 `branch_mean_contrast`：
  - heard-path template collapse
    已从上一条 strongest backbone
    的约 `0.989687`
    降到
    `0.978362`
  - 这说明：
    当前 route
    不是只靠 heuristic 阈值
    偶然逃过 auto-reject，
    而是确实把
    heard-path template collapse
    压低了一截

### 2. speech-emergence probe
- baseline aggregate：
  - `decoded_frame_template_cosine_mean = 0.978362`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.892581`
  - `spectral_centroid_gap_hz = 4218.044922`
  - `spectral_high_band_energy_ratio_gap = 0.346903`
- root-cause impact ranking 仍显示：
  - `conditioning_zero`
    明显最强
  - 其次是
    `noise_proxies_zero`
    与
    `event_probs_zero`
- 这说明：
  - 它不是偶然卡过 auto-reject
  - 当前 route 确实在更实质地使用 conditioning family

## 六、这条结果意味着什么
1. 当前可以正式保留：
   - `branch_mean_contrast`
     backbone
   - 输出侧
     `residual-shape` handoff
2. 但还不能宣称成功：
   - 三条样本仍全是
     `review_required`
   - `decoded_frame_rms_to_aligned_frame_rms_corr`
     仍在 `~0.90`
   - 剩余主故障仍是：
     `template-collapse + envelope-following`
3. 这条线的真正价值是：
   - 它把当前 decoder-side 候选
     从“全部 obvious buzz”
     收缩到了
     “第一次出现非 auto-reject operating region”

## 一句话结论
- 输出侧 `residual-shape` handoff
  是当前第一条值得继续保留的
  decoder-side branch-dynamics route，
  但它还只是把系统从
  `auto_reject`
  推到了
  `review_required`，
  还没有真正脱离
  `template-collapse + envelope-following`。
