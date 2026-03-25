# 347. Stage5 source semantic parity consumer round1 失败与 supervision 路线报告

## 结论
- 第一版
  `source_semantic_parity_framewise_v1`
  已确认真实进入
  Stage5 forward path，
  但当前结果仍应正式判停。
- 原因不是：
  - source parity
    资产缺失
  - metadata
    没接通
  - 或只差人工复核
- 而是：
  1. source-aware consumer
     已真实生效
  2. paired overfit24
     的共享量化指标
     略优于 metadata-only baseline
  3. 但 validation export
     仍被
     `stage5_buzz_reject_v1`
     直接判成：
     - `auto_reject_count = 2`
     - `all_records_auto_reject = true`

## 一、本轮做了什么
- 在
  `docs/346`
  的 metadata plumbing
  基础上，
  新增：
  - `semantic_consumer_mode = source_semantic_parity_framewise_v1`
- 该 consumer
  直接复用
  source parity sidecar
  的 source-frame timeline，
  不再使用
  target-side timeline
  的错位广播

## 二、代码改动
- 更新：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 当前逐帧特征包含：
  - `clause_active`
  - `clause_role_single`
  - `clause_role_initial`
  - `clause_role_middle`
  - `clause_role_final`
  - `clause_progress_norm`
  - `source_utterance_progress_norm`
  - `pause_boundary_window`
  - `terminal_boundary_window`
  - `boundary_any_window`

## 三、smoke 验证
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --train-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --validation-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_sourceparityconsumer_smoke_round1_1 `
  --device cpu `
  --selection-mode file_order `
  --skip-full-pass-verify `
  --target-event-semantic-sidecar data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --target-event-timing-semantic-sidecar data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl `
  --source-semantic-parity-sidecar data_prep/round1_1/paired_parallel_source_semantic_parity_sidecar/paired_parallel_source_semantic_parity_sidecar.jsonl `
  --semantic-consumer-mode source_semantic_parity_framewise_v1
```
- 关键确认：
  - `semantic_consumer_mode = source_semantic_parity_framewise_v1`
  - `feature_dim = 10`
  - `periodic_input_dim = 46`
  - `noise_input_dim = 46`
  - `feature_source = paired_parallel_source_semantic_parity_sidecar`

## 四、paired overfit24 对照结果

### baseline
- 运行：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.572382`
  - `loss_harmonic_envelope = 0.285243`
  - `loss_noise_envelope = 0.052113`
  - `loss_periodic_gate = 0.543894`
  - `loss_noise_gate = 0.631239`

### source parity consumer
- 运行：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityconsumer_round1_1/`
- validation step24：
  - `loss_total = 0.560476`
  - `loss_harmonic_envelope = 0.276871`
  - `loss_noise_envelope = 0.051777`
  - `loss_periodic_gate = 0.528601`
  - `loss_noise_gate = 0.630537`

### 当前判断
- source-aware consumer
  不是完全无效：
  - 共享量化指标
    略优于 baseline
- 但这还不足以继续投入：
  - 因为输出层面
    仍然没有摆脱
    obvious buzz

## 五、自动门禁结果
- baseline export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_sourceparityplumb_baseline_validation_trainingsync_round1_1/nores_vocoder_audio_export.json`
  - `all_records_auto_reject = true`
- source parity consumer export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_sourceparityconsumer_validation_trainingsync_round1_1/nores_vocoder_audio_export.json`
  - `all_records_auto_reject = true`
- 两者共同结论：
  - 机器门禁仍把两条 validation
    样本都判成：
    `auto_reject_obvious_buzz`

## 六、当前阶段判断
- 到这里可以正式写死：
  - 即便把 semantic
    从 target-only
    升级为 source-aware parity timeline，
    仅靠 Stage5 input-side consumer
    仍不足以推出 speech emergence
- 所以这条线不应继续做：
  - 再换一组 source parity channels
  - 再叠一个 source/target ratio 标量
  - 再改 boundary window
    半宽
- 这些都属于：
  - 已被本轮定性为
    层级仍然过低的
    Stage5 输入侧微调

## 七、下一步最有价值的调整
1. 正式停止：
   - Stage5
     source parity consumer
     变体
2. 下一步应上收到：
   - 更上游的
     semantic supervision route
3. 当前更推荐优先：
   - 构建能够进入
     teacher / student
     训练链的
     source-target parity-aware
     semantic supervision
   - 而不是继续把 semantic
     作为 Stage5 branch feature
     追加输入
