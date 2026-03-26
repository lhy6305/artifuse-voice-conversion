# 2026-03-26 Stage5 native teacher `f0_harmonicity_split_v1` objective-collapse probe 报告

## 结论
- 我已对刚完成 fail-fast 的
  `spectral_target_mode = f0_harmonicity_split_v1`
  线路补做 waveform-objective collapse probe。
- 结果非常直接：
  - baseline decode route 的
    `mean_weighted_wave_objective = 0.240339`
  - 两个 fixed-template oracle
    仍显著更低：
    - `oracle_active_frame_target_rms = 0.141467`
    - `oracle_sine_target_rms = 0.147455`
- 因而这条线不只是“真实 decoded 更差”；
  它在 objective 语义层也仍然允许，
  甚至更明显地允许，
  `fixed-template + target-RMS`
  这类 template-collapse 反例压过 baseline。
- 当前应更明确地说：
  - `f0_harmonicity_split_v1`
    没有修掉 objective permissiveness
  - 下一步不应继续停留在 package target family
    这层扩展，
    而应回到更根本的 objective meaning / collapse 诱因定位

## probe 入口
- 产物目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_f0harmonicity_round1_1/`
- 关键摘要：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_f0harmonicity_round1_1/stage5_waveform_objective_collapse_probe.json`
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_f0harmonicity_round1_1/stage5_waveform_objective_collapse_probe.md`
- 输入：
  - checkpoint：
    `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_f0harmonicity_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
  - checkpoint selection：
    `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_f0harmonicity_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - dataset index：
    `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_f0harmonicity_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - split：
    `validation`
  - `sample_count = 12`
  - decode 语义：
    - predicted gate `on`
    - smooth3
    - `post_ola_envelope`

## 一、weighted objective 排名
- `oracle_active_frame_target_rms`
  - `mean_weighted_wave_objective = 0.141467`
  - `delta_vs_baseline = -0.098871`
- `oracle_sine_target_rms`
  - `mean_weighted_wave_objective = 0.147455`
  - `delta_vs_baseline = -0.092883`
- `baseline_decode_route`
  - `mean_weighted_wave_objective = 0.240339`

## 二、关键侧证

### 1. baseline 在 MRSTFT / 归一化 logspec 上都明显更差
- `loss_mrstft_short_256_512_1024`
  - baseline：
    `0.321199`
  - oracle active：
    `0.109326`
  - oracle sine：
    `0.135768`
- `loss_frame_unit_rms_logspec_l1`
  - baseline：
    `0.953705`
  - oracle active：
    `0.629777`
  - oracle sine：
    `0.588792`

### 2. baseline 仍极强 template 化
- `decoded_frame_template_cosine_mean`
  - baseline：
    `0.997362`
  - oracle active：
    `0.923083`
  - oracle sine：
    `0.925485`
- `decoded_frame_rms_to_aligned_frame_rms_corr`
  - baseline：
    `0.816094`
  - oracle active：
    `0.998475`
  - oracle sine：
    `0.998668`

### 3. `frame_delta` 单独翻盘门槛很高
- `transition_delta_flip_thresholds`
  - `oracle_active_frame_target_rms`
    `flip_lambda_min = 6.516741`
  - `oracle_sine_target_rms`
    `flip_lambda_min = 6.729262`
- 这比此前 `contractv2_normfix`
  基线 probe 的门槛更差，
  说明当前 `f0_harmonicity`
  线路上的 objective landscape
  反而更不利。

## 三、targeted combo 结果

### 1. `active_template` 单独仍不够
- `active_template_targeted_summary.best_combo`
  - `template_lambda = 2.0`
  - `zero_jitter_lambda = 0.0`
  - `total_wins = 19 / 24`
- 仍有 residual：
  - `residual_count = 3`

### 2. `active_template + delta` 也没达到旧 probe 的 24/24
- `active_template_delta_targeted_summary.best_combo`
  - `template_lambda = 1.0`
  - `delta_lambda = 5.0`
  - `total_wins = 20 / 24`
- residual：
  - `residual_count = 2`
  - `target::chapter3_2_firefly_212`
  - `target::chapter3_2_firefly_155`

### 3. transition-side 组合几乎没有翻盘能力
- `transition_targeted_hard_failure_summary.best_combo`
  - `delta_lambda = 0.5`
  - `flux_lambda = 2.0`
  - `total_wins = 1 / 24`
- repeated hard failures
  仍覆盖当前 validation 关键失败样本：
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_4_firefly_106`
  - 以及多条额外记录

## 四、如何解读
- 这份 probe 说明：
  - `f0_harmonicity_split_v1`
    不是“target family 更正确，所以 objective permissiveness 至少会减轻”
  - 真实情况恰好相反：
    它连 objective 侧的 baseline 排名都更差，
    fixed-template 反例仍能稳定压过 baseline
- 更重要的是：
  - 先前在 `contractv2_normfix`
    基线 probe 里最有力的
    `active_template + frame_delta`
    组合，
    放到这条更差 target family 上，
    也不再表现成 `24 / 24`
    的完整压制
- 因而当前主线应继续收紧：
  - 不再把 package-level target family
    当作默认突破口
  - objective-side 根因分析
    应回到 corrected baseline 主线来做，
    而不是继续在更差 target family 上叠 penalty

## 一句话结论
- `f0_harmonicity_split_v1`
  不仅在真实 `decoded.wav`
  上比 corrected baseline 更差，
  在 waveform-objective collapse probe
  上也仍明显输给 fixed-template oracle，
  因而当前 Stage5 主线应停止继续扫
  package target family，
  转向更根本的 objective meaning / collapse 诱因定位。
