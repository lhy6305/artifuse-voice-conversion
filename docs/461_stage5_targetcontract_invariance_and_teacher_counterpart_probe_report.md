# 461 Stage5 target-contract invariance and teacher counterpart probe

## 结论
- `target_contract_mode` 不是当前 fixed Stage5 handoff 的有效自由度。
  - 在同一个 averaged student packet、同一个 Stage5 checkpoint、同一个 `validation3` 上，把 synthetic package 从 `legacy_proxy` 改成
    - `v2core_aper_energy_only_v1`
    - `teacher_e_evt_gate_targets_v1`
  - 最终 handoff 指标逐项一致，`decoded_post_ola_gate` 和 hidden collapse 指标都没有任何变化。
- 原因已经明确。
  - `target_contract_mode` 只改 package 内的 `periodic_gate_target / noise_gate_target` 监督目标。
  - 当前 `analyze-stage5-nores-waveform-handoff` 在 fixed checkpoint 推理时只消费 package `inputs`，不消费这些 target supervision。
  - 所以不重训 Stage5 的前提下，改 `target_contract_mode` 不可能改变 handoff 结果。
- teacher counterpart 对照说明 student 输入流形确实会把同一个 Stage5 ckpt 往更坏 attractor 推一点，但不是唯一根因。
  - teacher package 和 student package 在同一 ckpt 下都还是 `3/3 auto_reject_obvious_buzz`
  - 但 teacher aggregate hidden/template collapse 略轻，说明 student synthetic contract/input manifold 确实有负贡献
  - 同时 teacher route 自己也没过关，说明当前 ckpt 本体也仍然带着强 collapse/buzz 问题

## 实验对象
- student averaged candidate:
  - `reports/runtime/streaming_student_downstream_control_packet_avg_baseline24_warm6step15_round1_2/streaming_student_downstream_control_packet.json`
- fixed Stage5 checkpoint family:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - `selection_target = best_validation`
- shared comparison records:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

## A. target_contract_mode invariance probe

### built synthetic datasets
- `v2core_aper_energy_only_v1`
  - dataset:
    - `reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_v2coreaperenergy_validation3_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_v2coreaperenergy_validation3_round1_1/stage5_waveform_handoff_probe.json`
- `teacher_e_evt_gate_targets_v1`
  - dataset:
    - `reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_teachereevtgates_validation3_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_teachereevtgates_validation3_round1_1/stage5_waveform_handoff_probe.json`

### package metadata check
- `v2core_aper_energy_only_v1`
  - `contract_family = v2core_aper_energy_only_v1`
  - `periodic_gate_formula = vuv`
  - `noise_gate_formula = aper * E_log_rms_norm`
- `teacher_e_evt_gate_targets_v1`
  - `contract_family = teacher_e_evt_gate_targets_v1`
  - `periodic_gate_formula = max(vuv, p_voicing)`
  - `noise_gate_formula = max(aper * E_log_rms_norm, max(max(p_frication, p_stop_closure, p_burst, a_aper), max(p_pause_boundary, p_terminal_boundary) * max(aper, E_log_rms_norm)))`

### handoff aggregate
- base `legacy_proxy`:
  - `auto_reject = 3/3`
  - `centroid_gap = 9278.554688`
  - `high_band_gap = 0.712497`
  - `template_cos = 0.943517`
  - `adjacent_cos = 0.997297`
  - `rms_corr = 0.900798`
  - `fused_hidden_template = 0.963773`
  - `decoder_hidden_template = 0.963773`
  - `waveform_frames_template = 0.962746`
- `v2core_aper_energy_only_v1`:
  - 与 base 逐项一致
- `teacher_e_evt_gate_targets_v1`:
  - 与 base 逐项一致

### 结论
- 这不是“两个替代合同都失败了”，而是“这两个合同根本没有进入 fixed handoff 的推理路径”。
- 代码层证据也一致：
  - `offline_vocoder_training.py` 已明确说明
    - `target_contract_mode controls how Stage5 periodic_gate_target / noise_gate_target are built inside each package; this is the supervision-side contract, not another input-side semantic consumer.`
  - `stage5_waveform_handoff_probe.py` 只从 package 读取 `periodic_branch_features / noise_branch_features` 做 forward，然后分析 hidden/logits/frames/waveform routes。

