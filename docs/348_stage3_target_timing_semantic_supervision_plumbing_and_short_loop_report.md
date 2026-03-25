# 348. Stage3 target timing semantic supervision 接线与短 loop 对照报告

## 结论
- `target_event_timing_semantic_sidecar`
  已正式接入
  Stage3 `streaming_student`
  的
  config / data / teacher-label summary / supervision / train-step / train-loop
  链路。
- 这次不是只做 metadata：
  - timing sidecar
    已进入 batch
  - timing-aware semantic multipliers
    已进入
    `teacher_event_prior / teacher_event / teacher_z_art`
    的 loss weighting
  - 真实 train step / train loop
    都已跑通
- 但当前短 loop 结果说明：
  - “只加 timing bonus 重加权”
    信号偏弱，
    还不足以当成下一条主突破口。
  - 严格可比的
    12-step sampled validation
    上，
    更可比的
    `loss_total_semantic_disabled_reference`
    基本打平：
    - baseline:
      `8.181766`
    - timing-enabled:
      `8.181019`
- 所以下一步不应继续做：
  - 再微调
    `timing_*_bonus`
  - 再扫一组
    `alpha`
  - 再做更多“只改重加权”的小实验
- 更有价值的下一步应改成：
  - 把 timing semantic
    从
    sample-level weighting
    升级为
    更强的
    target shaping / mask-aware supervision

## 一、本轮代码改动

### 1. Stage3 data 链路新增 target timing sidecar
- 更新：
  - `src/v5vc/streaming_student/data.py`
- 关键变化：
  - 新增
    `target_event_timing_semantic_sidecar`
    到
    `StreamingStudentTargetExample`
  - `attach_sidecars_if_available(...)`
    现在会解析并 attach：
    - `target_event_timing_semantic_sidecar_path`
  - collate batch
    现在会导出：
    - `batch["target_event_timing_semantic_sidecar"]`

### 2. Stage3 semantic supervision 升级为 timing-aware
- 更新：
  - `src/v5vc/streaming_student/losses.py`
- 新增配置键：
  - `required_timing_contract_version`
  - `timing_ready_bonus`
  - `timing_multi_clause_bonus`
  - `timing_pause_present_bonus`
  - `timing_terminal_present_bonus`
- 当前行为：
  - `build_semantic_loss_multipliers(...)`
    会同时读取：
    - `target_event_semantic_sidecar`
    - `target_event_timing_semantic_sidecar`
  - 并新增统计：
    - `timing_sidecar_present_ratio`
    - `semantic_timing_ready_sample_ratio`
    - `semantic_timing_multi_clause_sample_ratio`
    - `semantic_timing_pause_present_sample_ratio`
    - `semantic_timing_terminal_present_sample_ratio`

### 3. Stage3 dry-run summary 补齐 timing semantic 摘要
- 更新：
  - `src/v5vc/streaming_student/training_data_entry.py`
  - `src/v5vc/streaming_student/supervision_entry.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `configs/streaming_student_stage_template.json`
- 当前行为：
  - scaffold plan
    会显式记录：
    `target_event_timing_semantic_sidecar_path`
  - training-data / supervision
    summary
    都会写出：
    `timing_semantic_sidecar_summary`

### 4. teacher-label export 摘要新增 timing 元数据
- 更新：
  - `src/v5vc/streaming_student/teacher_labels.py`
- 当前行为：
  - teacher-label index row
    会写出：
    - `timing_source`
    - `timing_contract_version`
    - `timing_alignment_type`
    - `timing_clause_region_count`
    - `timing_pause_boundary_event_count`
    - `timing_terminal_boundary_event_count`
  - split summary
    会统计：
    - `timing_contract_version_counts`
    - `timing_inventory_status_counts`
    - `timing_label_status_counts`
    - `timing_alignment_type_counts`

### 5. 新增对照 override
- 新增：
  - `configs/streaming_student_loss_weights_timingsemantic_disabled_v1.json`
- 作用：
  - 只关闭 timing bonuses，
    保留其它 semantic supervision，
    作为严格可比 baseline

## 二、验证

### 1. py_compile
- 已执行：
```powershell
.\python.exe -m py_compile `
  src/v5vc/streaming_student/data.py `
  src/v5vc/streaming_student/losses.py `
  src/v5vc/streaming_student/training_data_entry.py `
  src/v5vc/streaming_student/supervision_entry.py `
  src/v5vc/streaming_student/teacher_labels.py `
  src/v5vc/streaming_student/plan_entry.py
```
- 结果：
  - 通过

### 2. scaffold / dry-run / supervision
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-stage `
  --output-dir reports/plans/streaming_student_stage_timingsemantic_round1_1 `
  --experiment-id streaming_student_stage_timingsemantic_round1_1
```
- 关键结果：
  - `target_event_timing_semantic_sidecar_path`
    已显式落盘

- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-training-data `
  --output-dir reports/plans/streaming_student_training_data_timingsemantic_round1_1 `
  --batch-size 4
