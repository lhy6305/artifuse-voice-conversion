# 340. Stage5 target-side semantic forward consumer bootstrap 报告

## 结论
- 我没有继续停留在
  package weighting；
  这次已经把
  `target_event_semantic_sidecar`
  接成了真正的
  Stage5 forward consumer。
- 当前实现形态是：
  - `semantic_consumer_mode = target_sidecar_broadcast_v1`
  - 把 target-side semantic
    编成 9 维静态向量
  - 按 frame broadcast
    后拼到
    periodic / noise
    branch features
- 这条线已经完成：
  - package build smoke
  - 1-step training smoke
  - paired overfit24
    strict comparable run
  - validation training-sync export
  - obvious-buzz 机器门禁复核
- 当前阶段判断是：
  1. 这是第一条真正进入 Stage5 forward path 的
     target-side semantic consumer
  2. 量化上有正向信号：
     - `loss_total`
       略优于 baseline
     - `loss_stft`
       明显优于 baseline
     - `loss_rms_guard`
       明显优于 baseline
  3. 更关键的是：
     - 它不再被
       current obvious-buzz
       机器门禁
       直接判死
     - 当前状态从
       `auto_reject_obvious_buzz`
       进入了
       `review_required`
  4. 但这仍不是成功结论；
     下一问仍然是听感

## 一、这次接了什么

### 1. 新的 package build 模式
- CLI 新增：
  - `--semantic-consumer-mode`
- 当前实现的模式：
  - `target_sidecar_broadcast_v1`

### 2. forward consumer 具体做法
- 从
  `target_event_semantic_sidecar`
  抽出 9 维静态特征：
  - `clean_text_available`
  - `nonverbal_only`
  - `lexical_char_count_norm`
  - `clause_count_norm`
  - `pause_boundary_count_norm`
  - `terminal_boundary_count_norm`
  - `structure_single_clause_terminal`
  - `structure_multi_clause_single_terminal`
  - `structure_multi_terminal`
- 然后：
  - 对每条 package
    按 frame broadcast
  - 同时拼到
    periodic / noise
    branch features
- 所以这次 semantic
  不再只是 metadata，
  也不再只是 loss weighting；
  它已经进入了模型 forward path

## 二、接线验证

### 1. semantic-consumer package smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_semanticconsumer_smoke_round1_1/`
- 关键验证：
  - `semantic_consumer_mode = target_sidecar_broadcast_v1`
  - `feature_dim = 9`
  - `periodic_input_dim = 45`
  - `noise_input_dim = 45`
- 对照旧 baseline：
  - 原先输入维度是
    `36 / 36`
  - 现在变为
    `45 / 45`
- 这证明：
  - semantic broadcast
    不是只写进 json，
    而是真的改写了训练输入张量

### 2. 1-step training smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit_semanticconsumer_smoke_round1_1/`
- 结果：
  - 正常完成 step1
  - 说明新输入维度下，
    Stage5 dataset loop
    可正常 forward / backward / checkpoint

## 三、paired overfit24 可比结果

### baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_semanticplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.856916`
  - `loss_waveform = 0.159986`
  - `loss_stft = 0.364732`
  - `loss_rms_guard = 0.021712`
  - `decoded_to_target_rms_ratio = 0.978607`

### semantic consumer
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_semanticconsumer_round1_1/`
- validation step24：
  - `loss_total = 0.852640`
  - `loss_waveform = 0.165847`
  - `loss_stft = 0.315007`
  - `loss_rms_guard = 0.006695`
  - `decoded_to_target_rms_ratio = 0.993335`

### 当前解释
- 量化层面：
  - `loss_total`
    小幅优于 baseline
  - `loss_stft`
    明显优于 baseline
  - `loss_rms_guard`
    也明显优于 baseline
- 负向面：
  - `loss_waveform`
    略差
- 因而当前最合理的描述不是：
  - semantic consumer
    已经成功
- 而是：
  - 它比此前
    “只做 semantic weighting”
    更像一条值得继续审的 forward-path 候选

## 四、validation export 与机器门禁

### export
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_semanticconsumer_validation_trainingsync_round1_1/`

### obvious-buzz 门禁结果
- `buzz_reject_summary`：
  - `record_count = 2`
  - `auto_reject_count = 0`
  - `review_required_count = 2`
  - `all_records_auto_reject = false`

### 为什么这很重要
- 上一批 paired overfit24
  baseline / semantic-weight
  都还是：
  - `all_records_auto_reject = true`
- 而这次 semantic consumer
  首次变成：
  - 不再被机器直接判成 obvious-buzz
- 但记录里仍有共同信号：
  - `decoded short-time frames remain highly template-collapsed relative to aligned target diversity`
- 所以当前更准确的结论是：
  - 它跨过了“明显失败”的门槛
  - 但还远不到“已证明 speech emergence”

## 五、最小听审包
- 目录：
  - `reports/audio/stage5_paired_parallel_overfit24_semanticconsumer_compare_quick_audit_20260325/`
- 文件：
  - case107：
    - `source`
    - `target_aligned`
    - `baseline_decoded`
    - `semanticconsumer_decoded`
  - case132：
    - `source`
    - `target_aligned`
    - `baseline_decoded`
    - `semanticconsumer_decoded`

## 六、当前阶段判断
- 这次最关键的工程意义不是：
  - 指标小幅变好
- 而是：
  1. target-side semantic
     终于第一次进入了
     Stage5 forward path
  2. 这条线没有像之前那些候选一样，
     立刻被机器门禁判成
     obvious-buzz
  3. 所以它成为当前第一条
     值得继续人工复核的
     semantic mainline candidate

## 七、下一步
1. 听：
   - `reports/audio/stage5_paired_parallel_overfit24_semanticconsumer_compare_quick_audit_20260325/`
2. 只回答：
   - `semanticconsumer_decoded`
     是否比 baseline
     更接近 target
3. 若听感仍然只是 pure buzz / pure fuzz，
   就说明：
   - 仅靠 current
     target-side semantic broadcast
     仍不足以推出
     template-collapse
   - 下一步就该继续向：
     - 更明确的
       design-state
       `e_evt`
       consumer
     走，
     而不是停留在这版 static broadcast
