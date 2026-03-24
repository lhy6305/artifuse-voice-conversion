# 317. Stage5 `contractv2_normfix` + `periodic_gate rms_floor=0.65` fused-branch cross-point test and listening bundle

## 一、目的
1. 按
   `docs/316_stage5_contractv2_normfix_periodicgate_rmsfloor065_fusedbranch_shadow_microtune_round2_report.md`
   的建议，
   先测试交叉点：
   - `fusedbranch=0.15 + stft=0.575`
2. 若信号足够接近前两条 shadow 角点，
   不再继续微扫，
   而是直接进入一轮正式 fixed-6 听审包导出
3. 本轮同时修复一个阻塞听审的真实回归：
   - `export-offline-mvp-nores-vocoder-audio`
     仍按旧签名调用
     `compute_nores_vocoder_losses`

## 二、交叉点实验

### 配置
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch015_stft0575_smoke_round1_1`
- 固定主线:
  - `periodic_plus_noise_residual_shape_recurrent`
  - `periodic_waveform_frame_delta = 0.25`
  - `periodic_waveform_frame_adjacent_cosine = 0.01`
  - `periodic_waveform_frame_rms_floor = 0.65`
  - `waveform = 0.5`
  - `rms_guard = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`
- 本轮变量:
  - `fused_hidden_branch_mean_weight = 0.15`
  - `stft_weight = 0.575`

## 三、step4 validation 对比

### baseline
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.123779`

### `fusedbranch=0.15 + stft=0.55`
- `loss_waveform = 0.120489`
- `loss_stft = 0.591651`
- `loss_rms_guard = 0.187982`
- `loss_active_template = 0.159557`
- `loss_frame_adjacent_cosine = 328.740318`
- `decoded_to_target_rms_ratio = 0.863287`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.678262`

### `fusedbranch=0.20 + stft=0.575`
- `loss_waveform = 0.120396`
- `loss_stft = 0.590633`
- `loss_rms_guard = 0.189334`
- `loss_active_template = 0.160303`
- `loss_frame_adjacent_cosine = 328.753412`
- `decoded_to_target_rms_ratio = 0.861790`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.668934`

### 交叉点：`fusedbranch=0.15 + stft=0.575`
- `loss_waveform = 0.120089`
- `loss_stft = 0.587991`
- `loss_rms_guard = 0.194383`
- `loss_active_template = 0.162886`
- `loss_frame_adjacent_cosine = 328.770272`
- `decoded_to_target_rms_ratio = 0.856890`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.678487`

### validation 解读
1. 交叉点确实把：
   - `waveform`
   - `stft`
   拉到了本轮最好
2. 但代价也最清楚：
   - `rms_guard`
     回吐到差于 baseline
   - `decoded_to_target_rms_ratio`
     也回吐到差于 baseline
   - `adjacent cosine`
     甚至略差于 baseline
3. 因而交叉点不是：
   - 新的单一 leader
4. 它更像：
   - 把 waveform/STFT recovery
     推到最强，
   - 但同时把剩余冲突暴露得更彻底

## 四、fixed 6 条 aggregate

### baseline
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870710`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.123373`

### `fusedbranch=0.15 + stft=0.55`
- `loss_waveform = 0.120779`
- `loss_stft = 0.590959`
- `loss_rms_guard = 0.143093`
- `loss_active_template = 0.138029`
- `loss_frame_adjacent_cosine = 313.546954`
- `decoded_to_target_rms_ratio = 0.870352`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.675398`

### `fusedbranch=0.20 + stft=0.575`
- `loss_waveform = 0.120690`
- `loss_stft = 0.589958`
- `loss_rms_guard = 0.144852`
- `loss_active_template = 0.139137`
- `loss_frame_adjacent_cosine = 313.558665`
- `decoded_to_target_rms_ratio = 0.868812`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.666137`

### 交叉点：`fusedbranch=0.15 + stft=0.575`
- `loss_waveform = 0.120370`
- `loss_stft = 0.587190`
- `loss_rms_guard = 0.150729`
- `loss_active_template = 0.141351`
- `loss_frame_adjacent_cosine = 313.575287`
- `decoded_to_target_rms_ratio = 0.863754`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.675502`

### fixed-6 解读
1. fixed-6
   与 validation
   保持同方向：
   - 交叉点拿到了最好的
     `waveform / stft`
   - 但也拿到了最差的
     `rms_guard / rms_ratio`
2. 这条结果把当前 shadow 线的结构写得更清楚了：
   - `0.15 + 0.55`
     是 near-baseline balance 点
   - `0.20 + 0.575`
     是 waveform/STFT-recovery 点
   - `0.15 + 0.575`
     不是兼得点，
     而是 recovery 继续过头的交叉点
3. 所以这轮的正确动作不是：
   - 再往周围继续扫
4. 而是：
   - 立刻把当前最值得听的几条包导出来，
     用听审去回答
     “是否还在 buzz-only”

## 五、导出回归修复

### 发现的问题
1. 本轮首次执行：
   - `export-offline-mvp-nores-vocoder-audio`
   时，
   直接报错：
   - `compute_nores_vocoder_losses() missing 1 required positional argument: 'sample_rate'`
2. 根因是：
   - [nores_vocoder_audio_export.py](F:/proj_dev/tmp/workdir4/src/v5vc/nores_vocoder_audio_export.py)
     仍按旧签名调用
     `compute_nores_vocoder_losses`

### 修复内容
1. 已在
   [nores_vocoder_audio_export.py](F:/proj_dev/tmp/workdir4/src/v5vc/nores_vocoder_audio_export.py)
   补上：
   - `sample_rate=int(runtime["sample_rate"])`
2. 修复后已通过：
   - 单条 export smoke
   - 四路 fixed-6 正式导出

## 六、听审包

### 根目录
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_fusion_shadow_compare_round1_1/`

### 子目录
- `baseline/`
- `fusedbranch015_stft055/`
- `fusedbranch020_stft0575/`
- `fusedbranch015_stft0575/`

### 推荐主听对象
- `*__decoded_pitch_matched.wav`

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### 导出语义
- `listening_audio_source = decoded_pitch_matched`
- `pitch_match_reference = aligned_target`
- `use_predicted_activity_gate = true`
- `predicted_activity_gate_apply_mode = pre_overlap_add`

### bundle 说明文件
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_fusion_shadow_compare_round1_1/README.md`

## 七、当前判断
1. 数值侧到这里已经足够：
   - 继续同构微扫的收益开始明显下降
2. 交叉点没有形成新 leader，
   但它也不是无价值：
   - 它证明了当前 shadow line
     的主要剩余冲突已经收敛到
     `rms_guard / rms_ratio`
3. 因而当前最合理的下一步不再是：
   - 再扫更多
     `fusedbranch/stft`
     点
4. 而是：
   - 直接对这四路 fixed-6 包做人工听审

## 一句话结论
- `fusedbranch=0.15 + stft=0.575`
  没有成为新的单一 winner；
  它把
  `waveform / stft`
  推到最好，
  但把
  `rms_guard / rms_ratio`
  回吐得最明显。
- 本轮真正完成的推进是：
  - 补测了交叉点
  - 修复了 no-res audio export 回归
  - 已把 baseline 与三条最值得听的候选
    导成正式 fixed-6 听审包
  - 现在可以直接听，
    不必再等下一轮数值微扫
