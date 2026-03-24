# 2026-03-24 Stage5 `contractv2_normfix` periodic-gate local RMS-floor follow-up 报告

## 结论
- 已在当前最优主线
  `periodic_plus_noise_residual_shape_recurrent + periodic temporal losses`
  上，
  新增一个更局部的稳态锚点：
  - **`periodic_waveform_frame_log_rms_floor`**
- 第一版曾错误地用
  `predicted_activity = max(periodic_gate, noise_gate)`
  作为 frame gain，
  会诱导
  `noise_gate`
  抬高来钻空子。
- 修正为**只使用 `periodic_gate`** 后，
  这条线第一次同时出现：
  - `adjacent cosine` 继续改善
  - `active_template` 继续改善
  - `decoded_to_target_rms_ratio` 明显回升
- 当前最平衡点是：
  - **`periodic_waveform_frame_rms_floor_weight = 0.5`**
- 但它还没强到值得导听审包，因为：
  - `waveform / stft` 仍明显差于当前无 floor 的候选

## 一、背景
- `docs/307`
  已确认：
  - `recurrent + explicit temporal loss`
    可以把
    `adjacent cosine`
    真正继续往下推
  - 但
    RMS / 能量稳态
    仍然偏低
- 直接提高全局
  `rms_guard`
  到
  `0.3`
  虽能拉回能量，
  但会明显吃掉：
  - `waveform`
  - `stft`
  - 部分 temporal 改善
- 因此本轮不再扫全局
  `rms_guard`，
  而是改做：
  - **只给 periodic 主干一个局部 frame-level log-RMS floor**

## 二、实现改动
- `src/v5vc/offline_vocoder_training.py`
  - 新增：
    - `compute_frame_log_rms_floor_loss_against_aligned_target(...)`
  - 新增 loss 权重：
    - `periodic_waveform_frame_rms_floor_weight`
  - 新增指标：
    - `loss_periodic_waveform_frame_log_rms_floor_excess`
    - `periodic_waveform_active_frame_rms_mean`
    - `aligned_active_frame_rms_mean`
- `src/v5vc/cli.py`
  - 已把
    `--periodic-waveform-frame-rms-floor-weight`
    接到：
    - train step
    - training loop
    - dataset training loop

## 三、先验踩坑

