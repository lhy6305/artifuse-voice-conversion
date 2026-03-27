# 2026-03-27 Stage5 output-head `bpae01` 重定位结论与最小听审交付报告

## 结论
- 本轮已把一个更直接的问题打到训练图里：
  - 在 `waveform_decoder_base_logits`
    上新增
    `aper * noise_E_log_rms_norm`
    的
    `abs_zero_lag_corr`
    约束
- 新候选记为：
  - `output_head_bpae01`
- 这条线不是无效接线：
  - smoke 已确认新 loss 真正参与训练
  - fullsplit24 已跑通
  - user-line / native validation3 / stage temporal coupling
    都已回投
- 当前量化结论不是简单失败：
  - 相比上一轮已听审失败的
    `bhb01`
  - `bpae01`
    继续明显压低了三条 fixed pure-buzz 样本的
    centroid / high-band
  - native validation3
    仍保持
    `auto_reject = 0/3`
  - `decoded_post_ola_gate`
    的
    `centroid_gap / high_band_gap`
    继续从：
    - `3211.714111 / 0.198100`
    到：
    - `2516.162109 / 0.111581`
- 但这条线当前也不能升格为新主候选：
  - user-line
    `decoded_post_ola_gate`
    的
    `template`
    反而从
    `0.870602`
    回升到
    `0.887733`
  - 说明它更像是：
    - 继续把声音压暗
    - 但没有明确把系统拉离
      pure-buzz / tonal-buzz
      区间
- 更关键的结构层结论是：
  - `aper * noise_E`
    在
    `decoder_hidden -> waveform_decoder_base_logits`
    的大 jump
    确实被压平了：
    - `0.270616 -> 0.696298`
      变成
    - `0.376493 -> 0.391278`
  - 但这不等于问题被消掉：
    - 新峰值改落在
      `waveform_residual_shape_delta = 0.434913`
  - 同时
    `aper`
    和
    `noise_E`
    单项在
    `waveform_decoder_base_logits`
    上反而更强
- 因而当前正式口径应写成：
  - `bpae01`
    证明
    `aper * noise_E`
    这个乘积项本身确实是可调的
  - 但只压乘积项，
    还会把剩余问题重新分配到：
    - residual-shape 分支
    - 以及 base-logits 上更单项化的
      `aper / noise_E`
      放大
  - 所以它不是可直接 promoted 的 winner，
    也不值得开 GUI 打分；
    当前只值得做一个最小 wav 听审，
    判断它是否仍停留在 pure buzz 区间

## 一、这轮新增的训练接线
- 新增 loss：
  - `waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr_weight`
- 已补齐的文件：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- smoke 命令：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_abne_smoke_fullsplit1step_round1_1 `
  --device cuda:0 `
  --num-steps 1 `
  --packages-per-step 4 `
  --validation-interval 1 `
  --checkpoint-interval 1 `
  --sampler-mode shuffle `
  --seed 20260327 `
  --deterministic `
  --learning-rate 0.001 `
  --max-grad-norm 5.0 `
  --harmonic-weight 1.0 `
  --noise-weight 1.0 `
  --periodic-gate-weight 0.2 `
  --noise-gate-weight 0.2 `
  --activity-gate-weight 0.2 `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode pre_overlap_add `
  --fusion-mode branch_mean_contrast_residual_v1 `
  --waveform-decoder-mode fused_single `
  --use-residual-shape-branch-condition-adapter `
  --residual-shape-branch-condition-scale 1.0 `
  --residual-shape-branch-condition-mode raw_additive_v1 `
  --waveform-decoder-base-logits-high-band-excess-weight 0.1 `
  --waveform-decoder-base-logits-active-template-weight 0.1 `
  --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.1 `
  --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-weight 0.1 `
  --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.1 `
  --waveform-residual-shape-delta-noise-energy-abs-zero-lag-corr-weight 0.1
```
- smoke summary 已确认新项真实生效：
  - `loss_waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr = 0.364905`
  - `waveform_decoder_base_logits_to_aper_noise_energy_zero_corr = -0.364905`
  - `waveform_decoder_base_logits_to_aper_noise_energy_abs_zero_corr = 0.364905`

## 二、fullsplit24 候选与 probe 入口
- fullsplit24 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bhb01_bpae01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- best checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bhb01_bpae01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- validation `loss_total`：
  - `1.136829`
- user-line waveform handoff：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_headstruct_bhb01_bpae01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`
- native validation3 waveform handoff：
  - `reports/runtime/stage5_waveform_handoff_probe_headstruct_bhb01_bpae01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_val3_r1_1/`
- stage temporal coupling：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_stcp_headstruct_bhb01_bpae01_bta01_baa01_bna01_rsna01_fbmc_rs_fs24_r1_1/`

