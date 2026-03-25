# 349. Stage3 target timing frame routing 短 loop 对照报告

## 结论
- 第一版
  timing-aware
  frame routing
  已真实接入
  Stage3 supervision，
  不是停留在配置或 summary。
- 它当前做的是：
  - 从
    `target_event_timing_semantic_sidecar`
    rasterize
    boundary / final-clause
    frame mask
  - 再把这份 mask
    作用到：
    - `teacher_event_prior`
    - `teacher_event`
    - `teacher_z_art`
    的逐帧 loss 权重
- 但严格可比的
  12-step sampled validation
  上，
  更可比的
  `loss_total_semantic_disabled_reference`
  只出现极小改善：
  - baseline:
    `8.181766`
  - routing-enabled:
    `8.180736`
- 同时：
  - `loss_teacher_event`
    变差：
    `5.395409 -> 5.572047`
  - `loss_teacher_event_prior`
    变差：
    `6.399268 -> 6.900500`
  - `loss_teacher_z_art`
    也略差：
    `0.082022 -> 0.082627`
- 所以当前结论应写死：
  - timing frame routing
    已证明“可以真实接入”
  - 但仍不足以成为下一条值得继续扫参的主线
- 下一步不应继续做：
  - routing multiplier
    微调
  - boundary boost
    再扫一组
  - nonboundary scale
    再扫一组
- 更值钱的下一步应是：
  - 更强的
    target shaping
    或
    显式 boundary/clause-aware
    target contract

## 一、本轮代码改动

### 1. `losses.py` 新增 timing-aware frame routing
- 更新：
  - `src/v5vc/streaming_student/losses.py`
- 新增配置：
  - `timing_frame_routing_enabled`
  - `timing_nonboundary_scale`
  - `timing_pause_boundary_boost`
  - `timing_terminal_boundary_boost`
  - `timing_final_clause_boost`
  - `timing_event_prior_mask_alpha`
  - `timing_event_mask_alpha`
  - `timing_z_art_mask_alpha`
- 当前行为：
  - `build_timing_frame_loss_multipliers(...)`
    会读取
    `target_event_timing_semantic_sidecar`
  - 把
    `boundary_events / clause_regions`
    rasterize 成逐帧 mask
  - 生成三路 frame multiplier：
    - `teacher_event_prior`
    - `teacher_event`
    - `teacher_z_art`
  - 再与
    `frame_weight`
    相乘进入逐帧 loss

### 2. 模板配置补齐默认 routing 参数
- 更新：
  - `configs/streaming_student_stage_template.json`

### 3. 新增严格可比 baseline override
- 新增：
  - `configs/streaming_student_loss_weights_timingsemantic_routing_disabled_v1.json`
- 作用：
  - 显式关闭：
    - timing bonuses
    - timing frame routing

## 二、验证

### 1. py_compile
- 已执行：
```powershell
.\python.exe -m py_compile `
  src/v5vc/streaming_student/losses.py `
  src/v5vc/streaming_student/train_step_entry.py
```
- 结果：
  - 通过

### 2. supervision dry-run
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-supervision `
  --output-dir reports/plans/streaming_student_supervision_timingrouting_round1_1 `
  --batch-size 4
```
- 关键结果：
  - 已出现：
    - `timing_frame_routing_enabled = true`
    - `timing_frame_mask_applied_ratio = 1.0`
    - `timing_boundary_frame_ratio = 0.006586`
    - `timing_event_prior_frame_multiplier_mean = 0.928198`

### 3. one-step train smoke
- 已执行：
```powershell
.\python.exe manage.py run-streaming-student-training-step `
  --output-dir reports/training/streaming_student_timingrouting_smoke_round1_1 `
  --experiment-id streaming_student_stage_step_timingrouting_smoke_round1_1 `
  --batch-size 4
```
- 关键结果：
  - log 中已出现：
    - `timing_frame_routing_enabled = true`
    - `timing_frame_mask_applied_ratio = 1.0`
    - `timing_boundary_frame_ratio = 0.006586`
    - `timing_event_prior_frame_multiplier_mean = 0.928198`
- 说明：
  - routing
    已进入真实 train step

## 三、12-step 严格可比短 loop

### baseline
- 运行：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --output-dir reports/training/streaming_student_loop_timingrouting_baseline12_round1_1 `
  --experiment-id streaming_student_stage_loop_timingrouting_baseline12_round1_1 `
  --batch-size 4 `
  --validation-batch-size 4 `
  --num-steps 12 `
  --validation-interval 4 `
  --checkpoint-interval 4 `
  --validation-batches 4 `
  --validation-mode sampled `
  --loss-weight-overrides configs/streaming_student_loss_weights_timingsemantic_routing_disabled_v1.json
```
- checkpoint-selection
  选中的 step12 validation：
  - `loss_total = 9.515196`
  - `loss_total_semantic_disabled_reference = 8.181766`
  - `loss_teacher_z_art = 0.082022`
  - `loss_teacher_event = 5.395409`
  - `loss_teacher_event_prior = 6.399268`
  - `timing_frame_routing_enabled = false`

### routing-enabled
- 运行：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --output-dir reports/training/streaming_student_loop_timingrouting_enabled12_round1_1 `
  --experiment-id streaming_student_stage_loop_timingrouting_enabled12_round1_1 `
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
  - `loss_total = 9.946549`
  - `loss_total_semantic_disabled_reference = 8.180736`
  - `loss_teacher_z_art = 0.082627`
  - `loss_teacher_event = 5.572047`
  - `loss_teacher_event_prior = 6.900500`
  - `timing_frame_mask_applied_ratio = 1.0`
  - `timing_boundary_frame_ratio = 0.007677`
  - `timing_final_clause_frame_ratio = 0.303366`
  - `timing_event_prior_frame_multiplier_mean = 0.936353`

## 四、当前判断

### 已确认成立的事
1. target timing semantic
   不仅能做
   sample-level weighting，
   也能真实进入
   frame-level routing
2. 当前 routing
   的实现不是伪接线：
   - dry-run
     有指标
   - train step
     有指标
   - train loop
     也有指标

### 已确认不值得继续投入的事
1. 这版 routing
   在当前层级下，
   收益仍然太弱。
2. 如果继续做：
   - routing boost
     微调
   - boundary ratio
     微调
   - final clause boost
     微调
   本质上仍是在
   已被验证为弱信号的
   weighting/routing 层
   打转。

## 五、下一步
1. 正式停止：
   - timing bonus
     微调
   - timing frame routing
     微调
2. 下一步更推荐：
   - 更强的
     timing-aware
     target shaping
   - 或显式
     boundary/clause-aware
     teacher target contract
3. 继续保持边界：
   - 当前不能把
     `target_event_timing_semantic_sidecar`
     误写成
     design-state
     `e_evt`
   - 也不能把这轮弱收益
     误解成
     “只差一组 routing 参数”
