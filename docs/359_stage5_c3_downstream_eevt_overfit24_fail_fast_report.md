# 359. Stage5 `C3` downstream `e_evt v3` overfit24 fail-fast 报告

## 结论
- 我按最快闭环把
  `Stage5 C3 downstream e_evt v3`
  推到了：
  - paired overfit24
  - validation training-sync export
  - `stage5_buzz_reject_v1`
    自动门禁
- 结果应直接判为：
  - 当前这条
    source-only bootstrap
    路线
    **不值得继续扩到 fullsplit
    或再交人工试听**
- 原因不是：
  - contract 没接通
  - 或样本还没导出来
- 而是：
  1. package 已真实升级到
     `offline_teacher_vocoder_input_scaffold_v3`
  2. paired overfit24
     已完成
  3. 但 validation export
     仍被机器门禁直接判成：
     - `auto_reject_count = 2`
     - `all_records_auto_reject = true`

## 一、本轮执行内容

### 1. paired overfit `v3` dataset package
- 命令：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --train-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --validation-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevtv3_smoke_round1_1 `
  --device cpu `
  --selection-mode file_order `
  --skip-full-pass-verify
```
- 关键确认：
  - `train_packages = 2`
  - `validation_packages = 2`
  - `source_scaffold_version = offline_teacher_vocoder_input_scaffold_v3`
  - `semantic_consumer_mode = none`
  - `periodic_input_dim = 36`
  - `noise_input_dim = 36`

### 2. paired overfit24 training loop
- 命令：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevtv3_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtv3_round1_1 `
  --device cpu `
  --num-steps 24 `
  --packages-per-step 2 `
  --validation-interval 24 `
  --checkpoint-interval 24 `
  --sampler-mode sequential `
  --seed 20260325 `
  --reconstruction-frame-gain-apply-mode pre_overlap_add
```

### 3. validation training-sync export
- 命令：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtv3_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt `
  --split-name validation `
  --sample-count 2 `
  --activity-gate-weight 0.0 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_eevtv3_validation_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```

## 二、paired overfit24 与旧 baseline 的最小对照

### 1. 旧 metadata-only baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.572382`
  - `loss_harmonic_envelope = 0.285243`
  - `loss_noise_envelope = 0.052113`
  - `loss_periodic_gate = 0.543894`
  - `loss_noise_gate = 0.631239`

### 2. 新 `e_evt v3` downstream route
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtv3_round1_1/`
- validation step24：
  - `loss_total = 0.584024`
  - `loss_harmonic_envelope = 0.287515`
  - `loss_noise_envelope = 0.055594`
  - `loss_periodic_gate = 0.553126`
  - `loss_noise_gate = 0.651450`

### 3. 当前解释
- 这说明：
  - 把 Stage5 downstream
    event family
    从 legacy
    `event_probs`
    切到 bootstrap
    `e_evt`
  - **在当前 source-only / zero-filled-boundary bootstrap 口径下**
    还不够
- 更具体地说：
  - 共享主指标
    没有优于旧 baseline
  - 不是“量化略好但还需听审”
  - 而是“量化也没站住”

## 三、自动门禁结果
- 新 export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_eevtv3_validation_trainingsync_round1_1/nores_vocoder_audio_export.json`
- 关键结果：
  - `record_count = 2`
  - `auto_reject_count = 2`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 两条记录都被判成：
  - `auto_reject_obvious_buzz`

### 代表性信号
- `107`：
  - `decoded_spectral_summary.centroid_hz = 12365.886926`
  - `aligned_spectral_summary.centroid_hz = 1035.383633`
  - `decoded_frame_template_cosine_mean = 0.954839`
  - `decoded_frame_adjacent_cosine_mean = 0.997855`
- `132`：
  - `decoded_spectral_summary.centroid_hz = 12355.850275`
  - `aligned_spectral_summary.centroid_hz = 1718.693230`
  - `decoded_frame_template_cosine_mean = 0.950904`
  - `decoded_frame_adjacent_cosine_mean = 0.997530`

## 四、当前阶段判断
1. `docs/358`
   的 plumbing
   不是白费：
   - 它完成了
     Stage5 `C3`
     downstream
     对显式
     `e_evt`
     的真实消费接线
2. 但作为一个
   **可直接推进到可听样本**
   的训练路线，
   当前这版
   `source-only e_evt v3`
   应正式判停
3. 所以现在不该继续做：
   - fullsplit
   - 听审 bundle
   - 同层 decode / gate
     小修
4. 下一步若还要保留
   `e_evt`
   主线，
   必须上收到：
   - 更强的 boundary-aware
     `e_evt` 资产
   - 或更明确的
     Stage5 target contract /
     supervision route

## 五、结论收口
1. 这轮已经完成了
   “尽快推进到可听样本并确认是否白费劲”
   的目标
2. 当前答案是：
   - plumbing 有价值
   - 但当前
     `source-only e_evt v3`
     这版实验路线
     不值得继续投入
3. 后续不应再因为
   `Stage5 已显式吃到 e_evt`
   就默认认为：
   - downstream 已有突破机会
