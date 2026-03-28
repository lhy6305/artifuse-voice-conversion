# 465 Stage5 validation24 corrected-manifold scale-out report

## 结论
- 这轮把 corrected-manifold 从 `3-record` 正式扩大到了 `24-record`。
- 结果比上一轮更强，也更稳定：
  - `24-record corrected pre-handoff` 明显优于 `24-record base pre-handoff`
  - `24-record corrected finetune` 的 validation 也优于 `24-record base finetune`
  - `24-record corrected finetune` 的 handoff 指标继续优于 `24-record base finetune`
- 但最关键的结论没有变：
  - 即便在 `24-record corrected-manifold + init-finetune` 下，仍然是 `24/24 auto_reject_obvious_buzz`
  - diagnosis 仍是 `buzz_present_by_waveform_frames_before_gate`
- 所以主线判断更新为：
  - corrected-manifold 不是 3-record 偶然性，它在更大子集上仍然是正确方向
  - 但它仍然只能把 fixed family 往更好的失败盆地里推，不能真正打开 route

## A. 本轮新增/变更

### code
- Stage5 dataset loop 现在支持 `--init-checkpoint`
  - [cli.py](F:/proj_dev/tmp/workdir4/src/v5vc/cli.py)
  - [offline_vocoder_training.py](F:/proj_dev/tmp/workdir4/src/v5vc/offline_vocoder_training.py)
- 初始化行为：
  - 恢复 checkpoint `model_state_dict`
  - 按 checkpoint `model_config` 还原模型结构
  - 恢复 optimizer state
  - 然后把 optimizer `lr` 显式重置成命令行传入值，避免沿用旧学习率

### data artifacts
- `24-record` student packet:
  - `reports/runtime/streaming_student_downstream_control_packet_avg_baseline24_warm6step15_validation24_round1_1/streaming_student_downstream_control_packet.json`
- student base Stage5 package:
  - `reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_validation24_round1_1/streaming_student_stage5_dataset_index.json`
- teacher counterpart Stage5 package:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_packages_teacher_validation24_counterpart_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- corrected-manifold Stage5 package:
  - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_validation24_acousticstateswap_eventzero_round1_1/streaming_student_stage5_dataset_index.json`

## B. validation24 packet status

### packet readiness
- `record_count = 24`
- `f0_ready_count = 0`
- `vuv_ready_count = 5`
- `aper_ready_count = 24`
- `energy_ready_count = 12`
- `all_records_auto_reject = true`

### note
- 这说明即便放大到 24 条，Stage3 packet 侧仍然没有自然打开 route。
- 所以这轮重点仍然是：看 corrected-manifold 是否能在 Stage5 handoff 上持续改善，而不是期待 packet 自己翻盘。

## C. validation24 pre-handoff

### base
- `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_validation24_round1_1/stage5_waveform_handoff_probe.json`
- `auto_reject = 24/24`
- `centroid_gap = 9111.987305`
- `high_band_gap = 0.677834`
- `template_cos = 0.938590`
- `adjacent_cos = 0.998455`
- `rms_corr = 0.890132`
- `fused_hidden_template = 0.958404`
- `waveform_frames_template = 0.958503`

### corrected
- `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_validation24_acousticstateswap_eventzero_round1_1/stage5_waveform_handoff_probe.json`
- `auto_reject = 24/24`
- `centroid_gap = 8944.391602`
- `high_band_gap = 0.675128`
- `template_cos = 0.927848`
- `adjacent_cos = 0.998596`
- `rms_corr = 0.898937`
- `fused_hidden_template = 0.949010`
- `waveform_frames_template = 0.952202`

### interpretation
- corrected-manifold 在 24 条上继续保持了之前 3 条时的正确方向：
  - `centroid` 更低
  - `high_band` 更低
  - `template collapse` 更低
  - `fused_hidden template` 更低
  - `rms_corr` 更高
- 这已经能排除“3-record 只是偶然挑中了有利样本”的担心。

## D. validation24 init-finetune

### minimal train/val indices
- base24 train/val:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_base24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- corr24 train/val:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`