### 1. loophole 版本
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_rmsfloor1_smoke_round1_1/`
- 问题：
  - floor loss 用了
    `predicted_activity=max(periodic_gate, noise_gate)`
  - 结果模型会抬
    `noise_gate`
    来满足 floor，
    这不是我们想要的
    periodic 主干补能量

### 2. 修正版本
- 现在 floor loss 只使用：
  - `periodic_gate`
  作为 frame gain
- 这会把能量补偿压力压回：
  - periodic 主干本身

## 四、step4 validation 对比

### `recurrent + temporal` baseline
- `loss_waveform = 0.116954`
- `loss_stft = 0.556761`
- `loss_rms_guard = 0.258219`
- `loss_active_template = 0.264665`
- `loss_frame_adjacent_cosine = 329.022577`
- `decoded_to_target_rms_ratio = 0.799152`
- `periodic_gate_pred_mean = 0.426346`
- `noise_gate_pred_mean = 0.373949`

### `periodic_gate rms_floor = 0.5`
- `loss_waveform = 0.119274`
- `loss_stft = 0.582114`
- `loss_rms_guard = 0.206667`
- `loss_active_template = 0.176304`
- `loss_frame_adjacent_cosine = 328.791717`
- `decoded_to_target_rms_ratio = 0.845259`
- `periodic_gate_pred_mean = 0.456957`
- `noise_gate_pred_mean = 0.388525`

### `periodic_gate rms_floor = 1.0`
- `loss_waveform = 0.124360`
- `loss_stft = 0.614724`
- `loss_rms_guard = 0.144586`
- `loss_active_template = 0.156582`
- `loss_frame_adjacent_cosine = 328.825518`
- `decoded_to_target_rms_ratio = 0.916870`
- `periodic_gate_pred_mean = 0.487816`
- `noise_gate_pred_mean = 0.395487`

### validation 解读
1. `weight = 0.5`
   是第一条更像
   “正确方向的局部稳态修正”
   的候选：
   - `adjacent cosine`
     继续下降
   - `active_template`
     大幅下降
   - `rms_guard`
     与
     `rms_ratio`
     明显改善
   - 而
     `waveform / stft`
     虽变差，
     但还没有像
     `1.0`
     那样明显恶化
2. `weight = 1.0`
   说明这条线是有效的，
   但已经过头：
   - 能量几乎回到 baseline
   - `adjacent cosine`
     也仍优于无 floor
   - 但
     `waveform / stft`
     被明显拉差

## 五、fixed 6 条 aggregate

### `recurrent + temporal` baseline
- `loss_waveform = 0.116993`
- `loss_stft = 0.555195`
- `loss_rms_guard = 0.225920`
- `loss_active_template = 0.245094`
- `loss_frame_adjacent_cosine = 313.810717`
- `decoded_to_target_rms_ratio = 0.801979`
- `periodic_gate_pred_mean = 0.427772`
- `noise_gate_pred_mean = 0.377215`

### `periodic_gate rms_floor = 0.5`
- `loss_waveform = 0.119534`
- `loss_stft = 0.581669`
- `loss_rms_guard = 0.165095`
- `loss_active_template = 0.154763`
- `loss_frame_adjacent_cosine = 313.599436`
- `decoded_to_target_rms_ratio = 0.851549`
- `periodic_gate_pred_mean = 0.459422`
- `noise_gate_pred_mean = 0.391652`

### `periodic_gate rms_floor = 1.0`
- `loss_waveform = 0.124611`
- `loss_stft = 0.613895`
- `loss_rms_guard = 0.098816`
- `loss_active_template = 0.133458`
- `loss_frame_adjacent_cosine = 313.622932`
- `decoded_to_target_rms_ratio = 0.924965`
- `periodic_gate_pred_mean = 0.490472`
- `noise_gate_pred_mean = 0.398530`

### fixed 6 解读
1. `weight = 0.5`
   是当前最好平衡点：
   - `adjacent cosine`
     优于无 floor
   - `active_template`
     明显优于无 floor
   - `rms_ratio`
     从
     `0.801979`
     拉到
     `0.851549`
   - 且没有像
     `1.0`
     那样把
     `waveform / stft`
     拉得过头
2. `weight = 1.0`
   虽然能量恢复更强，
   但当前看已经过度牺牲：
   - `waveform`
   - `stft`

## 六、阶段判断
1. 当前可以明确写成：
   - **局部 periodic-path RMS floor 比全局 `rms_guard` 更贴近真实问题**
2. 更具体地说：
   - 全局 `rms_guard`
     更像是在结果端拉音量
   - `periodic_gate` 局部 floor
     更像是在主干路径里补回有效能量
3. 这也是为什么：
   - `weight = 0.5`
     能同时改善：
     - `adjacent cosine`
     - `active_template`
     - `rms_ratio`
4. 但当前还不能导听审包，
   因为：
   - `waveform / stft`
     的代价仍然偏大，
   还没到“值得用户花时间再听一轮”的强信号

## 七、下一步建议
1. 下一条最值钱的补点，
   不再是：
   - 扫全局 `rms_guard`
   - 或继续换 decoder 结构
2. 最值得做的是：
   - 以
     `periodic_gate rms_floor = 0.5`
     为中心，
     做一个极窄的局部权重微扫：
     - `0.35`
     - `0.5`
     - `0.75`
3. 目的不是继续盲扫，
   而是回答一个非常具体的问题：
   - 能不能在保住
     `adjacent cosine / active_template / rms_ratio`
     三者同时改善的前提下，
     少吃一点
     `waveform / stft`
