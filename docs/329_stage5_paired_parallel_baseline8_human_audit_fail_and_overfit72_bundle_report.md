# 329. Stage5 paired parallel baseline8 听审失败与 overfit72 听审包报告

## 结论
- 用户已完成对
  `328`
  的 paired baseline8
  quick audit
  听审，
  主观结论是：
  - **不存在任何人声**
  - **依旧纯 buzz**
  - **音调 / 响度也没有太大变化**
- 这条主观结论已经足够把
  `paired baseline8`
  的阶段判断写硬成：
  - 真实 source-to-target
    口径已接入
  - 但当前 baseline
    仍没有出现
    speech emergence
- 基于这个结果，
  本轮没有回去继续叠新 loss，
  而是直接推进到下一条更有判别力的实验：
  - **两条真实配对上的 tiny overfit72**

## 一、为什么下一步不是继续 baseline8 微调
- 当前 paired baseline8
  已经给出一个足够明确的可听结论：
  - 仍是 pure buzz
- 在这种情况下，
  最有价值的问题不再是：
  - “再多几步 baseline8
     会不会碰巧转正”
- 而是：
  - **现有 paired route
    在仅有的两条真实配对上，
    连过拟合出任何人声雏形的能力都有没有**

## 二、本轮 overfit72 设计

### 1. 数据
- 目录：
  - `data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/`
- 说明：
  - train / validation
    都放入同样两条真实配对：
    - `parallel_firefly_107 -> target_firefly_107`
    - `parallel_firefly_132 -> target_firefly_132`
- 这不是泛化评估，
  而是最小记忆能力诊断。

### 2. 训练命令
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit72_round1_1 `
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
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode pre_overlap_add
```

## 三、overfit72 结果

### 1. 数值
- train loss：
  - `step1 = 1.740600`
  - `step72 = 0.805446`
- validation loss：
  - `best_validation(step72) = 0.803014`
- selection：
  - `best_validation = step72`
  - `selected_stable_late_stop = step72`

### 2. training-sync export
- 已执行：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_overfit72_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 2 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit72_validation_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```

### 3. 导出后的关键指标
- `107`：
  - `decoded_to_target_rms_ratio = 1.008819`
- `132`：
  - `decoded_to_target_rms_ratio = 0.992918`
- 说明：
  - 这轮 tiny overfit
    至少已经把最基本的
    振幅匹配
    收到了非常接近
    `1.0`
  - 但这仍不等于
    已经长出人声

## 四、最小听审包

### 目录
- `reports/audio/stage5_paired_parallel_overfit72_quick_audit_20260325/`

### 文件
- `01_case107_source.wav`
- `02_case107_target_aligned.wav`
- `03_case107_decoded.wav`
- `04_case132_source.wav`
- `05_case132_target_aligned.wav`
- `06_case132_decoded.wav`
- `README.md`

## 五、当前阶段判断
- 当前已经有两条明确事实：
  1. `paired baseline8`
     听审已失败，
     仍是纯 buzz
  2. `paired overfit72`
     已把两条真实配对
     的数值显著往下压，
     且 export-side
     RMS 已基本贴住 target
- 现在最关键的新问题只剩一个：
  - **即便在这种 tiny overfit 条件下，
    听感是否仍然完全没有人声**

## 六、下一步
1. 先听
   `overfit72`
   quick audit
   包。
2. 如果仍是纯 buzz，
   那就可以把结论再写硬一层：
   - 当前
     `v2-core + no-res baseline + 现有 waveform objective`
     在两条真实配对上，
     **连 tiny overfit
     都长不出人声**
3. 到那一步，
   下一主线就不该再是：
   - 继续 baseline
     步数微调
   - 或继续小型 inference tweak
   而应切回：
   - objective / head
     主线问题

## 一句话结论
- `paired baseline8`
  的人工听审已经正式失败；
  本轮已把问题推进到
  `tiny overfit72`
  层级，
  下一棒直接听：
  两条真实配对在过拟合后，
  是否仍然完全没有人声。
