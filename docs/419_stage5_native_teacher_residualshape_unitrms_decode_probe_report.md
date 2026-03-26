# 2026-03-27 Stage5 native teacher `residualshapecond shape_only_unit_rms_v1` inference-only decode probe 报告

## 结论
- 我没有直接把
  `residual_shape_branch_condition_mode = shape_only_unit_rms_v1`
  推进到 fullsplit training，
  而是先做了一个更便宜的
  inference-only route-level probe：
  - 固定使用已经稳定的
    `branch_mean_contrast_residual_v1 + residualshapecond scale=0.25`
    step24 checkpoint
  - 仅改 checkpoint `model_config`
    中的：
    - `residual_shape_branch_condition_mode`
      从
      `raw_additive_v1`
      改为
      `shape_only_unit_rms_v1`
- 结果是否定：
  - 它没有减轻
    `envelope-following`
  - 也没有降低
    heard-path template collapse
  - 相反在当前稳定 route 上，
    它把：
    - `decoded_frame_template_cosine_mean`
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    全部推向更差的方向
- 因而当前主线应保持：
  - `residual_shape_branch_condition_mode = raw_additive_v1`
  - operating region
    仍写作
    `scale = 0.25 ~ 0.5`
- 同时记录一个实现事实：
  - 这条 mode
    从随机初始化训练时，
    在最小 smoke 上
    第一步 optimizer update 之后
    就触发了
    `binary_cross_entropy` 输入越界，
    暂不值得为它单独投入训练稳定化预算

## 一、这轮为什么先做 inference-only probe
- 当前已知稳定 route 是：
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_scale = 0.25`
- 我新增了：
  - `residual_shape_branch_condition_mode`
    支持
    `shape_only_unit_rms_v1`
- 但最小训练 smoke 表明：
  - 随机初始化训练在 step1 后
    validation 路径会报：
    - `RuntimeError: all elements of input should be between 0 and 1`
  - 这说明：
    - 该 mode
      当前至少存在明显的数值稳定性风险
- 因而更合理的顺序应是：
  1. 先做 inference-only route probe
  2. 只有当 decode 方向明显更好时，
     再考虑训练稳定化

## 二、产物

### 1. checkpoint override
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_override_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_unitrmsdecode_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`

### 2. validation3 export
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_unitrmsdecode_validation3_round1_1/nores_vocoder_audio_export.json`

### 3. waveform decoder structure probe
- `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_unitrmsdecode_round1_1/stage5_waveform_decoder_structure_probe.json`

### 4. speech-emergence probe
- `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_unitrmsdecode_round1_1/stage5_speech_emergence_probe.json`

### 5. 对照基线
- `raw_additive_v1 scale=0.25` export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- `raw_additive_v1 scale=0.25` structure probe：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_round1_1/stage5_waveform_decoder_structure_probe.json`
- `raw_additive_v1 scale=0.25` speech probe：
  - `reports/runtime/stage5_speech_emergence_probe_contractv2_normfix_fusionbranchmeancontrast_residualshape_scale025_round1_1/stage5_speech_emergence_probe.json`

## 三、validation3 export 对照

### 1. buzz gate
- 基线：
  - `auto_reject_count = 0`
  - `review_required_count = 3`
- `unit_rms decode override`：
  - `auto_reject_count = 0`
  - `review_required_count = 3`
- 解读：
  - 它没有把 route 打回
    `auto_reject`
  - 但也没有出现任何额外正向突破

### 2. 三条记录
- `target::chapter3_3_firefly_162`
  - `decoded_frame_template_cosine_mean`
    - `0.981364 -> 0.981465`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `0.908384 -> 0.908462`
  - `spectral_centroid_gap_hz`
    - `4250.343184 -> 4323.979847`
  - `spectral_high_band_energy_ratio_gap`
    - `0.383631 -> 0.388935`
