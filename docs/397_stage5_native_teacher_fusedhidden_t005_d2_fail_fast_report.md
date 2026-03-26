# 2026-03-26 Stage5 native teacher `fused_hidden_template=0.05 + fused_hidden_delta=2.0` fail-fast 报告

## 结论
- 这条 `fusion -> fused_hidden` 弱正则候选也应正式停线。
- 它比刚停掉的 `acttmpl005 + zerojitter4` 更接近 baseline，但仍然是 `3/3 auto_reject_obvious_buzz`。
- 相对 corrected native baseline，它没有把系统拉出 buzz 区，仍不值得继续扩成同族小权重 sweep。

## 背景
- 这条线不是拍脑袋新增。
- 选择它的原因是当前修正后的 decoder-structure probe 明确指出：
  - 更大的 collapse 已发生在 `fusion -> fused_hidden`
  - `fused_hidden_from_periodic_hidden / from_branch_mean / from_noise_hidden`
    都能显著降低 decoded template 化
- 但此前这条具体 loss family 只做过 minimal smoke，未在当前修正后语义下跑 fullsplit 真 decoded fail-fast。

## 候选配置
- `waveform = 0.5`
- `stft = 0.5`
- `rms_guard = 0.2`
- `activity_gate = 0.2`
- `fused_hidden_template = 0.05`
- `fused_hidden_delta = 2.0`
- `use_predicted_activity_gate = true`
- `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 产物
- 训练 summary：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusedhidden_t005_d2_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
- checkpoint 选择：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusedhidden_t005_d2_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 真实导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusedhidden_t005_d2_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 关键结果
- selected checkpoint:
  - `step = 24`
  - `validation loss_total = 0.786927`
- relative to corrected native baseline：
  - baseline selected checkpoint `loss_total = 0.554104`
  - 仍明显更差

### validation3 real decoded
- `buzz_reject_summary.auto_reject_count = 3`
- `buzz_reject_summary.all_records_auto_reject = true`

### 162 对照
- baseline:
  - `loss_total = 0.55544`
  - `spectral_centroid_gap_hz = 4999.124195`
  - `spectral_high_band_energy_ratio_gap = 0.338207`
- candidate:
  - `loss_total = 0.803225`
  - `spectral_centroid_gap_hz = 6813.963812`
  - `spectral_high_band_energy_ratio_gap = 0.502304`

## 判断
- 这条候选说明：
  - `fusion -> fused_hidden` 的确是有信息量的病灶层
  - 但单靠弱的 `fused_hidden template/delta` 正则，不足以把系统从 native teacher buzz 假解里拉出来
- 所以后续不再继续：
  - `fused_hidden_template`
  - `fused_hidden_delta`
  - 它们的同族小权重 sweep

## 下一步
- 当前更合理的方向不是再叠弱 loss，而是更直接的 `forward-path structural` 候选：
  - 例如显式 branch-side dynamics 注入或更强的 fusion operating-point 改写
- 也就是说，下一条候选应从“加一个小 penalty”升级为“改 forward handoff 形态”。
