# 2026-03-24 Stage5 `contractv2_normfix` `periodic_gate rms_floor=0.65` + periodic-path high-band restraint follow-up 报告

## 结论
- 已在当前最佳主线
  `recurrent + periodic temporal losses + periodic_gate rms_floor=0.65`
  上，
  完成一轮更窄的 periodic-path 高频能量 restraint 微扫：
  - `periodic_waveform_high_band_excess_weight = 0.02`
  - `0.05`
  - `0.1`
- 这条 restraint **确实被触发了**，
  而且方向很清楚：
  - 权重越高，
    `periodic_waveform_high_band_energy_ratio`
    越低
  - `loss_periodic_waveform_high_band_excess`
    也越低
- 但它没有形成比原始
  `rms_floor=0.65`
  更好的 Pareto 点。
- 更准确地说：
  1. 它确实在压 periodic-path 的高频占比；
  2. 同时也会把系统整体推向：
     - 更高的 RMS 比例
     - 更差的 `waveform / stft`
     - 更差的 `active_template`
     - 更差的 `adjacent cosine`
- 因而这条 high-band restraint **当前不值得导听审包**，
  也不值得继续做同构权重微扫。

## 一、实验目录
- baseline:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_smoke_round1_1/`
- `highband=0.02`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_highband002_smoke_round1_1/`
- `highband=0.05`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_highband005_smoke_round1_1/`
- `highband=0.1`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_highband01_smoke_round1_1/`

## 二、运行口径
- 保持和当前 baseline 一致：
  - `num_steps = 4`
  - `packages_per_step = 4`
  - `validation_interval = 2`
  - `checkpoint_interval = 2`
  - `seed = 20260324`
  - `deterministic = true`
  - `device = cuda:0`
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- 共同保留：
  - `waveform = 0.5`
  - `stft = 0.5`
  - `rms_guard = 0.2`
  - `activity_gate = 0.2`
  - `periodic_waveform_frame_delta = 0.25`
  - `periodic_waveform_frame_adjacent_cosine = 0.01`
  - `periodic_waveform_frame_rms_floor = 0.65`
- 唯一新变量：
  - `periodic_waveform_high_band_excess_weight`

## 三、step4 validation 对比

### baseline: `rms_floor=0.65`
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`

### `highband = 0.02`
- `loss_waveform = 0.121169`
- `loss_stft = 0.592681`
- `loss_rms_guard = 0.185520`
- `loss_active_template = 0.181613`
- `loss_frame_adjacent_cosine = 328.814077`
- `decoded_to_target_rms_ratio = 0.867795`
- `loss_periodic_waveform_high_band_excess = 0.660588`
- `periodic_waveform_high_band_energy_ratio = 0.742021`
- `aligned_waveform_high_band_energy_ratio = 0.081433`

### `highband = 0.05`
- `loss_waveform = 0.122480`
- `loss_stft = 0.595553`
- `loss_rms_guard = 0.177339`
- `loss_active_template = 0.204243`
- `loss_frame_adjacent_cosine = 328.926356`
- `decoded_to_target_rms_ratio = 0.878453`
- `loss_periodic_waveform_high_band_excess = 0.612289`
- `periodic_waveform_high_band_energy_ratio = 0.693722`
- `aligned_waveform_high_band_energy_ratio = 0.081433`

### `highband = 0.1`
- `loss_waveform = 0.126106`
- `loss_stft = 0.603563`
- `loss_rms_guard = 0.150684`
- `loss_active_template = 0.255143`
- `loss_frame_adjacent_cosine = 329.131280`
- `decoded_to_target_rms_ratio = 0.915469`
- `loss_periodic_waveform_high_band_excess = 0.531518`
- `periodic_waveform_high_band_energy_ratio = 0.612951`
- `aligned_waveform_high_band_energy_ratio = 0.081433`

### validation 解读
1. 这条新 loss
   不是“没触发”的假实验：
   - `loss_periodic_waveform_high_band_excess`
     明显非零
   - 且随着权重上升持续下降
2. 也就是说：
   - 它确实把 periodic-path
     的高频占比往下压了
3. 但共享指标方向很明确：
   - `waveform`
     变差
   - `stft`
     变差
   - `active_template`
     变差
   - `adjacent cosine`
     变差
4. 同时：
   - `rms_guard`
     变好
   - `decoded_to_target_rms_ratio`
     更接近
     `1.0`
5. 所以它更像是在：
   - 把 periodic-path 从
     “过亮、过尖”
     往回压
   - 但也把当前主线辛苦拿到的结构收益一起吐掉

## 四、fixed 6 条 aggregate

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### baseline: `rms_floor=0.65`
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870710`

