# 331. Stage5 `acttmpl005_delta6` 听审失败与 recurrent + fusion-side `fusedbranch020` 对比听审包报告

## 结论
- 用户已完成对
  `330`
  中
  `acttmpl005_delta6`
  对比包的人工试听，
  主观结论是：
  - **与 baseline overfit72 没有可感知差异**
  - **仍不存在人声结构**
  - **仍是贴能量包络的单声调 buzz**
- 这意味着：
  - `decode-side objective`
    继续围绕
    `active_template / frame_delta`
    追加，
    当前已经没有继续投入的价值
- 因而本轮正式切到下一类更高层候选：
  - **`recurrent decoder + periodic temporal + periodic rms_floor + fusion-side branch_mean`**

## 一、为什么现在必须转向 `fusion-side / decoder family`
- 到目前为止，
  paired tiny overfit
  上已经连续确认三层事实：
  1. baseline overfit72：
     - 无人声
     - 定调 buzz
     - 但包络更贴输入
  2. `acttmpl005_delta6`：
     - 数值上压低了 template 轴
     - 但听感与 baseline
       **没有可感知差异**
  3. 因而当前问题不能再写成：
     - “只差一点 decode-side loss”
- 更合理的总判断已经收敛为：
  - 当前 `fused_single`
    路线即使在 tiny overfit 上，
    也仍被困在
    `template-buzz + envelope-following`

## 二、本轮新候选

### 1. 候选来源
- 本轮不是拍脑袋换结构，
  而是直接承接：
  - `docs/314_stage5_contractv2_normfix_periodicgate_rmsfloor065_fusedbranch_followup_report.md`
  - `docs/315_stage5_contractv2_normfix_periodicgate_rmsfloor065_fusedbranch_shadow_microtune_report.md`
  - `docs/316_stage5_contractv2_normfix_periodicgate_rmsfloor065_fusedbranch_shadow_microtune_round2_report.md`
- 这些文档共同给出的信号是：
  - `recurrent + periodic temporal + fusion-side branch_mean`
    是当前少数真正能同时推动：
    - `fused_hidden`
      更贴 branch 动态
    - `active_template`
      下降
    - `rms_ratio`
      仍大致守住
    的路线

### 2. 本轮 paired overfit72 配置
- dataset：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- output：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/`
- 关键配置：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `fused_hidden_branch_mean_weight = 0.2`
  - `periodic_waveform_frame_delta_weight = 0.25`
  - `periodic_waveform_frame_adjacent_cosine_weight = 0.01`
  - `periodic_waveform_frame_rms_floor_weight = 0.65`
  - `stft_weight = 0.55`
  - `waveform_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

### 3. 训练命令
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1 `
  --device cpu `
  --num-steps 72 `
  --packages-per-step 2 `
  --validation-interval 12 `
  --checkpoint-interval 12 `
  --sampler-mode sequential `
  --seed 20260325 `
  --deterministic `
  --activity-gate-weight 0.2 `
  --waveform-weight 0.5 `
  --stft-weight 0.55 `
  --rms-guard-weight 0.2 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode pre_overlap_add `
  --waveform-decoder-mode periodic_plus_noise_residual_shape_recurrent `
  --periodic-waveform-frame-delta-weight 0.25 `
  --periodic-waveform-frame-adjacent-cosine-weight 0.01 `
  --periodic-waveform-frame-rms-floor-weight 0.65 `
  --fused-hidden-branch-mean-weight 0.2
```

## 三、本轮数值结果

### 1. selection
- 已执行：
```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 1.0 `
  --max-rms-ratio-deviation 1.0
```
- 结果：
  - `best_validation = step72`
  - `selected_stable_late_stop = step72`
  - `best_validation loss_total = 4.236360`
  - `best_validation decoded_to_target_rms_ratio = 0.983388`

### 2. training-sync export
- 已执行：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 2 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit72_recurrent_periodictemporal_rmsfloor065_fusedbranch020_stft055_validation_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```

### 3. export-side 关键指标
- `case107`：
  - `loss_active_frame_template_excess_relu_0p02 = 0.312774`
  - `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.057061`
  - `decoded_to_target_rms_ratio = 0.988226`
- `case132`：
  - `loss_active_frame_template_excess_relu_0p02 = 0.373368`
  - `loss_fused_hidden_to_branch_mean_unit_rms_l1 = 0.070903`
  - `decoded_to_target_rms_ratio = 0.978549`

## 四、为什么这条线值得听
- 它和
  `acttmpl005_delta6`
  的根本区别不是：
  - 又换了一组 loss weight
- 而是：
  - **直接换了 waveform decoder family**
  - 同时把
    `fusion-side`
    明确拉向
    `branch_mean`
  - 并引入
    recurrent + periodic temporal
    的更强结构先验
- 大白话说：
  - 上一轮是在同一台会发 buzz 的机器上
    调旋钮
  - 这一轮是把机器内部结构也换了

## 五、最小对比听审包

### 1. 听审命令
```powershell
ii reports/audio/stage5_paired_parallel_overfit72_recurrent_fusedbranch020_compare_quick_audit_20260325
```

### 2. bundle 目录
- `reports/audio/stage5_paired_parallel_overfit72_recurrent_fusedbranch020_compare_quick_audit_20260325/`

### 3. 听审结果输出目录
- `reports/audio_reviews/stage5_paired_parallel_overfit72_recurrent_fusedbranch020_compare_quick_audit_20260325/`

### 4. 文件
- `01_case107_source.wav`
- `02_case107_target_aligned.wav`
- `03_case107_baseline_overfit72_decoded.wav`
- `04_case107_recurrent_fusedbranch020_decoded.wav`
- `05_case132_source.wav`
- `06_case132_target_aligned.wav`
- `07_case132_baseline_overfit72_decoded.wav`
- `08_case132_recurrent_fusedbranch020_decoded.wav`
- `README.md`

### 5. 本轮主对比目标
- `04`
  相比
  `03`
  是否第一次出现：
  - 更像人声的共振骨架
  - 不再锁死在单一音调上的发声
- `08`
  相比
  `07`
  是否有同类改善，
  或至少没有更坏

### 6. 本轮试听重点
- 不再把重点放在：
  - 能量包络是否更贴
- 因为 baseline
  已经证明它会贴
- 这轮只看：
  - **有没有第一次出现人声结构**

## 六、当前阶段判断
- 到这一步，
  当前主线已经非常清楚：
  1. `fused_single baseline`
     paired overfit72
     失败
  2. `decode-side objective`
     追加
     `acttmpl005_delta6`
     也失败
  3. 下一条还值得验证的，
     只剩：
     - `fusion-side / decoder family`
       改线

## 七、下一步
1. 先听这份
   `baseline overfit72`
   vs
   `recurrent_fusedbranch020`
   对比包。
2. 如果仍然没有任何人声，
   那就可以把结论写得更硬：
   - 当前 Stage5
     不是“再调几组 loss”
     能解决的问题
   - 下一步应升级到：
     - 更强 waveform target family
     - 或真正不同的 vocoder head
3. 如果哪怕出现极弱的人声雏形，
   再决定是否围绕：
   - `recurrent_fusedbranch020`
   继续做更窄的 paired overfit 放大

## 一句话结论
- `acttmpl005_delta6`
  已被人工确认失败；
  本轮已把下一类真正不同的候选
  `recurrent + fusion-side fusedbranch020`
  跑到 paired overfit72，
  并整理成最小对比听审包，
  下一棒直接听它能不能第一次长出人声结构。
