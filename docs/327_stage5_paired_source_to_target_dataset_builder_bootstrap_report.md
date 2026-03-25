# 327. Stage5 paired source-to-target dataset builder bootstrap 报告

## 结论
- 本轮已把
  Stage5 dataset package
  builder
  从
  `target self-reconstruction`
  单一路径，
  扩成支持最小
  `paired source-to-target`
  口径。
- 当前实现选择的是：
  - **显式 pair-spec jsonl**
    方案
  - 不改现有默认
    `target_train / target_validation`
    自重建入口
  - 只在需要时，
    用
    `source_audio_path + target_audio_path`
    覆盖它
- 已完成两层实际验证：
  1. `107 -> 107`
     train /
     `132 -> 132`
     validation
     的最小 paired package
     导出
  2. 基于这份 paired dataset index
     的
     `1-step`
     Stage5 dataset training smoke

## 一、为什么这一轮现在最有价值
- 当前仓库此前已经明确：
  - user-line
    真正的问题不是
    plumbing
    是否打通
  - 而是
    Stage5
    长期没有在真实
    `source -> target`
    口径上受训，
    仍主要停留在
    `target self-reconstruction`
    里
- 如果不先把这个训练口径缺口补上，
  继续围绕：
  - semantic weighting
  - decoder conditioning
  - objective 小修
  做微调，
  信息增量都很有限

## 二、本轮代码改动

### 1. `offline_vocoder_training.py`
- 新增：
  - `resolve_dataset_record_duration_sec(...)`
  - `resolve_dataset_record_paths(...)`
- 当前行为：
  - 若 record
    只有
    `audio_path`
    则保持旧行为：
    - teacher 输入
      和训练 target
      都来自同一路径
  - 若 record
    提供：
    - `source_audio_path`
    - `target_audio_path`
    则：
    - teacher contract
      从
      `source_audio_path`
      导出
    - aligned waveform target
      来自
      `target_audio_path`
- dataset index
  现在会额外落盘：
  - `train_pair_spec_path`
  - `validation_pair_spec_path`
  - 每条 package 的
    `record_mode`
    `source_audio_path`
    `target_audio_path`

### 2. `cli.py`
- `build-offline-mvp-nores-vocoder-dataset-packages`
  新增参数：
  - `--train-pair-spec`
  - `--validation-pair-spec`
- 当前口径：
  - 若传 pair-spec，
    它会覆盖对应 split
  - 不传则仍沿用旧默认：
    - `target_train.jsonl`
    - `target_validation.jsonl`

## 三、本轮新增最小 paired smoke 资产

### 1. pair-spec
- 目录：
  - `data_prep/round1_1/stage5_paired_source_to_target_smoke/`
- 文件：
  - `parallel_train_pairs.jsonl`
  - `parallel_validation_pairs.jsonl`

### 2. 当前两条显式配对
- train：
  - source：
    `data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav`
  - target：
    `data_convert/dataset_firefly_raw/chapter3_17_firefly_107.wav`
- validation：
  - source：
    `data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_132.wav`
  - target：
    `data_convert/dataset_firefly_raw/chapter3_17_firefly_132.wav`

### 3. 为什么只先用这两条
- 它们是当前仓库里已经正式登记过的
  same-content
  平行 source
  主听样例
- 先用这两条做 smoke，
  可以最大限度避免：
  - pairing 逻辑不清
  - 新增变量过多
  - 训练口径还没站住就扩成大工程

## 四、实际运行

### 1. paired dataset package build
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --train-pair-spec data_prep/round1_1/stage5_paired_source_to_target_smoke/parallel_train_pairs.jsonl `
  --validation-pair-spec data_prep/round1_1/stage5_paired_source_to_target_smoke/parallel_validation_pairs.jsonl `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_smoke_round1_1 `
  --device cpu `
  --selection-mode file_order `
  --skip-full-pass-verify
```
- 结果：
  - `train_packages = 1`
  - `validation_packages = 1`
  - `duration_sec = 1.570499`
- 关键确认：
  - train package：
    - `source_audio_path = ...parallel...107.wav`
    - `target_audio_path = ...raw...107.wav`
  - validation package：
    - `source_audio_path = ...parallel...132.wav`
    - `target_audio_path = ...raw...132.wav`
  - `record_mode`
    都是：
    - `paired_source_to_target`

### 2. paired dataset training smoke
- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_smoke_round1_1 `
  --device cpu `
  --num-steps 1 `
  --packages-per-step 1 `
  --validation-interval 1 `
  --checkpoint-interval 1 `
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
- 结果：
  - `step1 train loss_total = 1.706274`
  - `step1 validation loss_total = 1.614548`
  - `best_checkpoint = step1`
- 这证明：
  - paired package
    不只是能导出
  - 也已经能真实进入
    Stage5 dataset loop
    的梯度路径

## 五、当前阶段判断
- 这一步的价值是：
  - **正式补上了真实 source-to-target 训练口径入口**
- 这一步没有证明：
  - 已经出现人声
  - 当前 paired smoke
    的 decoded
    已优于旧 self-reconstruction
  - `107/132`
    两条就足以代表后续正式训练规模
- 当前最准确的写法是：
  - Stage5
    终于不再被迫只能在
    `target self-reconstruction`
    上启动
  - 但真实 paired
    训练仍只停在
    极小 smoke
    阶段

## 六、下一步
1. 先扩
   pair-spec
   到一个更合理的小子集，
   不再只用
   `107 / 132`
   两条。
2. 在同一 paired 口径下，
   先跑一轮
   baseline
   小规模 dataset smoke，
   不叠新 loss，
   只回答：
   - 真实配对训练
     会不会比
     self-reconstruction
     更早出现
     speech emergence
3. 只有在 paired baseline
   自己站住后，
   才值得再讨论：
   - objective 强化
   - fusion-side 修正
   - 更复杂结构

## 一句话结论
- 本轮已经把
  Stage5
  的最小真实
  `source -> target`
  训练入口接进仓库，
  并完成了
  package build
  与
  `1-step`
  training smoke；
  当前下一棒应是
  扩成更合理的小型 paired subset baseline，
  而不是再回去调
  `student semantic`
  或旧的
  self-reconstruction
  微调线。
