# 2026-03-24 Stage5 `contractv2_normfix` residual-shape / factorized / temporal follow-up 报告

## 结论
- 本轮在
  `periodic + noise residual`
  结构线上，
  连续完成了 3 条 follow-up：
  1. `periodic_plus_noise_residual_shape`
  2. `periodic_plus_noise_factorized_residual`
  3. `periodic_plus_noise_residual_shape_temporal`
- 当前最重要的结论不是：
  - 哪条共享指标最低
- 而是：
  - **`periodic_plus_noise_residual_shape`**
    仍是目前非对称 residual 路线里
    最平衡的一条
  - 后续两条升级：
    - `factorized_residual`
    - `shape_temporal`
    都没有形成更强正信号
- 因而当前正式判断是：
  1. `noise residual`
     方向成立
  2. `frame-level shape gate`
     已经比更粗的结构更合理
  3. 但：
     - `adjacent cosine`
       仍没有真正被打下来
     - `decoded_to_target_rms_ratio`
       仍未回到接近 baseline
  4. 所以当前**仍不导听审包**

## 一、本轮实验列表

### 1. `periodic_plus_noise_residual_shape`
- 已有有效目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodic_plus_noise_residual_shape_smoke_round1_1/`
- 核心结构：
  - `periodic` 主干
  - `noise residual`
  - 每帧一个
    sample-shape
    envelope

### 2. `periodic_plus_noise_factorized_residual`
- 有效目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodic_plus_noise_factorized_residual_smoke_round1_1/`
- 核心结构：
  - 将
    `noise residual`
    拆成：
    - unit-RMS shape
    - scalar gain
    - sample envelope

### 3. `periodic_plus_noise_residual_shape_temporal`
- 有效目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodic_plus_noise_residual_shape_temporal_smoke_round1_2/`
- 核心结构：
  - 在
    `residual_shape`
    路线上，
    给
    `periodic_hidden / noise_hidden`
    各加一个最小 temporal refiner

## 二、step4 validation 对比

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

### `residual_shape`
- `loss_waveform = 0.118170`
- `loss_stft = 0.552888`
- `loss_rms_guard = 0.225688`
- `loss_active_template = 0.361305`
- `loss_frame_adjacent_cosine = 329.916952`
- `decoded_to_target_rms_ratio = 0.822399`

### `factorized_residual`
- `loss_waveform = 0.115584`
- `loss_stft = 0.542060`
- `loss_rms_guard = 0.266204`
- `loss_active_template = 0.366383`
- `loss_frame_adjacent_cosine = 329.875876`
- `decoded_to_target_rms_ratio = 0.786111`

### `shape_temporal`
- `loss_waveform = 0.118176`
- `loss_stft = 0.559967`
- `loss_rms_guard = 0.226199`
- `loss_active_template = 0.440033`
- `loss_frame_adjacent_cosine = 330.205057`
- `decoded_to_target_rms_ratio = 0.822036`

### validation 解读
1. `factorized_residual`
   虽然
   `waveform / stft`
   还可以，
   但
   `rms_guard`
   与
   `decoded_to_target_rms_ratio`
   都更差，
   没有比
   `residual_shape`
   更强
2. `shape_temporal`
   没有带来期望中的
   `adjacent cosine`
   改善，
   反而把
   `active_template`
   拉差了
3. 因此：
   - 当前最平衡的仍是
     `residual_shape`

## 三、fixed 6 条 aggregate 对比

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

### `residual_shape`
- `loss_waveform = 0.118601`
- `loss_stft = 0.551679`
- `loss_rms_guard = 0.188589`
- `loss_active_template = 0.335626`
- `loss_frame_adjacent_cosine = 314.625717`
- `decoded_to_target_rms_ratio = 0.831210`

### `factorized_residual`
- `loss_waveform = 0.115950`
- `loss_stft = 0.540327`
- `loss_rms_guard = 0.234582`
- `loss_active_template = 0.343952`
- `loss_frame_adjacent_cosine = 314.598127`
- `decoded_to_target_rms_ratio = 0.793896`

### `shape_temporal`
- `loss_waveform = 0.118591`
- `loss_stft = 0.559985`
- `loss_rms_guard = 0.190156`
- `loss_active_template = 0.427638`
- `loss_frame_adjacent_cosine = 314.898926`
- `decoded_to_target_rms_ratio = 0.829840`

### fixed 6 解读
1. `residual_shape`
   仍是当前最合理平衡点：
   - `active_template`
     最低
   - `rms_guard`
     明显优于
     `dual_branch_mix`
   - `decoded_to_target_rms_ratio`
     也显著优于
     `dual_branch_mix`
2. `factorized_residual`
   没把
   RMS
   拉稳，
   因而不成立
3. `shape_temporal`
   也没有把
   `adjacent cosine`
   实质打下来，
   因而当前 temporal refiner
   这条最小实现也不成立

## 四、当前阶段判断
1. 当前可以更明确地写成：
   - decoder 结构路线成立
   - `noise residual`
     方向成立
2. 但现在仍然缺失的，
   不是更多 decoder 宽度，
   而是：
   - 能真正改变
     frame-to-frame
     行为的机制
3. 也就是说：
   - 共享指标已经反复证明
     “结构改动有效”
   - 但
     `adjacent cosine`
     这个主失败项
     基本不动，
     说明当前所有这些结构
     还没真正碰到
     temporal behavior

## 五、为什么当前仍不导听审包
1. 用户已明确要求：
   - 信号不够强就不要导包
2. 当前虽然：
   - 结构路线持续优于 baseline
3. 但：
   - `adjacent cosine`
     没有清楚下降
   - `decoded_to_target_rms_ratio`
     仍没回到接近 baseline
4. 所以当前仍不值得占用人工听审时间

## 六、下一步建议
1. 当前最值得做的，
   已不是继续在 decoder 内部
   叠更多局部模块
2. 下一条更有信息价值的实验应转向：
   - **显式 temporal objective**
     或
   - **显式 temporal latent / transition path**
3. 具体地说，
   我现在最推荐的是：
   - 在当前最好结构
     `periodic_plus_noise_residual_shape`
     上，
     重新启用一个
     **强得多的 frame-adjacent / delta 约束**
     但只作用在：
     - `periodic_waveform_frames`
     - 或
       `waveform_frames`
   - 而不是再继续纯结构微调

## 一句话结论
- 这组 follow-up
  已经把一个事实钉死了：
  **结构改动本身不能自动把 `adjacent cosine` 打下来。**
  当前最平衡的实现仍是
  `periodic_plus_noise_residual_shape`，
  但下一步要想继续推进，
  应该把重点从“再换一种 decoder 小结构”
  转到
  **显式 temporal behavior 约束**。
