# 2026-03-27 Stage5 output-head headstruct high-band 候选突破报告

## 结论
- 在 `docs/440_stage5_output_head_headstruct_raw_edb_dual_route_rejection_report.md`
  否决了
  `active-template + abs-zero-lag`
  但缺少显式 anti-brightness 的 stronger headstruct 路线以后，
  我把下一条最小候选直接补成：
  - 保持 raw headstruct 主体不变
  - 在
    `waveform_decoder_base_logits`
    上新增直接的
    `high_band_excess`
    约束
- 这条路线还顺手补了一个实现缺口：
  - 训练侧已有
    `waveform_decoder_base_logits_high_band_excess_weight`
  - 但 CLI
    之前没有把它暴露出来，
    当前已在
    `src/v5vc/cli.py`
    补齐
- 当前结果和前两条 rejection
  已经明显不同：
  1. smoke 里新 high-band loss
     真实进链路，
     量级稳定在
     `0.65 ~ 0.80`
  2. native validation3
     从：
     - `auto_reject = 3/3`
       直接恢复到：
     - `auto_reject = 0/3`
  3. user-line brightness
     明显回落到更合理的区间
  4. `waveform_handoff`
     诊断首次变成：
     - `likely_failure_already_present_by_frames_before_gate = false`
- 因而当前判断是：
  - 这条 `headstruct + high-band`
    不能被立刻否决
  - 但也还不能直接写成最终 winner
  - 它已经进入：
    - 值得继续做人工听审与更细 root-cause 收敛
    的状态

## 一、候选定义
- 代码入口：
  - `src/v5vc/cli.py`
  - `src/v5vc/offline_vocoder_training.py`
- forward path：
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_mode = raw_additive_v1`
- 正式训练 loss 组合：
  - `waveform_decoder_base_logits_high_band_excess = 0.1`
  - `waveform_decoder_base_logits_active_template = 0.1`
  - `waveform_decoder_base_logits_aper_abs_zero_lag_corr = 0.1`
  - `waveform_decoder_base_logits_noise_energy_abs_zero_lag_corr = 0.1`
  - `waveform_residual_shape_delta_noise_energy_abs_zero_lag_corr = 0.1`

## 二、运行目录
- smoke：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_hbe_smoke_fullsplit1step_round1_1/`
- 正式训练：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bhb01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- user-line 回投：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_headstruct_bhb01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- native validation3 回投：
  - `reports/runtime/stage5_waveform_handoff_probe_headstruct_bhb01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_val3_r1_1/`
- stage temporal coupling probe：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_stcp_headstruct_bhb01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`

## 三、smoke
- smoke 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_hbe_smoke_fullsplit1step_round1_1/`
- 关键观察：
  - `loss_waveform_decoder_base_logits_high_band_excess = 0.749232`
  - `waveform_decoder_base_logits_high_band_energy_ratio = 0.816849`
  - `waveform_decoder_base_logits_target_high_band_energy_ratio = 0.067618`
- 读法：
  - 这不是“参数接上了但基本没梯度”，
    而是：
  - 新 loss
    已经稳定打在
    raw waveform head
    的高频亮度异常上

## 四、正式训练
- 正式训练 best checkpoint：
  - `step24`
- `validation loss_total = 1.040928`
- 读法：
  - 训练 objective
    仍然高于旧 strongest candidate
  - 但因为当前 total loss
    已经包含新的 interface-local penalties，
    它不能单独作为否决依据
  - 当前是否继续保留这条线，
    主要要看：
    - user-line
    - native validation3
    - 与 stage temporal coupling
      的联合回投

## 五、user-line 回投

### 1. `decoded_no_gate`
- `template = 0.874273`
- `activity_corr = -0.135681`
- `centroid = 5095.748535`
- `high_band = 0.282291`

### 2. `decoded_post_ola_gate`
- `template = 0.870602`
- `activity_corr = 0.980820`
- `centroid = 4804.712891`
- `high_band = 0.259251`

### 3. 读法
- 相比旧 strongest candidate
  的 user-line 参考：
  - `template = 0.984637`
  - `activity_corr = 0.519889`
  - `centroid = 6510.052734`
  - `high_band = 0.449300`
- 当前 high-band route
  的核心变化是：
  - brightness 明显被压下来了
  - 输出不再停留在
    `9k ~ 12k`
    那种明显偏亮偏 buzz
    的区间
- 更关键的是：
  - `waveform_handoff`
    当前诊断变成：
    - `likely_failure_already_present_by_frames_before_gate = false`
  - 这说明当前 route
    已不再是
    “在 waveform_frames
    之前就彻底坏死”
    的类型

## 六、Stage5 native validation3 回投

### 1. `decoded_no_gate`
- `auto_reject_count = 0/3`
- `template = 0.806369`
- `rms_corr = 0.404107`
- `centroid_gap = 3619.810547`
- `high_band_gap = 0.235650`

### 2. `decoded_post_ola_gate`
- `auto_reject_count = 0/3`
- `template = 0.796630`
- `rms_corr = 0.939670`
- `centroid_gap = 3211.714111`
- `high_band_gap = 0.198100`

### 3. 与前序候选对比
- 相比 `docs/440`
  里的 raw / edb：
  - `auto_reject = 3/3`
    直接恢复为：
    - `0/3`
- 相比旧 strongest candidate
  在文档中的参考：
  - `centroid_gap ≈ 4405.95`
  - `high_band_gap ≈ 0.361477`
- 当前 gated route
  已进一步改善到：
  - `3211.714111`
  - `0.198100`

## 七、stage temporal coupling 补充验证
- probe 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_stcp_headstruct_bhb01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- 当前观察：
  - `aper`
    不再以
    `decoder_hidden -> waveform_decoder_base_logits`
    作为最大 jump，
    当前更大的 jump
    转成了：
    - `waveform_decoder_base_logits -> waveform_residual_shape_delta`
  - `noise_E_log_rms_norm`
    的 peak zero-lag
    回到了：
    - `noise_hidden`
    而不是 output head
  - 但
    `aper * noise_E`
    这条乘积项
    仍然还有：
    - `decoder_hidden -> waveform_decoder_base_logits`
      的大 jump
      `+0.425682`
- 读法：
  - current route
    已经把
    output head
    的最坏 brightness / zero-lag
    问题压下来一大截
  - 但并没有把所有 noise-family
    temporal coupling
    完全消干净

## 八、当前判断
- 这条候选当前不能写成：
  - 已最终转正
- 但同样不能再写成：
  - 和 `439/440`
    一样的失败路线
- 更准确的状态应是：
  - 它是当前 output-head 主线里
    第一条同时满足：
    - native `auto_reject` 清零
    - brightness gap 明显回落
    - `waveform_handoff`
      不再显示
      “frames 前就已坏死”
    的可继续候选
- 当前下一步应优先转向：
  - 保持这条 high-band route
    不动，
    进入人工听审治理
  - 同时继续追
    `aper * noise_E`
    在
    `decoder_hidden -> waveform_decoder_base_logits`
    仍残留的 jump

## 一句话结论
- 给 `waveform_decoder_base_logits` 加显式 high-band excess 后，output-head 路线第一次摆脱了“必然双退化”的状态：native validation3 已恢复到 `auto_reject=0` 且 brightness gap 明显优于 strongest candidate，但 user-line 仍需人工听审确认，因此当前应把它升级为可继续治理的主候选，而不是直接定胜负。
