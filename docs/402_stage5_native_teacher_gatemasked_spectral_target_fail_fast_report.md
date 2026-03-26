# 402. Stage5 native teacher `gate_masked_halfsplit_v1` spectral target fail-fast 报告

## 结论
- 这条 `spectral_target_mode = gate_masked_halfsplit_v1` 路线应正式停线。
- 它确实把 `harmonic_target / noise_target` 改成了显式 gate-masked 版本，但真实 `validation3 decoded.wav` 结果比 corrected native baseline 明显更差。
- 当前可以更硬地下结论：
  - 不是 “raw half-split spectral target 少了一层显式 gate mask”
  - 简单把 spectral target 乘上 `periodic_gate_target / noise_gate_target` 只会把 native teacher 往更亮、更硬的 buzz 推

## 背景
- 这条线不是 decoder mode 变体，而是更上游的 target/contract 语义变体。
- 核心改动是：
  - `harmonic_target = harmonic_target * periodic_gate_target`
  - `noise_target = noise_target * noise_gate_target`
- 目标是验证：
  - 当前 Stage5 的 half-split spectral target 是否因为没有显式 gate mask，才给了 decoder 过宽的 envelope-following 假解空间

## 配置与产物
- dataset package：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_gatemasked_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- sample package target summary：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_gatemasked_round1_1/packages/validation/target__chapter3_3_firefly_162/train_targets/offline_mvp_nores_vocoder_train_targets.json`
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_gatemasked_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_gatemasked_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_gatemasked_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 关键结果
- selected checkpoint：
  - `step = 24`
  - `validation loss_total = 0.793686`
- validation3 real decoded：
  - `buzz_reject_summary.auto_reject_count = 3`
  - `buzz_reject_summary.all_records_auto_reject = true`

## 和 corrected baseline 的对照
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_2/nores_vocoder_audio_export.json`
  - `target::chapter3_3_firefly_162`
    - `loss_total = 0.55544`
    - `spectral_centroid_gap_hz = 4999.124195`
    - `spectral_high_band_energy_ratio_gap = 0.338207`

- candidate：
  - `target::chapter3_3_firefly_162`
    - `loss_total = 0.893706`
    - `spectral_centroid_gap_hz = 10557.221838`
    - `spectral_high_band_energy_ratio_gap = 0.645643`
  - `target::chapter3_3_firefly_138`
    - `loss_total = 0.820152`
    - `spectral_centroid_gap_hz = 10458.448843`
    - `spectral_high_band_energy_ratio_gap = 0.588543`
  - `target::chapter3_4_firefly_106`
    - `loss_total = 0.786767`
    - `spectral_centroid_gap_hz = 10484.588393`
    - `spectral_high_band_energy_ratio_gap = 0.591834`

## 解读
- 这条线回答了一个现在已经不必再回头的问题：
  - 当前 native teacher 的主故障不是 “spectral target 没有显式乘 gate”
- 相反，直接做 gate-masked spectral target 会带来两个坏后果：
  - 高频亮度显著恶化
  - template-collapse 仍然不动，甚至更硬
- 所以后续不再继续：
  - `spectral_target_mode` 同族 gate-masking 变体
  - `harmonic/noise spectral target` 与现有 `gate target` 的乘法式简单绑死

## 下一步
- 当前 native teacher 主线不再继续扫 decoder mode，也不再继续扫简单 gate-masked spectral target。
- 下一步应回到更上游的：
  - native teacher objective / target / contract 语义
  - 尤其是 noise/periodic 目标本身的含义，而不是再给它们叠乘法 mask
