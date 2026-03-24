# 315. Stage5 `contractv2_normfix` + `periodic_gate rms_floor=0.65` fusion shadow micro-tune follow-up

## 一、目的
1. 延续
   `docs/314_stage5_contractv2_normfix_periodicgate_rmsfloor065_fusedbranch_followup_report.md`
   的结论，
   围绕当前 shadow candidate：
   - `fused_hidden_branch_mean_weight = 0.25`
   - `stft_weight = 0.55`
   做更窄的单变量微调
2. 本轮只验证两个最小候选：
   - `fusedbranch=0.25 + stft=0.525`
   - `fusedbranch=0.20 + stft=0.55`
3. 目标不是直接导听审，
   而是先判断：
   - 哪个方向更接近
     “保住 fusion-side 结构收益，
     同时继续回收 waveform / stft 税”

## 二、实验配置

### 固定不变的主线
- dataset index:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- device:
  - `cuda:0`
- num_steps:
  - `4`
- packages_per_step:
  - `4`
- validation_interval:
  - `2`
- checkpoint_interval:
  - `2`
- sampler_mode:
  - `shuffle`
- seed:
  - `20260324`
- deterministic:
  - `true`
- hidden_dim:
  - `64`
- learning_rate:
  - `0.001`
- max_grad_norm:
  - `5.0`
- harmonic_weight:
  - `1.0`
- noise_weight:
  - `1.0`
- periodic_gate_weight:
  - `0.2`
- noise_gate_weight:
  - `0.2`
- activity_gate_weight:
  - `0.2`
- waveform_weight:
  - `0.5`
- rms_guard_weight:
  - `0.2`
- use_predicted_activity_gate:
  - `true`
- reconstruction_frame_gain_apply_mode:
  - `pre_overlap_add`
- waveform_decoder_mode:
  - `periodic_plus_noise_residual_shape_recurrent`
- periodic_waveform_frame_delta_weight:
  - `0.25`
- periodic_waveform_frame_adjacent_cosine_weight:
  - `0.01`
- periodic_waveform_frame_rms_floor_weight:
  - `0.65`

### 本轮新增候选
1. `fusedbranch=0.25 + stft=0.525`
   - output:
     `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch025_stft0525_smoke_round1_1`
2. `fusedbranch=0.20 + stft=0.55`
   - output:
     `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch020_stft055_smoke_round1_1`

### 对照组
1. baseline
   - `periodic_gate rms_floor=0.65`
2. 旧 shadow candidate
   - `fusedbranch=0.25 + stft=0.55`

## 三、step4 validation 对比

### baseline
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.123779`

### 旧 shadow：`fusedbranch=0.25 + stft=0.55`
- `loss_waveform = 0.121054`
- `loss_stft = 0.596347`
- `loss_rms_guard = 0.179176`
- `loss_active_template = 0.153965`
- `loss_frame_adjacent_cosine = 328.703049`
- `decoded_to_target_rms_ratio = 0.872401`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.657094`

### 新候选 A：`fusedbranch=0.25 + stft=0.525`
- `loss_waveform = 0.121469`
- `loss_stft = 0.600149`
- `loss_rms_guard = 0.173609`
- `loss_active_template = 0.151088`
- `loss_frame_adjacent_cosine = 328.688904`
- `decoded_to_target_rms_ratio = 0.878752`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.652621`

### 新候选 B：`fusedbranch=0.20 + stft=0.55`
- `loss_waveform = 0.120794`
- `loss_stft = 0.594176`
- `loss_rms_guard = 0.183506`
- `loss_active_template = 0.157196`
- `loss_frame_adjacent_cosine = 328.718112`
- `decoded_to_target_rms_ratio = 0.867901`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.669151`

### validation 解读
1. `fusedbranch=0.25 + stft=0.525`
   没有把系统往 baseline 拉回：
   - `waveform / stft`
     反而比
     `0.25 + 0.55`
     更差
   - 但
     `rms_guard / active_template / adjacent cosine / rms_ratio / branch_mean`
     继续更好
2. 也就是说：
   - 在当前点附近，
     单纯把
     `stft_weight`
     从
     `0.55`
     往下调到
     `0.525`
     并不是
     “更保守”
     的方向
