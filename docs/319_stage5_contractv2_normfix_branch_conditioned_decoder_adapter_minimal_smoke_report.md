# 319. Stage5 `contractv2_normfix` branch-conditioned decoder adapter 最小 smoke 报告

## 一、目的
1. 按
   `docs/318_stage5_contractv2_normfix_fusion_shadow_compare_human_audit_fail_and_next_plan.md`
   的计划，
   在当前最强骨架上做第一次：
   - **非线性、结构级 forward-path conditioning**
     最小验证
2. 本轮不再继续：
   - `fused_hidden_branch_mean + stft`
     loss-side
     微调
3. 本轮只回答一个问题：
   - 在当前最强骨架上，
     一个最小的
     `branch-conditioned decoder adapter`
     能不能先在 fixed-6 上形成值得导听审的候选

## 二、代码改动

### 新增结构
- 文件：
  - `src/v5vc/offline_vocoder_scaffold.py`
- 新增开关：
  - `use_decoder_branch_condition_adapter`
- adapter 输入：
  - `fused_hidden`
  - `branch_mean_hidden`
  - `fused_hidden - branch_mean_hidden`
- adapter 输出：
  - `decoder_branch_condition_gate`
  - `decoder_fused_condition`
  - `decoder_periodic_condition`
  - `decoder_noise_condition`
- 作用方式：
  - 在 `fused_single`
    下，
    给
    `decoder_hidden`
    加一个 gated correction
  - 在 branch-style decoder
    下，
    给进入 waveform decoder / residual decoder 的 branch hidden
    加 gated correction

### 透传接线
- 文件：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
  - `src/v5vc/nores_vocoder_audio_export.py`
- 新增 CLI 参数：
  - `--use-decoder-branch-condition-adapter`
- 同步完成：
  - train step
  - training loop
  - dataset loop
  - checkpoint 反推建模
  - audio export summary

### 导出回归兼容
- audio export
  已能自动从 checkpoint
  state_dict
  识别 adapter 模块存在与否

## 三、实验配置

### 固定主线
- baseline:
  - `periodic_plus_noise_residual_shape_recurrent`
  - `periodic_waveform_frame_delta = 0.25`
  - `periodic_waveform_frame_adjacent_cosine = 0.01`
  - `periodic_waveform_frame_rms_floor = 0.65`
  - `waveform = 0.5`
  - `stft = 0.5`
  - `rms_guard = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

### 本轮候选
1. `branchcondadapter`
   - output:
     `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_branchcondadapter_smoke_round1_1`
2. `branchcondadapter_conservative`
   - 与上者相同，
     但 adapter 做了保守初始化：
     - gate 权重置零
     - gate bias 设为 `-2.0`
     - 三个 correction projection
       全零初始化
   - output:
     `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_branchcondadapter_conservative_smoke_round1_1`

## 四、step4 validation 对比

### baseline
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`

### `branchcondadapter`
- `loss_waveform = 0.118478`
- `loss_stft = 0.542374`
- `loss_rms_guard = 0.207510`
- `loss_active_template = 0.286174`
- `loss_frame_adjacent_cosine = 329.830888`
- `decoded_to_target_rms_ratio = 0.835155`

### `branchcondadapter_conservative`
- `loss_waveform = 0.119979`
- `loss_stft = 0.550005`
- `loss_rms_guard = 0.193689`
- `loss_active_template = 0.264050`
- `loss_frame_adjacent_cosine = 329.594893`
- `decoded_to_target_rms_ratio = 0.851279`

### validation 解读
1. 两条 adapter
   都非常明确地拉低了：
   - `waveform`
   - `stft`
2. 但共享回吐也同样明确：
   - `active_template`
     大幅变差
   - `adjacent cosine`
     变差
   - `rms_guard`
     变差
   - `decoded_to_target_rms_ratio`
     也更差
3. 保守初始化版
   相比原始版：
   - 的确把回吐减轻了一些
   - 但没有改变方向
4. 因而它不是：
   - “只差初始化”
   的问题

## 五、fixed 6 条 aggregate

### baseline
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870710`

### `branchcondadapter`
- `loss_waveform = 0.118880`
- `loss_stft = 0.539548`
- `loss_rms_guard = 0.169937`
- `loss_active_template = 0.280082`
- `loss_frame_adjacent_cosine = 314.547119`
- `decoded_to_target_rms_ratio = 0.846113`

### `branchcondadapter_conservative`
- `loss_waveform = 0.120210`
- `loss_stft = 0.544413`
- `loss_rms_guard = 0.153712`
- `loss_active_template = 0.253424`
- `loss_frame_adjacent_cosine = 314.313416`
- `decoded_to_target_rms_ratio = 0.860224`

### fixed-6 解读
1. fixed-6
   与 validation
   完全同方向：
   - `waveform / stft`
     明显变好
   - 但
     `active_template / adjacent cosine / rms_guard / rms_ratio`
     一起回吐
2. 其中保守初始化版
   已经是本轮更好的 adapter 形态：
   - 相比非保守版，
     它把
     `active_template`
     从
     `0.280082`
     拉回到
     `0.253424`
   - `adjacent cosine`
     从
     `314.547119`
     拉回到
     `314.313416`
   - `rms_ratio`
     也从
     `0.846113`
     回到
     `0.860224`
3. 但即便如此，
   它仍明显差于 baseline：
   - `active_template`
   - `adjacent cosine`
   - `rms_guard`
   - `rms_ratio`
4. 因而这条最小 adapter
   **还不到值得导 fixed-6 听审包的程度**

## 六、当前判断
1. 这轮最重要的新信息不是：
   - adapter 彻底失败
2. 而是：
   - **“宽范围 branch-conditioned hidden correction” 这条最小形态不对**
3. 更具体地说：
   - 它会很快买到
     `waveform / stft`
     改善
   - 但会同时破坏当前最强骨架已经建立起来的：
     - 局部结构收益
     - 能量稳态
4. 这说明当前最小 adapter
   介入位置仍然太宽，
   它不是：
   - 稳定地校正 decoder 工作区
   更像是：
   - 对 branch hidden 做了过强、过早的分布改写

## 七、更新后的下一步方案
1. 当前不导听审包
2. 下一版结构验证
   不应继续沿：
   - 整个 periodic/noise decoder hidden
     做 broad correction
3. 更合理的下一发应收窄到：
   - **只改 residual-shape path**
4. 也就是：
   - 保持
     `temporal_periodic_hidden`
     与
     `temporal_noise_hidden`
     主干不动
   - 只在
     `noise_residual_shape_head`
     或 residual envelope
     这一级
     注入 branch-conditioned adapter
5. 这样做的目的很明确：
   - 尽量保住当前骨架已经拿到的
     `active_template / adjacent cosine / rms_ratio`
   - 只在 timbre / residual shaping
     这一小块
     给 decoder 新的工作区

## 一句话结论
- 第一次
  `branch-conditioned decoder adapter`
  最小 smoke
  已经完成，
  但它的当前形态不成立：
  它会快速改善
  `waveform / stft`，
  却同步破坏
  `active_template / adjacent cosine / rms_ratio`
  这些更关键的结构指标。
- 因而下一步不该导听审，
  也不该继续围着这条
  broad hidden correction
  形态打转；
  更合理的是把 adapter
  收窄到
  **residual-shape-only**
  路径。
