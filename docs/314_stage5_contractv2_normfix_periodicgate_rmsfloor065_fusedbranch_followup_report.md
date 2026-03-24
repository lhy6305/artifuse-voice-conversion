# 2026-03-24 Stage5 `contractv2_normfix` `periodic_gate rms_floor=0.65` + fusion-side `fused_hidden_branch_mean` follow-up 报告

## 结论
- 已在当前最强主线
  `recurrent + periodic temporal losses + periodic_gate rms_floor=0.65`
  上，
  做了一轮 fusion-side 最小跟进：
  - `fused_hidden_branch_mean_weight = 0.10`
  - `0.25`
  - `0.40`
- 当前最重要的新结论是：
  - **在更强骨架上，fusion-side `branch_mean` 约束不再是“纯无效小改动”**
- 更准确地说：
  1. 权重越高，
     `loss_fused_hidden_to_branch_mean_unit_rms_l1`
     单调下降，
     说明
     `fused_hidden`
     确实被持续拉向
     `branch_mean`
  2. 同时：
     - `active_template`
       稳定改善
     - `adjacent cosine`
       也有小幅改善
     - `rms_guard / decoded_to_target_rms_ratio`
       也一起改善
  3. 但代价是：
     - `waveform`
       变差
     - `stft`
       变差
- 所以这条线当前**不是失败**，
  但也**还没有单独形成新的无争议前沿**。

## 一、实验目录
- baseline:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_smoke_round1_1/`
- `fusedbranch=0.10`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch010_smoke_round1_1/`
- `fusedbranch=0.25`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch025_smoke_round1_1/`
- `fusedbranch=0.40`:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch040_smoke_round1_1/`
- 组合跟进：
  - `fusedbranch=0.25 + stft=0.55`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch025_stft055_smoke_round1_1/`

## 二、运行口径
- 共同保持：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `num_steps = 4`
  - `packages_per_step = 4`
  - `validation_interval = 2`
  - `checkpoint_interval = 2`
  - `seed = 20260324`
  - `deterministic = true`
  - `device = cuda:0`
  - `activity_gate = 0.2`
  - `waveform = 0.5`
  - `stft = 0.5`
  - `rms_guard = 0.2`
  - `periodic_waveform_frame_delta = 0.25`
  - `periodic_waveform_frame_adjacent_cosine = 0.01`
  - `periodic_waveform_frame_rms_floor = 0.65`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- 本轮唯一主变量：
  - `fused_hidden_branch_mean_weight`
- 组合跟进唯一额外变量：
  - `stft_weight: 0.5 -> 0.55`

## 三、step4 validation 对比

### baseline
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.123779`

### `fusedbranch = 0.10`
- `loss_waveform = 0.121142`
- `loss_stft = 0.596586`
- `loss_rms_guard = 0.179189`
- `loss_active_template = 0.159674`
- `loss_frame_adjacent_cosine = 328.715641`
- `decoded_to_target_rms_ratio = 0.873095`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.689983`

### `fusedbranch = 0.25`
- `loss_waveform = 0.121909`
- `loss_stft = 0.604450`
- `loss_rms_guard = 0.167505`
- `loss_active_template = 0.145175`
- `loss_frame_adjacent_cosine = 328.652036`
- `decoded_to_target_rms_ratio = 0.885898`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.650363`

### `fusedbranch = 0.40`
- `loss_waveform = 0.122719`
- `loss_stft = 0.611166`
- `loss_rms_guard = 0.156498`
- `loss_active_template = 0.132341`
- `loss_frame_adjacent_cosine = 328.626565`
- `decoded_to_target_rms_ratio = 0.898878`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.634203`

### validation 解读
1. 当前这条线和 high-band restraint
   不同：
   - 它不是改善一项、回吐其余全部
   - 而是：
     - `active_template`
       更好
     - `adjacent cosine`
       也略好
     - `rms_guard`
       更好
     - `rms_ratio`
       更接近
       `1.0`
2. 代价集中在：
   - `waveform`
   - `stft`
3. 并且这种 tradeoff
   呈单调：
   - 权重越高，
     upstream `branch_mean` 对齐越强，
     结构/能量侧越好，
     但
     `waveform / stft`
     越差
4. 因而：
   - 这是一条真的有料的 Pareto 线，
     不是无效小调参

## 四、fixed 6 条 aggregate

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### baseline
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870710`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.123373`

### `fusedbranch = 0.10`
- `loss_waveform = 0.121433`
- `loss_stft = 0.595901`
- `loss_rms_guard = 0.132008`
- `loss_active_template = 0.137978`
- `loss_frame_adjacent_cosine = 313.525185`
- `decoded_to_target_rms_ratio = 0.880299`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.686881`