### `highband = 0.02`
- `loss_waveform = 0.121368`
- `loss_stft = 0.591731`
- `loss_rms_guard = 0.139129`
- `loss_active_template = 0.159453`
- `loss_frame_adjacent_cosine = 313.612023`
- `decoded_to_target_rms_ratio = 0.874057`
- `loss_periodic_waveform_high_band_excess = 0.719057`
- `periodic_waveform_high_band_energy_ratio = 0.757255`
- `aligned_waveform_high_band_energy_ratio = 0.038199`

### `highband = 0.05`
- `loss_waveform = 0.122578`
- `loss_stft = 0.594373`
- `loss_rms_guard = 0.132331`
- `loss_active_template = 0.183062`
- `loss_frame_adjacent_cosine = 313.710688`
- `decoded_to_target_rms_ratio = 0.884104`
- `loss_periodic_waveform_high_band_excess = 0.669538`
- `periodic_waveform_high_band_energy_ratio = 0.707737`
- `aligned_waveform_high_band_energy_ratio = 0.038199`

### `highband = 0.1`
- `loss_waveform = 0.126007`
- `loss_stft = 0.601310`
- `loss_rms_guard = 0.107092`
- `loss_active_template = 0.237088`
- `loss_frame_adjacent_cosine = 313.902120`
- `decoded_to_target_rms_ratio = 0.920404`
- `loss_periodic_waveform_high_band_excess = 0.585324`
- `periodic_waveform_high_band_energy_ratio = 0.623522`
- `aligned_waveform_high_band_energy_ratio = 0.038199`

### fixed 6 解读
1. fixed-6
   和 validation
   方向完全一致：
   - 权重越高，
     高频占比越低
   - 但
     `waveform / stft / active_template / adjacent cosine`
     越差
2. `highband=0.02`
   是三条 high-band 候选里最轻的一条，
   但仍没有超过 baseline：
   - `rms_guard`
     更好
   - `rms_ratio`
     更强
   - 但
     `waveform / stft / active_template / adjacent cosine`
     全都回吐
3. `0.05`
   与
   `0.1`
   则已经是同方向继续加重：
   - 高频压得更多
   - 结构/重建侧也回吐更多

## 五、当前判断
1. 这轮已经把一个新事实写实了：
   - **即使把频谱守护缩到“只罚 periodic-path 的高频占比过量”，它仍然会和当前结构收益发生冲突**
2. 也就是说：
   - 当前问题不只是：
     - “不要做整段 STFT”
   - 而是：
     - “频谱 restrain 这件事本身，就可能在当前层级上和结构目标竞争”
3. 因而这条线当前不建议继续扫：
   - `0.15`
   - `0.2`
   - 或更细的
     `0.01 / 0.03`
     同构权重

## 六、和前两轮 follow-up 的关系
1. 全局 `stft_weight`
   跟进：
   - 会把
     `waveform / stft`
     收回来
   - 但回吐
     `adjacent cosine / active_template / rms_ratio`
2. local periodic `stft`
   跟进：
   - 结论同类
3. 当前这轮
   high-band restraint：
   - 不是把
     `waveform / stft`
     拉回
   - 更像是把
     高频能量
     往下压
   - 但最终仍然出现：
     - 结构侧回吐
     - 重建侧回吐
4. 因而可以把当前结论写得更硬：
   - **当前 decode-side periodic spectral restraint family，至少在这几种最小形态上，都没有给出比原始 `rms_floor=0.65` 更好的点**

## 七、下一步建议
1. 当前不建议导听审包
2. 当前也不建议继续扫：
   - `periodic_waveform_high_band_excess_weight`
3. 如果还坚持沿 periodic spectral line 只做一个最小新实验，
   更像样的下一发应改成：
   - `spectral tilt restraint`
   而不是单个
   `high_band_energy_ratio`
4. 但如果从当前全局价值判断，
   我更倾向于把 decode-side periodic spectral restraint 线先暂停，
   回到更上游的：
   - `fusion / fused_hidden`
   主线

## 一句话结论
- periodic-path high-band restraint
  确实被触发并能单调压低高频占比；
  但它没有形成新的更优 Pareto 点，
  反而继续证明：
  当前 decode-side periodic spectral restraint family
  仍然会把
  `rms_floor=0.65`
  主线的结构收益往回拉。
