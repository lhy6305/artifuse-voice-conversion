# 2026-03-24 Stage5 `contractv2_normfix` `fused_hidden_branch_mean=0.25` 最小 smoke 报告

## 结论
- 本轮已实现并跑通一条新的
  fusion-side
  最小候选：
  - `fused_hidden_branch_mean_weight = 0.25`
- 这条候选的定位是：
  - 不再继续做
    decode-side
    `active_template / frame_adjacent_cosine / frame_delta`
    小调参
  - 改为直接约束：
    - `fused_hidden`
      向
      `0.5 * (periodic_hidden + noise_hidden)`
      的
      unit-RMS
      表征靠拢
- 当前结果比之前两条
  `fused_hidden_template / delta`
  轻量 penalty
  更有价值：
  1. step4 validation
     上：
     - `loss_waveform`
       略优于 baseline
     - `loss_rms_guard`
       略优于 baseline
     - `loss_active_template`
       明显下降
  2. fixed 6 条 aggregate
     也延续同方向
  3. `loss_fused_hidden_to_branch_mean_unit_rms_l1`
     从 baseline 的
     `1.144644`
     降到
     `0.861832`
     约
     `-24.7%`
- 但它还不能直接写成
  “已转正”：
  - `loss_stft`
    仍有一定恶化
  - `frame_adjacent_cosine`
    几乎没动
- 因此当前更准确的阶段判断是：
  - 这是第一条
    **真正碰到 fusion 有效层级**
    的最小训练候选
  - 已足够值得进入
    **固定 6 条听审**
  - 但还不是能直接晋级成长训的结论

## 一、背景
- `docs/299`
  的 bypass probe
  已确认：
  - 现有 decoder
    在拿到更动态的 branch hidden
    时会响应
  - 但直接硬喂 branch hidden
    会掉进
    高频、过响、非语音区域
- 因此本轮最小训练实验的目标不是：
  - 直接把 branch hidden
    硬塞给 decoder
- 而是：
  - 让训练中的
    `fused_hidden`
    向 branch mean
    轻量靠拢
  - 同时保留：
    - `waveform`
    - `stft`
    - `rms_guard`
    作为稳定锚点

## 二、实现改动
- 已在训练损失里新增：
  - `loss_fused_hidden_to_branch_mean_unit_rms_l1`
- 含义：
  - 先计算
    `branch_mean = 0.5 * (periodic_hidden + noise_hidden)`
  - 再把：
    - `fused_hidden`
    - `branch_mean`
    都做
    unit-RMS
    归一化
  - 最后在
    active-frame
    权重下
    计算逐帧 L1
- dataset loop
  新增参数：
  - `--fused-hidden-branch-mean-weight`

## 三、运行配置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 有效训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_fusedhidden_branchmean025_smoke_round1_1/`
- smoke 配置：
  - `num_steps = 4`
  - `packages_per_step = 4`
  - `validation_interval = 2`
  - `checkpoint_interval = 2`
  - `device = cuda:0`
  - `seed = 20260324`
  - `deterministic = true`
  - `activity_gate_weight = 0.2`
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `active_template_weight = 0.0`
  - `frame_delta_weight = 0.0`
  - `frame_adjacent_cosine_weight = 0.0`
  - `fused_hidden_template_weight = 0.0`
  - `fused_hidden_delta_weight = 0.0`
  - `fused_hidden_branch_mean_weight = 0.25`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 四、step4 validation 结果

### baseline 参考
- 使用：
  - `docs/294`
    中的
    `contractv2_normfix_baseline_smoke_round1_2`