```
- 关键结果：
  - `available_target_sidecars`
    现在包含：
    `target_event_timing_semantic_sidecar`
  - dry-run summary
    已出现：
    `timing_semantic_sidecar_summary`

- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-supervision `
  --output-dir reports/plans/streaming_student_supervision_timingsemantic_round1_1 `
  --batch-size 4
```
- 关键结果：
  - supervision config
    已包含：
    - `required_timing_contract_version = target_event_timing_semantic_sidecar_v1`
    - `timing_ready_bonus = 0.04`
    - `timing_multi_clause_bonus = 0.04`
    - `timing_pause_present_bonus = 0.03`
    - `timing_terminal_present_bonus = 0.03`
  - `target_train`
    dry-run 上：
    - `timing_sidecar_present_ratio = 1.0`
    - `semantic_timing_ready_sample_ratio = 1.0`
    - `semantic_timing_multi_clause_sample_ratio = 1.0`
    - `semantic_timing_pause_present_sample_ratio = 1.0`
    - `semantic_timing_terminal_present_sample_ratio = 0.75`
    - `semantic_base_multiplier_mean = 1.4175`

### 3. teacher-label smoke
- 已执行：
```powershell
.\python.exe manage.py build-streaming-student-teacher-labels `
  --data-output-dir data_prep/round1_1/streaming_student_teacher_labels_timingsemantic_smoke_round1_1 `
  --report-output-dir reports/data/streaming_student_teacher_labels_timingsemantic_smoke_round1_1 `
  --batch-size 2 `
  --max-records-per-slice 2
```
- 关键结果：
  - `record_count = 6`
  - 三个 split
    都出现：
    - `timing_contract_version_counts = {'target_event_timing_semantic_sidecar_v1': 2}`
    - `timing_alignment_type_counts = {'weak_punctuation_lexical_progress_v1': 2}`
  - index row
    已真实写出 timing 字段。
    例如：
    `target::archive_firefly_1`
    包含：
    - `timing_clause_region_count = 6`
    - `timing_pause_boundary_event_count = 4`
    - `timing_terminal_boundary_event_count = 2`

### 4. one-step train smoke
- 已执行：
```powershell
.\python.exe manage.py run-streaming-student-training-step `
  --output-dir reports/training/streaming_student_timingsemantic_smoke_round1_1 `
  --experiment-id streaming_student_stage_step_timingsemantic_smoke_round1_1 `
  --batch-size 4
```
- 关键结果：
  - log 中已出现：
    - `timing_sidecar_present_ratio = 1.0`
    - `semantic_timing_ready_sample_ratio = 1.0`
    - `semantic_base_multiplier_mean = 1.4175`
  - 说明 timing-aware weighting
    已进入真实 train step

## 三、12-step 严格可比短 loop

### baseline
- 运行：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --output-dir reports/training/streaming_student_loop_timingsemantic_baseline12_round1_1 `
  --experiment-id streaming_student_stage_loop_timingsemantic_baseline12_round1_1 `
  --batch-size 4 `
  --validation-batch-size 4 `
  --num-steps 12 `
  --validation-interval 4 `
  --checkpoint-interval 4 `
  --validation-batches 4 `
  --validation-mode sampled `
  --loss-weight-overrides configs/streaming_student_loss_weights_timingsemantic_disabled_v1.json
```
- checkpoint-selection
  选中的 step12 validation：
  - `loss_total = 9.515196`
  - `loss_total_semantic_disabled_reference = 8.181766`
  - `loss_teacher_z_art = 0.082022`
  - `loss_teacher_event = 5.395409`
  - `loss_teacher_event_prior = 6.399268`

### timing-enabled
- 运行：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --output-dir reports/training/streaming_student_loop_timingsemantic_enabled12_round1_1 `
  --experiment-id streaming_student_stage_loop_timingsemantic_enabled12_round1_1 `
  --batch-size 4 `
  --validation-batch-size 4 `
  --num-steps 12 `
  --validation-interval 4 `
  --checkpoint-interval 4 `
  --validation-batches 4 `
  --validation-mode sampled
```
- checkpoint-selection
  选中的 step12 validation：
  - `loss_total = 9.94682`
  - `loss_total_semantic_disabled_reference = 8.181019`
  - `loss_teacher_z_art = 0.082807`
  - `loss_teacher_event = 5.572083`
  - `loss_teacher_event_prior = 6.900272`

### 当前判断
- 如果直接看
  `loss_total`，
  timing-enabled
  更差，
  但这主要包含了
  semantic weighting
  本身带来的放大，
  不能直接当成训练效果退化。
- 更可比的是：
  `loss_total_semantic_disabled_reference`
  与若干原始 teacher proxy loss。
- 在这个口径上：
  - `loss_total_semantic_disabled_reference`
    只有极小改善：
    `8.181766 -> 8.181019`
  - `loss_teacher_z_art`
    略差
  - `loss_teacher_event`
    略差
  - `loss_teacher_event_prior`
    略差
- 所以当前最稳妥的判断是：
  - timing-aware weighting
    已真实接通
  - 但短 loop
    尚未给出足够强的收益信号

## 四、阶段判断与下一步

### 当前阶段判断
1. 这条线现在的价值，
   在于它第一次把
   target timing semantic
   真正接进了
   Stage3 supervision
   主链。
2. 但当前结果同时说明：
   - 仅靠
     timing bonus
     做 sample-level / loss-level
     重加权，
     提升很弱。
3. 因此这条线不应继续沉没在：
   - bonus 微调
   - alpha 微调
   - 更长但同构的纯 weighting 小实验

### 下一步
1. 保留本轮 plumbing
   作为正式底座。
2. 下一步更推荐：
   把 timing semantic
   升级成更强 supervision，
   例如：
   - event-prior target shaping
   - boundary / clause-aware mask
   - timing-aware selective loss routing
3. 继续保持边界：
   - 当前 Stage3
     仍是 target-only record route
   - `source_semantic_parity_sidecar`
     不应被硬塞进当前 target-only student pipeline
