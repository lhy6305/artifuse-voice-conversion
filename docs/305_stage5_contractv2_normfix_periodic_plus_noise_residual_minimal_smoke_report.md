# 2026-03-24 Stage5 `contractv2_normfix` `periodic_plus_noise_residual` 最小 smoke 报告

## 结论
- 本轮按既定结构计划，
  在双路 decoder
  之后继续引入更强先验：
  - `periodic`
    路作为主干
  - `noise`
    路只作为残差注入
- 具体结构为：
  - `periodic_frames = periodic_waveform_decoder(periodic_hidden)`
  - `noise_residual = noise_residual_decoder(noise_hidden)`
  - `noise_residual_gate = sigmoid(gate_head(noise_hidden, periodic_gate, noise_gate))`
  - `waveform_frames = tanh(periodic_frames + scale * noise_residual_gate * noise_residual)`
- 当前结果说明：
  1. 这条结构先验
     **比 baseline 明显更强**
  2. 但相对上一轮
     `dual_branch_mix`
     ，并没有形成决定性胜出
  3. 尤其是：
     - `adjacent cosine`
       仍只出现很小变化
     - `decoded_to_target_rms_ratio`
       仍明显偏低
- 因而按照当前门槛：
  - **本轮仍不导出听审包**

## 一、结构改动
- 新增
  `waveform_decoder_mode = periodic_plus_noise_residual`
- 与上一轮
  `dual_branch_mix`
  的区别是：
  1. 不再让
     `noise`
     路与
     `periodic`
     路对称混合
  2. 改为：
     - `periodic`
       负责主体 waveform
     - `noise`
       只负责附加残差
  3. 并用一个基于：
     - `noise_hidden`
     - `periodic_gate`
     - `noise_gate`
     的标量 gate
     控制残差强度

## 二、运行配置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 有效训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodic_plus_noise_residual_smoke_round1_1/`
- smoke 配置：
  - `waveform_decoder_mode = periodic_plus_noise_residual`
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

### `dual_branch_mix`
- `loss_waveform = 0.115348`
- `loss_stft = 0.529199`
- `loss_rms_guard = 0.253930`
- `loss_active_template = 0.386726`
- `loss_frame_adjacent_cosine = 330.408142`
- `decoded_to_target_rms_ratio = 0.792719`

### `periodic_plus_noise_residual`
- `loss_waveform = 0.115785`
- `loss_stft = 0.542432`
- `loss_rms_guard = 0.263711`
- `loss_active_template = 0.364784`
- `loss_frame_adjacent_cosine = 329.895932`
- `decoded_to_target_rms_ratio = 0.788134`

### validation 解读
1. 相比 baseline，
   新结构依然大幅改善：
   - `waveform`
   - `stft`
   - `active_template`
2. 相比
   `dual_branch_mix`
   ：
   - `active_template`
     更好
   - `adjacent cosine`
     也略好
   - 但
     `waveform / stft`
     略差
   - `rms_guard`
     仍更差
3. 这说明：
   - 非对称
     `periodic 主干 + noise 残差`
     先验
     是合理方向
   - 但当前的
     frame-level
     标量残差 gate
     还不够

## 四、fixed 6 条 aggregate

### baseline
- `loss_waveform = 0.125503`
- `loss_stft = 0.602313`
- `loss_rms_guard = 0.107393`
- `loss_active_template = 0.497106`
- `loss_frame_adjacent_cosine = 315.431819`
- `decoded_to_target_rms_ratio = 0.908930`

### `dual_branch_mix`
- `loss_waveform = 0.116400`
- `loss_stft = 0.535268`
- `loss_rms_guard = 0.216017`
- `loss_active_template = 0.363578`
- `loss_frame_adjacent_cosine = 315.077474`
- `decoded_to_target_rms_ratio = 0.808070`

### `periodic_plus_noise_residual`
- `loss_waveform = 0.116172`
- `loss_stft = 0.540959`
- `loss_rms_guard = 0.231634`
- `loss_active_template = 0.342115`
- `loss_frame_adjacent_cosine = 314.614802`
- `decoded_to_target_rms_ratio = 0.796210`

### fixed 6 解读
1. 相比 baseline：
   - `waveform`
     更好
   - `stft`
     更好
   - `active_template`
     更好
2. 相比
   `dual_branch_mix`
   ：
   - `waveform`
     略好
   - `active_template`
     更好
   - `adjacent cosine`
     略好
   - 但
     `stft`
     略差
   - `rms_guard`
     更差
   - `decoded_to_target_rms_ratio`
     进一步下降
3. 因而它更像是：
   - **方向更合理**
   - 但**当前实现还不够稳**

## 五、当前阶段判断
1. 到目前为止，
   结构路线已经连续给出同一结论：
   - 改 decoder 结构
     确实比调 loss
     更有效
2. 当前新结果进一步说明：
   - `noise`
     作为残差注入
     比对称混合更符合语音先验
3. 但当前真正没解决的，
   仍是两个问题：
   - 帧间站稳性
   - 能量稳态
4. 所以当前不应把这轮写成：
   - 已接近可听语音
   - 或值得打断用户去听

## 六、为什么这轮仍不导包
1. 用户已明确要求：
   - 除非信号明显变强，
     否则不要导听审包
2. 当前虽然结构方向继续改善，
   但：
   - `adjacent cosine`
     仍没有足够强的改善幅度
   - `decoded_to_target_rms_ratio`
     仍明显恶化
3. 因此当前仍属于：
   - 不值得占用人工听审时间

## 七、下一步建议
1. 下一条最有价值的结构升级，
   不是再扫：
   - residual scale
   - gate weight
   - 之类小参数
2. 更合理的下一个结构实验应是：
   - 把当前
     frame-level
     标量残差 gate
     升级成
     **subframe-level / sample-shape**
     的残差调制
3. 更具体地说，
   建议改成：
   - `periodic_frames`
     作为主干
   - `noise_residual`
     先经过一个
     frame-local
     shape/envelope
     头
   - 再按更细粒度地注入
   而不是只用一个
   每帧标量

## 一句话结论
- `periodic_plus_noise_residual`
  比
  `dual_branch_mix`
  更像一个合理方向，
  但当前收益仍主要停留在
  共享量化指标层面，
  还没有强到值得导出听审包；
  下一步应继续升级为
  **更细粒度的 residual 注入结构**，
  而不是回到参数微扫。