- `target::chapter3_3_firefly_138`
  - `decoded_frame_template_cosine_mean`
    - `0.979332 -> 0.979487`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `0.898847 -> 0.898496`
  - `spectral_centroid_gap_hz`
    - `4144.882615 -> 4219.787021`
  - `spectral_high_band_energy_ratio_gap`
    - `0.325393 -> 0.330953`
- `target::chapter3_4_firefly_106`
  - `decoded_frame_template_cosine_mean`
    - `0.970994 -> 0.971226`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `0.907293 -> 0.907065`
  - `spectral_centroid_gap_hz`
    - `4291.474083 -> 4365.052423`
  - `spectral_high_band_energy_ratio_gap`
    - `0.334355 -> 0.340002`

### 3. 读法
- 三条样本几乎全部同向恶化：
  - template collapse 略升
  - brightness 略升
  - `envelope-following`
    没有被削弱
- 因而不能把
  `shape_only_unit_rms_v1`
  解释成：
  - “在 frame-level 去掉振幅信息，
     应该自然更抗 envelope-following”

## 四、structure probe 对照
- 基线 `raw_additive_v1 scale=0.25`：
  - `fused_hidden_template_cosine_mean = 0.962289`
  - `waveform_frames_template_cosine_mean = 0.987695`
  - `decoded_frames_template_cosine_mean = 0.975636`
  - `fused_to_waveform_template_cosine_gap = 0.025406`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`
- `shape_only_unit_rms_v1`：
  - `fused_hidden_template_cosine_mean = 0.966157`
  - `waveform_frames_template_cosine_mean = 0.98883`
  - `decoded_frames_template_cosine_mean = 0.977393`
  - `fused_to_waveform_template_cosine_gap = 0.022673`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`

### 如何解读
- 这条 mode
  没有改善：
  - heard-path collapse
- 它只是把 collapse 形态
  重新向更模板化的方向推了一点
- 同时 diagnosis 没变：
  - 主病灶仍然不是一个可以靠 decoder head
    单点解释的局部问题

## 五、speech-emergence probe 对照
- 基线 `raw_additive_v1 scale=0.25`：
  - `decoded_frame_template_cosine_mean = 0.975636`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.891069`
  - `spectral_centroid_gap_hz = 4036.778076`
  - `spectral_high_band_energy_ratio_gap = 0.333024`
- `shape_only_unit_rms_v1`：
  - `decoded_frame_template_cosine_mean = 0.977393`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.904674`
  - `spectral_centroid_gap_hz = 4302.939941`
  - `spectral_high_band_energy_ratio_gap = 0.353297`

### 如何解读
- 这组 aggregate 已经足够给方向性判断：
  - template collapse 更差
  - `envelope-following`
    更差
  - brightness 更差
- 也就是说：
  - 当前 residual-shape route
    不是因为
    “残差里振幅信息太多”
    才保留住
    `envelope-following`
  - 至少用
    `unit_rms shape-only`
    这种归一化手法，
    不能把问题压下去

## 六、对当前主线的影响
1. `residual_shape_branch_condition_mode = shape_only_unit_rms_v1`
   当前可以先降级停线：
   - decode-only probe 没有正向收益
   - 训练 smoke 还暴露了明显不稳
2. 当前 Stage5 主线不变：
   - 保留
     `branch_mean_contrast_residual_v1`
   - 保留
     `raw_additive_v1 residualshapecond`
   - 继续把 operating region
     写作
     `scale = 0.25 ~ 0.5`
3. 下一步不应：
   - 围绕
     `unit_rms / shape_only`
     同族归一化做微扫
4. 更合理的下一步仍应是：
   - 在已成立的
     `raw_additive_v1 residualshapecond`
     route 上，
     继续定位并削弱
     `envelope-following`
     的真实来源

## 一句话结论
- `shape_only_unit_rms_v1`
  这条 residual-shape 归一化假设，
  在当前最强稳定 route 上
  没有方向性价值；
  它既没有减轻
  `template-collapse`
  也没有减轻
  `envelope-following`，
  当前主线应回到
  `raw_additive_v1 scale=0.25 ~ 0.5`
  继续推进。
