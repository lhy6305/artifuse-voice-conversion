# 392. Stage5 native teacher `acttmpl005_delta6` fail-fast 报告

## 修正说明（2026-03-26）
- 本报告里的 native baseline 与 candidate decoded 对照，建立在旧版 `export-offline-mvp-nores-vocoder-audio` 语义之上。
- 因此当前只保留这些确定事实：
  - `acttmpl005_delta6` 训练候选已真实跑过
  - 相应 checkpoint selection 已完成
- 但以下依赖旧 export 的结论，必须在修正后 export 语义下回补确认：
  - `3/3 auto_reject_obvious_buzz`
  - candidate 相对 native baseline 的 decoded 级恶化幅度
  - 各条样本的 `spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
- 统一修正口径见：
  - `docs/393_stage5_export_semantics_correction_scope_and_rerun_requirements.md`
  - `docs/394_stage5_export_semantics_rerun_confirmation_report.md`
- 当前状态更新：
  - `392` 已按修正后的 export 语义完成最小回补重跑
  - 主结论成立，恢复为当前可直接引用结论

## 结论
- 我已按新的主线要求，直接在 native teacher 路线上做了一个最小训练候选：
  - `active_template_weight = 0.05`
  - `frame_delta_weight = 6.0`
- 这条候选不是空想配置，而是来自既有 `waveform objective collapse probe` 里当前最强的 train-side 指向。
- 但它在真实 `decoded.wav` 上应立即判停：
  - validation `3-sample` 仍然 `3/3 auto_reject_obvious_buzz`
  - 而且相对当前 native teacher baseline，明显更差
- 因此：
  - `native teacher buzz` 的下一步不再是直接把 `acttmpl005_delta6` 推成长 horizon
  - 这条训练侧 objective 组合在当前 fullsplit native route 上已 fail-fast 失败

## 一、本轮执行

### 1. 训练
- 命令：
  - `python manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_delta6_fullsplit24_round1_1 --device cuda:0 --num-steps 24 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260326 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --active-template-weight 0.05 --frame-delta-weight 6.0 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add`
- 训练摘要：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_delta6_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 2. checkpoint selection
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_delta6_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 结果：
  - `best_validation = step24`
  - `loss_total = 6.481872`
  - `decoded_to_target_rms_ratio = 0.911093`

### 3. 真实 decoded 导出
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_acttmpl005_delta6_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`
- 真实音频：
  - `target__chapter3_3_firefly_162__decoded.wav`
  - `target__chapter3_3_firefly_138__decoded.wav`
  - `target__chapter3_4_firefly_106__decoded.wav`

## 二、fail-fast 结果

### 1. 机器门禁
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 相对当前 native baseline，不是“仍失败而已”，而是更差
- 基线复核：
  - `docs/391_stage5_native_teacher_buzz_recheck_and_physiology_data_assessment.md`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1/nores_vocoder_audio_export.json`
- 当前候选：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_acttmpl005_delta6_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

### 3. 典型恶化
- `target::chapter3_3_firefly_162`
  - baseline:
    - `spectral_centroid_gap_hz = 5003.986643`
    - `spectral_high_band_energy_ratio_gap = 0.338412`
  - candidate:
    - `spectral_centroid_gap_hz = 10648.190268`
    - `spectral_high_band_energy_ratio_gap = 0.624066`
- `target::chapter3_3_firefly_138`
  - baseline:
    - `4956.085863`
    - `0.286543`
  - candidate:
    - `10606.247333`
    - `0.571392`
- `target::chapter3_4_firefly_106`
  - baseline:
    - `5113.494065`
    - `0.298650`
  - candidate:
    - `10713.934050`
    - `0.580414`

## 三、解释
- 这说明当前 `acttmpl005_delta6` 在 native fullsplit teacher route 上，虽然理论上更针对 template-collapse，
  但实际先把 decoded 推向了更亮、更尖锐的 harsh buzz 区域。
- 所以这里不能沿着 paired tiny-overfit 的旧直觉继续加步数。
- 当前更合理的结论是：
  - 这条 objective 组合在 native teacher route 上与当前承接层/decoder 相互作用不好
  - 应正式停线

## 四、下一步
- 不继续：
  - `acttmpl005_delta6` 的更长 horizon
  - 同族小范围扫参
- 下一步应转去：
  - 更直接针对 native teacher `waveform decoder structure`
  - 或更保守的 objective / decode semantics 修复候选
  - 但不再默认从这条组合继续扩