### candidate step4 validation
- `loss_waveform = 0.124456`
- `loss_stft = 0.612116`
- `loss_rms_guard = 0.152025`
- `loss_active_template = 0.465209`
- `loss_frame_delta = 0.936839`
- `loss_frame_adjacent_cosine = 330.738667`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.862593`
- `decoded_to_target_rms_ratio = 0.903583`

### 相比 baseline
- baseline：
  - `loss_waveform = 0.125092`
  - `loss_stft = 0.601828`
  - `loss_rms_guard = 0.155673`
  - `loss_active_template = 0.503176`
  - `loss_frame_delta = 0.936750`
  - `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.143996`
  - `decoded_to_target_rms_ratio = 0.899397`
- 当前解释：
  - `loss_waveform`
    轻微改善
    `0.125092 -> 0.124456`
  - `loss_rms_guard`
    轻微改善
    `0.155673 -> 0.152025`
  - `loss_active_template`
    明显下降
    `0.503176 -> 0.465209`
  - `loss_fused_hidden_to_branch_mean_unit_rms_l1`
    明显下降
    `1.143996 -> 0.862593`
  - 但
    `loss_stft`
    变差
    `0.601828 -> 0.612116`
  - `frame_adjacent_cosine`
    基本不动
    `330.772771 -> 330.738667`

## 五、fixed 6 条记录 aggregate

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### baseline
- `loss_waveform = 0.125503`
- `loss_stft = 0.602313`
- `loss_rms_guard = 0.107393`
- `loss_active_template = 0.497106`
- `loss_frame_delta = 0.898517`
- `loss_frame_adjacent_cosine = 315.431819`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 1.144644`
- `decoded_to_target_rms_ratio = 0.908930`

### candidate
- `loss_waveform = 0.124739`
- `loss_stft = 0.615690`
- `loss_rms_guard = 0.103738`
- `loss_active_template = 0.457772`
- `loss_frame_delta = 0.898638`
- `loss_frame_adjacent_cosine = 315.399851`
- `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.861832`
- `decoded_to_target_rms_ratio = 0.913369`

### aggregate 解释
- 这 6 条 fixed-record
  与 validation
  保持同方向：
  - `waveform`
    小幅改善
  - `rms_guard`
    小幅改善
  - `active_template`
    明显改善
  - `branch_mean`
    约束项
    明显下降
  - `stft`
    小幅变差
  - `frame_adjacent_cosine`
    基本不变

## 六、试听包状态
- 已完成 candidate
  固定 6 条音频导出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusedhidden_branchmean025_smoke_round1_1/`
- 对照 baseline
  仍使用：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`
- 导出语义：
  - `listening_audio_source = decoded_pitch_matched`
  - `pitch_match_reference = aligned_target`
  - `use_predicted_activity_gate = true`
  - `predicted_activity_gate_apply_mode = pre_overlap_add`

## 七、当前阶段判断
1. 这条候选比
   `docs/297`
   的
   `fused_hidden_template=0.05 + fused_hidden_delta=2.0`
   更像真正碰到了有用层级
2. 它的价值不在于：
   - 把
     `frame_adjacent_cosine`
     拉下来了
3. 而在于：
   - 在不明显伤害
     `waveform / rms_guard`
     的前提下，
     真正推动了
     `fused_hidden`
     向 branch-side
     动态结构靠近
   - 同时把
     `active_template`
     一并拉低
4. 当前不能直接写成：
   - 已找到可长训 recipe
5. 但已经足够写成：
   - 当前最值得进入人工听审的
     fusion-side
     候选

## 八、建议下一步
1. 第一优先：
   - 先听
     baseline
     vs
     `fused_hidden_branchmean025`
     的 fixed 6 条包
2. 听审重点：
   - 是否仍是纯 buzz
   - 是否出现比 baseline
     更稳定的人声感或更少模板味
   - 高频刺感是否明显变重
3. 若听感有正向信号：
   - 下一步可做
     `branch_mean_weight`
     小 sweep
     例如：
     - `0.10`
     - `0.25`
     - `0.40`
4. 若听感仍无正向信号：
   - 当前也不建议立即退回
     decode-side
     小 loss
   - 更合理的是：
     - 在
       `branch_mean`
       约束基础上，
       补一个更强的
       stability / spectral
       抑制项

## 一句话结论
- `fused_hidden_branch_mean=0.25`
  是目前第一条
  值得认真听的
  fusion-side
  最小候选：
  - 它确实把
    `fused_hidden`
    往 branch-side
    动态结构拉近了，
  - 也带来了
    `waveform / rms_guard / active_template`
    的小幅到中幅改善；
  但
  `stft`
  仍偏差，
  `adjacent cosine`
  还没真正动起来，
  所以现在最合理的下一步是
  **先听，不先长训**。
