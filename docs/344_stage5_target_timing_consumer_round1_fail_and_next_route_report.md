# 344. Stage5 target timing consumer round1 失败与下一步路线报告

## 结论
- 第一版
  `target_timing_sidecar_framewise_v1`
  已确认真实进入
  Stage5 forward path，
  但当前结果应正式判失败。
- 失败依据不是：
  - plumbing 未接通
  - 或只差人工复核
- 而是：
  1. package
     输入维度已从
     `36 / 36`
     变成
     `46 / 46`
  2. paired overfit24
     相对 baseline
     没有形成更好的共享主指标平衡
  3. 更关键的是：
     validation training-sync export
     被
     `stage5_buzz_reject_v1`
     直接判成：
     - `auto_reject_count = 2`
     - `all_records_auto_reject = true`

## 一、本轮做了什么
- 在
  `docs/343`
  的 metadata plumbing
  基础上，
  新增第一版
  framewise timing consumer：
  - `semantic_consumer_mode = target_timing_sidecar_framewise_v1`
- 当前逐帧特征包含：
  - `clause_active`
  - `clause_role_single`
  - `clause_role_initial`
  - `clause_role_middle`
  - `clause_role_final`
  - `clause_progress_norm`
  - `utterance_progress_norm`
  - `pause_boundary_window`
  - `terminal_boundary_window`
  - `boundary_any_window`

## 二、代码改动
- 更新：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 当前行为：
  - `build-offline-mvp-nores-vocoder-dataset-packages`
    支持：
    - `--semantic-consumer-mode target_timing_sidecar_framewise_v1`
  - package build
    会把
    `target_event_timing_semantic_sidecar`
    rasterize 成逐帧 sparse channels
  - `input_semantics.periodic_feature_semantics`
    会追加：
    - `target_timing_sidecar_framewise_v1`

## 三、smoke 验证
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --train-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --validation-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_timingconsumer_smoke_round1_1 `
  --device cpu `
  --selection-mode file_order `
  --skip-full-pass-verify `
  --target-event-semantic-sidecar data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --target-event-timing-semantic-sidecar data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl `
  --semantic-consumer-mode target_timing_sidecar_framewise_v1
```
- 结果：
  - `train_packages = 2`
  - `validation_packages = 2`
- 关键确认：
  - `chapter3_17_firefly_107`
    package
    中：
    - `semantic_consumer_mode = target_timing_sidecar_framewise_v1`
    - `feature_dim = 10`
    - `periodic_input_dim = 46`
    - `noise_input_dim = 46`

## 四、paired overfit24 对照结果

### baseline
- 运行：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_timingplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.856916`
  - `loss_waveform = 0.159986`
  - `loss_stft = 0.364732`
  - `loss_rms_guard = 0.021712`
  - `decoded_to_target_rms_ratio = 0.978607`

### timing consumer
- 运行：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_timingconsumer_round1_1/`
- validation step24：
  - `loss_total = 0.867541`
  - `loss_waveform = 0.163164`
  - `loss_stft = 0.361870`
  - `loss_rms_guard = 0.006484`
  - `decoded_to_target_rms_ratio = 0.993538`

### 当前判断
- 这不是完全无变化，
  但也不是值得继续在同层微调的结果：
  - `loss_stft`
    略好
  - `loss_rms_guard`
    更好
  - 但
    `loss_total`
    和
    `loss_waveform`
    仍差于 baseline

## 五、自动门禁结果
- 已执行：
```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_timingconsumer_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt `
  --split-name validation `
  --sample-count 2 `
  --activity-gate-weight 0.0 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_timingconsumer_validation_trainingsync_round1_1 `
  --use-predicted-activity-gate `
  --predicted-activity-gate-apply-mode pre_overlap_add
```
- 结果：
  - `auto_reject_count = 2`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 两条记录都被判成：
  - `auto_reject_obvious_buzz`

## 六、当前阶段判断
- 到这里可以正式写死：
  - Stage5
    target-only
    weak timing semantic
    即便升级成
    framewise sparse consumer，
    仍不足以推出 speech emergence
- 所以这条线不应再继续做：
  - 再换一组 frame channels
  - 再改 clause progress
  - 再加几个 boundary 类型
- 这些都属于
  已经被本轮失败定性的
  同层微调

## 七、下一步最有价值的调整
1. 正式停止：
   - Stage5 target-only
     weak timing consumer
     变体
2. 下一步应上收到：
   - source-side / parity-aware
     semantic asset
     或
   - 更上游的
     teacher / student
     semantic supervision route
3. 当前更推荐优先：
   - 不再继续在
     Stage5 input
     侧堆 target-only hints
   - 而是转回
     更接近设计态
     `e_evt`
     的上游 supervision / parity 资产层
