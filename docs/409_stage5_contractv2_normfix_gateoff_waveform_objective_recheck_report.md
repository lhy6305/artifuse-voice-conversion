# 2026-03-26 Stage5 `contractv2_normfix` gate-off waveform objective 复核报告

## 结论
- 旧 `docs/293_stage5_contractv2_normfix_waveform_objective_recheck_report.md`
  使用的是 gate-on decode 语义：
  - predicted gate `on`
  - smooth3
  - `post_ola_envelope`
- 但当前 corrected native baseline 的真实听审主路由
  已经是 gate-off。
- 本轮补做 gate-off 复核后，
  结论不但没有变轻，反而更重：
  - baseline decode route 的
    `mean_weighted_wave_objective = 0.293871`
  - 两个 fixed-template oracle
    仍显著更低：
    - `oracle_active_frame_target_rms = 0.141467`
    - `oracle_sine_target_rms = 0.147455`
- 这说明：
  - 当前真实听审路由下的 objective permissiveness
    比旧 gate-on probe 看到的还更严重
  - 因而不应再把 `293`
    里的 objective-side 候选
    直接当作当前默认训练候选

## probe 入口
- 产物目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_gateoff_round1_1/`
- 关键摘要：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_gateoff_round1_1/stage5_waveform_objective_collapse_probe.json`
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_gateoff_round1_1/stage5_waveform_objective_collapse_probe.md`
- 输入：
  - checkpoint selection：
    `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json`
  - dataset index：
    `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - split：
    `validation`
  - `sample_count = 12`
  - decode 语义：
    - `use_predicted_activity_gate = false`
    - `predicted_activity_gate_apply_mode = post_ola_envelope`

## 一、weighted objective 排名
- `oracle_active_frame_target_rms`
  - `mean_weighted_wave_objective = 0.141467`
  - `delta_vs_baseline = -0.152404`
- `oracle_sine_target_rms`
  - `mean_weighted_wave_objective = 0.147455`
  - `delta_vs_baseline = -0.146416`
- `baseline_decode_route`
  - `mean_weighted_wave_objective = 0.293871`

## 二、和旧 gate-on probe 的关系
- 旧 `293`
  的 gate-on baseline：
  - `mean_weighted_wave_objective = 0.149037`
  - `decoded_frame_template_cosine_mean = 0.993590`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.874109`
- 本轮 gate-off baseline：
  - `mean_weighted_wave_objective = 0.293871`
  - `decoded_frame_template_cosine_mean = 0.995873`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = -0.039668`
- 当前更合理的解释是：
  - gate-off 听审路由
    不是“更接近修好”
  - 而是把当前 collapse/buzz
    以另一种更差的 objective 形态显露出来：
    - 仍高度 template 化
    - 但 envelope 跟随也塌掉了
    - `waveform / stft / rms_guard`
      三项 aggregate 都显著更差

## 三、关键侧证

### 1. baseline 在 MRSTFT / 归一化 logspec 上仍明显落后 oracle
- `loss_mrstft_short_256_512_1024`
  - baseline：
    `0.269837`
  - oracle active：
    `0.109326`
  - oracle sine：
    `0.135768`
- `loss_frame_unit_rms_logspec_l1`
  - baseline：
    `0.741496`
  - oracle active：
    `0.629777`
  - oracle sine：
    `0.588792`

### 2. `frame_delta` 单独翻盘门槛已非常高
- `transition_delta_flip_thresholds`
  - `oracle_active_frame_target_rms`
    `flip_lambda_min = 10.180628`
  - `oracle_sine_target_rms`
    `flip_lambda_min = 10.765091`
- 这明显高于旧 gate-on probe，
  说明当前真实听审路由下，
  `frame_delta`
  这类旧候选更不可能单独解释主问题。

### 3. `active_template + delta` 也只做到 `20 / 24`
- `active_template_delta_targeted_summary.best_combo`
  - `template_lambda = 1.0`
  - `delta_lambda = 3.0`
  - `total_wins = 20 / 24`
- residual：
  - `target::chapter3_2_firefly_212`
  - `target::chapter3_2_firefly_155`

## 四、结论口径
- 当前应把 `293`
  视为：
  - 对 gate-on 路由的历史 probe
  - 不是当前真实听审主路由的最终 objective 口径
- 当前新的正式口径应是：
  - corrected baseline gate-off 听审路由下，
    objective permissiveness
    依然成立，
    而且比旧 gate-on probe 更严重
- 因而下一步不再默认：
  - 直接重启 `acttmpl005_delta6`
    或同族旧 objective 候选
- 应转去：
  - 当前真实听审语义下的 collapse 根因定位
  - 尤其是 `fusion / fused_hidden`
    与 decode semantics 的关系
