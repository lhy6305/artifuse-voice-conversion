# 2026-03-26 Stage5 native teacher `v2core_aper_energy_only_v1` target contract fail-fast 报告

## 结论
- 这条 `target_contract_mode = v2core_aper_energy_only_v1` 路线也应正式停线。
- 它不是“没真实生效”的假实验：
  - full-split package 已完整重导
  - fullsplit24 训练、checkpoint selection、validation3 真实 `decoded.wav` 都已跑通
- 但最终结果依然是否定：
  - `validation3` 真实导出仍是 `3/3 auto_reject_obvious_buzz`
  - 相对 corrected native baseline，
    三条样本的：
    - `loss_total`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    都明显更差
- 当前可以更硬地说：
  - 不是“legacy proxy 里把 event_presence_proxy 混进 noise_gate_target”这件事本身在害当前 native teacher
  - 直接把 noise gate 收缩成纯 `aper * E_log_rms_norm`
    只会把 native teacher 推向更亮、更硬的 buzz

## 一、本轮动机
- 当前 Stage5 主线已经连续否掉：
  - decoder mode family
  - recurrent / residual decoder family
  - simple gate-masked spectral target
  - `activity_gate` 同层开关
  - `teacher_e_evt_gate_targets_v1`
- 代码里仍保留一条更保守、且尚未完成 fullsplit24 fail-fast 的 supervision-side contract：
  - `v2core_aper_energy_only_v1`
- 它的核心变化是：
  - `periodic_gate_target = vuv`
  - `noise_gate_target = aper * E_log_rms_norm`
  - 显式排除旧 `event_presence_proxy`
    以及 `e_evt` 相关 event/boundary 维度
- 这条线要回答的问题是：
  - 当前 native teacher 的主故障是否来自
    `legacy_proxy_v2`
    把 noise gate 绑得过宽，
    于是 decoder 一直吃到过多 event-presence/noise 激活

## 二、产物目录

### 1. full-split dataset package
- `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_aperenergyonly_round1_1/offline_mvp_nores_vocoder_dataset_index.json`

### 2. training loop
- `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_aperenergyonly_fullsplit24_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

### 3. checkpoint selection
- `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_aperenergyonly_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`

### 4. 真实 decoded 导出
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_aperenergyonly_fullsplit24_validation3_round1_1/nores_vocoder_audio_export.json`

## 三、dataset package 核验

### 1. package 规模
- `train = 592`
- `validation = 66`
- `total = 658`

### 2. 并行导出参数
- `worker_processes = 4`
- 导出耗时：
  - `duration_sec = 466.042451`

### 3. 合同是否真实生效
- dataset index 顶层：
  - `target_contract_mode = v2core_aper_energy_only_v1`
- 单包 `target_contract`：
  - `contract_family = v2core_aper_energy_only_v1`
  - `periodic_gate_formula = vuv`
  - `noise_gate_formula = aper * E_log_rms_norm`
  - `uses_explicit_e_evt = false`
  - `excluded_e_evt_dimensions`
    包含：
    - `p_frication`
    - `p_stop_closure`
    - `p_burst`
    - `p_voicing`
    - `p_pause_boundary`
    - `p_terminal_boundary`
    - `p_final_clause_boundary`
- 因而本轮不是 metadata-only；
  target contract 的 supervision 语义已经真实切换

## 四、训练口径
- 数据集：
  - `offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_aperenergyonly_round1_1`
- runtime：
  - `device = cuda:0`
- 训练预算：
  - `num_steps = 24`
  - `packages_per_step = 4`
  - `validation_interval = 12`
  - `checkpoint_interval = 12`
  - `sampler_mode = shuffle`
  - `seed = 20260326`
  - `deterministic = true`
- 保持和当前 native teacher baseline 同层可比的主损失：
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `activity_gate_weight = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- forward-path 不改：
  - `waveform_decoder_mode = fused_single`
  - `decoder_branch_mean_mix_alpha = 0.0`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = false`

## 五、训练与 checkpoint 结果

### 1. 选中的 checkpoint
- `best_validation_checkpoint.step = 24`
- `loss_total = 0.792035`
- `loss_waveform = 0.119549`
- `loss_stft = 0.315097`
- `loss_rms_guard = 0.12772`
- `decoded_to_target_rms_ratio = 0.903642`

### 2. 如何解读
- 这说明：
  - 这条线不是完全静止
  - 训练在数值上确实收敛到了一个稳定解
- 但这组训练数值并没有转化成更好的真实 decoded：
  - best-validation 只是说明当前 bootstrap objective 下更容易拟合
  - 不说明 native teacher 已脱离 buzz 假解

