# 2026-03-27 Stage5 native teacher `residualshapecond` decode-time ablation probe 报告

## 结论
- 在 `docs/419`
  已经否掉
  `shape_only_unit_rms_v1`
  之后，
  我继续做了一个更直接的归因实验：
  - 固定使用已经稳定的
    `branch_mean_contrast_residual_v1 + raw_additive_v1 residualshapecond scale=0.25`
    step24 checkpoint
  - 仅在 decode 时把：
    - `residual_shape_branch_condition_scale`
      改成
      `0.0`
  - 不改任何训练权重
- 结果说明：
  - 当前这条 route
    首次离开 `auto_reject`
    的收益，
    不是主要靠
    “decode-time 这点 residual-shape additive delta”
    在单独撑着
  - 把它当场 ablate 掉以后，
    route 仍然保持：
    - `3/3 review_required`
  - 而且 brightness / template-collapse
    还出现了非常轻微的改善；
    但
    `decoded_frame_rms_to_aligned_frame_rms_corr`
    并没有改善，
    反而略差
- 因而当前更准确的口径应改成：
  - `residualshapecond`
    的价值更像
    training-time handoff shaping
  - 而不是当前 inference-time additive delta
    本身还在持续提供主要收益
- 下一步不应：
  - 围绕
    decode-time residual-shape gain
    做更多微扫
  - 也不应把
    `scale = 0.25`
    这点 decode 增量，
    误写成当前 `review_required`
    operating region 的主承载项

## 一、实验设计
- 基线 checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- ablation checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_override_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale000_decodeablate_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- 唯一修改：
  - `model_config["residual_shape_branch_condition_scale"] = 0.0`
- 为避免旧 probe 文件与当前代码口径混比，
  我还补跑了一个当前代码下的 raw baseline refresh：
  - export：
    - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_refresh_validation3_round1_1/nores_vocoder_audio_export.json`
  - structure probe：
    - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_refresh_round1_1/stage5_waveform_decoder_structure_probe.json`
  - speech-emergence probe：
    - `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_refresh_round1_1/stage5_speech_emergence_probe.json`

## 二、产物

### 1. decode-time ablation export
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale000_decodeablate_validation3_round1_1/nores_vocoder_audio_export.json`

### 2. decode-time ablation structure probe
- `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale000_decodeablate_round1_1/stage5_waveform_decoder_structure_probe.json`

### 3. decode-time ablation speech-emergence probe
- `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale000_decodeablate_round1_1/stage5_speech_emergence_probe.json`

## 三、validation3 export：refresh 基线 vs scale0 decode ablation

### 1. buzz gate
- refresh baseline：
  - `auto_reject_count = 0`
  - `review_required_count = 3`
- `scale = 0.0 decode ablation`：
  - `auto_reject_count = 0`
  - `review_required_count = 3`

### 2. 三条记录
- `target::chapter3_3_firefly_162`
  - `decoded_frame_template_cosine_mean`
    - `0.981364 -> 0.981346`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `0.908384 -> 0.908324`
  - `spectral_centroid_gap_hz`
    - `4250.343184 -> 4215.047212`
  - `spectral_high_band_energy_ratio_gap`
    - `0.383631 -> 0.380826`
- `target::chapter3_3_firefly_138`
  - `decoded_frame_template_cosine_mean`
    - `0.979332 -> 0.979291`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `0.898847 -> 0.899027`
  - `spectral_centroid_gap_hz`
    - `4144.882615 -> 4109.825451`
  - `spectral_high_band_energy_ratio_gap`
    - `0.325393 -> 0.322483`
- `target::chapter3_4_firefly_106`
  - `decoded_frame_template_cosine_mean`
    - `0.970994 -> 0.970935`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `0.907293 -> 0.907404`
  - `spectral_centroid_gap_hz`
    - `4291.474083 -> 4257.488831`
  - `spectral_high_band_energy_ratio_gap`
    - `0.334355 -> 0.331408`

### 3. 读法
- 这不是大幅改善，
  但足够说明：
  - 当前 decode-time residual-shape delta
    被拿掉以后，
    route 没有塌回
    `auto_reject`
  - brightness / template-collapse
    甚至还略微更低
- 同时：
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    没有出现明确下降，
    基本持平略差
- 因而剩余主病灶仍然是：
  - `envelope-following`

## 四、structure probe：refresh 基线 vs scale0 decode ablation
- refresh baseline：
  - `fused_hidden_template_cosine_mean = 0.966157`
  - `waveform_frames_template_cosine_mean = 0.988883`
  - `decoded_frames_template_cosine_mean = 0.97723`
  - `fused_to_waveform_template_cosine_gap = 0.022726`
- `scale = 0.0 decode ablation`：
  - `fused_hidden_template_cosine_mean = 0.966157`
  - `waveform_frames_template_cosine_mean = 0.98892`
  - `decoded_frames_template_cosine_mean = 0.977191`
  - `fused_to_waveform_template_cosine_gap = 0.022763`

### 如何解读
- `fused_hidden`
  完全不变，
  说明这次对照确实只是在看 decode-time additive delta，
  没有碰训练出来的 backbone。
- heard-path collapse
  只发生了极小变化：
  - `decoded_frames_template_cosine_mean`
    还略低一点
- 这再次说明：
  - 当前 `review_required`
    operating region
    不是被这点 inference-time additive delta
    单独扛住的

## 五、speech-emergence probe：refresh 基线 vs scale0 decode ablation
- refresh baseline：
  - `decoded_frame_template_cosine_mean = 0.97723`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.904841`
  - `spectral_centroid_gap_hz = 4228.900391`
  - `spectral_high_band_energy_ratio_gap = 0.347793`
- `scale = 0.0 decode ablation`：
  - `decoded_frame_template_cosine_mean = 0.977191`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.904918`
  - `spectral_centroid_gap_hz = 4194.120605`
  - `spectral_high_band_energy_ratio_gap = 0.344906`

### 如何解读
- brightness 与 collapse
  都是极轻微地更好：
  - `template`
    `0.97723 -> 0.977191`
  - `centroid_gap`
    `4228.900391 -> 4194.120605`
  - `high_band_gap`
    `0.347793 -> 0.344906`
- 但
  `decoded_frame_rms_to_aligned_frame_rms_corr`
  反而：
  - `0.904841 -> 0.904918`
- 因而这条对照不能支持：
  - “继续提高 decode-time residual-shape gain
     会更接近解决 envelope-following”

## 六、对当前主线的影响
1. 当前 `residualshapecond`
   的主要价值，
   更应解释为：
   - training-time handoff shaping
   - 它改变了训练出来的 backbone / decoder operating region
2. 当前不应再把焦点放在：
   - decode-time residual-shape gain 调节
   - `scale = 0.25` 和 `scale = 0.0`
     之间做更多小扫
3. 当前更值得做的事是：
   - 直接研究
     residual-shape handoff
     在训练时
     到底把哪一层语义塑形了
   - 尤其是：
     为什么 brightness / template-collapse
     已经被压下一截，
     但 `envelope-following`
     仍然残留

## 一句话结论
- 把当前 route 的
  decode-time residual-shape additive delta
  直接切到 `0.0`，
  并不会把系统打回
  `auto_reject`；
  这说明当前 `residualshapecond`
  的收益，
  主要不是 inference-time 这点增量本身，
  而更像训练期对 handoff / decoder operating region
  的塑形结果。
