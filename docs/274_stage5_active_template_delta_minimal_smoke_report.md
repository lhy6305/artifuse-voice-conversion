# 2026-03-24 Stage5 active-template + delta 最小训练冒烟报告

## 结论
- 本轮已经把
  `active_template_excess`
  和
  `frame_delta`
  正式接进了
  Stage5 no-res
  训练主链，
  包括：
  - train-step
  - single-package loop
  - dataset loop
  - validation
  - audio export metrics
- 最小双臂 source-to-target smoke
  已实际跑通：
  - baseline 臂
  - `active_template + delta`
    candidate 臂
- 当前 smoke 的直接结果是：
  - candidate 臂
    确实开始显著压低
    `loss_active_frame_template_excess_relu_0p02`
  - 但
    `loss_frame_delta_unit_rms_l1`
    还几乎没动
  - 同时
    `waveform / stft`
    目前略差于 baseline 臂

先说人话：
- 这说明我们现在已经不再停留在
  “离线 probe 猜想”
  了，
  而是已经拿到了
  真训练 checkpoint
  和新的试听包
- 但这轮还不能写成：
  - 新 objective
    已经明显改善听感
- 更准确的写法是：
  - candidate objective
    已经开始改写模型的
    anti-template 行为
  - 但还没有把这种变化
    转成更好的
    waveform/stft
    路线

## 本轮工程动作

### 1. 训练 plumbing 正式接线
- 更新文件：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
  - `src/v5vc/nores_vocoder_audio_export.py`
- 当前新增训练侧权重：
  - `--active-template-weight`
  - `--frame-delta-weight`
- 新 loss
  已进入：
  - `compute_nores_vocoder_losses`
  - 训练 step / loop / dataset loop
  - validation
  - export-side metric recompute

### 2. 单包 train-step 冒烟
- 命令目标：
  - `target::chapter3_2_firefly_212`
- 产物目录：
  - [offline_mvp_nores_vocoder_train_step_active_template_delta_smoke_chapter3_2_firefly_212_round1_1](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_train_step_active_template_delta_smoke_chapter3_2_firefly_212_round1_1)
- 结果：
  - train step
    实际完成
  - backward / optimizer / checkpoint
    路径已确认跑通

### 3. 最小双臂 dataset smoke
- 共同口径：
  - dataset index:
    `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - `num_steps = 4`
  - `packages_per_step = 4`
  - `validation_interval = 2`
  - `checkpoint_interval = 2`
  - `device = cuda:0`
  - `seed = 20260324`
  - `deterministic = true`
  - `waveform = 0.5`
  - `stft = 0.5`
  - `rms_guard = 0.2`
  - `activity_gate = 0.2`
  - `use_predicted_activity_gate = true`
- baseline 臂输出：
  - [offline_mvp_nores_vocoder_dataset_training_loop_baseline_smoke_round1_2](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_baseline_smoke_round1_2)
- candidate 臂输出：
  - [offline_mvp_nores_vocoder_dataset_training_loop_active_template_delta_smoke_round1_2](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_active_template_delta_smoke_round1_2)
- candidate 额外权重：
  - `active_template = 0.1`
  - `frame_delta = 4.0`

## 关键结果

### 1. candidate 臂已经真正进梯度，并开始压低 anti-template 指标
- step4 validation
  aggregate 对比：

#### baseline 臂
- `loss_total = 1.229875`
- `loss_waveform = 0.122327`
- `loss_stft = 0.557616`
- `loss_rms_guard = 0.186210`
- `loss_active_frame_template_excess_relu_0p02 = 0.485220`
- `loss_frame_delta_unit_rms_l1 = 0.936003`

#### candidate 臂
- `loss_total = 5.021665`
- `loss_waveform = 0.123931`
- `loss_stft = 0.585449`
- `loss_rms_guard = 0.168018`
- `loss_active_frame_template_excess_relu_0p02 = 0.344566`
- `loss_frame_delta_unit_rms_l1 = 0.936355`

直接结论：
- candidate 臂
  最明确的变化是：
  - `active_template_excess`
    从
    `0.485220`
    降到
    `0.344566`
- 但
  `frame_delta`
  目前几乎不变
- 同时
  `waveform / stft`
  当前略差于 baseline

### 2. 6 条试听对照记录上，candidate 臂的变化方向也一致
- 对照记录：
  - `target::chapter3_2_firefly_212`
  - `target::chapter3_2_firefly_155`
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_17_firefly_133`
  - `target::chapter3_3_firefly_245`
  - `target::chapter3_2_firefly_163`
- 在这 6 条上，
  candidate 臂的
  `loss_active_frame_template_excess_relu_0p02`
  都下降约：
  - `0.143` 到 `0.150`
- 但
  `loss_frame_delta_unit_rms_l1`
  仍基本不变
  （约 `+0.0002` 到 `+0.0011`）

## 新试听包

### 1. baseline smoke bundle
- [offline_mvp_nores_vocoder_audio_export_baseline_smoke_round1_2](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_baseline_smoke_round1_2)

### 2. candidate smoke bundle
- [offline_mvp_nores_vocoder_audio_export_active_template_delta_smoke_round1_2](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_active_template_delta_smoke_round1_2)

### 3. 当前 bundle 记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

## 训练后 collapse probe 复查
- baseline smoke checkpoint
  的 `baseline_decode_route` aggregate：
  - `weighted_wave_objective = 0.370979`
  - `active_template_excess = 0.485107`
  - `frame_delta = 0.960002`
- candidate smoke checkpoint
  的 `baseline_decode_route` aggregate：
  - `weighted_wave_objective = 0.381877`
  - `active_template_excess = 0.344369`
  - `frame_delta = 0.960397`

直接结论：
- candidate 训练
  已经把模型
  往
  anti-template
  方向推了
- 但当前并没有同时改善
  raw weighted waveform objective
  或 frame-delta
  行为

## 本轮关键修正
- 初版训练 helper
  误沿用了
  probe 里的
  `detach().cpu()`
  写法
- 症状是：
  - baseline / candidate
    两臂训练后，
    validation sidecar
    几乎完全一致
- 修正后：
  - helper 保持 tensor
    在训练 device 上，
    新项才真正进入梯度

## 对下一步的直接含义
1. 当前已经具备
   真训练最小闭环：
   - candidate objective
   - checkpoint
   - 并排试听包
2. 当前不建议马上扩大训练步数，
   因为这轮已经显示：
   - active-template 指标
     在变好
   - 但 frame-delta
     没接住
   - waveform/stft
     还略变差
3. 更合理的下一步是：
   - 先回听
     新的 candidate smoke bundle
   - 再决定是：
     - 继续调
       `active_template / delta`
       的耦合方式
     - 还是把
       delta
       从“大权重直接压总分”
       改成更局部的 residual repair 形式

## 一句话结论
- 最小 source-to-target 训练冒烟已经跑通，
  candidate objective
  也开始真实改变模型行为；
  但当前变化主要体现在
  anti-template 指标，
  还没有转成明确更好的
  waveform/stft
  或可听进展。
