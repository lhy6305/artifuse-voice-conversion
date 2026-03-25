# 334. Stage5 short-window MRSTFT 在可比 baseline 下的重检报告

## 结论
- 在补齐调用链之后，
  short-window MRSTFT
  已经真正进入
  dataset-level paired overfit24
  训练。
- 但在这次严格可比的
  `activity_gate_weight = 0.0`
  baseline
  对照下，
  当前
  `multires_stft_short_weight = 0.2`
  的结果并没有形成
  “可直接推广”的正收益：
  - 单分辨率
    `loss_stft`
    有改善
  - 但
    `loss_total`
    变差
  - `loss_waveform`
    也略差
  - `decoded_to_target_rms_ratio`
    基本打平
- 因此，
  当前更合理的判断不是：
  - short-window MRSTFT
    完全无效
- 而是：
  - **它已接通且确实在起作用，
    但在当前权重 `0.2`
    下，
    尚未形成值得默认保留的净收益。**

## 后续校正
- 上述
  `0.2`
  判断
  的主要意义是：
  - 先把“是否真正接通”这件事确认下来
- 后续在
  `docs/335_stage5_mrstft_short_low_weight_sweep_report.md`
  中，
  已进一步按
  `0 / 0.05 / 0.1 / 0.2`
  的共享指标做了更完整 sweep，
  并明确回避把
  `loss_total`
  当作跨 objective
  的唯一排序依据

## 对照对象

### A. 可比 baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_activitygate000_baseline_round1_1/`
- 关键口径：
  - paired tiny overfit dataset
  - `24` 步
  - `packages_per_step = 2`
  - `--use-predicted-activity-gate`
  - `activity_gate_weight = 0.0`
  - `multires_stft_short_weight = 0.0`

### B. MRSTFT 候选
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort020_smoke_round1_2/`
- 关键口径：
  - 与 baseline
    其余条件一致
  - 唯一新增：
    - `multires_stft_short_weight = 0.2`

## 关键结果

### step24 validation 对照
- baseline
  (`activitygate000_baseline_round1_1`)
  - `loss_total = 0.856925`
  - `loss_stft = 0.364725`
  - `loss_waveform = 0.159988`
  - `decoded_to_target_rms_ratio = 0.978607`
- MRSTFT
  (`mrstftshort020_smoke_round1_2`)
  - `loss_total = 0.914235`
  - `loss_stft = 0.337852`
  - `loss_waveform = 0.161479`
  - `decoded_to_target_rms_ratio = 0.980703`
  - `loss_mrstft_short_256_512_1024 = 0.336557`

### 如何解释
1. `loss_mrstft_short_256_512_1024`
   非零且被压到
   `0.336557`，
   说明新目标确实在优化，
   不是空转。
2. 单分辨率
   `loss_stft`
   从
   `0.364725`
   降到
   `0.337852`，
   说明短窗频谱侧约束
   对频谱重建有一定帮助。
3. 但与此同时：
   - `loss_total`
     从
     `0.856925`
     升到
     `0.914235`
   - `loss_waveform`
     从
     `0.159988`
     升到
     `0.161479`
4. 这更像：
   - 当前权重下，
     MRSTFT
     在拉低 STFT 轴，
     但没有换来整体更优的共享目标平衡。

## 当前阶段判断
- 若当前问题是：
  - “short-window MRSTFT
     现在能不能直接升格成默认 loss family”
- 当前答案应是：
  - **不能。**
- 若当前问题是：
  - “它是不是已经真正接通并对优化产生影响”
- 当前答案是：
  - **是。**

## 下一步建议
1. 不把
   `multires_stft_short_weight = 0.2`
   直接推广到更大训练。
2. 若还要继续追这条线，
   更合理的是：
   - 降权重做最小 sweep，
     例如
     `0.05 / 0.1`
   - 只看共享指标是否还能保住
     `loss_total / loss_waveform`
3. 若当前主线优先级更高，
   也可以先把这条线收口为：
   - “已接通，
      当前 `0.2`
      没有形成净收益，
      暂不升级为默认设置”
