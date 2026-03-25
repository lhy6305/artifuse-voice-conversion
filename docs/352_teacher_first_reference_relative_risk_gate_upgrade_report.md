# 352. teacher-first reference-relative 风险门升级报告

## 结论
- `teacher_first_vc_demo`
  原来的
  `teacher_first_runtime_risk_v1`
  只看绝对频谱阈值：
  - `spectral_centroid`
  - `high_band_energy_ratio`
- 这会把
  “已经接近当前 Stage5 reference decoder 分布”
  的样本也一律打成
  `high_risk`，
  误报过重。
- 本轮已经升级为：
  - `teacher_first_runtime_risk_v2_reference_relative`
  - 优先拿当前 checkpoint
    在 in-distribution
    training packages
    上的 decoder 行为
    作为 reference
  - 再对 user-line 输出做
    `reference_shift`
    判定
- 当前结果：
  - 默认链路
    不再被误判成
    `high_risk`，
    而是：
    `elevated_risk`
  - 当前最佳 inference-only
    候选
    `reference_affine_match + event_probs=reference_mean + gate_off`
    也被判为：
    `elevated_risk`
    但它的
    `reference_shift`
    明显更小，
    说明它更接近 reference
    区间

## 一、本轮代码改动
- 更新：
  - `src/v5vc/teacher_first_vc_demo.py`

### 1. 新增 reference decoder behavior 缓存
- 新目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_reference_decoder_behavior_cache/`
- 当前会按：
  - branch label
  - reference package count
  缓存：
  - `reference_decoder_behavior_summary.json`
- 目的：
  - 避免每次 demo
    重复扫同一组
    reference packages

### 2. `applicability_risk`
  接入 reference-relative 判定
- 当前 summary
  现在会额外写出：
  - `reference_decoder_behavior`
  - `applicability_risk.reference_shift`
  - `waveform_decode.decoded_scalar_metrics`
- 核心逻辑：
  - 若有 reference decoder summary，
    就计算：
    - `abs_z_median`
    - `outside_q01_q99_fraction`
  - 再结合旧绝对阈值，
    给出：
    - `high_risk`
    - `elevated_risk`
    - `low_risk`

## 二、执行命令
- 已执行：
```powershell
.\python.exe -m py_compile src/v5vc/teacher_first_vc_demo.py src/v5vc/cli.py
```

### 默认链路
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_bestval_riskv2_round1_1 `
  --device cpu `
  --max-audio-sec 3.0 `
  --vocoder-checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation
```

### 当前最佳 inference-only 候选
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_affine_events_refmean_gateoff_riskv2_round1_1 `
  --device cpu `
  --max-audio-sec 3.0 `
  --vocoder-checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --normalization-strategy reference_affine_match `
  --control-family-override event_probs=reference_mean `
  --no-use-predicted-activity-gate
```

## 三、关键结果

### 1. 默认链路
- 产物：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_bestval_riskv2_round1_1/teacher_first_vc_demo.json`
- 当前结果：
  - `heuristic_version = teacher_first_runtime_risk_v2_reference_relative`
  - `status = elevated_risk`
  - `decoded_spectral_centroid_hz = 5848.471197`
  - `decoded_spectral_high_band_energy_ratio = 0.343068`
  - `reference_shift.abs_z_median = 1.696638`
  - `reference_shift.outside_q01_q99_fraction = 0.5`

### 2. 当前最佳 inference-only 候选
- 产物：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_affine_events_refmean_gateoff_riskv2_round1_1/teacher_first_vc_demo.json`
- 当前结果：
  - `heuristic_version = teacher_first_runtime_risk_v2_reference_relative`
  - `status = elevated_risk`
  - `decoded_spectral_centroid_hz = 6011.220354`
  - `decoded_spectral_high_band_energy_ratio = 0.353249`
  - `reference_shift.abs_z_median = 0.929385`
  - `reference_shift.outside_q01_q99_fraction = 0.125`

### 3. reference cache
- 已生成：
  - `reports/runtime/offline_mvp_teacher_first_vc_reference_decoder_behavior_cache/stage5_best_validation_step72__decode_smooth3_postenv/packages_032/reference_decoder_behavior_summary.json`
  - `reports/runtime/offline_mvp_teacher_first_vc_reference_decoder_behavior_cache/stage5_best_validation_step72__decode_gateoff/packages_032/reference_decoder_behavior_summary.json`

## 四、当前判断
- 现在可以正式写死：
  1. 旧
     `risk_v1`
     的绝对阈值
     已经过时，
     不能再单独作为
     teacher-first
     用户线的主判据
  2. reference-relative
     风险门
     更符合当前真实状态：
     - 默认链路
       仍需警惕
     - 但不再能被直接写成
       obvious buzz
     - 当前最佳 inference-only
       候选
       相比默认链路，
       更接近 reference
       分布
  3. 这不等于 user-line
     已经转正，
     因为当前两个候选
     都还是
     `elevated_risk`

## 五、下一步
1. 后续 teacher-first
   的自动治理默认应采用：
   - `risk_v2`
   - 不再回退到
     `risk_v1`
2. 下一步最值钱的动作不是再争论
   “centroid 为什么高”，
   而是：
   - 围绕
     `reference_shift`
     最敏感的指标，
     继续做少量 inference-only
     候选比较
3. 只要状态仍是
   `elevated_risk`，
   就继续保留：
   - 自动不过度判死
   - 但仍要求复核
