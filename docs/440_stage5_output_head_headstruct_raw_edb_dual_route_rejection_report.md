# 2026-03-27 Stage5 output-head stronger headstruct raw/edb 双候选否决报告

## 结论
- 在 `docs/439_stage5_output_head_lagcorr_fullsplit24_rejection_report.md`
  否决了较弱的
  `target-relative lagcorr excess`
  以后，
  我把 output-head 路线继续加强成两条更直接的 interface-local 候选：
  - `raw_additive_v1`
    下直接对
    `waveform_decoder_base_logits`
    加：
    - active-template
    - `aper` abs-zero-lag corr
    - `noise_E` abs-zero-lag corr
    - 以及对
      `waveform_residual_shape_delta`
      加
      `noise_E` abs-zero-lag corr
  - 在同一 loss 组合上，
    再把 residual-shape consumer
    改成：
    - `shape_only_energy_debiased_v1`
- 这两条路线都已经完成：
  - smoke
  - 24-step fullsplit 正式训练
  - user-line fixed triplet 回投
  - Stage5 native validation3 回投
- 当前结论足够明确：
  - 这两条 stronger headstruct 候选都不能升格成主线
  - `shape_only_energy_debiased_v1`
    也没有带来转正，
    反而比 raw 版更差

## 一、候选定义
- 代码入口：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/cli.py`
- 两条路线共用的训练侧约束：
  - `waveform_decoder_base_logits_active_template = 0.1`
  - `waveform_decoder_base_logits_aper_abs_zero_lag_corr = 0.1`
  - `waveform_decoder_base_logits_noise_energy_abs_zero_lag_corr = 0.1`
  - `waveform_residual_shape_delta_noise_energy_abs_zero_lag_corr = 0.1`
- raw 版 forward path：
  - `residual_shape_branch_condition_mode = raw_additive_v1`
- edb 版 forward path：
  - `residual_shape_branch_condition_mode = shape_only_energy_debiased_v1`

## 二、运行目录
- raw 版正式训练：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- raw 版 user-line 回投：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_headstruct_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- raw 版 native validation3 回投：
  - `reports/runtime/stage5_waveform_handoff_probe_headstruct_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_val3_r1_1/`
- edb 版正式训练：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_edb_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- edb 版 user-line 回投：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_headstruct_edb_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- edb 版 native validation3 回投：
  - `reports/runtime/stage5_waveform_handoff_probe_headstruct_edb_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_val3_r1_1/`

## 三、训练侧结果
- strongest native candidate
  参考：
  - `validation loss_total = 0.850578`
- raw 版：
  - `best_checkpoint = step24`
  - `validation loss_total = 1.037664`
- edb 版：
  - `best_checkpoint = step24`
  - `validation loss_total = 1.039311`
- 读法：
  - 这两条 stronger headstruct route
    都没有在训练侧形成优势
  - edb 版还略差于 raw 版

## 四、user-line 回投

### 1. raw 版
- `decoded_no_gate template = 0.807166`
- `activity_corr = -0.054555`
- `centroid = 9250.702148`
- `high_band = 0.643441`
- 诊断：
  - `likely_failure_already_present_by_frames_before_gate = true`

### 2. edb 版
- `decoded_no_gate template = 0.798158`
- `activity_corr = -0.087543`
- `centroid = 9430.278320`
- `high_band = 0.647224`
- 诊断：
  - `likely_failure_already_present_by_frames_before_gate = true`

### 3. 读法
- 这不是“亮度稍微降了一点但路线还算正常”，
  而是：
  - 两条路线都把 user-line
    推进了更异常的输出分布
  - edb 版在 brightness
    和整体可用性上
    还略差于 raw 版
- 更关键的是：
  - failure 仍然在
    `waveform_frames`
    之前就已经形成，
    predicted activity gate
    并没有改变这件事

## 五、Stage5 native validation3 回投

### 1. raw 版
- `decoded_no_gate auto_reject_count = 3/3`
- `template = 0.706192`
- `rms_corr = 0.652670`
- `centroid_gap = 7220.358887`
- `high_band_gap = 0.594071`

### 2. edb 版
- `decoded_no_gate auto_reject_count = 3/3`
- `template = 0.690718`
- `rms_corr = 0.494628`
- `centroid_gap = 7481.787598`
- `high_band_gap = 0.605874`

### 3. 读法
- 两条 stronger headstruct 路线
  在 native validation3
  上都仍是：
  - `auto_reject = 3/3`
- edb 版不仅没有修复，
  还把：
  - `rms_corr`
  压得更低，
  同时把：
  - `centroid_gap`
  - `high_band_gap`
  推得更坏

## 六、最终判断
- 当前可以正式定性为：
  - `active-template + abs-zero-lag corr`
    这套 stronger interface-local route
    在没有显式 anti-brightness 约束时，
    仍然不能转正
  - `shape_only_energy_debiased_v1`
    在当前 strongest backbone 上
    也不能作为默认 residual-shape consumer 升格
- 因而下一步不应继续做：
  - raw / edb
    之间的小权重或小语义 sweep
- 更合理的下一步应转向：
  - 真正显式的
    output-head anti-brightness
    约束
  - 而不是只靠
    template / zero-lag
    去间接逼它变暗

## 一句话结论
- stronger headstruct raw/edb 双候选都已完成正式回投并被否决：仅靠 output-head active-template 与 abs-zero-lag 去压 interface coupling 还不够，`shape_only_energy_debiased_v1` 也没有救回来，下一步必须显式补上 anti-brightness 路线。
