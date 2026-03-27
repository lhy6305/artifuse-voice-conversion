# 2026-03-27 Stage5 noise-family lag-aware corrreg fullsplit24 否决报告

## 结论
- 我把上一轮计划中的 `branch-specific / lag-aware / target-relative temporal regularization` 落成了真实可训练候选，并在原始 `contractv2_normfix` fullsplit 上完成了 smoke、正式训练、user-line 回投、Stage5 native 回投。
- 这条候选的实现形态是：
  - 保持原始 inference scaffold 与 dataset 分布不变
  - 继续使用 strongest backbone：
    - `branch_mean_contrast_residual_v1 + fused_single + residualshapecond`
  - 不再使用旧的全局 zero-lag corrreg
  - 改为在 `waveform_frames` 上加入两个 noise-family 的 center-weighted lag-profile excess loss：
    - `loss_noise_energy_frame_rms_lagcorr_excess`
    - `loss_noise_aper_energy_frame_rms_lagcorr_excess`
  - 只惩罚“预测 frame-RMS 与 acoustic-state 的 lag-corr 曲线在近零延迟窗口上高于 aligned target 自身曲线”的 excess 部分
- 当前结论已经足够明确：
  - 这条 `noise-family lag-aware corrreg` 也不能升格成主线
  - 它比上一轮全局 zero-lag corrreg 更贴 probe 结论，但正式回投仍未摆脱 `Stage5 native validation3 auto_reject = 3/3`
  - user-line 的 `template / activity_corr` 继续轻微改善，但 brightness 仍未回到 strongest candidate，native 侧反而比全局 corrreg 略差

## 一、代码与训练入口
- 代码入口：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增内容：
  - differentiable lag-corr curve helper：
    - `compute_lagged_sequence_correlation_curve(...)`
    - `build_triangular_lag_weights(...)`
    - `compute_frame_rms_lagcorr_excess_loss_against_aligned_target(...)`
  - 新增 loss：
    - `loss_noise_energy_frame_rms_lagcorr_excess`
    - `loss_noise_aper_energy_frame_rms_lagcorr_excess`
  - 新增日志指标：
    - `waveform_frame_rms_to_energy_control_lagcorr`
    - `waveform_frame_rms_to_aper_energy_lagcorr`
    - `frame_rms_lagcorr_max_lag_frames`
  - CLI 新参数：
    - `--noise-energy-frame-rms-lagcorr-excess-weight`
    - `--noise-aper-energy-frame-rms-lagcorr-excess-weight`
    - `--frame-rms-lagcorr-max-lag-frames`

## 二、1-step smoke
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_smoke_fullsplit1step_round1_1/`
- 命令语义：
  - 原始 `contractv2_normfix` fullsplit
  - strongest backbone 保持不变
  - 只打开：
    - `noise_energy_frame_rms_lagcorr_excess_weight = 0.2`
    - `noise_aper_energy_frame_rms_lagcorr_excess_weight = 0.2`
    - `frame_rms_lagcorr_max_lag_frames = 4`
- smoke 结果：
  - dataset loop 正常跑通
  - checkpoint 正常导出
  - summary 已写入新 lagcorr weights
  - validation 侧已出现非零 lagcorr 项：
    - `loss_noise_energy_frame_rms_lagcorr_excess = 0.020582`
    - `loss_noise_aper_energy_frame_rms_lagcorr_excess = 0.000405`
- 读法：
  - 这证明新正则不是“只写到 CLI/summary，没有真正进入训练”的假接线
  - 它已经进入真实 dataset loop / validation 路径

## 三、fullsplit24 正式训练
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_nea02_fbmc_rs_fs24_r1_1/`
- 最佳 checkpoint：
  - `step = 24`
  - `checkpoint_path = reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_lagcorr_nea02_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- validation loss：
  - strongest native candidate：`0.850578`
  - 全局 zero-lag corrreg：`0.825239`
  - 当前 lag-aware 候选：`0.825358`
- 读法：
  - objective 继续明显优于 strongest native candidate
  - 但相对上一轮全局 corrreg，并没有形成新的训练侧突破

## 四、user-line 固定 pure buzz triplet 回投
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_lagcorr_nea02_fbmc_rs_fs24_r1_1/`
- 对比对象：
  - strongest candidate：
    - `template = 0.984637`
    - `activity_corr = 0.519889`
    - `centroid = 6510.052734`
    - `high_band = 0.449300`
  - 上一轮全局 zero-lag corrreg：
    - `template = 0.982265`
    - `activity_corr = 0.414830`
    - `centroid = 7095.264160`
    - `high_band = 0.584512`
