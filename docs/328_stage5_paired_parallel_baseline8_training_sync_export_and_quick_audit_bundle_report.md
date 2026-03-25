# 328. Stage5 paired parallel baseline8 training-sync 导出与最小听审包报告

## 结论
- 在
  `327`
  已补齐
  paired source-to-target
  dataset builder
  后，
  本轮继续推进了第一轮真正可听的
  paired baseline smoke：
  1. 基于当前仅有的两条
     same-content parallel source
     跑完
     `8-step`
     baseline 训练
  2. 完成 checkpoint selection
  3. 分别导出：
     - train case
     - validation case
     的 decoded 音频
  4. 已整理出最小听审包：
     - `reports/audio/stage5_paired_parallel_baseline8_quick_audit_20260325/`
- 当前最重要的新信息不是：
  - 已经证明出现人声
- 当前最重要的新信息是：
  - paired baseline
    已不再停留在
    package / train-loop
    层面，
    而是已经具备真正可听的
    source / target / decoded
    对照包

## 一、为什么这一步现在值得做
- 当前仓库里正式可用的
  same-content parallel source
  只有两条：
  - `chapter3_17_firefly_107.wav`
  - `chapter3_17_firefly_132.wav`
- 因此当前无法诚实地把 paired subset
  直接扩成更大规模；
  最合理的下一步不是伪造更多配对，
  而是先把这两条真实配对
  推到第一轮可听 baseline。

## 二、本轮训练

### 1. 数据入口
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- train：
  - `paired::parallel_firefly_107_to_target_firefly_107`
- validation：
  - `paired::parallel_firefly_132_to_target_firefly_132`

### 2. 训练命令
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_baseline8_round1_1 `
  --device cpu `
  --num-steps 8 `
  --packages-per-step 1 `
  --validation-interval 2 `
  --checkpoint-interval 2 `
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

### 3. 结果
- train loss：
  - `step1 = 1.706274`
  - `step8 = 1.168237`
- validation loss：
  - `step2 = 1.518202`
  - `step4 = 1.344046`
  - `step6 = 1.264442`
  - `step8 = 1.213325`
- 说明：
  - 至少在这条极小 paired baseline 上，
    train / validation
    都是单调改善，
    没有出现最基本的训练不稳定

## 三、selection 与 export

### 1. checkpoint selection
- selection 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_baseline8_round1_1/`
- 当前结果：
  - `best_validation = step8`
  - `selected_stable_late_stop = step8`

### 2. 一个关键导出 caveat
- 若直接用默认 export 口径，
  会落到：
  - `use_predicted_activity_gate = false`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`
- 这和本轮训练语义不一致，
  并且会把 export-side
  `decoded_to_target_rms_ratio`
  明显拉坏：
  - train：
    `1.733875`
  - validation：
    `1.855734`
- 因而这轮正式主听不采用默认导出。

### 3. 本轮采用的 training-sync export
- train：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_baseline8_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name train `
  --sample-count 1 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_baseline8_train_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```
- validation：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_paired_parallel_baseline8_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 1 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_baseline8_validation_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```

### 4. training-sync 导出结果
- train：
  - `decoded_to_target_rms_ratio = 0.937042`
- validation：
  - `decoded_to_target_rms_ratio = 0.991506`
- 这和训练 loop
  summary
  已经基本同口径，
  比默认 export
  明显更可信。

## 四、最小听审包

### 目录
- `reports/audio/stage5_paired_parallel_baseline8_quick_audit_20260325/`

### 文件
- `01_train_source.wav`
- `02_train_target_aligned.wav`
- `03_train_decoded.wav`
- `04_validation_source.wav`
- `05_validation_target_aligned.wav`
- `06_validation_decoded.wav`
- `README.md`

### 为什么这样整理
- 当前阶段最重要的问题只有一个：
  - paired baseline
    有没有第一次出现
    可辨识人声成分
- 所以这份包刻意不导大 bundle，
  只保留：
  - source
  - target
  - decoded

## 五、当前阶段判断
- 这一步证明了：
  1. paired baseline
     可以真实训练到
     `step8`
  2. 可以完成 selection
     和导出
  3. 已有一份真正可听的
     paired quick audit
     入口
- 这一步没有证明：
  1. 当前 paired baseline
     已经脱离 buzz
  2. 当前两条样例
     足以代表后续正式 paired 训练
  3. 旧的 self-reconstruction
     路线已经可以彻底停止

## 六、下一步
1. 先听这份
   quick audit
   包，
   只判断：
   - 是否第一次出现
     任何可辨识人声成分
2. 如果仍完全没有人声，
   下一步就不要急着叠新 loss；
   先把问题写清：
   - “真实 paired baseline
      也仍无 speech emergence”
3. 如果哪怕只有极弱发声雏形，
   再考虑：
   - 把 paired asset
     从 `2`
     条扩到新的小批
   - 或把现有 paired baseline
     多跑一档步数

## 一句话结论
- 当前已经拿到第一份真正基于
  paired source-to-target baseline
  的最小听审包；
  下一棒不是继续猜测，
  而是直接听：
  这两条真实配对上，
  `decoded`
  是否第一次开始像“发声”，
  而不是纯 buzz。