3. `fusedbranch=0.20 + stft=0.55`
   则明显更像：
   - 把 waveform / stft 税往回收
   - 同时保留一部分 fusion-side 结构收益
4. validation 上，
   它相对旧 shadow：
   - `waveform`
     更好
   - `stft`
     更好
   - `rms_guard`
     更接近 baseline
   - 但
     `active_template / adjacent cosine / rms_ratio / branch_mean`
     收益略弱

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

### 旧 shadow：`fusedbranch=0.25 + stft=0.55`
- `loss_waveform = 0.121363`
- `loss_stft = 0.595842`
- `loss_rms_guard = 0.132278`
- `loss_active_template = 0.133114`
- `loss_frame_adjacent_cosine = 313.509746`
- `decoded_to_target_rms_ratio = 0.879752`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.654443`

### 新候选 A：`fusedbranch=0.25 + stft=0.525`
- `loss_waveform = 0.121780`
- `loss_stft = 0.599744`
- `loss_rms_guard = 0.126824`
- `loss_active_template = 0.130351`
- `loss_frame_adjacent_cosine = 313.496531`
- `decoded_to_target_rms_ratio = 0.886262`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.649925`

### 新候选 B：`fusedbranch=0.20 + stft=0.55`
- `loss_waveform = 0.121093`
- `loss_stft = 0.593603`
- `loss_rms_guard = 0.137627`
- `loss_active_template = 0.136079`
- `loss_frame_adjacent_cosine = 313.526286`
- `decoded_to_target_rms_ratio = 0.875094`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.666396`

### fixed 6 解读
1. fixed-6
   与 validation
   完全同方向：
   - `0.25 + 0.525`
     继续往结构/能量收益方向推，
     但也继续付出更大
     `waveform / stft`
     税
   - `0.20 + 0.55`
     则更像把旧 shadow
     往 baseline
     拉近了一步
2. `0.20 + 0.55`
   相比 baseline：
   - `waveform`
     只多付了很小的税
   - `stft`
     也只多付了很小的税
   - 同时
     `active_template / adjacent cosine / rms_guard / rms_ratio / branch_mean`
     仍全部优于 baseline
3. 但它相对旧 shadow
   也确实让出了一部分：
   - `active_template`
   - `adjacent cosine`
   - `rms_guard`
   - `rms_ratio`
   - `branch_mean`
     改进幅度
4. 因而：
   - `0.20 + 0.55`
     是当前更平衡的新 shadow leader
   - 但它仍未形成对 baseline 的全面无争议胜出

## 五、当前判断
1. 本轮最重要的新信息不是：
   - 又找到一个更低的
     `stft_weight`
2. 而是：
   - 在这条 fusion-side Pareto 线上，
     微调的两个轴并不对称
3. 更具体地说：
   - 降
     `stft_weight`
     到
     `0.525`
     没有成为更保守的回收动作
   - 降
     `fused_hidden_branch_mean_weight`
     到
     `0.20`
     才是当前更有效的平衡方向
4. 因而当前最值得保留的 shadow candidate
   应更新为：
   - `fusedbranch=0.20 + stft=0.55`
5. 但默认 leader
   仍然是：
   - 原始
     `periodic_gate rms_floor=0.65`

## 六、下一步建议
1. 当前仍不导听审包
2. 如果继续只做一个最小新实验，
   当前最推荐的是：
   - 以
     `fusedbranch=0.20 + stft=0.55`
     为新 shadow base
   - 再做更窄的一发：
     - `fusedbranch=0.15 + stft=0.55`
     - 或
       `fusedbranch=0.20 + stft=0.575`
3. 如果不继续同构微调，
   更值钱的升级仍然是：
   - 把
     `branch_mean`
     从纯 loss
     升级成更强的
     forward-path
     条件化

## 一句话结论
- `fusedbranch=0.25 + stft=0.525`
  不是更平衡的修正，
  而是把模型进一步推向
  “更强结构收益 + 更高 waveform/STFT 税”
  的方向。
- `fusedbranch=0.20 + stft=0.55`
  则成为新的最佳 shadow candidate；
  它比旧 shadow 更接近 baseline，
  但仍保留了明确的 fusion-side 收益，
  只是还不足以取代原始
  `rms_floor=0.65`
  主线。