## 三、和 `bhb01` 的关键对比

### 1. user-line `decoded_post_ola_gate`
- `bhb01`
  - `template = 0.870602`
  - `activity_corr = 0.980820`
  - `centroid = 4804.712891`
  - `high_band = 0.259251`
- `bpae01`
  - `template = 0.887733`
  - `activity_corr = 0.971190`
  - `centroid = 4163.743652`
  - `high_band = 0.197849`
- 共通 diagnosis：
  - `likely_failure_already_present_by_frames_before_gate = false`
- 当前解释：
  - 更暗了，
    但更模板化了，
    所以不能把它直接写成
    `bhb01`
    的明确主观升级

### 2. native validation3 `decoded_post_ola_gate`
- `bhb01`
  - `auto_reject = 0/3`
  - `template = 0.796630`
  - `rms_corr = 0.939670`
  - `centroid_gap = 3211.714111`
  - `high_band_gap = 0.198100`
- `bpae01`
  - `auto_reject = 0/3`
  - `template = 0.824535`
  - `rms_corr = 0.932531`
  - `centroid_gap = 2516.162109`
  - `high_band_gap = 0.111581`
- 共通 diagnosis：
  - `buzz_before_predicted_activity_gate = false`
  - `primary_localization = needs_more_localization`
- 当前解释：
  - native 侧 anti-brightness
    的确继续正向，
    但并没有把 localization
    从
    `needs_more_localization`
    推进成更明确的结构胜利

### 3. temporal coupling 的真正新信息
- 对乘积项
  `aper * noise_E_log_rms_norm`
  而言：
  - `bhb01`
    - `decoder_hidden = 0.270616`
    - `base_logits = 0.696298`
    - `residual_shape = 0.497116`
  - `bpae01`
    - `decoder_hidden = 0.376493`
    - `base_logits = 0.391278`
    - `residual_shape = 0.434913`
- 这说明：
  - 原先最突出的
    `decoder_hidden -> base_logits`
    乘积 jump
    已被明显压平
  - 但乘积项并没有被消失，
    只是重新定位到：
    - residual-shape 分支成为新峰值
- 同时单项控制反而更糟：
  - `aper`
    - `base_logits = 0.654614 -> 0.790334`
  - `noise_E`
    - `base_logits = 0.705608 -> 0.841032`
- 当前解释：
  - 这条线更像是在用：
    - 降亮度
    - 重分配 coupling
    来换取量化改善
  - 而不是在生成更接近人声结构的真实解

## 四、最小 wav 听审交付
- 当前不走 GUI。
- 这轮只需要回答：
  - `output_head_bpae01`
    是否仍然是 pure buzz，
    还是已经跨出了这个门槛
- 三路固定对比：
  - `strongest_native_candidate`
  - `output_head_high_band_bhb01`
  - `output_head_bpae01`
- 生成命令：
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -InputSpecJsonl tmp/teacher_first_output_head_highband_compare_specs/input_specs_round1_1.jsonl `
  -VocoderSpecJsonl tmp/teacher_first_output_head_abne_compare_specs/vocoder_specs_round1_1.jsonl `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_bpae01_vs_bhb01_vs_strongest_round1_1 `
  -Device cuda `
  -SkipFullPassVerify
```
- 当前 bundle 状态：
  - `case_count = 3`
  - `variant_count = 3`
  - `variant_runs_succeeded = 9 / 9`
  - `positive_controls_ready = 3 / 3`
- 直接听 wav 的目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_bpae01_vs_bhb01_vs_strongest_round1_1/listening/`
- 这轮不再提供 GUI 打分说明。

## 五、听审时只看这三件事
- 相比你已经听过的
  `bhb01`
  - `bpae01`
    是否仍然只是更暗的 tonal buzz，
    还是开始出现更稳定的人声结构
- 在
  `segment_0061`
  上，
  是否只是把亮度压下去，
  但边界和主体仍保留明显 buzz 核心
- 在
  `peak_011`
  上，
  是否开始出现“像发声结构”的线索，
  还是依旧只是带音高起伏的 buzz

## 一句话结论
- `bpae01` 证明直接约束 `waveform_decoder_base_logits -> aper * noise_E` 可以压平旧的 base-logits product jump，并继续显著压低 brightness；但它没有把系统明确拉离 pure-buzz 区间，而是把剩余问题重新分配到 residual-shape 与单项 `aper / noise_E` 放大上，所以当前只值得做最小 wav 听审，不值得升格或走 GUI。