## B. teacher counterpart probe

### counterpart dataset
- subset split:
  - `tmp/stage5_teacher_handoff_validation3_subset.jsonl`
- teacher Stage5 dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_packages_teacher_validation3_counterpart_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- teacher handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_teacher_validation3_counterpart_round1_1/stage5_waveform_handoff_probe.json`

### aggregate comparison
- student averaged package:
  - `auto_reject = 3/3`
  - `centroid_gap = 9278.554688`
  - `high_band_gap = 0.712497`
  - `template_cos = 0.943517`
  - `adjacent_cos = 0.997297`
  - `rms_corr = 0.900798`
  - `branch_mean_hidden_template = 0.966703`
  - `fused_hidden_template = 0.963773`
  - `decoder_hidden_template = 0.963773`
  - `waveform_frames_template = 0.962746`
- teacher counterpart package:
  - `auto_reject = 3/3`
  - `centroid_gap = 9266.612305`
  - `high_band_gap = 0.713724`
  - `template_cos = 0.941868`
  - `adjacent_cos = 0.997561`
  - `rms_corr = 0.893252`
  - `branch_mean_hidden_template = 0.963507`
  - `fused_hidden_template = 0.957539`
  - `decoder_hidden_template = 0.957539`
  - `waveform_frames_template = 0.960643`

### per-record post-OLA comparison
- `target::chapter3_3_firefly_162`
  - student:
    - `template = 0.954066`
    - `rms_corr = 0.916301`
    - `high_band_gap = 0.731653`
    - `centroid_gap = 9146.747438`
  - teacher:
    - `template = 0.953127`
    - `rms_corr = 0.899185`
    - `high_band_gap = 0.735297`
    - `centroid_gap = 9161.449617`
- `target::chapter3_3_firefly_138`
  - student:
    - `template = 0.949838`
    - `rms_corr = 0.892434`
    - `high_band_gap = 0.691870`
    - `centroid_gap = 9209.425496`
  - teacher:
    - `template = 0.946333`
    - `rms_corr = 0.885647`
    - `high_band_gap = 0.692539`
    - `centroid_gap = 9195.569270`
- `target::chapter3_4_firefly_106`
  - student:
    - `template = 0.926647`
    - `rms_corr = 0.893659`
    - `high_band_gap = 0.713969`
    - `centroid_gap = 9479.491314`
  - teacher:
    - `template = 0.926145`
    - `rms_corr = 0.894923`
    - `high_band_gap = 0.713336`
    - `centroid_gap = 9442.814958`

### interpretation
- teacher 对照没有打开 route。
  - diagnosis 仍是
    - `buzz_before_predicted_activity_gate = true`
    - `predicted_activity_gate_changes_auto_reject_status = false`
    - `primary_localization = buzz_present_by_waveform_frames_before_gate`
- 但 teacher aggregate 的
  - `branch_mean_hidden_template`
  - `fused_hidden_template`
  - `decoder_hidden_template`
  - `waveform_frames_template`
  都低于 student averaged package。
- 所以当前更准确的表述是：
  - Stage5 ckpt 本体仍有强 collapse attractor，teacher 路线自己也没过关
  - student synthetic contract/input manifold 会把这个 attractor 再往更坏方向推一点
  - 因此“只修 student”或者“只怪 student event/aper”都不完整

## 当前更新后的判断
- `target_contract_mode` 不是下一步主线，因为不重训 Stage5 时它不会改变 fixed handoff。
- 当前真正还值得继续的方向，是 fixed Stage5 推理实际消费到的输入流形：
  - student scaffold branch features 的 family-level / normalization-level override
  - 或更深一层的 `branch_mean_hidden -> fused_hidden` attractor 诊断
- 如果继续 root-cause isolation，优先级应改成：
  1. 直接比较 teacher vs student package 的 branch feature statistics / hidden geometry
  2. 对真正进入 forward 的 input families 做 reference-mean / affine-match / partial swap probe
  3. 只有当输入流形定位明确后，再决定是否需要新的 Stage5 retrain，而不是继续试 supervision-side contract 名字