### shared setup
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- training:
  - `num_steps = 8`
  - `packages_per_step = 6`
  - `validation_interval = 4`
  - `checkpoint_interval = 4`
  - `learning_rate = 1e-4`
  - loss family unchanged from promoted checkpoint route

### finetune outputs
- base24:
  - run:
    - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_base24_round1_1/`
  - best checkpoint:
    - `step8`
  - best validation loss:
    - `1.188258`
- corr24:
  - run:
    - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_round1_1/`
  - best checkpoint:
    - `step8`
  - best validation loss:
    - `1.182152`

### interpretation
- 这次和 `3-record` 不同，corrected-manifold 在 `24-record` 上已经开始在 validation 上占优。
- 说明 corrected-manifold 不只是 handoff metrics 更顺眼，它在更大的最小训练集上也开始提供更一致的优化信号。

## E. validation24 handoff after finetune

### base finetune
- `reports/runtime/stage5_waveform_handoff_probe_finetune_base24_step8_round1_1/stage5_waveform_handoff_probe.json`
- `auto_reject = 24/24`
- `centroid_gap = 8878.956055`
- `high_band_gap = 0.664934`
- `template_cos = 0.933328`
- `adjacent_cos = 0.998368`
- `rms_corr = 0.885848`
- `fused_hidden_template = 0.958113`
- `waveform_frames_template = 0.956357`

### corrected finetune
- `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_step8_round1_1/stage5_waveform_handoff_probe.json`
- `auto_reject = 24/24`
- `centroid_gap = 8774.619141`
- `high_band_gap = 0.660415`
- `template_cos = 0.920997`
- `adjacent_cos = 0.998532`
- `rms_corr = 0.892176`
- `fused_hidden_template = 0.948296`
- `waveform_frames_template = 0.949051`

### corrected pre -> corrected finetune delta
- `template_cos: -0.006851`
- `high_band_gap: -0.014713`
- `centroid_gap: -169.772461`
- `rms_corr: -0.006761`
- `fused_hidden_template: -0.000714`

### interpretation
- corrected finetune 继续明显压低了：
  - `template collapse`
  - `high-band excess`
  - `spectral centroid gap`
  - `fused_hidden template collapse`
- 但代价是 `rms_corr` 比 corrected pre 略掉。
- 更重要的是：
  - 即使这些指标继续改善，`auto_reject` 仍然完全不松动

## F. current diagnosis
- corrected finetune diagnosis 仍然是：
  - `buzz_before_predicted_activity_gate = true`
  - `predicted_activity_gate_changes_auto_reject_status = false`
  - `tanh_is_main_new_collapse_site = false`
  - `logits_show_heavy_saturation_pressure = false`
  - `primary_localization = buzz_present_by_waveform_frames_before_gate`

### meaning
- 问题仍然不是 gate
- 也不是 tanh/logit 末端才新引入的崩坏
- 仍然是更早的 waveform-frame / fusion-side attractor 问题

## 当前更新后的判断
- corrected-manifold 路线现在已经有三个层面的正信号：
  1. `3-record pre-handoff` 优于 base
  2. `24-record pre-handoff` 仍优于 base
  3. `24-record init-finetune` 在 validation 和 handoff 上都优于 base24
- 但它仍然没有打开 route。
- 所以当前更准确的表述是：
  - corrected-manifold 是对的，但还不够
  - 现在的限制已经不是“方向不确定”，而是“还缺能跨出失败盆地的机制”

## 下一步
- 不建议再继续做同配方、同结构的短步数 corrected-manifold 微调。
- 更合理的后续只剩两类：
  1. 继续扩大 corrected-manifold 的训练集规模，做真正的 Stage5 corrected-manifold retrain / longer finetune
  2. 直接转去 fusion/decoder attractor 机制修复，因为当前 family 已经被推到更好的区域，但 still trapped in buzz basin
