# 2026-03-24 Stage5 `contractv2_normfix` recurrent decoder + temporal follow-up 报告

## 结论
- 已完成 3 轮最小 smoke：
  1. `periodic_plus_noise_residual_shape_recurrent`
  2. `periodic_plus_noise_residual_shape_recurrent + periodic_waveform_frame_delta=0.25 + periodic_waveform_frame_adjacent_cosine=0.01`
  3. 在 2 的基础上把 `rms_guard_weight: 0.2 -> 0.3`
- 当前最有价值的结论不是“已经可听”，而是：
  - **`recurrent + explicit temporal loss` 是目前第一条能继续把 `adjacent cosine` 往下推的路线**
  - 但它还没有同步守住：
    - `waveform / stft`
    - `decoded_to_target_rms_ratio`
- 按用户要求，本轮**没有导出听审包**。

## 一、实验目录

### 1. recurrent 结构 smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodic_plus_noise_residual_shape_recurrent_smoke_round1_2/`
- 结构：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - 在 `periodic_hidden / noise_hidden` 上各加一个最小 `GRU temporal refiner`

### 2. recurrent + temporal candidate
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_candidate_smoke_round1_1/`
- 配置：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `periodic_waveform_frame_delta_weight = 0.25`
  - `periodic_waveform_frame_adjacent_cosine_weight = 0.01`

### 3. recurrent + temporal + `rms_guard=0.3`
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_rmsguard03_smoke_round1_1/`
- 配置：
  - 与 2 相同
  - `rms_guard_weight = 0.3`

## 二、step4 validation 对比

### baseline
- `loss_waveform = 0.125092`
- `loss_stft = 0.601828`
- `loss_rms_guard = 0.155673`
- `loss_active_template = 0.503176`
- `loss_frame_adjacent_cosine = 330.772777`
- `decoded_to_target_rms_ratio = 0.899397`

### `residual_shape`
- `loss_waveform = 0.118170`
- `loss_stft = 0.552888`
- `loss_rms_guard = 0.225688`
- `loss_active_template = 0.361305`
- `loss_frame_adjacent_cosine = 329.916952`
- `decoded_to_target_rms_ratio = 0.822399`

### `recurrent`
- `loss_waveform = 0.115887`
- `loss_stft = 0.546007`
- `loss_rms_guard = 0.266539`
- `loss_active_template = 0.264310`
- `loss_frame_adjacent_cosine = 329.597637`
- `decoded_to_target_rms_ratio = 0.790257`

### `recurrent + temporal`
- `loss_waveform = 0.116954`
- `loss_stft = 0.556761`
- `loss_rms_guard = 0.258219`
- `loss_active_template = 0.264665`
- `loss_frame_adjacent_cosine = 329.022577`
- `decoded_to_target_rms_ratio = 0.799152`

### `recurrent + temporal + rms_guard=0.3`
- `loss_waveform = 0.120635`
- `loss_stft = 0.583983`
- `loss_rms_guard = 0.203396`
- `loss_active_template = 0.258712`
- `loss_frame_adjacent_cosine = 329.207402`
- `decoded_to_target_rms_ratio = 0.850762`

### validation 解读
1. `recurrent`
   明显把
   `active_template`
   再往下拉，
   也把
   `adjacent cosine`
   再压一点，
   但
   RMS
   掉得更厉害
2. `recurrent + temporal`
   是本轮最重要的新信号：
   - 相比
     `recurrent`
     ：
     - `adjacent cosine`
       继续下降
     - `decoded_to_target_rms_ratio`
       略回升
   - 但：
     - `waveform / stft`
       变差
3. `rms_guard=0.3`
   证明当前主矛盾判断正确：
   - 能量稳态确实可以拉回一些
   - 但会明显吃掉
     `waveform / stft`
     ，
     而且
     `adjacent cosine`
     也会回吐一部分

## 三、fixed 6 条 aggregate

### baseline
- `loss_waveform = 0.125503`
- `loss_stft = 0.602313`
- `loss_rms_guard = 0.107393`
- `loss_active_template = 0.497106`
- `loss_frame_adjacent_cosine = 315.431819`
- `decoded_to_target_rms_ratio = 0.908930`

### `residual_shape`
- `loss_waveform = 0.118601`
- `loss_stft = 0.551679`
- `loss_rms_guard = 0.188589`
- `loss_active_template = 0.335626`
- `loss_frame_adjacent_cosine = 314.625717`
- `decoded_to_target_rms_ratio = 0.831210`

### `recurrent`
- `loss_waveform = 0.116047`
- `loss_stft = 0.544539`
- `loss_rms_guard = 0.235001`
- `loss_active_template = 0.245315`
- `loss_frame_adjacent_cosine = 314.333951`
- `decoded_to_target_rms_ratio = 0.794444`

### `recurrent + temporal`
- `loss_waveform = 0.116993`
- `loss_stft = 0.555195`
- `loss_rms_guard = 0.225920`
- `loss_active_template = 0.245094`
- `loss_frame_adjacent_cosine = 313.810717`
- `decoded_to_target_rms_ratio = 0.801979`

### `recurrent + temporal + rms_guard=0.3`
- `loss_waveform = 0.120680`
- `loss_stft = 0.584192`
- `loss_rms_guard = 0.161553`
- `loss_active_template = 0.237631`
- `loss_frame_adjacent_cosine = 313.964760`
- `decoded_to_target_rms_ratio = 0.855024`

### fixed 6 解读
1. `recurrent + temporal`
   是当前 fixed-6 上
   `adjacent cosine`
   最低的一条：
   - `314.333951 -> 313.810717`
2. 但它仍没有跨过：
   - “量化更好且能量不继续掉”
   这个门槛
3. `rms_guard=0.3`
   虽然把
   `decoded_to_target_rms_ratio`
   拉回到了
   `0.855024`
   ，
   但：
   - `waveform`
   - `stft`
   - `adjacent cosine`
   都部分回吐

## 四、代码改动
- `src/v5vc/offline_vocoder_scaffold.py`
  - 新增
    `periodic_plus_noise_residual_shape_recurrent`
  - 增加
    `periodic_temporal_gru / noise_temporal_gru`
  - 修复
    temporal 与 recurrent 分支的 forward 守卫顺序
- `src/v5vc/nores_vocoder_audio_export.py`
  - 增加 recurrent checkpoint 模式自动识别
- `src/v5vc/cli.py`
  - help 文案加入 recurrent 模式
  - 补上 `__main__` 入口，
    修复 `python -m v5vc.cli` 实际不执行的问题

## 五、当前判断
1. 当前最可靠的阶段结论是：
   - 单纯换 decoder 结构是不够的
   - 但
     `recurrent temporal path + explicit temporal loss`
     组合后，
     已经开始真正碰到
     `adjacent cosine`
     主失败项
2. 新的主瓶颈已经更明确：
   - **如何在保住 temporal 改善的同时守住 RMS / 频谱稳态**
3. 因此下一步不建议：
   - 再继续换 decoder 大结构
   - 或再回到纯 loss-only
4. 更值钱的下一发应是：
   - 在当前最好组合
     `recurrent + temporal`
     上，
     做更细粒度的能量稳态修正，
     但不要用粗暴提高
     `rms_guard`
     的方式
   - 更像是：
     - residual scale / gain 的更可控约束
     - 或针对 `periodic` 主干输出 RMS 的局部稳态锚点