### `fusedbranch = 0.25`
- `loss_waveform = 0.122238`
- `loss_stft = 0.604198`
- `loss_rms_guard = 0.121177`
- `loss_active_template = 0.124332`
- `loss_frame_adjacent_cosine = 313.461156`
- `decoded_to_target_rms_ratio = 0.893604`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.647602`

### `fusedbranch = 0.40`
- `loss_waveform = 0.123087`
- `loss_stft = 0.610914`
- `loss_rms_guard = 0.110914`
- `loss_active_template = 0.111904`
- `loss_frame_adjacent_cosine = 313.426178`
- `decoded_to_target_rms_ratio = 0.906964`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.631688`

### fixed 6 解读
1. fixed-6
   与 validation
   完全同方向：
   - `active_template`
     越来越低
   - `adjacent cosine`
     也越来越低
   - `rms_guard / rms_ratio`
     越来越稳
   - 同时
     `waveform / stft`
     越来越差
2. 其中
   `0.25`
   是一个比较清楚的中点：
   - 结构/能量改进已经明显
   - 但
     `waveform / stft`
     税也开始变得不小
3. `0.40`
   虽然让：
   - `active_template`
   - `adjacent cosine`
   - `rms_guard`
   - `rms_ratio`
   都来到本轮最好区间，
   但：
   - `waveform / stft`
     已经回吐得过多

## 五、组合跟进：`fusedbranch=0.25 + stft=0.55`

### step4 validation
- `loss_waveform = 0.121054`
- `loss_stft = 0.596347`
- `loss_rms_guard = 0.179176`
- `loss_active_template = 0.153965`
- `loss_frame_adjacent_cosine = 328.703049`
- `decoded_to_target_rms_ratio = 0.872401`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.657094`

### fixed 6 条 aggregate
- `loss_waveform = 0.121363`
- `loss_stft = 0.595842`
- `loss_rms_guard = 0.132278`
- `loss_active_template = 0.133114`
- `loss_frame_adjacent_cosine = 313.509746`
- `decoded_to_target_rms_ratio = 0.879752`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.654443`

### 组合解读
1. 这条组合确实做到了它想做的事：
   - 相比纯
     `fusedbranch=0.25`
   - 它把
     `waveform / stft`
     税收回来了一部分
2. 同时：
   - `active_template`
     仍明显优于 baseline
   - `adjacent cosine`
     仍优于 baseline
   - `rms_guard / rms_ratio`
     也仍优于 baseline
3. 但它还没有形成：
   - 对 baseline 的
     明确全面胜出
4. 更准确地说，
   它是当前可以正式记录的：
   - **一个更平衡的 shadow candidate**
   而不是：
   - 已能替换原始
     `rms_floor=0.65`
     的新默认

## 六、当前判断
1. 这轮最重要的新事实是：
   - **fusion-side `branch_mean` 约束在当前强骨架上是有效的**
2. 它和前面的 decode-side periodic spectral restraint family
   有本质区别：
   - 它不是把结构收益往回拉
   - 而是把结构/能量两边一起往前推，
     只是付出
     `waveform / stft`
     税
3. 再叠一个最轻的
   `stft=0.55`
   后，
   税可以部分回收，
   但还没强到形成新的无争议 leader

## 七、下一步建议
1. 当前仍不导听审包
2. 但这轮已经说明：
   - `fusion / fused_hidden`
     主线比
     decode-side periodic spectral restraint
     更值得继续
3. 如果继续只做一个最小实验，
   我现在最推荐的是：
   - 以
     `fusedbranch=0.25 + stft=0.55`
     作为 shadow base
   - 再做一个更窄的：
     - `stft=0.525`
     或
     - `fusedbranch=0.20`
     这类平衡点微调
4. 如果不想继续做同构微调，
   更值钱的升级则是：
   - 把当前
     `branch_mean`
     约束
     从纯 loss
     升级成更强的
     forward-path
     条件化

## 一句话结论
- fusion-side `fused_hidden_branch_mean`
  在当前最强主线上是真有效的；
  它不像 periodic spectral restraint 那样只是回摆，
  而是形成了一条真实 Pareto 线。
- 其中
  `fusedbranch=0.25 + stft=0.55`
  是目前最平衡的 shadow candidate，
  但还没强到足以替换原始
  `rms_floor=0.65`
  默认主线。
