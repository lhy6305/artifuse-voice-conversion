# 330. Stage5 paired parallel overfit72 基线听审失败与 `acttmpl005_delta6` 对比听审包报告

## 结论
- 用户已完成对
  `329`
  中
  `overfit72 baseline`
  听审包的人工试听，
  最新主观结论是：
  - **仍然没有任何人声**
  - **仍是音调基本不变的 buzz**
  - **但音量变化 / 能量包络比之前更贴输入**
- 这意味着当前 paired tiny overfit
  已经可以把：
  - 振幅
  - 包络
  收到更像输入 / target，
  但仍没有跨过
  **speech emergence**
  这道门槛。
- 基于
  `293`
  的 objective probe，
  本轮已继续完成第一条更强候选：
  - `active_template_weight = 0.05`
  - `frame_delta_weight = 6.0`
- 当前最有价值的下一步，
  不是继续看 loss，
  而是直接听：
  - **同两条 case 上，
    这个候选是否比 baseline
    更接近“摆脱定调 buzz”**

## 一、为什么 baseline overfit72 现在也可以判失败
- 这轮用户反馈非常关键，
  因为它比
  “还是 buzz”
  多补了一条诊断信息：
  - 模型不是完全没学到任何东西
  - 它已经学会了
    **更贴输入的能量包络**
  - 但仍被困在
    **固定音高 / 模板化 buzz**
- 换句话说，
  当前 baseline overfit72
  失败的形式不是：
  - 全面不收敛
- 而是：
  - **收敛到了错误解**

## 二、本轮 objective 候选

### 1. 训练命令
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_acttmpl005_delta6_round1_1 `
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
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --active-template-weight 0.05 `
  --frame-delta-weight 6.0 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode pre_overlap_add
```

### 2. selection
- 已执行：
```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_acttmpl005_delta6_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_overfit72_acttmpl005_delta6_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 1.0 `
  --max-rms-ratio-deviation 1.0
```
- 当前结果：
  - `best_validation = step72`
  - `selected_stable_late_stop = step72`

### 3. training-sync export
- 已执行：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_overfit72_acttmpl005_delta6_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 2 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit72_acttmpl005_delta6_validation_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```

## 三、当前候选给出的新事实

### 1. 新旧 `loss_total` 不能直接横比
- baseline overfit72
  和当前候选
  的 objective 组成不同，
  所以：
  - `0.803014`
    对
    `6.654291`
  不能直接解释成
  “训练退化了多少”
- 当前更应该看的，
  是共享轴和人工听感。

### 2. 共享轴上，候选确实压低了 template 信号
- `case107`
  export-side：
  - baseline
    `loss_active_frame_template_excess_relu_0p02 = 0.511814`
  - candidate
    `loss_active_frame_template_excess_relu_0p02 = 0.138900`
- `case132`
  export-side：
  - baseline
    `loss_active_frame_template_excess_relu_0p02 = 0.575812`
  - candidate
    `loss_active_frame_template_excess_relu_0p02 = 0.181709`
- 说明：
  - 当前候选
    至少在我们明确打击的
    template 轴上，
    不是空转

### 3. RMS 没有被破坏
- aggregate：
  - `best_validation decoded_to_target_rms_ratio = 0.989931`
- per-record：
  - `case107 = 0.994991`
  - `case132 = 0.984871`
- 说明：
  - 这轮候选不是靠把整体振幅搞坏
    来“假装去模板化”

## 四、最小对比听审包

### 1. 听审命令
```powershell
ii reports/audio/stage5_paired_parallel_overfit72_acttmpl005_delta6_compare_quick_audit_20260325
```

### 2. bundle 目录
- `reports/audio/stage5_paired_parallel_overfit72_acttmpl005_delta6_compare_quick_audit_20260325/`

### 3. 听审结果输出目录
- `reports/audio_reviews/stage5_paired_parallel_overfit72_acttmpl005_delta6_compare_quick_audit_20260325/`

### 4. 文件
- `01_case107_source.wav`
- `02_case107_target_aligned.wav`
- `03_case107_baseline_overfit72_decoded.wav`
- `04_case107_acttmpl005_delta6_decoded.wav`
- `05_case132_source.wav`
- `06_case132_target_aligned.wav`
- `07_case132_baseline_overfit72_decoded.wav`
- `08_case132_acttmpl005_delta6_decoded.wav`
- `README.md`

### 5. 本轮主对比目标
- `04`
  相比
  `03`
  是否第一次出现任何：
  - 更像人声的共振
  - 不再锁死在固定音调上的发声
- `08`
  相比
  `07`
  是否有同类改善，
  或至少没有更坏

### 6. 本轮试听重点
- 不是看：
  - 音量包络是否更贴
- 重点只看：
  - **固定音调 buzz
    有没有开始松动**
  - **有没有哪怕极弱的人声雏形**

## 五、当前阶段判断
- 到这一步，
  当前事实已经变成：
  1. paired baseline8
     听审失败
  2. paired overfit72 baseline
     也听审失败
  3. 失败形态已经更清楚：
     - 包络更贴，
       但仍是定调 buzz
  4. objective probe
     推荐的第一候选
     已真实训练并导出
- 因而下一条需要确认的
  只剩一个问题：
  - **打掉 template 轴后，
    听感有没有第一次摆脱“定调 buzz”**

## 六、下一步
1. 先听这份
   baseline vs candidate
   对比包。
2. 如果仍然没有任何人声，
   就可以把结论再写硬一层：
   - 当前
     `v2-core + no-res baseline + waveform head + 这组 objective`
     仍被困在
     `template-buzz + envelope-following`
3. 到那一步，
   主线就不该再是：
   - 继续加步数
   - 继续堆类似 loss weight
   而应升级到：
   - head / decoder family
     层面的改线

## 一句话结论
- `overfit72 baseline`
  已被人工确认成：
  “包络更贴了，
   但仍是定调 buzz”；
  本轮已把
  `acttmpl005_delta6`
  候选整理成最小对比听审包，
  下一棒直接听它有没有第一次撬动
  speech emergence。
