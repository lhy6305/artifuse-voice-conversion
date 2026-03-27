# 2026-03-27 Stage5 output-head lagcorr fullsplit24 否决报告

## 结论
- 我把上一轮刚定位出来的
  `output head / residual-shape injection`
  方向直接落成了训练侧最小候选：
  - 不改 inference scaffold
  - 不回到最终输出 `waveform_frames` corrreg
  - 直接在 `fused_single` 路径上暴露：
    - `waveform_decoder_base_logits`
    - `waveform_residual_shape_delta`
  - 然后对这两个子阶段加
    target-relative lagcorr excess
- 这条候选已经完成：
  - 代码接线
  - 1-step smoke
  - 24-step fullsplit 正式训练
  - user-line fixed pure buzz triplet 回投
  - Stage5 native validation3 回投
- 当前结论已经足够明确：
  - 这条最小 output-head lagcorr route 不能升格成主线
  - 它虽然比旧 strongest candidate
    在训练侧 `validation loss_total`
    略好：
    - `0.850578 -> 0.868231`
    实际上没有形成有效改善
  - 更关键的是：
    - user-line 明显退化到更亮、更高 activity_corr 的高频 buzz
    - native validation3 也退化到更高 `centroid_gap / high_band_gap`

## 一、候选定义
- 代码入口：
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增的训练侧 interface-local losses：
  - `loss_waveform_decoder_base_logits_aper_lagcorr_excess`
  - `loss_waveform_decoder_base_logits_noise_energy_lagcorr_excess`
  - `loss_waveform_residual_shape_delta_noise_energy_lagcorr_excess`
- 当前正式训练配置：
  - backbone：
    - `branch_mean_contrast_residual_v1 + fused_single + residualshapecond`
  - weights：
    - `waveform_decoder_base_logits_aper_lagcorr_excess = 0.1`
    - `waveform_decoder_base_logits_noise_energy_lagcorr_excess = 0.1`
    - `waveform_residual_shape_delta_noise_energy_lagcorr_excess = 0.1`
  - `frame_rms_lagcorr_max_lag_frames = 12`

## 二、smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headcorr_smoke_fullsplit1step_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headcorr_lag12_smoke_fullsplit1step_round1_1/`
- 读法：
  - 三项新 loss 已真实进入训练链路
  - 但当前最稳定被激活的是：
    - `waveform_decoder_base_logits_aper_lagcorr_excess`
  - `noise_E` 相关两项在 smoke 上基本为零，
    说明“按 aligned target 自身相关性做 excess”这件事在 native packages 上没有稳定提供有效梯度

## 三、fullsplit24 正式训练
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headcorr_bla01_nela01_rsne01_lag12_fbmc_rs_fs24_r1_1/`
- 最终 best checkpoint：
  - `step24`
  - `checkpoint_path = .../offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- 训练侧结果：
  - strongest native candidate：
    - `validation loss_total = 0.850578`
  - 当前 output-head candidate：
    - `validation loss_total = 0.868231`
- 读法：
  - 这条线没有在训练 objective 上形成突破，
    连 strongest candidate 自己都没超过
  - 而且从 step / validation 历史看，
    新损失真正稳定工作的仍主要是：
    - `base_logits -> aper`
  - 这说明当前“target-relative output-head lagcorr”
    形式太弱，没把 probe 里看到的 interface 问题真正转成有效训练压力

## 四、user-line 回投
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_headcorr_bla01_nela01_rsne01_lag12_fbmc_rs_fs24_r1_1/`
- strongest candidate 参考：
  - `decoded_no_gate template = 0.984637`
  - `activity_corr = 0.519889`
  - `centroid = 6510.052734`
  - `high_band = 0.449300`
- 当前 output-head candidate：
  - `decoded_no_gate template = 0.968218`
  - `activity_corr = 0.746334`
  - `centroid = 12284.659180`
  - `high_band = 0.764083`
  - `waveform_frame_logits_template_cosine_mean = 0.988167`
  - `waveform_frames_template_cosine_mean = 0.987964`
- 读法：
  - 这不是“局部改善但还没完全转正”，
    而是更坏的 user-line 高亮高频 buzz
  - `activity_corr`
    也大幅抬高，
    说明 residual `envelope-following`
    没有被真正压住

## 五、Stage5 native validation3 回投
- 输出目录：
  - `reports/runtime/stage5_waveform_handoff_probe_headcorr_bla01_nela01_rsne01_lag12_fbmc_rs_fs24_val3_r1_1/`
- 当前结果：
  - `decoded_no_gate auto_reject_count = 3/3`
  - `template = 0.960827`
  - `rms_corr = 0.755374`
  - `centroid_gap = 10108.721680`
  - `high_band_gap = 0.690970`
- strongest native candidate 参考：
  - `auto_reject_count = 0`
  - `template ≈ 0.979681`
  - `rms_corr ≈ 0.906013`
  - `centroid_gap ≈ 4405.950578`
  - `high_band_gap ≈ 0.361477`
- 读法：
  - native validation3 也一起明显退化，
    所以这不是 user-line 特有转移失败
  - 当前 candidate
    已经把 checkpoint 整体推回了更亮、更模板化的坏 manifold

## 六、最终判断
- 这轮可以正式定性为：
  - `output-head target-relative lagcorr excess`
    的最小实现路线已被否决
- 当前不能得出的结论是：
  - “只要继续细调这三个权重，它就会转正”
- 更合理的下一步应该是：
  - 不再沿用“aligned target 自身相关性以上才处罚”这套过弱约束
  - 直接转向更强的 interface-local 结构路线，例如：
    - 对 `waveform_decoder_base_logits`
      施加更直接的 anti-template / anti-brightness / anti-zero-lag interface target
    - 或把 `residual_shape_delta`
      从纯 additive correction
      改成更受限的 shape-only / gated-low-rank / energy-debiased consumer

## 一句话结论
- output-head 是对的定位层级，但当前这版 `target-relative lagcorr excess` 训练实现太弱，正式回投把 user-line 和 native 一起推回更坏的高频 buzz，因此已正式否决。