## 六、validation3 真实 decoded 结果

### 1. buzz gate 汇总
- `record_count = 3`
- `auto_reject_count = 3`
- `review_required_count = 0`
- `all_records_auto_reject = true`

### 2. 三条记录
- `target::chapter3_3_firefly_162`
- `target::chapter3_3_firefly_138`
- `target::chapter3_4_firefly_106`

## 七、和 corrected baseline 的对照

### 1. `target::chapter3_3_firefly_162`
- baseline：
  - `loss_total = 0.55544`
  - `spectral_centroid_gap_hz = 4999.124195`
  - `spectral_high_band_energy_ratio_gap = 0.338207`
  - `decoded_frame_template_cosine_mean = 0.989028`
  - `decoded_frame_adjacent_cosine_mean = 0.991827`
- candidate：
  - `loss_total = 0.805707`
  - `spectral_centroid_gap_hz = 10117.139012`
  - `spectral_high_band_energy_ratio_gap = 0.635497`
  - `decoded_frame_template_cosine_mean = 0.992416`
  - `decoded_frame_adjacent_cosine_mean = 0.993392`

### 2. `target::chapter3_3_firefly_138`
- baseline：
  - `loss_total = 0.595536`
  - `spectral_centroid_gap_hz = 4886.46595`
  - `spectral_high_band_energy_ratio_gap = 0.28214`
  - `decoded_frame_template_cosine_mean = 0.995464`
  - `decoded_frame_adjacent_cosine_mean = 0.998852`
- candidate：
  - `loss_total = 0.808913`
  - `spectral_centroid_gap_hz = 10039.378518`
  - `spectral_high_band_energy_ratio_gap = 0.579118`
  - `decoded_frame_template_cosine_mean = 0.996713`
  - `decoded_frame_adjacent_cosine_mean = 0.999096`

### 3. `target::chapter3_4_firefly_106`
- baseline：
  - `loss_total = 0.540066`
  - `spectral_centroid_gap_hz = 4982.211332`
  - `spectral_high_band_energy_ratio_gap = 0.291194`
  - `decoded_frame_template_cosine_mean = 0.993396`
  - `decoded_frame_adjacent_cosine_mean = 0.999483`
- candidate：
  - `loss_total = 0.795788`
  - `spectral_centroid_gap_hz = 10054.571387`
  - `spectral_high_band_energy_ratio_gap = 0.58119`
  - `decoded_frame_template_cosine_mean = 0.996873`
  - `decoded_frame_adjacent_cosine_mean = 0.999685`

## 八、解读
1. 这条线已经把一个还没被正式否掉的问题回答清楚了：
   - 当前 native teacher 的主故障，
     不是“noise gate 里混了 event_presence_proxy，所以只要改成纯 `aper * E` 就会更干净”
2. 真实结果恰好相反：
   - `aper_energy_only`
     让三条 validation3 样本的
     高频亮度 gap 全部翻倍左右
   - `loss_total`
     也全部比 corrected baseline 更差
3. 从 decoded 指标看，
   它不只是“亮了一点”，
   而是继续共享当前 native teacher 的同类失败模式：
   - short-time structure 仍高度 template-collapse
   - frame RMS 仍主要跟随 target envelope
   - 高频 harsh buzz 更重
4. 因而这条线不能解释成：
   - “方向是对的，只差再扫 `aper / energy` 的混合比例”
   - 目前更合理的口径是：
     `noise_gate_target = aper * E_log_rms_norm`
     这种更窄、更保守的 contract
     并不会自然把 native teacher 拉出当前假解

## 九、当前主线判断
- 到这一步，
  当前 Stage5 native teacher 已经明确否掉：
  - decoder mode family
  - recurrent / residual decoder family
  - `teacher_e_evt_gate_targets_v1`
  - `gate_masked_halfsplit_v1`
  - `activity_gate_weight = 0.0 + no gated reconstruction`
  - `v2core_aper_energy_only_v1`
- 因此当前不再值得继续：
  - `target_contract_mode`
    现有这几条同层 gate 公式小改
  - `aper / energy / event_presence`
    的简单加减法式 supervision 改写
- 下一步必须继续上收到：
  - 更根本的 objective meaning
  - noise/periodic target family 本身
  - 以及“当前 decoder 到底被什么 target 语义诱导成 template-collapse”

## 一句话结论
- `v2core_aper_energy_only_v1`
  这条更保守的 native teacher target contract
  在真实 `validation3 decoded.wav`
  上仍是 `3/3 auto_reject_obvious_buzz`，
  且相对 corrected baseline 明显更差，
  应正式停线。
