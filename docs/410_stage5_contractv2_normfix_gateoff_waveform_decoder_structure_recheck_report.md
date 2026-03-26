# 2026-03-26 Stage5 `contractv2_normfix` gate-off waveform decoder 结构复核报告

## 结论
- 旧 `docs/296_stage5_contractv2_normfix_waveform_decoder_structure_probe_report.md`
  使用的是 gate-on decode 语义。
- 本轮在当前 corrected baseline 的真实 gate-off 听审路由下，
  补做了同类 decoder-structure probe。
- 结果与旧结论保持一致，
  而且当前证据更硬：
  - `baseline_decoder_collapse_summary.diagnosis`
    仍是
    `collapse_not_localized_to_waveform_decoder`
  - `fused_hidden_template_cosine_mean = 0.991105`
  - `waveform_frames_template_cosine_mean = 0.999462`
  - `decoded_frames_template_cosine_mean = 0.995873`
- 当前更合理的说法是：
  - gate-off 听审路由虽然更差，
    但主坍缩点仍不在 `waveform_decoder` 单点内部
  - 更大的坍缩仍发生在
    `fusion -> fused_hidden`

## probe 入口
- 产物目录：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_gateoff_round1_1/`
- 关键摘要：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_gateoff_round1_1/stage5_waveform_decoder_structure_probe.md`
- 输入：
  - checkpoint selection：
    `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json`
  - dataset index：
    `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - split：
    `validation`
  - `sample_count = 12`
  - decode 语义：
    - `use_predicted_activity_gate = false`
    - `predicted_activity_gate_apply_mode = post_ola_envelope`

## 一、baseline 结构摘要
- `fused_hidden_template_cosine_mean = 0.991105`
- `waveform_frames_template_cosine_mean = 0.999462`
- `decoded_frames_template_cosine_mean = 0.995873`
- `fused_hidden_adjacent_cosine_mean = 0.999841`
- `waveform_frames_adjacent_cosine_mean = 0.999975`
- `fused_to_waveform_template_cosine_gap = 0.008357`
- `fused_to_waveform_adjacent_cosine_gap = 0.000056`
- 自动诊断：
  - `collapse_not_localized_to_waveform_decoder`

## 二、关键 bypass 结果

### 1. 直接用 `branch_mean / periodic_hidden / noise_hidden` 替换 `fused_hidden`
- `fused_hidden_from_branch_mean`
  - `waveform_mean_abs_delta_vs_baseline = 0.333961`
  - `decoded_template = 0.766340`
- `fused_hidden_from_periodic_hidden`
  - `waveform_mean_abs_delta_vs_baseline = 0.329319`
  - `decoded_template = 0.698365`
- `fused_hidden_from_noise_hidden`
  - `waveform_mean_abs_delta_vs_baseline = 0.317495`
  - `decoded_template = 0.786732`

这说明：
- 一旦绕过当前 `fusion`
  直接给 decoder 喂 branch-side hidden dynamics，
  输出会发生明显变化，
  而且 template 化程度会显著下降。

### 2. 仅把 branch hidden 压成 frame mean，变化很小
- `noise_hidden_frame_mean`
  - `waveform_mean_abs_delta_vs_baseline = 0.020272`
- `periodic_hidden_frame_mean`
  - `waveform_mean_abs_delta_vs_baseline = 0.018472`

这说明：
- branch 侧动态在当前 route 上
  仍有作用，
  但它们在经过 `fusion`
  之后大部分被压掉了。

### 3. `fused_hidden_frame_mean` 几乎不改变输出
- `fused_hidden_frame_mean`
  - `waveform_mean_abs_delta_vs_baseline = 0.008588`
  - `decoded_template = 0.998521`

这说明：
- gate-off 听审路由下，
  baseline 的 `fused_hidden`
  仍已经接近常模板，
  所以把它压成 frame mean
  几乎不会再带来变化。

## 三、和旧 gate-on probe 的关系
- 旧 `296`
  的方向判断是：
  - 更大的坍缩已经发生在
    `fusion -> fused_hidden`
- 本轮 gate-off 复核没有推翻这一点，
  而是把它和当前真实听审主路由重新对齐了。
- 因而当前不应把问题写成：
  - “只是 gate-off 导出更差”
  - “只要改 waveform decoder 单点结构就会自然修复”

## 四、结论口径
- 当前 corrected baseline 的真实 gate-off 听审路由下，
  仍应把主病灶优先定位在：
  - `fusion / fused_hidden`
  - 以及其后的 decode semantics 互动
- 不应默认继续：
  - decoder-only 孤立小改
  - 旧式 objective weight 小 sweep
- 下一步应更明确转向：
  - `fusion -> fused_hidden`
    为什么被压到近固定模板
  - 以及这层状态如何和 gate-off 听审路由
    一起放大当前 buzz
