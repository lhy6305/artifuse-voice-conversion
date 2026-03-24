# 2026-03-24 Stage5 `contractv2_normfix` `active_template=0.25 + frame_adjacent_cosine=0.25` 量化候选报告

## 结论
- 本轮已在
  `active_template=0.25`
  的现有 quant-only 路线基础上，
  补跑并核对：
  - `frame_adjacent_cosine_weight = 0.25`
- 结果可以明确写成两句：
  1. `adjacent cosine`
     确实被压下来了；
  2. 但压低幅度很有限，
     且共享重建指标明显变差，
     所以这不是可直接升级的好候选。
- 更具体地说：
  - 相比
    `active_template=0.25`
    单臂，
    step4 validation
    的
    `loss_frame_adjacent_cosine_excess_relu_0p02`
    从
    `329.727118`
    降到
    `321.258283`
    约
    `-2.57%`
  - 但同时：
    - `loss_waveform`
      `0.130195 -> 0.152367`
    - `loss_stft`
      `0.659763 -> 0.801631`
    - `loss_rms_guard`
      `0.106174 -> 0.197122`
    - `decoded_to_target_rms_ratio`
      `0.990619 -> 1.225243`
- 因而当前判断是：
  - 这条 `adjacent cosine`
    约束有真实方向性，
  - 但以当前形式和权重，
    它更像在强推一种代价很高的量化修正，
    还不能写成
    “真正把路线拉向更好解”。

## 一、背景与本轮目标
- 上一轮主线已经确认：
  - `active_template`
    这一轴
    能明显压模板化，
  - 但用户指出：
    - `adjacent cosine`
      仍然过高
- 因此本轮不做：
  - 新结构改造
  - 新听审包
  - decoder / fusion
    额外变量扩张
- 只做一条
  quant-only
  候选：
  - 在
    `active_template=0.25`
    基础上，
    加：
    - `frame_adjacent_cosine_weight = 0.25`

## 二、有效运行与参数确认

### 代码接线
- 当前工作区已恢复：
  - `src/v5vc/cli.py`
  - `src/v5vc/offline_vocoder_training.py`
- 已支持：
  - `--frame-adjacent-cosine-weight`
- 且 dataset loop
  summary
  已明确记录：
  - `frame_adjacent_cosine = 0.25`
- 所以本轮不是
  “参数没透传”的假实验。

### 有效训练目录
- candidate：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template025_adjcos025_smoke_round1_1/`
- 对照臂：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template025_smoke_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_baseline_smoke_round1_2/`

### 共同设置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- `num_steps = 4`
- `packages_per_step = 4`
- `validation_interval = 2`
- `checkpoint_interval = 2`
- `sampler_mode = shuffle`
- `seed = 20260324`
- `deterministic = true`
- `device = cuda:0`
- `use_predicted_activity_gate = true`
- `reconstruction_frame_gain_apply_mode = pre_overlap_add`

### 对照关系
- baseline：
  - `active_template = 0.0`
  - `frame_adjacent_cosine = 0.0`
- active-template 对照臂：
  - `active_template = 0.25`
  - `frame_adjacent_cosine = 0.0`
- 本轮 candidate：
  - `active_template = 0.25`
  - `frame_adjacent_cosine = 0.25`

## 三、step4 validation 结果

### baseline 复算参考
- `loss_waveform = 0.125092`
- `loss_stft = 0.601829`
- `loss_rms_guard = 0.155673`
- `loss_active_template = 0.503176`
- `loss_frame_delta = 0.936750`
- `loss_frame_adjacent_cosine = 330.772771`
- `decoded_to_target_rms_ratio = 0.899397`

### `active_template=0.25`
- `loss_waveform = 0.130195`
- `loss_stft = 0.659763`
- `loss_rms_guard = 0.106174`
- `loss_active_template = 0.018127`
- `loss_frame_delta = 0.939553`
- `loss_frame_adjacent_cosine = 329.727118`
- `decoded_to_target_rms_ratio = 0.990619`

### `active_template=0.25 + frame_adjacent_cosine=0.25`
- `loss_waveform = 0.152367`
- `loss_stft = 0.801631`
- `loss_rms_guard = 0.197122`
- `loss_active_template = 0.050746`
- `loss_frame_delta = 0.947508`
- `loss_frame_adjacent_cosine = 321.258283`
- `decoded_to_target_rms_ratio = 1.225243`

## 四、当前直接比较

### 相比 `active_template=0.25` 单臂
- `loss_frame_adjacent_cosine`
  确实下降：
  - `329.727118 -> 321.258283`
  - 约
    `-8.468835`
  - 相对降幅
    `-2.57%`
- 但共享重建指标同步恶化：
  - `loss_waveform`
    `+0.022172`
  - `loss_stft`
    `+0.141868`
  - `loss_rms_guard`
    `+0.090948`
  - `loss_frame_delta`
    `+0.007955`
  - `decoded_to_target_rms_ratio`
    `+0.234624`

### 相比 baseline
- `loss_frame_adjacent_cosine`
  也确实更低：
  - `330.772771 -> 321.258283`
  - 相对降幅
    约
    `-2.88%`
- 但 candidate
  的
  `waveform / stft / rms_guard`
  全部差于 baseline

## 五、该如何解释
1. 这条约束不是完全没用。
   它至少说明：
   - 当前 route
     对
     `decoded 相邻帧余弦高于 aligned target`
     这件事
     是可响应的
2. 但当前改善非常有限。
   如果目标是把
   “仍然过高的 adjacent cosine”
   真正压到可接受区，
   本轮还不能算做到。
3. 更关键的是，
   它现在像是在用较大代价
   换一个小幅量化下降：
   - `adjacent cosine`
     变好一点
   - 但重建质量和幅度稳定性
     明显变差
4. 因此当前更准确的阶段结论不是：
   - 这条线有效，
     可以继续同类微调
5. 而是：
   - 这条 loss
     有方向性，
     但当前形态太粗，
     还没有把系统推向更好的整体解

## 六、补充说明
- 历史
  `active_template=0.25`
  run
  的原始 summary
  尚未记录
  `loss_frame_adjacent_cosine_excess_relu_0p02`
  字段，
  因为当时该指标还未落到 summary。
- 为保证口径一致，
  本报告对：
  - baseline
  - `active_template=0.25`
  - `active_template=0.25 + frame_adjacent_cosine=0.25`
  三个 checkpoint
  都用当前 validation helper
  重新复算了一次
  step4 validation 指标。

## 七、下一步建议
1. 不建议把这条
   `active_template=0.25 + frame_adjacent_cosine=0.25`
   直接升级成长训
2. 若还想继续利用
   `adjacent cosine`
   这条信号，
   更合理的是：
   - 先重新设计它的进入方式
   - 或把它做成更局部、
     更有 gating 的约束
   - 而不是继续沿当前权重线性加压
3. 当前主线判断不变：
   - 真正的主要问题层级
     仍在
     `fusion / fused_hidden`
   - 本轮只说明：
     decode-side
     的 stationarity
     还能再被量化约束触碰，
     但这还不是足够好的解法

## 一句话结论
- `frame_adjacent_cosine_weight=0.25`
  在
  `active_template=0.25`
  基础上，
  确实把
  adjacent cosine
  压低了一点；
  但降幅只有
  `2% ~ 3%`
  量级，
  同时明显拖坏了
  `waveform / stft / rms / 幅度比例`，
  所以当前不能把它当成有效候选晋级。
