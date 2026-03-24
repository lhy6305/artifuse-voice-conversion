# 2026-03-24 Stage5 `contractv2_normfix` `periodic_gate rms_floor=0.65` + local periodic STFT guard follow-up 报告

## 结论
- 已在当前最佳主线
  `recurrent + periodic temporal losses + periodic_gate rms_floor=0.65`
  上，
  加了一个更局部的频谱守护：
  - `periodic_waveform_stft_weight = 0.1`
- 结果和全局
  `stft_weight`
  的方向一致：
  - `waveform / stft`
    确实变好
  - 但
    `adjacent cosine / active_template / rms_ratio`
    也一起回吐
- 所以这条 local periodic STFT guard **没有形成新的更优 Pareto 点**。
- 本轮仍然**不值得导听审包**。

## 一、实验目录
- baseline:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_smoke_round1_1/`
- candidate:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_periodicstft01_smoke_round1_1/`

## 二、实现改动
- `src/v5vc/offline_vocoder_training.py`
  - 新增：
    - `periodic_waveform_stft_weight`
    - `loss_periodic_waveform_stft`
  - 语义：
    - 仅对
      `periodic_waveform_frames`
      经
      `periodic_gate`
      重建后的 waveform
      施加 STFT 约束
- `src/v5vc/cli.py`
  - 新增：
    - `--periodic-waveform-stft-weight`

## 三、step4 validation 对比

### baseline: `rms_floor=0.65`
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`

### `periodic_waveform_stft_weight = 0.1`
- `loss_waveform = 0.118007`
- `loss_stft = 0.570701`
- `loss_rms_guard = 0.222791`
- `loss_active_template = 0.176702`
- `loss_frame_adjacent_cosine = 328.900631`
- `decoded_to_target_rms_ratio = 0.828603`
- `loss_periodic_waveform_stft = 0.603834`

### validation 解读
1. local periodic STFT
   确实做到了它要做的事：
   - `waveform`
     变好
   - `stft`
     变好
2. 但它也和全局
   `stft_weight`
   一样，
   会把当前最好主线重新往回拉：
   - `adjacent cosine`
     变差
   - `active_template`
     变差
   - `rms_ratio`
     变差

## 四、fixed 6 条 aggregate

### baseline: `rms_floor=0.65`
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870709`

### `periodic_waveform_stft_weight = 0.1`
- `loss_waveform = 0.118285`
- `loss_stft = 0.569936`
- `loss_rms_guard = 0.184488`
- `loss_active_template = 0.155223`
- `loss_frame_adjacent_cosine = 313.701057`
- `decoded_to_target_rms_ratio = 0.835073`
- `loss_periodic_waveform_stft = 0.604727`

### fixed 6 解读
1. 这条候选没有超过 baseline：
   - `waveform / stft`
     更好
   - 但
     `adjacent cosine / active_template / rms_ratio`
     都回吐
2. 因此它不像：
   - 新的 sweet spot
   更像：
   - “把系统重新拉回频谱重建偏好”

## 五、当前判断
1. 当前可以写得更清楚：
   - **不论是全局 STFT guard，还是 local periodic STFT guard，都会把当前主线往回拉**
2. 也就是说：
   - 当前更缺的不是：
     - 再多一点 STFT
   - 而是：
     - 不破坏当前结构/能量收益的前提下，
       再做更针对性的局部约束

## 六、下一步建议
1. 当前不建议导听审包
2. 当前也不建议继续扫：
   - 全局 `stft_weight`
   - `periodic_waveform_stft_weight`
3. 下一条更值钱的实验应转去：
   - 仍保留当前最佳主线
     `periodic_gate rms_floor = 0.65`
   - 但不再从 STFT 方向继续拉
4. 如果继续只做一个最小实验，
   我建议下一发改成：
   - **periodic-path 高频能量 restraint / spectral tilt restraint**
   而不是整段 STFT 对齐
