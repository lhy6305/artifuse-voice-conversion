# 2026-03-27 Stage5 全局 acoustic-state 超额零延迟相关正则 fullsplit24 否决报告

## 结论
- 我把“不要改 inference scaffold 分布，只在训练侧约束 `waveform_frames` 对 acoustic-state 的过强即时对齐”这条线真正落成了可训练候选，而不再停留在 probe 结论。
- 这条候选的实现形态是：
  - 保持原始 `contractv2_normfix` fullsplit 数据集不变
  - 训练时从 `source_scaffold_path` 按需回填 `aper` 和 `E_log_rms_norm`
  - 在 `waveform_frames` 上新增两个 soft regularizer：
    - `noise_energy_frame_rms_excess_corr`
    - `noise_aper_energy_frame_rms_excess_corr`
  - 只惩罚“预测 frame-RMS 的零延迟相关性高于 aligned target 自身相关性”的 excess 部分
- 当前结论已经足够明确：
  - 这条“全局 `E / aper*E` soft corrreg”不是下一阶段主线
  - 它不是完全无效，因为 user-line 的 template/activity 的确被压下了一截
  - 但它会把 Stage5 native validation3 明确推回 `auto_reject = 3/3`
  - 因而不能因为 objective 或 user-line 局部指标变好，就把它升格为正式训练方向

## 一、代码与训练入口
- 代码入口：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增内容：
  - 训练包读取时按需回填：
    - `aper_target`
    - `energy_control_target`
    - `energy_log_rms_norm_target`
  - 新增 loss：
    - `loss_noise_energy_frame_rms_corr_excess`
    - `loss_noise_aper_energy_frame_rms_corr_excess`
  - 新增日志指标：
    - `waveform_frame_rms_to_energy_control_corr`
    - `aligned_frame_rms_to_energy_control_corr`
    - `waveform_frame_rms_to_aper_energy_corr`
    - `aligned_frame_rms_to_aper_energy_corr`
  - CLI 新参数：
    - `--noise-energy-frame-rms-excess-corr-weight`
    - `--noise-aper-energy-frame-rms-excess-corr-weight`

## 二、原始 fullsplit 1-step smoke
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_corrreg_smoke_fullsplit1step_round1_1/`
- 命令语义：
  - 原始 `contractv2_normfix` fullsplit
  - strongest backbone 保持不变：
    - `branch_mean_contrast_residual_v1 + fused_single + residualshapecond`
  - 只额外打开：
    - `noise_energy_frame_rms_excess_corr_weight = 0.2`
    - `noise_aper_energy_frame_rms_excess_corr_weight = 0.2`
- smoke 结果：
  - 训练 loop 跑通
  - checkpoint 正常导出
  - summary 已写入新 loss weights
  - validation 侧已出现非零 corrreg 项：
    - `loss_noise_energy_frame_rms_corr_excess = 0.041719`
    - `loss_noise_aper_energy_frame_rms_corr_excess = 0.000970`
- 读法：
  - 这证明新增正则不是“只出现在 CLI 或 summary 里”的假接线
  - 它已经进入真实 dataset loop / validation 路径

## 三、fullsplit24 正式训练
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_corrreg_energyaper02_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/`
- 最佳 checkpoint：
  - `step = 24`
  - `checkpoint_path = reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_corrreg_energyaper02_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- validation loss：
  - 旧 strongest baseline：`0.850578`
  - 新 corrreg 候选：`0.825239`
- corrreg 侧指标：
  - step12：
    - `loss_noise_energy_frame_rms_corr_excess = 0.0`
    - `loss_noise_aper_energy_frame_rms_corr_excess = 0.000687`
  - step24：
    - `loss_noise_energy_frame_rms_corr_excess = 0.0`
    - `loss_noise_aper_energy_frame_rms_corr_excess = 0.0`
- 读法：
  - 训练目标表面上是更好的
  - 而且模型确实学会了把“全局 zero-lag excess corr”压到 target 以下
  - 但这还不能说明 heard-path 更好，必须回投 user-line 和 native validation

## 四、user-line 固定 pure buzz triplet 回投
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_cr_ea02_fbmc_rs_fs24_r1_1/`
- 对比对象：
  - `docs/427_teacher_first_candidate_transfer_report.md`
  - 旧 strongest candidate user-line aggregate：
    - `decoded_no_gate template = 0.984637`
    - `activity_corr = 0.519889`
    - `centroid = 6510.052734`
    - `high_band = 0.449300`