- 当前 lag-aware 候选 user-line aggregate：
  - `decoded_no_gate template = 0.982206`
  - `activity_corr = 0.401372`
  - `centroid = 7146.887207`
  - `high_band = 0.586353`
  - `waveform_frame_logits_template_cosine_mean = 0.993919`
  - `waveform_frames_template_cosine_mean = 0.993595`
  - `branch_mean_to_fused_template_cosine_gap = 0.003040`
  - `decoder_to_logits_template_cosine_gap = 0.014621`
- 读法：
  - 正向部分：
    - `template` 比全局 corrreg 再低一小步
    - `activity_corr` 比全局 corrreg 再低一小步
    - `branch_mean -> fused` 仍然维持在低坍缩区
  - 负向部分：
    - `centroid / high_band` 没有回到 strongest candidate
    - 相比全局 corrreg，brightness 仍是持平偏坏，不支持把这条线写成“用户线已恢复”

## 五、Stage5 native validation3 回投
- 输出目录：
  - `reports/runtime/stage5_waveform_handoff_probe_lagcorr_nea02_fbmc_rs_fs24_val3_r1_1/`
- 当前 lag-aware 候选结果：
  - `decoded_no_gate auto_reject_count = 3`
  - `template = 0.979618`
  - `rms_corr = 0.509435`
  - `centroid_gap = 5462.509277`
  - `high_band_gap = 0.553493`
  - `waveform_frame_logits_template_cosine_mean = 0.991388`
  - `waveform_frames_template_cosine_mean = 0.991087`
  - `branch_mean_to_fused_template_cosine_gap = 0.006894`
  - `decoder_to_logits_template_cosine_gap = 0.030169`
- 对比：
  - strongest native candidate：
    - `auto_reject_count = 0`
    - `template ≈ 0.979681`
    - `rms_corr ≈ 0.906013`
    - `centroid_gap ≈ 4405.950578`
    - `high_band_gap ≈ 0.361477`
  - 全局 zero-lag corrreg：
    - `auto_reject_count = 3`
    - `template = 0.979600`
    - `rms_corr = 0.537991`
    - `centroid_gap = 5426.240234`
    - `high_band_gap = 0.552879`
- 读法：
  - 当前 lag-aware 候选没有把 native validation3 从 `auto_reject = 3` 拉回来
  - 而且相对上一轮全局 corrreg，`rms_corr / centroid_gap / high_band_gap` 都没有改善，甚至略差

## 六、最终判断
- 这条线可以正式定性为：
  - `noise-family lag-aware corrreg` 只是把“zero-lag excess”升级成“近零延迟窗口 excess”
  - 但这仍然不足以把当前故障从主听感路径上拔掉
- 不能从这轮结果推出：
  - “只要继续细调 lag window 或权重，主方向就基本成立”
- 当前更合理的下一步应是：
  - 不继续围绕这条 output-side `frame_rms lagcorr` 做局部 sweep
  - 上收到更强的结构级方向，例如：
    - 更贴近 noise-family 内部表示的 regularization
    - `shape-aware / substage-aware` temporal target
    - 或直接约束 `noise_E / aper*E` 被消费成 waveform 的内部解码接口，而不是只在最终 `waveform_frames` 上做软惩罚

## 一句话结论
- `noise_E / aper*E` 的 lag-aware target-relative corrreg 已经完成正式验证，但它仍然把 Stage5 native validation3 留在 `auto_reject 3/3`，因此和上一轮全局 corrreg 一样，不能升格成当前主训练路线。
