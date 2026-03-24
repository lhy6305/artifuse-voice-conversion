# 2026-03-24 Stage5 `contractv2_normfix` decoder-side `branch_mean` forward-path mix sweep 报告

## 结论
- 本轮没有继续做
  loss-only
  小扫，
  而是直接改了
  decoder
  实际看到的 hidden：
  - `decoder_hidden = (1 - alpha) * fused_hidden + alpha * branch_mean`
  - 其中
    `branch_mean = 0.5 * (periodic_hidden + noise_hidden)`
- 已完成
  `alpha = 0.15 / 0.30 / 0.50`
  的
  4-step smoke
  微扫。
- 当前最有价值的点是：
  - **`alpha = 0.30`**
- 但这条线还不能写成：
  - 已摆脱 buzz-only
  - 或已可直接晋级长训
- 更准确的阶段结论是：
  1. 直接改
     decoder
     输入分布，
     **比 loss-only 更能真正推动共享指标**
  2. 但当前这条
     线性 mix
     仍未触达：
     - `adjacent cosine`
       的实质改善
     - RMS/能量稳态
       的同步修复
  3. 因而这轮的价值是：
     - 证明
       **forward-path 干预方向是对的**
     - 但也同时说明：
       **仅线性混入 branch_mean 仍不够**

## 一、背景
- `docs/301`
  已确认：
  - `fused_hidden_branch_mean=0.25`
    这条
    loss-only
    候选
    人工听审仍是
    pure buzz
- 所以本轮不再继续：
  - `branch_mean_weight`
    小 sweep
- 而是改做更直接的问题提问：
  - 如果训练和导出时，
    真正让 decoder
    看到混入
    `branch_mean`
    的 hidden，
    系统会不会比
    loss-only
    更明显地离开当前失败区