- 新 corrreg 候选 user-line aggregate：
  - `decoded_no_gate template = 0.982265`
  - `activity_corr = 0.414830`
  - `centroid = 7095.264160`
  - `high_band = 0.584512`
  - `waveform_frame_logits_template_cosine_mean = 0.993815`
  - `waveform_frames_template_cosine_mean = 0.993474`
  - `branch_mean_to_fused_template_cosine_gap = 0.002990`
  - `decoder_to_logits_template_cosine_gap = 0.014417`
- 读法：
  - 正向部分：
    - template 更低
    - residual envelope-following 更低
    - `branch_mean -> fused` 仍保持在低坍缩区间，没有退回 plain baseline
  - 负向部分：
    - 高频亮度明显升高
    - centroid / high-band 都比旧 strongest candidate 更差
  - 所以 user-line 不能写成“成功”，更像是：
    - 压下了一部分 template/activity
    - 但同时换来了更亮、更尖的 buzz

## 五、Stage5 native validation3 回投
- 输出目录：
  - `reports/runtime/stage5_waveform_handoff_probe_corrreg_energyaper02_fusionbranchmeancontrast_residualshape_fullsplit24_validation3_round1_1/`
- 新 corrreg 候选结果：
  - `decoded_no_gate auto_reject_count = 3`
  - `decoded_no_gate template = 0.979600`
  - `decoded_no_gate rms_corr = 0.861156`
  - `decoded_no_gate centroid_gap = 5426.240234`
  - `decoded_no_gate high_band_gap = 0.552879`
  - `waveform_frame_logits_template_cosine_mean = 0.991220`
  - `waveform_frames_template_cosine_mean = 0.990871`
  - `branch_mean_to_fused_template_cosine_gap = 0.006780`
  - `decoder_to_logits_template_cosine_gap = 0.029778`
- 对比旧 strongest native candidate：
  - `docs/417_stage5_native_teacher_fusion_branchmean_contrast_residualshape_breakthrough_report.md`
  - 当时是：
    - `auto_reject_count = 0`
    - `review_required_count = 3`
    - 三条记录平均大约：
      - `template ≈ 0.979681`
      - `rms_corr ≈ 0.906013`
      - `centroid_gap ≈ 4405.950578`
      - `high_band_gap ≈ 0.361477`
- 读法：
  - 新 corrreg 候选不是“template 变好所以整体更好”
  - 它把 native validation3 明确推回 auto-reject
  - 而且 brightness/high-band 比旧 strongest native candidate 明显更坏

## 六、最终判断
- 这条线可以正式定性为：
  - “全局 `E / aper*E` 超额零延迟相关正则”只提供了部分方向性证据
  - 但它不是可直接保留的正式训练候选
- 不能从这轮结果推出：
  - “只要把 acoustic-state 的 zero-lag corr 压下去，heard-path 就会自然变好”
- 当前更合理的下一步是：
  - 不改 inference scaffold 分布
  - 不继续扫这条全局 corrreg 的权重
  - 转向更接近 probe 结论的结构：
    - branch-specific
    - lag-aware / shape-aware
    - target-relative temporal regularization
  - 优先围绕 `noise_E_log_rms_norm` 家族，而不是全局 `E`

## 一句话结论
- hard-shuffle 输入训练已经正式否决；现在补上的“全局 acoustic corrreg”也不能升格成主线，因为它虽然压住了一部分 user-line template/activity，却把 Stage5 native validation3 明确推回了 `auto_reject 3/3`。
