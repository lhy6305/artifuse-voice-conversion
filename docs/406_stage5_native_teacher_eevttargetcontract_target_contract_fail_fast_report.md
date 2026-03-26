# 2026-03-26 Stage5 native teacher `teacher_e_evt_gate_targets_v1` target contract fail-fast 报告

## 结论
- `target_contract_mode = teacher_e_evt_gate_targets_v1`
  已在当前 corrected native-teacher fullsplit24 主线上完成：
  - full-split package export
  - 24-step training
  - checkpoint selection
  - validation3 real decoded export
- 结果仍应立即判停：
  - `3/3 auto_reject_obvious_buzz`
  - 相对 corrected baseline 三条样本都明显更差
- 因此当前 `target_contract_mode` 家族已经在 native-teacher corrected 主线上完成封口：
  - `legacy_proxy`
  - `v2core_aper_energy_only_v1`
  - `teacher_e_evt_gate_targets_v1`
  都不能把系统拉出当前 template-collapse / harsh buzz 假解。

## 背景
- 旧报告
  `docs/361_stage5_eevt_target_contract_supervision_route_fail_fast_report.md`
  已经在 paired overfit 旧路线里否掉过
  `teacher_e_evt_gate_targets_v1`。
- 但那还不是当前 corrected export 语义下的 native-teacher fullsplit24 主线。
- 本轮的目的就是把这条尚未补齐的 contract family
  在当前正式主线上补完一次最小真验证，
  避免后续再把它当成“也许还没公平验证”。

## package export
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_eevttargetcontract_round1_1/`
- 顶层 index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_eevttargetcontract_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 关键确认：
  - `worker_processes = 4`
  - `target_contract_mode = teacher_e_evt_gate_targets_v1`
  - `train_package_count = 592`
  - `validation_package_count = 66`
  - 单包 `target_contract` 已真实记录：
    - `contract_family = teacher_e_evt_gate_targets_v1`
    - `uses_explicit_e_evt = true`
    - `periodic_gate_formula = max(vuv, p_voicing)`
    - `noise_gate_formula = max(aper * E_log_rms_norm, max(max(p_frication, p_stop_closure, p_burst, a_aper), max(p_pause_boundary, p_terminal_boundary) * max(aper, E_log_rms_norm)))`

## 训练与选择
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_eevttargetcontract_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_eevttargetcontract_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- selected checkpoint：
  - `step = 24`
  - `validation loss_total = 0.832195`
  - `loss_waveform = 0.12138`
  - `loss_stft = 0.313746`
  - `loss_rms_guard = 0.111283`
  - `decoded_to_target_rms_ratio = 0.92736`

## 真实导出
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_eevttargetcontract_fullsplit24_validation3_round1_1/`
- 主摘要：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_eevttargetcontract_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### machine gate
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`
- 被拒记录：
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

## 相对 corrected baseline 的对照
- baseline export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1/nores_vocoder_audio_export.json`
- baseline checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json`

### 162
- baseline：
  - `loss_total = 0.601405`
  - `spectral_centroid_gap_hz = 5003.986643`
  - `spectral_high_band_energy_ratio_gap = 0.338412`
- candidate：
  - `loss_total = 0.866376`
  - `spectral_centroid_gap_hz = 10600.610316`
  - `spectral_high_band_energy_ratio_gap = 0.651674`

### 138
- baseline：
  - `loss_total = 0.674103`
  - `spectral_centroid_gap_hz = 4956.085863`
  - `spectral_high_band_energy_ratio_gap = 0.286543`
- candidate：
  - `loss_total = 0.856697`
  - `spectral_centroid_gap_hz = 10517.630162`
  - `spectral_high_band_energy_ratio_gap = 0.595205`

### 106
- baseline：
  - `loss_total = 0.607221`
  - `spectral_centroid_gap_hz = 5113.494065`
  - `spectral_high_band_energy_ratio_gap = 0.29865`
- candidate：
  - `loss_total = 0.83094`
  - `spectral_centroid_gap_hz = 10532.195908`
  - `spectral_high_band_energy_ratio_gap = 0.597873`

## 判断
- 这条结果说明：
  - 即使把 supervision-side gate target
    升级成显式 `e_evt` 公式，
    当前 native-teacher route 仍会掉回同一类 harsh buzz 假解。
- 更具体地说：
  - `periodic_gate_target = max(vuv, p_voicing)`
  - `noise_gate_target`
    显式吸收 `frication / closure / burst / a_aper / boundary`
    这些语义后，
    并没有带来更合理的 decoded 结构，
    反而把三条样本的高频亮度与总误差一起推得更差。

## 结论口径
- 当前不再继续：
  - `teacher_e_evt_gate_targets_v1` 同层扩展
  - `pause / terminal / frication / burst`
    在现有 `target_contract_mode`
    里的加减法小修
  - `target_contract_mode`
    家族的更多 gate 公式微扫
- 下一步若继续留在 native teacher 主线，
  必须继续上收到：
  - 更根本的 noise/periodic target family
  - objective meaning
  - template-collapse 的诱因定位
