# 2026-03-26 Stage5 native teacher `f0_harmonicity_split_v1` spectral target fail-fast 报告

## 结论
- `spectral_target_mode = f0_harmonicity_split_v1`
  已在当前 corrected native-teacher fullsplit24 主线上完成：
  - full-split package export
  - 24-step training
  - checkpoint selection
  - validation3 real decoded export
- 结果应立即判停：
  - `3/3 auto_reject_obvious_buzz`
  - 相对 corrected baseline，
    三条样本的
    `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
    全面更差
- 因而当前不再继续：
  - `spectral_target_mode`
    的 package-level 同族 target family 扩展
  - 把 `F0 / vuv`
    显式编码进 harmonic/noise spectral target
    的近邻小变体

## 背景
- `docs/402_stage5_native_teacher_gatemasked_spectral_target_fail_fast_report.md`
  已经否掉：
  - `spectral_target_mode = gate_masked_halfsplit_v1`
- 但那还不能回答另一条更强解释：
  - 当前 native teacher 的主故障，
    是否来自 `harmonic/noise spectral target`
    本身过于粗糙，
    只做了固定频带 half-split，
    没有显式承接 `F0 / vuv`
    所描述的谐波结构
- 本轮就是把这条“更显式、更像设计态”的 target family
  补成一次完整 fullsplit24 fail-fast。

## package export
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_f0harmonicity_round1_1/`
- 顶层 index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_f0harmonicity_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 关键确认：
  - `worker_processes = 4`
  - `target_contract_mode = legacy_proxy`
  - `spectral_target_mode = f0_harmonicity_split_v1`
  - `train_package_count = 592`
  - `validation_package_count = 66`
  - 单包 `spectral_target_contract`
    已真实记录：
    - `contract_family = f0_harmonicity_split_v1`
    - `uses_gate_masking = false`
    - `harmonic_mask_formula = harmonic_bins_from_f0_hz_and_vuv`
    - `noise_mask_formula = spectral_complement_of_harmonic_mask`
- 这说明本轮不是 metadata-only；
  `harmonic/noise spectral target`
  已真实切换到按 `F0 / vuv`
  构造的谐波掩模语义。

## 训练与选择
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_f0harmonicity_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_f0harmonicity_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- selected checkpoint：
  - `step = 24`
  - `validation loss_total = 0.788936`
  - `loss_waveform = 0.123886`
  - `loss_stft = 0.320643`
  - `loss_rms_guard = 0.106407`
  - `decoded_to_target_rms_ratio = 0.944386`

## 真实导出
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_f0harmonicity_fullsplit24_validation3_round1_1/`
- 主摘要：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_f0harmonicity_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

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
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.170058`
- candidate：
  - `loss_total = 0.827025`
  - `spectral_centroid_gap_hz = 10756.9882`
  - `spectral_high_band_energy_ratio_gap = 0.650874`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.838634`

### 138
- baseline：
  - `loss_total = 0.674103`
  - `spectral_centroid_gap_hz = 4956.085863`
  - `spectral_high_band_energy_ratio_gap = 0.286543`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.041527`
- candidate：
  - `loss_total = 0.797874`
  - `spectral_centroid_gap_hz = 10662.001846`
  - `spectral_high_band_energy_ratio_gap = 0.594065`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.807484`

### 106
- baseline：
  - `loss_total = 0.607221`
  - `spectral_centroid_gap_hz = 5113.494065`
  - `spectral_high_band_energy_ratio_gap = 0.29865`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.025772`
- candidate：
  - `loss_total = 0.790915`
  - `spectral_centroid_gap_hz = 10703.131113`
  - `spectral_high_band_energy_ratio_gap = 0.598144`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.856177`

## 判断
- 这条结果说明：
  - 当前 native teacher 的主故障，
    不是“half-split spectral target 太粗，
    只要按 `F0 / vuv`
    构造 harmonic/noise 掩模就会自然转正”
- 更具体地说：
  - `f0_harmonicity_split_v1`
    并没有带来更合理的短时结构
  - 它反而把三条样本进一步推向：
    - 更亮的高频 harsh buzz
    - 更强的 envelope-following
    - 以及更高的总误差
- 当前更合理的口径是：
  - package-level `spectral_target_mode`
    这层“更像设计态”的 target family 改写，
    仍不足以把 native teacher 拉出当前 template-collapse 假解

## 结论口径
- 当前不再继续：
  - `f0_harmonicity_split_v1` 同层扩展
  - `spectral_target_mode`
    的近邻 package-level target family 微扫
- 下一步若继续留在这条主线，
  应转去：
  - 更根本的 objective meaning
  - template-collapse 的诱因定位
  - 以及为什么当前 decoder/objective
    会把更“显式”的 target family
    仍然收敛成同类 buzz
