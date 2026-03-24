# 2026-03-24 Stage5 `contractv2_normfix` periodic-gate RMS-floor narrow sweep 报告

## 结论
- 已完成
  `periodic_gate rms_floor`
  的极窄微扫：
  - `0.35`
  - `0.5`
  - `0.6`
  - `0.65`
  - `0.75`
  - 以及已有对照
    `0.0 / 1.0`
- 当前 sweep 已经收敛出明确 sweet spot：
  - **`periodic_waveform_frame_rms_floor_weight = 0.65`**
- 原因不是它在某一项绝对最好，
  而是它在当前所有点里给出了最好的综合平衡：
  - `adjacent cosine`
    已到当前 sweep 最低区间
  - `active_template`
    明显优于
    `0.35 / 0.5`
  - `decoded_to_target_rms_ratio`
    明显优于
    `0.5`
  - 同时
    `waveform / stft`
    又没有像
    `0.75 / 1.0`
    那样继续恶化太多
- 仍然**没有导出听审包**。

## 一、实验目录
- `0.35`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor035_smoke_round1_1/`
- `0.5`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor05_smoke_round1_1/`
- `0.6`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor06_smoke_round1_1/`
- `0.65`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_smoke_round1_1/`
- `0.75`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor075_smoke_round1_1/`

## 二、step4 validation 关键对比

### `0.0`
- `loss_waveform = 0.116954`
- `loss_stft = 0.556761`
- `loss_rms_guard = 0.258219`
- `loss_active_template = 0.264665`
- `loss_frame_adjacent_cosine = 329.022577`
- `decoded_to_target_rms_ratio = 0.799152`

### `0.35`
- `loss_waveform = 0.117364`
- `loss_stft = 0.568412`
- `loss_rms_guard = 0.237386`
- `loss_active_template = 0.193062`
- `loss_frame_adjacent_cosine = 328.822158`
- `decoded_to_target_rms_ratio = 0.815911`

### `0.5`
- `loss_waveform = 0.119274`
- `loss_stft = 0.582114`
- `loss_rms_guard = 0.206667`
- `loss_active_template = 0.176304`
- `loss_frame_adjacent_cosine = 328.791717`
- `decoded_to_target_rms_ratio = 0.845259`

### `0.6`
- `loss_waveform = 0.120064`
- `loss_stft = 0.587506`
- `loss_rms_guard = 0.195563`
- `loss_active_template = 0.172719`
- `loss_frame_adjacent_cosine = 328.759759`
- `decoded_to_target_rms_ratio = 0.856378`

### `0.65`
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`

### `0.75`
- `loss_waveform = 0.121681`
- `loss_stft = 0.598466`
- `loss_rms_guard = 0.174299`
- `loss_active_template = 0.165823`
- `loss_frame_adjacent_cosine = 328.763024`
- `decoded_to_target_rms_ratio = 0.879276`

### `1.0`
- `loss_waveform = 0.124360`
- `loss_stft = 0.614724`
- `loss_rms_guard = 0.144586`
- `loss_active_template = 0.156582`
- `loss_frame_adjacent_cosine = 328.825518`
- `decoded_to_target_rms_ratio = 0.916870`

### validation 解读
1. `0.35 -> 0.65`
   基本呈现稳定单调趋势：
   - `adjacent cosine`
     逐步下降
   - `active_template`
     逐步下降
   - `rms_ratio`
     逐步上升
2. 超过
   `0.65`
   以后，
   主要开始体现为：
   - `waveform / stft`
     继续恶化
   - 但
     `adjacent cosine`
     已不再继续明显改善
3. 因而：
   - validation 上的 sweet spot
     已经落在
     `0.6 ~ 0.65`

## 三、fixed 6 条 aggregate

### `0.0`
- `loss_waveform = 0.116993`
- `loss_stft = 0.555195`
- `loss_rms_guard = 0.225920`
- `loss_active_template = 0.245094`
- `loss_frame_adjacent_cosine = 313.810717`
- `decoded_to_target_rms_ratio = 0.801979`

### `0.35`
- `loss_waveform = 0.117599`
- `loss_stft = 0.567922`
- `loss_rms_guard = 0.201539`
- `loss_active_template = 0.172680`
- `loss_frame_adjacent_cosine = 313.630493`
- `decoded_to_target_rms_ratio = 0.821187`

### `0.5`
- `loss_waveform = 0.119534`
- `loss_stft = 0.581669`
- `loss_rms_guard = 0.165095`
- `loss_active_template = 0.154763`
- `loss_frame_adjacent_cosine = 313.599436`
- `decoded_to_target_rms_ratio = 0.851549`

### `0.6`
- `loss_waveform = 0.120309`
- `loss_stft = 0.586874`
- `loss_rms_guard = 0.151931`
- `loss_active_template = 0.150917`
- `loss_frame_adjacent_cosine = 313.569028`
- `decoded_to_target_rms_ratio = 0.862821`

### `0.65`
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870709`

### `0.75`
- `loss_waveform = 0.121930`
- `loss_stft = 0.597681`
- `loss_rms_guard = 0.127908`
- `loss_active_template = 0.143794`
- `loss_frame_adjacent_cosine = 313.570768`
- `decoded_to_target_rms_ratio = 0.886364`

### `1.0`
- `loss_waveform = 0.124611`
- `loss_stft = 0.613895`
- `loss_rms_guard = 0.098816`
- `loss_active_template = 0.133458`
- `loss_frame_adjacent_cosine = 313.622932`
- `decoded_to_target_rms_ratio = 0.924965`

### fixed 6 解读
1. `0.65`
   是 fixed-6 上最稳的 sweet spot：
   - `adjacent cosine`
     达到本轮最低：
     `313.562889`
   - `active_template`
     继续优于
     `0.6`
   - `rms_ratio`
     继续优于
     `0.6`
   - 但
     `waveform / stft`
     还没有恶化到
     `0.75 / 1.0`
     那么重
2. `0.75`
   虽然能量更强，
   但：
   - `adjacent cosine`
     已经不再更好
   - `waveform / stft`
     继续恶化
3. 所以：
   - `0.75`
     不再值得继续往上推
   - 最合理的收口点就是
     `0.65`

## 四、阶段判断
1. 这轮 sweep 把一个关键判断写实了：
   - `periodic_gate local RMS floor`
     不是偶然起作用，
     而是形成了一条稳定可调的 Pareto 曲线
2. 当前最重要的新结论是：
   - **`0.65` 已经把结构时序侧和能量稳态侧同时推到了当前最好区间**
3. 但它仍未通过
   “值得人工听审”
   的门槛，
   因为：
   - `waveform / stft`
     仍明显差于
     无 floor 候选

## 五、下一步建议
1. 当前不再建议继续扫：
   - `0.75+`
   - 或更大的全局
     `rms_guard`
2. 最有价值的下一步应是：
   - 以
     `periodic_gate rms_floor = 0.65`
     为新的主干基线
   - 再加一个**尽量小的频谱守护修正**
3. 最小候选建议：
   - 保持：
     - `periodic_waveform_frame_delta = 0.25`
     - `periodic_waveform_frame_adjacent_cosine = 0.01`
     - `periodic_waveform_frame_rms_floor = 0.65`
   - 仅小幅上调：
     - `stft_weight`
       从
       `0.5 -> 0.6`
4. 目标很具体：
   - 看能不能在不明显回吐：
     - `adjacent cosine`
     - `active_template`
     - `rms_ratio`
   的前提下，
   把
   `stft`
   往回收一点
