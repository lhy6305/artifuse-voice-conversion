# 2026-03-27 teacher-first stage temporal coupling output-head 定位报告

## 结论
- 我没有继续做新的训练权重试错，而是先把 user-line strongest candidate 的残余 `envelope-following` 再往内部拆了一层。
- 新 probe：
  - `analyze-offline-mvp-teacher-first-vc-stage-temporal-coupling`
  - 输出目录：
    - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_stcp_fbmc_rs/`
- 当前结论已经足够明确：
  1. 剩余 acoustic-state 时间对齐的主放大点，不在
     `noise_hidden -> branch_mean -> fused -> decoder_hidden`
     这条上游链路。
  2. 三个 control 家族里，最大的绝对零延迟耦合跳变都落在：
     - `decoder_hidden -> waveform_decoder_base_logits`
  3. 再把 output head 拆成 `base_logits` 与 `residual_shape_delta` 后可以更准确地写成：
     - `aper` / `aper*noise_E` 的主 jump 更像是 raw waveform head 自身带出来的
     - `noise_E_log_rms_norm` 的峰值则更高地落在 `waveform_residual_shape_delta`
  4. 因而当前下一步主线不该再回到：
     - fusion regularizer
     - output-side `frame_rms` corrreg
     - 或 `decoder_hidden` 前的局部小修
  5. 下一步应直接转向：
     - output head / residual-shape injection interface
     - 也就是 `waveform_decoder(decoder_hidden)` 与 `residual_shape_branch_condition_delta`
       这两个子阶段的结构约束或训练目标

## 一、这轮新增的 probe
- 代码入口：
  - `src/v5vc/teacher_first_vc_demo.py`
  - `src/v5vc/cli.py`
- 新命令：
  - `analyze-offline-mvp-teacher-first-vc-stage-temporal-coupling`
- 诊断口径：
  - source scaffold 的 noise-family controls：
    - `aper`
    - `noise_E_log_rms_norm`
    - `aper * noise_E_log_rms_norm`
  - 对比对象：
    - `noise_hidden frame_rms`
    - `branch_mean_hidden frame_rms`
    - `fused_hidden frame_rms`
    - `decoder_hidden frame_rms`
    - `waveform_decoder_base_logits frame_rms`
    - `waveform_residual_shape_delta frame_rms`
    - `waveform_frame_logits frame_rms`
    - `waveform_frames frame_rms`
    - `decoded_no_gate frame_rms`
- 关键实现细节：
  - 诊断主要看：
    - `abs_zero_lag_corr`
    - `abs_zero_minus_best_abs_nonzero_corr`
  - 原因是 `noise_E` 在不同样本上会有符号翻转，直接看 signed corr 会误判放大点。

## 二、运行对象
- 输入样本：
  - fixed pure buzz triplet
- checkpoint：
  - `branch_mean_contrast_residual_v1 + residualshapecond`
  - selector：
    - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - `selection_target = best_validation`

## 三、聚合结果

### 1. `aper`
- upstream：
  - `noise_hidden abs_zero_lag = 0.739391`
  - `branch_mean abs_zero_lag = 0.748764`
  - `fused / decoder_hidden abs_zero_lag = 0.712963`
- output head：
  - `waveform_decoder_base_logits abs_zero_lag = 0.877875`
  - `waveform_residual_shape_delta abs_zero_lag = 0.728842`
  - `waveform_frame_logits abs_zero_lag = 0.876952`
- 最大 jump：
  - `decoder_hidden -> waveform_decoder_base_logits = +0.164912`
- 读法：
  - `aper` 的残余时间对齐主 jump
    不是 residual-shape delta 新加出来的，
    而是 raw waveform head 自身就已经把它放大了。

### 2. `noise_E_log_rms_norm`
- upstream：
  - `noise_hidden abs_zero_lag = 0.847913`
  - `branch_mean abs_zero_lag = 0.774020`
  - `fused / decoder_hidden abs_zero_lag = 0.714462`
- output head：
  - `waveform_decoder_base_logits abs_zero_lag = 0.951540`
  - `waveform_residual_shape_delta abs_zero_lag = 0.986067`
  - `waveform_frame_logits abs_zero_lag = 0.943529`
- 最大 jump：
  - `decoder_hidden -> waveform_decoder_base_logits = +0.237078`
- 峰值：
  - `waveform_residual_shape_delta = 0.986067`
- 读法：
  - `noise_E` 的主 jump 先在 raw waveform head 出现，
    但最大峰值是在 residual-shape delta 里被进一步顶高。
  - 这说明 output head 与 residual-shape 支路都在消费 `noise_E`，
    但 residual-shape 支路对它更敏感。

### 3. `aper * noise_E_log_rms_norm`
- upstream：
  - `noise_hidden abs_zero_lag = 0.294070`
  - `branch_mean abs_zero_lag = 0.354007`
  - `fused / decoder_hidden abs_zero_lag = 0.339522`
- output head：
  - `waveform_decoder_base_logits abs_zero_lag = 0.411101`
  - `waveform_residual_shape_delta abs_zero_lag = 0.369589`
  - `waveform_frame_logits abs_zero_lag = 0.407530`
- 最大 jump：
  - `decoder_hidden -> waveform_decoder_base_logits = +0.071579`
- 读法：
  - 乘积项也延续同一方向，
    只是量级弱于单独的 `aper` 和 `noise_E`。

## 四、方向更新
- 现在不能再把剩余故障的主要落点写成：
  - `fusion` 残留
  - `decoder_hidden manifold` 自身继续塌
  - 或最终输出上的 `frame_rms` corrreg 不够强
- 更准确的主线应更新为：
  - 当前 strongest candidate 剩余的 residual `envelope-following`
    已主要收缩到
    `output head / residual-shape injection`
    这个接口
- 因此下一步应优先研究：
  - 如何限制 `waveform_decoder_base_logits`
    对 `aper / noise_E`
    的即时时间对齐放大
  - 以及如何限制
    `residual_shape_branch_condition_delta`
    对 `noise_E`
    的进一步峰值放大

## 一句话结论
- strongest candidate 上，剩余 acoustic-state 时间对齐的主放大点已经从上游 fusion 链收缩到 output head 边界：`aper / aper*noise_E` 更像 raw waveform head 在放大，`noise_E` 则在 residual-shape delta 上达到峰值。
