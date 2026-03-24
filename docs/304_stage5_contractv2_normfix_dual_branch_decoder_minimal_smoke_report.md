# 2026-03-24 Stage5 `contractv2_normfix` 双路 waveform decoder 最小 smoke 报告

## 结论
- 本轮已按结构级路线，
  把原来的单路：
  - `waveform_decoder(fused_hidden)`
  升级成双路：
  - `periodic_waveform_decoder(periodic_hidden)`
  - `noise_waveform_decoder(noise_hidden)`
  - 再用轻量
    frame-level
    mixer gate
    融合两路 waveform frames
- 这条结构候选的量化结果，
  **明显强于此前的 loss-only 和 linear mix**
  ：
  - `loss_waveform`
    明显下降
  - `loss_stft`
    明显下降
  - `loss_active_template`
    明显下降
- 但当前还不能把它写成：
  - 已值得人工听审
  - 或已足够晋级长训
- 因为两个关键失败信号仍在：
  1. `loss_frame_adjacent_cosine`
     仍几乎不动
  2. `decoded_to_target_rms_ratio`
     进一步恶化到
     `0.79 ~ 0.81`
- 所以按照当前停损标准，
  **本轮不导出听审包**。

## 一、结构改动
- 新增
  `waveform_decoder_mode`
  参数：
  - `fused_single`
  - `dual_branch_mix`
- 在
  `dual_branch_mix`
  模式下：
  1. `periodic_hidden`
     进入
     `periodic_waveform_decoder`
  2. `noise_hidden`
     进入
     `noise_waveform_decoder`
  3. `waveform_frame_mixer`
     读取：
     - `periodic_hidden`
     - `noise_hidden`
     - `periodic_gate`
     - `noise_gate`
  4. 输出一个
     frame-level
     标量 gate，
     用于融合两路 decoder frame
- 旧的
  `fused_single`
  路径仍保留，
  旧 checkpoint
  读取兼容未破坏

## 二、运行配置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 有效训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_dual_branch_decoder_smoke_round1_1/`
- smoke 配置：
  - `waveform_decoder_mode = dual_branch_mix`
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
  - `decoder_branch_mean_mix_alpha = 0.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 三、step4 validation 对比

### baseline
- `loss_waveform = 0.125092`
- `loss_stft = 0.601828`
- `loss_rms_guard = 0.155673`
- `loss_active_template = 0.503176`
- `loss_frame_adjacent_cosine = 330.772777`
- `decoded_to_target_rms_ratio = 0.899397`

### dual-branch decoder
- `loss_waveform = 0.115348`
- `loss_stft = 0.529199`
- `loss_rms_guard = 0.253930`
- `loss_active_template = 0.386726`
- `loss_frame_adjacent_cosine = 330.408142`
- `decoded_to_target_rms_ratio = 0.792719`

### validation 解读
1. 相比 baseline：
   - `loss_waveform`
     `0.125092 -> 0.115348`
     约 `-7.79%`
   - `loss_stft`
     `0.601828 -> 0.529199`
     约 `-12.07%`
   - `loss_active_template`
     `0.503176 -> 0.386726`
     约 `-23.14%`
2. 这说明：
   - **双路 decoder**
     的确比
     单路 fused-hidden
     更能改变输出行为
3. 但代价同样很大：
   - `loss_rms_guard`
     `0.155673 -> 0.253930`
     约 `+63.12%`
   - `decoded_to_target_rms_ratio`
     `0.899397 -> 0.792719`
4. `loss_frame_adjacent_cosine`
   只从
   `330.772777`
   到
   `330.408142`，
   仍然基本不动

## 四、fixed 6 条 aggregate

### baseline
- `loss_waveform = 0.125503`
- `loss_stft = 0.602313`
- `loss_rms_guard = 0.107393`
- `loss_active_template = 0.497106`
- `loss_frame_adjacent_cosine = 315.431819`
- `decoded_to_target_rms_ratio = 0.908930`

### dual-branch decoder
- `loss_waveform = 0.116400`
- `loss_stft = 0.535268`
- `loss_rms_guard = 0.216017`
- `loss_active_template = 0.363578`
- `loss_frame_adjacent_cosine = 315.077474`
- `decoded_to_target_rms_ratio = 0.808070`

### fixed 6 解读
1. 与 validation
   保持同方向：
   - `waveform`
     更好
   - `stft`
     更好
   - `active_template`
     更好
2. 其中：
   - `loss_waveform`
     约 `-7.25%`
   - `loss_stft`
     约 `-11.13%`
   - `loss_active_template`
     约 `-26.86%`
3. 但：
   - `loss_rms_guard`
     `0.107393 -> 0.216017`
     约翻倍
   - `decoded_to_target_rms_ratio`
     `0.908930 -> 0.808070`
4. `adjacent cosine`
   仍几乎没有实质改善，
   所以当前还不能把这些共享指标改善，
   直接解释成：
   - 已接近 speech emergence

## 五、当前阶段判断
1. 到目前为止，
   这是第一条在结构级上
   真正显著推动：
   - `waveform`
   - `stft`
   - `active_template`
   三者同步改善的路线
2. 这进一步支持：
   - 当前主瓶颈
     确实不只是
     loss weight，
     而是
     decoder 结构
3. 但当前这版
   `dual_branch_mix`
   仍然没有解决：
   - 帧间 stationarity
   - 能量稳态
4. 因而这轮更适合写成：
   - **结构方向成立**
   - 但**当前实现还不够成熟**

## 六、为什么这轮不导出听审包
1. 用户已明确要求：
   - 除非信号明显变强，
     否则不要导听审包
2. 当前虽然共享指标改善更强，
   但：
   - `adjacent cosine`
     基本没动
   - `RMS ratio`
     明显更差
3. 在这两个失败标志仍在的情况下，
   当前不值得打断用户去听

## 七、下一步建议
1. 下一条最有价值的结构升级，
   不建议回退到：
   - loss sweep
   - linear mix sweep
2. 更合理的下一个结构实验应是：
   - **把当前 frame-level 标量 mixer**
     升级为
     **sample-level 或 subframe-level mixing**
   - 或者：
     - 保留
       `periodic_frames`
     - 让
       `noise_frames`
       只作为残差注入
3. 核心原因是：
   - 当前双路结构已经证明
     “分路 decoder”
     有效
   - 但单个
     frame scalar gate
     过于粗糙，
     还不足以同时处理：
     - 细粒度帧内结构
     - 能量稳态

## 一句话结论
- 双路 waveform decoder
  是目前最像
  正确结构方向
  的候选；
  但这版
  frame-level
  标量 mixer
  仍然没有把系统推出
  buzz-only
  失败区，
  因此当前只记录为：
  **结构方向成立，但还不到值得听审的程度。**
