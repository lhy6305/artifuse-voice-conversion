# 2026-03-24 Stage5 `contractv2_normfix` `periodic_gate rms_floor=0.65` + STFT guard follow-up 报告

## 结论
- 已在当前最佳点
  `periodic_gate rms_floor = 0.65`
  上，
  做了最小的频谱守护尝试：
  - `stft_weight = 0.55`
  - `stft_weight = 0.6`
- 结果是：
  - **`stft_weight = 0.55` 比 `0.6` 更平衡**
  - 但两者都没有超过原始
    `0.65`
    主线
- 更准确地说：
  1. 提高
     `stft_weight`
     确实能把
     `waveform / stft`
     往回收
  2. 但会同步回吐：
     - `adjacent cosine`
     - `active_template`
     - `decoded_to_target_rms_ratio`
  3. 所以这条线目前**还不值得导听审包**

## 一、实验目录
- baseline:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_smoke_round1_1/`
- `stft=0.55`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_stft055_smoke_round1_1/`
- `stft=0.6`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_stft06_smoke_round1_1/`

## 二、step4 validation 对比

### `rms_floor=0.65`
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`

### `rms_floor=0.65 + stft=0.55`
- `loss_waveform = 0.119713`
- `loss_stft = 0.583239`
- `loss_rms_guard = 0.201096`
- `loss_active_template = 0.173477`
- `loss_frame_adjacent_cosine = 328.808129`
- `decoded_to_target_rms_ratio = 0.850837`

### `rms_floor=0.65 + stft=0.6`
- `loss_waveform = 0.118898`
- `loss_stft = 0.576153`
- `loss_rms_guard = 0.213544`
- `loss_active_template = 0.177903`
- `loss_frame_adjacent_cosine = 328.863001`
- `decoded_to_target_rms_ratio = 0.838610`

### validation 解读
1. `stft=0.55`
   已经体现出清楚的折中：
   - `waveform / stft`
     好于原始
     `0.65`
   - 但
     `adjacent cosine / active_template / rms_ratio`
     都出现回吐
2. `stft=0.6`
   方向一致但更过头：
   - `waveform / stft`
     收回更多
   - 但结构/能量侧回吐也更明显

## 三、fixed 6 条 aggregate

### `rms_floor=0.65`
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870709`

### `rms_floor=0.65 + stft=0.55`
- `loss_waveform = 0.119959`
- `loss_stft = 0.582242`
- `loss_rms_guard = 0.158387`
- `loss_active_template = 0.151619`
- `loss_frame_adjacent_cosine = 313.614464`
- `decoded_to_target_rms_ratio = 0.857271`

### `rms_floor=0.65 + stft=0.6`
- `loss_waveform = 0.119141`
- `loss_stft = 0.575034`
- `loss_rms_guard = 0.173071`
- `loss_active_template = 0.156219`
- `loss_frame_adjacent_cosine = 313.667191`
- `decoded_to_target_rms_ratio = 0.844798`

### fixed 6 解读
1. 当前最佳
   仍然是：
   - **纯 `rms_floor=0.65`**
2. `stft=0.55`
   是两条 STFT guard 候选里更平衡的一条，
   但它更像：
   - “把 current sweet spot 往回拉一点”
   而不是
   - “生成新的更优 Pareto 点”
3. `stft=0.6`
   已明显过度：
   - `stft`
     虽更好
   - 但
     `adjacent cosine`
     与
     `rms_ratio`
     回吐更多

## 四、当前判断
1. 这轮可以把一个结论写得很明确：
   - 当前最优主线
     `rms_floor=0.65`
     上，
     **直接提高全局 `stft_weight` 不是高价值修正**
2. 原因是：
   - 它并不是只修频谱，
     而是会把系统整体重新拉回：
     - 更容易重建频谱
     - 但更弱的结构/能量改进
3. 因而这条线目前不值得继续扫：
   - `stft=0.65`
   - `stft=0.7`
   - 等等

## 五、下一步建议
1. 当前不建议导听审包
2. 下一条更值钱的实验，
   不再是全局
   `stft_weight`
   微扫
3. 更合理的下一发应是：
   - 保持当前最佳主线：
     - `recurrent + periodic temporal losses + periodic_gate rms_floor=0.65`
   - 但把频谱修正改成**更局部的 periodic-path spectral guard**
4. 如果保持“只做一个最小实验”的原则，
   我建议下一发优先尝试：
   - 对
     `periodic_waveform_frames`
     自身引入一个轻量的 frame-level spectral / high-frequency restraint，
     而不是继续调全局 decode-side
     `stft_weight`
