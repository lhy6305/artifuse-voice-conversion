# 2026-03-24 teacher-first 最小链路 inference adaptation probe 报告

## 结论
- 当前最值得继续推进的，
  已经不是：
  - “再解释 loss
     为什么高/低”
- 而是：
  - 把最小 user-line
    链路推进到
    第一次明确脱离 buzz
- 本轮 probe
  的当前最佳候选是：
  - `reference_affine_match`
  - `event_probs=reference_mean`
  - `gate_off`
- 这套组合已经被接进
  主 demo 命令，
  并导出正式产物：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_affine_events_refmean_gateoff_round1_1/`

## 一、当前为什么不该先回到 loss 解释
- 当前训练主线已经完成：
  - `contractv2_normfix`
    `best_validation = 0.554104`
  - 略优于旧 baseline
    `0.564671`
- 但 user-line
  最小链路仍没有
  可正式转正的听感结论
- 所以当前最高信息量问题是：
  - 为什么 validation
    已改善，
    user-line
    仍处于诊断态

## 二、applicability probe：上游 scaffold 不是主矛盾

### 执行
- 命令：
```powershell
.\python.exe manage.py analyze-offline-mvp-teacher-first-vc-applicability `
  --input-audio data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_applicability_probe_contractv2_normfix_parallel107 `
  --device cuda `
  --max-audio-sec 3.0 `
  --chunk-ms 33.333333
```

### 结果
- periodic：
  - `mean_abs_z_median = 0.059605`
  - `mean_abs_z_max = 1.369596`
  - `out_of_q01_q99_fraction_mean = 0.018889`
- noise：
  - `mean_abs_z_median = 0.044703`
  - `mean_abs_z_max = 1.312041`
  - `out_of_q01_q99_fraction_mean = 0.021145`

### 当前判断
- 这说明：
  - `parallel107`
    在 `contractv2_normfix`
    下的 scaffold
    并不算严重 OOD
- 因此当前更合理的解释是：
  - user-line 问题
    主要不是 contract
    一出来就完全偏离
  - 而是 decoder
    在把中等偏移
    放大

## 三、decoder-behavior probe：默认最小链路偏离很大

### 默认链路
- 默认最小链路：
  - 当前 `normfix`
    best validation
  - `post_ola_envelope`
  - gate on
  - 无 inference-only
    normalization
- probe 结果：
  - `centroid_hz = 6004.709495`
  - `high_band_energy_ratio = 0.352201`
  - `abs_z_median = 6.129032`
  - `outside_frac = 0.952381`

### 当前解释
- 这说明默认最小链路的 decoder 行为，
  相比同 checkpoint
  在训练内分布上的 reference
  输出，
  偏离仍很大

## 四、当前扫过的 inference-only 候选

### 1. 单纯 gate off
- 结果：
  - `centroid_hz = 6080.493021`
  - `high_band_energy_ratio = 0.357483`
  - `abs_z_median = 5.354968`
- 判断：
  - 单关 gate
    信息量有限，
    不足以把行为拉回参考区

### 2. 单纯 `reference_q01_q99_clip`
- 结果几乎与默认链路一致
- 判断：
  - 只做裁剪
    对当前 case
    基本没帮助

### 3. 单纯 `reference_affine_match`
- 结果：
  - `centroid_hz = 5824.803320`
  - `high_band_energy_ratio = 0.341817`
  - `abs_z_median = 1.514207`
  - `outside_frac = 0.380952`
- 判断：
  - 这是第一条
    明显把 decoder
    行为拉回 reference
    区间的候选

### 4. `reference_affine_match + event_probs=reference_mean`
- gate on：
  - `centroid_hz = 5848.719277`
  - `high_band_energy_ratio = 0.344490`
  - `abs_z_median = 1.621951`
  - `outside_frac = 0.380952`
- gate off：
  - `centroid_hz = 5930.847097`
  - `high_band_energy_ratio = 0.347720`
  - `abs_z_median = 1.302657`
  - `outside_frac = 0.333333`

### 当前最佳候选
- 当前以 probe
  指标看，
  最优候选是：
  - `reference_affine_match`
  - `event_probs=reference_mean`
  - `gate_off`
- 原因：
  - 当前
    `abs_z_median`
    最低
  - `outside_frac`
    也是当前已扫候选里最低

## 五、主 demo 已接入 inference-only 适配参数

### 代码
- 已在：
  - `src/v5vc/teacher_first_vc_demo.py`
  - `src/v5vc/cli.py`
  接入：
  - `--normalization-strategy`
  - `--control-family-override`
  - `--reference-package`
  - `--reference-package-limit`

### 当前实验产物
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_contractv2_normfix_parallel107_affine_events_refmean_gateoff_round1_1 `
  --device cuda `
  --max-audio-sec 3.0 `
  --vocoder-checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --normalization-strategy reference_affine_match `
  --control-family-override event_probs=reference_mean `
  --no-use-predicted-activity-gate
```

### 结果
- `status = succeeded`
- `decoded_audio_exists = true`
- `decoded_audio_sec = 2.998639`
- `decoded_waveform_rms = 0.17213`
- `centroid_hz = 5930.847097`
- `high_band_energy_ratio = 0.347720`

## 六、关于当前 `high_risk` 判断的正式提醒

### 观察
- 当前 probe 的 reference
  健康输出分布本身就接近：
  - `centroid ≈ 5859 Hz`
  - `high_band_energy_ratio ≈ 0.345`
- 但旧
  `teacher_first_runtime_risk_v1`
  的固定阈值仍是：
  - `centroid >= 3200 Hz`
  - `high_band_energy_ratio >= 0.25`

### 当前判断
- 这意味着：
  - 旧 risk heuristic
    很可能仍停留在
    更早期、
    更坏 checkpoint
    的 user-line
    经验区间
- 因而从现在开始，
  不能再把：
  - `status = high_risk`
  直接等同于：
  - “当前仍然一定是 buzz”

## 七、当前边界
- 当前还没有
  人工听审结果，
  所以不能正式写成：
  - 最优候选已经
    “确认脱离 buzz”
- 现在能正式写的只有：
  - 它是目前最接近
    reference decoder
    分布的最小链路候选

## 八、下一步
1. 直接听审对比：
   - 默认
     `contractv2_normfix`
     `parallel107`
   - `affine + event_probs refmean + gate_off`
     候选
2. 若候选首次明确脱离 buzz，
   把它固化为：
   - 实验线当前最小 user-line
     适配口径
3. 同时重做
   user-line risk
   制度，
   不再只靠旧固定阈值

## 一句话结论
- 当前最小链路推进的最高价值方向，
  已经从 loss 解释
  转为
  inference-only 适配；
  目前最有希望的候选是
  `reference_affine_match + event_probs=reference_mean + gate_off`，
  但是否首次真正脱离 buzz，
  仍需人工听审确认。