## 二、实现改动
- 已在以下代码中接入
  `decoder_branch_mean_mix_alpha`
  参数：
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/cli.py`
- 具体语义：
  - 保留
    `fused_hidden`
    作为表征与 loss 观测值
  - 新增
    `decoder_hidden`
    作为真正送入
    `waveform_decoder`
    的输入
  - 当
    `alpha > 0`
    时：
    - `decoder_hidden`
      由
      `fused_hidden`
      与
      `branch_mean`
      线性混合得到
- 导出侧也已同步接通同一参数，
  因此：
  - checkpoint
    可按训练时同口径重建
  - 导出听审包
    也能准确复现该 forward-path

## 三、运行配置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- smoke 公共配置：
  - `num_steps = 4`
  - `packages_per_step = 4`
  - `validation_interval = 2`
  - `checkpoint_interval = 2`
  - `device = cuda:0`
  - `seed = 20260324`
  - `deterministic = true`
  - `activity_gate_weight = 0.2`
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `active_template_weight = 0.0`
  - `frame_delta_weight = 0.0`
  - `frame_adjacent_cosine_weight = 0.0`
  - `fused_hidden_template_weight = 0.0`
  - `fused_hidden_delta_weight = 0.0`
  - `fused_hidden_branch_mean_weight = 0.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- 三个有效训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_decoder_mix015_smoke_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_decoder_mix030_smoke_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_decoder_mix050_smoke_round1_1/`

## 四、step4 validation 对比

### baseline
- `loss_waveform = 0.125092`
- `loss_stft = 0.601828`
- `loss_rms_guard = 0.155673`
- `loss_active_template = 0.503176`
- `loss_frame_adjacent_cosine = 330.772777`
- `decoded_to_target_rms_ratio = 0.899397`

### `alpha = 0.15`
- `loss_waveform = 0.123086`
- `loss_stft = 0.597514`
- `loss_rms_guard = 0.172624`
- `loss_active_template = 0.487087`
- `loss_frame_adjacent_cosine = 330.789395`
- `decoded_to_target_rms_ratio = 0.878597`

### `alpha = 0.30`
- `loss_waveform = 0.121521`
- `loss_stft = 0.588136`
- `loss_rms_guard = 0.185487`
- `loss_active_template = 0.434199`
- `loss_frame_adjacent_cosine = 330.742817`
- `decoded_to_target_rms_ratio = 0.864195`

### `alpha = 0.50`
- `loss_waveform = 0.121704`
- `loss_stft = 0.594520`
- `loss_rms_guard = 0.175172`
- `loss_active_template = 0.444536`
- `loss_frame_adjacent_cosine = 330.761154`
- `decoded_to_target_rms_ratio = 0.872239`

### validation 解读
1. `alpha = 0.30`
   是三者里最强：
   - `loss_waveform`
     最低
   - `loss_stft`
     最低
   - `loss_active_template`
     也最低
2. 相比 baseline，
   `alpha = 0.30`
   的主要变化是：
   - `loss_waveform`
     `0.125092 -> 0.121521`
     约 `-2.85%`
   - `loss_stft`
     `0.601828 -> 0.588136`
     约 `-2.27%`
   - `loss_active_template`
     `0.503176 -> 0.434199`
     约 `-13.71%`
3. 但代价同样明确：
   - `loss_rms_guard`
     `0.155673 -> 0.185487`
     约 `+19.15%`
   - `decoded_to_target_rms_ratio`
     `0.899397 -> 0.864195`
     进一步偏低
4. `loss_frame_adjacent_cosine`
   基本不动，
   说明当前线性 mix
   还没有真正解决：
   - active-frame
     相邻帧过高相似性

## 五、fixed 6 条 aggregate

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### baseline
- `loss_waveform = 0.125503`
- `loss_stft = 0.602313`
- `loss_rms_guard = 0.107393`
- `loss_active_template = 0.497106`
- `loss_frame_adjacent_cosine = 315.431819`
- `decoded_to_target_rms_ratio = 0.908930`

### `alpha = 0.30`
- `loss_waveform = 0.121969`
- `loss_stft = 0.590654`
- `loss_rms_guard = 0.139043`
- `loss_active_template = 0.426038`
- `loss_frame_adjacent_cosine = 315.400007`
- `decoded_to_target_rms_ratio = 0.873627`

### fixed 6 解读
1. 与 validation
   保持同方向：
   - `waveform`
     更好
   - `stft`
     更好
   - `active_template`
     明显更好
2. 其中
   `loss_active_template`
   从
   `0.497106`
   降到
   `0.426038`
   约 `-14.30%`
3. 但：
   - `loss_rms_guard`
     从
     `0.107393`
     升到
     `0.139043`
     约 `+29.47%`
   - `decoded_to_target_rms_ratio`
     从
     `0.908930`
     降到
     `0.873627`
4. `adjacent cosine`
   几乎不变，
   再次说明当前收益
   主要来自：
   - decoder
     输入 manifold
     被改动后的
     谱形/模板层改善
   而不是
   帧间相似性主问题

## 六、听审包
- 已导出当前最有价值候选：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_decoder_mix030_smoke_round1_1/`
- 关键导出设置：
  - `listening_audio_source = decoded_pitch_matched`
  - `pitch_match_reference = aligned_target`
  - `use_predicted_activity_gate = true`
  - `predicted_activity_gate_apply_mode = pre_overlap_add`
  - `decoder_branch_mean_mix_alpha = 0.30`
- baseline 对照包继续使用：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`

## 七、阶段判断
1. 相比
   `branch_mean`
   loss-only，
   当前结论更偏正面：
   - 直接改
     decoder
     输入分布
     的确更有效
2. 但这条线还不能写成：
   - speech emergence
     已出现
   - 或 linear mix
     已足够
3. 更准确的判断是：
   - **forward-path 是对的**
   - 但
     **当前线性 mix 还不够强，也不够稳**

## 八、下一步建议
1. 第一优先仍是：
   - 先听
     `decoder_mix030`
     对照 baseline
2. 如果听感仍是 pure buzz，
   下一步不建议再做：
   - `0.20 / 0.35 / 0.40`
     这种同类微扫
3. 那时更合理的升级应转向：
   - 非线性或调度式 forward-path
     干预
   - 或更直接的
     decoder 训练范式改造

## 一句话结论
- 这轮已经证明：
  **真正改 decoder 输入**
  比
  `branch_mean`
  这类
  loss-only
  拉近更有用；
  但当前最佳点
  `alpha = 0.30`
  仍只是把系统往正确方向推了一截，
  还没有显示出足以宣告脱离
  buzz-only
  区域的证据。
