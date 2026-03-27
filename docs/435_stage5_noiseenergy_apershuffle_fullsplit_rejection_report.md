# 2026-03-27 Stage5 `noise_E_log_rms_norm + aper` hard-shuffle fullsplit 候选否决报告

## 结论
- 我没有把
  `noise_E_log_rms_norm + aper`
  的联动去耦
  停留在
  smoke，
  而是把它物化成
  fullsplit 数据集，
  并用当前已成立的
  `branch_mean_contrast_residual_v1 + residualshapecond`
  骨架
  跑了正式 dataset loop，
  然后把 best checkpoint
  同时回投到：
  - user-line 固定三条 pure buzz
  - 原始 `contractv2_normfix` validation3
- 当前结论已经足够硬：
  - 这条
    `aper=time_shuffle + noise_E_log_rms_norm=time_shuffle`
    的 hard input variant
    不是可继续微调的候选，
    而是应正式降级的错误方向
- 更准确地说：
  - 它让 training validation loss
    从旧 strongest baseline 的
    `0.850578`
    略降到
    `0.841304`
  - 但 user-line 与 Stage5 native
    两侧 heard-path
    都明显回退成
    更亮、更模板化的高频 buzz
- 因而当前不能把
  probe 里成立的
  `time_shuffle`
  直接解释成：
  - 可被全程固化到训练输入里的
    正式 supervision 语义

## 一、fullsplit 物化与训练
- 变体索引：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_inputvariant_noiseenergy_apershuffle_fullsplit_round1_1/`
- 训练输出：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_inputvariant_noiseenergy_apershuffle_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/`
- 物化内容：
  - `aper = time_shuffle`
  - `noise_E_log_rms_norm = time_shuffle`
- 数据规模：
  - `592 train / 66 validation`
- 训练骨架保持不变：
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_scale = 1.0`

## 二、训练侧表面结果
- 旧 strongest baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/`
  - `validation loss_total = 0.850578`
- 新候选：
  - `validation loss_total = 0.841304`
- 读法：
  - objective
    确实略有改善，
    但这次已经明确不能把它当成
    正向证据，
    因为 heard-path
    同时明显恶化

## 三、user-line 回投结果
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_iv_ne_apshuf_fbmc_rs_fs24_r1_1/`
- 旧 strongest candidate
  来自：
  - `docs/427_teacher_first_candidate_transfer_report.md`
- 旧 strongest candidate
  的 user-line aggregate：
  - `decoded_no_gate template = 0.984637`
  - `decoded_no_gate activity_corr = 0.519889`
  - `decoded_no_gate centroid = 6510.052734`
  - `decoded_no_gate high_band = 0.449300`
- 新 hard-shuffle 候选
  的 user-line aggregate：
  - `decoded_no_gate template = 0.988341`
  - `decoded_no_gate activity_corr = 0.543954`
  - `decoded_no_gate centroid = 13654.723633`
  - `decoded_no_gate high_band = 0.793869`
  - `waveform_frame_logits_template_cosine_mean = 0.996818`
  - `waveform_frames_template_cosine_mean = 0.996629`
- 读法：
  - 这不是
    “还保住原本 manifold，
    只是 residual EF
    没继续下降”
  - 而是直接回退到：
    - 更高模板
    - 更高高频
    - 更亮的 obvious buzz 工作区

## 四、Stage5 native validation 对照
- 目录：
  - `reports/runtime/stage5_waveform_handoff_probe_inputvariant_noiseenergy_apershuffle_fusionbranchmeancontrast_residualshape_fullsplit24_validation3_round1_1/`
- 新 checkpoint
  在原始
  `contractv2_normfix`
  validation3 上的结果：
  - `diagnosis.primary_localization = buzz_present_by_waveform_frames_before_gate`
  - `decoded_no_gate auto_reject_count = 3/3`
  - `decoded_no_gate template = 0.986660`
  - `decoded_no_gate rms_corr = 0.632198`
  - `decoded_no_gate centroid_gap = 11348.081055`
  - `decoded_no_gate high_band_gap = 0.737495`
  - `logits_template = 0.994400`
  - `frames_template = 0.994168`
- 旧 strongest native candidate
  来自：
  - `docs/417_stage5_native_teacher_fusion_branchmean_contrast_residualshape_breakthrough_report.md`
- 旧 strongest native candidate
  的 validation3 读法是：
  - `auto_reject_count = 0`
  - `review_required_count = 3`
  - 三条记录的
    `decoded_frame_template_cosine_mean`
    约为
    `0.982943 / 0.981688 / 0.974411`
  - `spectral_centroid_gap_hz`
    约为
    `4436 / 4321 / 4461`
  - `spectral_high_band_energy_ratio_gap`
    约为
    `0.397825 / 0.339005 / 0.347602`
- 读法：
  - 新候选不只是
    user-line transfer fail，
    它在原始 native validation
    上也一起回退
  - 所以这不是：
    - “训练指标改善，
      但 user-line 特殊集成失败”
  - 而是：
    - hard-shuffle 输入训练
      把 checkpoint
      直接推离了原始 runtime manifold

## 五、当前主线如何更新
1. `aper + noise_E_log_rms_norm = time_shuffle`
   仍然是一个强 probe 诊断工具，
   但不能再被当成：
   - 可直接固化到全训练输入里的
     正式候选
2. 当前应正式否决的是：
   - full-package
     hard shuffle
     数据集变体训练
3. 下一步更合理的方向应是：
   - 保持原始 inference scaffold
     语义不变
   - 改做：
     - 软约束
     - 正则化
     - 部分概率扰动
     - 或只作用于训练时
       内部表示的时间去耦
   - 而不是把
     `time_shuffle`
     直接写死成输入分布

## 一句话结论
- `noise energy + aper`
  的 hard-shuffle
  在 probe 里是有效诊断，
  但一旦被固化成 fullsplit 训练输入，
  就会把 checkpoint
  推向更亮、更模板化的 buzz manifold；
  这条训练候选应正式降级为失败方向。 
