# 316. Stage5 `contractv2_normfix` + `periodic_gate rms_floor=0.65` fusion shadow micro-tune round 2

## 一、目的
1. 延续
   `docs/315_stage5_contractv2_normfix_periodicgate_rmsfloor065_fusedbranch_shadow_microtune_report.md`
   的判断，
   以当前 shadow base：
   - `fusedbranch=0.20 + stft=0.55`
   为中心，
   再做两发更窄的微调
2. 本轮要回答的是：
   - 继续减弱
     `fused_hidden_branch_mean_weight`
     到
     `0.15`
     是否能进一步回收共享指标税收
   - 在
     `fusedbranch=0.20`
     下把
     `stft_weight`
     提到
     `0.575`
     是否能把
     `waveform / stft`
     税完全收回

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
1. `fusedbranch=0.15 + stft=0.55`
   - output:
     `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch015_stft055_smoke_round1_1`
2. `fusedbranch=0.20 + stft=0.575`
   - output:
     `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_fusedbranch020_stft0575_smoke_round1_1`

### 对照组
1. baseline
   - 原始
     `periodic_gate rms_floor=0.65`
2. 当前 shadow base
   - `fusedbranch=0.20 + stft=0.55`

## 三、step4 validation 对比

### baseline
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.123779`

### 当前 shadow：`fusedbranch=0.20 + stft=0.55`
- `loss_waveform = 0.120794`
- `loss_stft = 0.594176`
- `loss_rms_guard = 0.183506`
- `loss_active_template = 0.157196`
- `loss_frame_adjacent_cosine = 328.718112`
- `decoded_to_target_rms_ratio = 0.867901`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.669151`

### 新候选 A：`fusedbranch=0.15 + stft=0.55`
- `loss_waveform = 0.120489`
- `loss_stft = 0.591651`
- `loss_rms_guard = 0.187982`
- `loss_active_template = 0.159557`
- `loss_frame_adjacent_cosine = 328.740318`
- `decoded_to_target_rms_ratio = 0.863287`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.678262`

### 新候选 B：`fusedbranch=0.20 + stft=0.575`
- `loss_waveform = 0.120396`
- `loss_stft = 0.590633`
- `loss_rms_guard = 0.189334`
- `loss_active_template = 0.160303`
- `loss_frame_adjacent_cosine = 328.753412`
- `decoded_to_target_rms_ratio = 0.861790`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.668934`

### validation 解读
1. 两个新候选都把
   `waveform / stft`
   税显著收回了
2. 其中：
   - `0.15 + 0.55`
     更像是
     “减弱 fusion-side 对齐压力”
     后得到的近 baseline 平衡点
   - `0.20 + 0.575`
     则更像是
     “保住 branch 对齐，
     再用更强 STFT 把共享重建拉回来”
3. validation 上，
   `0.20 + 0.575`
   已经把：
   - `loss_waveform`
   - `loss_stft`
     都压到 baseline 附近甚至略优
4. 但代价也很明确：
   - `rms_guard`
     回吐到略差于 baseline
   - `decoded_to_target_rms_ratio`
     也略差于 baseline
5. `0.15 + 0.55`
   则保持了更温和的 tradeoff：
   - `waveform`
     略优于 baseline
   - `stft / rms_guard / rms_ratio`
     都与 baseline 极接近
   - 同时
     `active_template / adjacent cosine / branch_mean`
     仍优于 baseline

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

### 当前 shadow：`fusedbranch=0.20 + stft=0.55`
- `loss_waveform = 0.121093`
- `loss_stft = 0.593603`
- `loss_rms_guard = 0.137627`
- `loss_active_template = 0.136079`
- `loss_frame_adjacent_cosine = 313.526286`
- `decoded_to_target_rms_ratio = 0.875094`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.666396`

### 新候选 A：`fusedbranch=0.15 + stft=0.55`
- `loss_waveform = 0.120779`
- `loss_stft = 0.590959`
- `loss_rms_guard = 0.143093`
- `loss_active_template = 0.138029`
- `loss_frame_adjacent_cosine = 313.546954`
- `decoded_to_target_rms_ratio = 0.870352`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.675398`

### 新候选 B：`fusedbranch=0.20 + stft=0.575`
- `loss_waveform = 0.120690`
- `loss_stft = 0.589958`
- `loss_rms_guard = 0.144852`
- `loss_active_template = 0.139137`
- `loss_frame_adjacent_cosine = 313.558665`
- `decoded_to_target_rms_ratio = 0.868812`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.666137`

### fixed 6 解读
1. fixed-6
   也给出和 validation
   一致的两角分化：
   - `0.15 + 0.55`
     是更稳的 near-baseline balance 点
   - `0.20 + 0.575`
     是更激进的 waveform/STFT-recovery 点
2. `0.15 + 0.55`
   相比 baseline：
   - `waveform`
     略优
   - `stft`
     只略差
   - `rms_guard / rms_ratio`
     基本回到 baseline
   - `active_template / adjacent cosine / branch_mean`
     仍保留了可见收益
3. `0.20 + 0.575`
   相比 baseline：
   - `waveform`
     更好
   - `stft`
     也更好
   - `branch_mean`
     仍明显更好
   - 但
     `rms_guard / rms_ratio`
     成为新的主要回吐位点
   - 同时
     `active_template / adjacent cosine`
     的收益也比
     `0.20 + 0.55`
     缩小
4. 因而：
   - 这轮没有出现新的单一支配解
   - 而是把 shadow line
     切成了两个风格不同的近优角点

## 五、当前判断
1. 本轮最重要的新事实是：
   - fusion-side shadow line
     已经把
     `waveform / stft`
     税几乎全部收回
2. 但收回之后，
   剩余冲突开始集中到：
   - `rms_guard`
   - `decoded_to_target_rms_ratio`
3. 当前更准确的表述不再是：
   - 只有一个 shadow candidate
4. 而是：
   - `fusedbranch=0.15 + stft=0.55`
     是当前最平衡的 near-baseline shadow candidate
   - `fusedbranch=0.20 + stft=0.575`
     是当前最强的 waveform/STFT-recovery shadow candidate
5. 两者都还没有形成：
   - 对 baseline 的无争议全面胜出
6. 因而默认 leader
   仍然是：
   - 原始
     `periodic_gate rms_floor=0.65`

## 六、下一步建议
1. 当前仍不导听审包
2. 如果继续只做一个最小新实验，
   我现在最推荐的是：
   - 做一个交叉点：
     `fusedbranch=0.15 + stft=0.575`
3. 这发的价值在于：
   - 它最有可能把：
     - `0.15 + 0.55`
       的 near-baseline 稳定性
     - 和
       `0.20 + 0.575`
       的 waveform/STFT 回收
     合到一起
4. 如果这发仍不能形成明显支配解，
   那更值钱的升级就不再是继续微扫，
   而是：
   - 把
     `branch_mean`
     从纯 loss
     升级成更强的
     forward-path
     条件化

## 一句话结论
- 这轮没有找到新的单一 leader，
  但把 fusion-side shadow line
  缩到了两个很近的角点：
  - `fusedbranch=0.15 + stft=0.55`
  - `fusedbranch=0.20 + stft=0.575`
- 其中前者更平衡，
  后者更偏 waveform/STFT 回收；
  下一发最值得做的是它们的交叉点
  `fusedbranch=0.15 + stft=0.575`。
