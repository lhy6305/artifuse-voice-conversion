# 454 Stage5 streaming student handoff probe: baseline24 vs warm6 step15

## 结论
- 对 `vuvbalancedgate24` 和 `warm6_18.step15` 做了同口径 Stage5 fail-fast waveform handoff 对照。
- 结果没有打开 Stage5 主线：
  - 两条 student 路线在 `3 records x 3 decode routes` 下全部仍是 `auto_reject_obvious_buzz`
  - `warm6_18.step15` 相比 `vuvbalancedgate24` 只有很弱的 mixed signal，没有形成明确 downstream 改善
- 因此当前主线状态保持不变：
  - packet-facing reference 仍为 `vuvbalancedgate24`
  - `warm6_18.step15` 仍只算 packet-aware next-best candidate，不进入 Stage5 handoff 主线

## 试验设置
- Stage5 checkpoint family：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - `selection_target = best_validation`
  - 实际解析到的 checkpoint：
    - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- Student Stage5 synthetic dataset：
  - baseline24:
    - `reports/runtime/streaming_student_stage5_dataset_packages_vuvbalancedgate24_contractv2_normfix_validation3_round1_1/`
  - warm6 step15:
    - `reports/runtime/streaming_student_stage5_dataset_packages_timingfocus6warm_baseline18_step15_contractv2_normfix_validation3_round1_1/`
- Stage5 handoff probe 输出：
  - baseline24:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_vuvbalancedgate24_contractv2_normfix_validation3_round1_1/`
  - warm6 step15:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_timingfocus6warm_baseline18_step15_contractv2_normfix_validation3_round1_1/`
- 说明：
  - 旧 `contractv2_normfix` dataset index 没显式记录 `semantic_consumer_mode / target_contract_mode`
  - 本轮按当前 handoff 代码默认值构建：
    - `semantic_consumer_mode = none`
    - `target_contract_mode = legacy_proxy`
    - `noise_event_family = e_evt`
  - synthetic package 构建成功，说明这条合同在当前 Stage5 family 上至少是结构兼容的

## A. 总体判断
- 两条路线在所有 route 上都没有通过 buzz reject：
  - `decoded_no_gate`
  - `decoded_pre_ola_gate`
  - `decoded_post_ola_gate`
- 所以从最重要的 fail-fast 口径看，这轮结果是：
  - `baseline24`: no-go
  - `warm6 step15`: 仍然 no-go

## B. `decoded_post_ola_gate` 主听感路线对比
- `vuvbalancedgate24`
  - `auto_reject_count = 3/3`
  - `centroid_hz = 10171.926`
  - `high_band_energy_ratio = 0.752118`
  - `decoded_frame_template_cosine_mean = 0.942398`
  - `decoded_frame_adjacent_cosine_mean = 0.997326`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.893369`
  - `decoded_frame_rms_cv = 0.197239`
- `warm6_18.step15`
  - `auto_reject_count = 3/3`
  - `centroid_hz = 10168.383`
  - `high_band_energy_ratio = 0.752909`
  - `decoded_frame_template_cosine_mean = 0.945929`
  - `decoded_frame_adjacent_cosine_mean = 0.997283`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.910440`
  - `decoded_frame_rms_cv = 0.193378`

## C. baseline24 -> warm6 step15 的变化
- 有利变化：
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `+0.017071`
  - `decoded_frame_rms_cv`
    - `-0.003861`
  - `decoded_spectral_centroid_hz`
    - `-3.543`
- 不利变化：
  - `high_band_energy_ratio`
    - `+0.000791`
  - `decoded_frame_template_cosine_mean`
    - `+0.003531`
- 解读：
  - candidate 确实让 envelope 跟随对齐目标更紧了一点
  - 但同时也让短时模板化程度更高，且高频能量比没有改善
  - 这仍然落在 Stage5 obvious buzz / template-collapse 失败族里

## D. hidden handoff aggregate 对比
- `branch_mean_hidden_template_cosine_mean`
  - baseline24: `0.965944`
  - warm6 step15: `0.967939`
- `decoder_hidden_template_cosine_mean`
  - baseline24: `0.961636`
  - warm6 step15: `0.965892`
- `decoder_hidden_frame_rms_mean`
  - baseline24: `0.757870`
  - warm6 step15: `0.759056`
- `decoder_hidden_frame_rms_cv`
  - baseline24: `0.010727`
  - warm6 step15: `0.008991`
- `decoder_hidden_frame_delta_abs_mean`
  - baseline24: `0.008395`
  - warm6 step15: `0.008694`

## E. 代表记录观察
- `target::chapter3_3_firefly_162`
  - post-OLA route:
    - baseline24:
      - `centroid = 9987.418`
      - `high_band = 0.735699`
      - `template_cos = 0.953881`
      - `rms_corr = 0.909408`
    - warm6 step15:
      - `centroid = 9975.027`
      - `high_band = 0.735492`
      - `template_cos = 0.954897`
      - `rms_corr = 0.924303`
- `target::chapter3_3_firefly_138`
  - post-OLA route:
    - baseline24:
      - `centroid = 10173.639`
      - `high_band = 0.752971`
      - `template_cos = 0.948788`
      - `rms_corr = 0.883382`
    - warm6 step15:
      - `centroid = 10167.232`
      - `high_band = 0.753694`
      - `template_cos = 0.951893`
      - `rms_corr = 0.904614`
- `target::chapter3_4_firefly_106`
  - post-OLA route:
    - baseline24:
      - `centroid = 10354.720`
      - `high_band = 0.767684`
      - `template_cos = 0.924525`
      - `rms_corr = 0.887316`
    - warm6 step15:
      - `centroid = 10362.889`
      - `high_band = 0.769540`
      - `template_cos = 0.930997`
      - `rms_corr = 0.902403`

## 最终判断
- `warm6_18.step15` 的改进只停留在：
  - packet cheap screen 比 `warm6_18.step18` 更稳
  - Stage5 handoff 上某些 envelope-following 信号略好
- 但它没有解决真正决定去留的两个问题：
  - `all routes auto reject`
  - `template-collapse / high-band harsh buzz` 仍未脱离失败族
- 所以下一步不该把这条 checkpoint 送进 Stage5 主线，而应继续留在 Stage3 / packet-facing 校准侧收窄
