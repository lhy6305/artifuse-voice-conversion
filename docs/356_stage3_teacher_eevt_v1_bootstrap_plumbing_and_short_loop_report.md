# 356. Stage3 `teacher_e_evt_v1` bootstrap 接线与短 loop 验证报告

## 结论
- 本轮已把
  `design-state e_evt`
  的第一版 bootstrap 合同
  真正接进 Stage3：
  - teacher-label export
  - data batch
  - loss
  - 1-step train smoke
  - 12-step short loop
- 这次不是再做 target-only semantic weighting，
  而是让 Stage3 不再把旧
  `teacher_event_probs`
  当成最终 event contract。
- 当前实现口径是：
  - `teacher_e_evt_v1`
  仍是 bootstrap bridge，
  不是最终 teacher 真值；
  但它已经是显式命名语义合同，
  比匿名 heuristic event 向量更接近设计稿主线。

## 一、本轮代码改动

### 1. 新增 `e_evt_v1` 元数据与桥接生成器
- 更新：
  - `src/v5vc/event_semantics.py`
- 新增：
  - `design_state_e_evt_v1`
    合同常量
  - `build_design_state_e_evt_v1_meta()`
  - `build_teacher_e_evt_v1_targets(...)`
  - `rasterize_target_timing_semantic_sidecar(...)`

### 2. `teacher_labels` 正式导出 `teacher_e_evt`
- 更新：
  - `src/v5vc/streaming_student/teacher_labels.py`
- 当前导出 payload
  除保留旧：
  - `event_logits`
  - `event_probs`
  外，
  还新增：
  - `e_evt`
  - `e_evt_meta`
  - `e_evt_summary`
- `teacher_label_index.jsonl`
  也新增：
  - `teacher_event_contract_version = design_state_e_evt_v1`
  - `teacher_event_label_space_version = design_state_e_evt_bootstrap_bridge_v1`

### 3. Stage3 data/loss 改为真实消费 `teacher_e_evt`
- 更新：
  - `src/v5vc/streaming_student/data.py`
  - `src/v5vc/streaming_student/losses.py`
  - `src/v5vc/streaming_student/proxy_acoustic.py`
  - `src/v5vc/streaming_student/training_data_entry.py`
- 当前行为：
  - batch 中新增
    `teacher_e_evt`
  - `teacher_event / teacher_event_prior`
    损失现在对齐到
    `teacher_e_evt`
  - `vuv_proxy`
    改读
    `teacher_e_evt[..., 3]`
  - `aper_proxy`
    改读
    `teacher_e_evt[..., 4]`
  - `proxy_acoustic`
    不再假设
    `event_probs[..., 0]`
    就是活动门，
    而是改成
    `amax(event_probs)`
    做弱事件存在 proxy

## 二、当前 `teacher_e_evt_v1` 的 8 维定义
- `0`
  `p_frication`
- `1`
  `p_stop_closure`
- `2`
  `p_burst`
- `3`
  `p_voicing`
- `4`
  `a_aper`
- `5`
  `p_pause_boundary`
- `6`
  `p_terminal_boundary`
- `7`
  `p_final_clause`

### 当前来源
- 前五维来自：
  - legacy
    `event_probs`
    的启发式桥接
- 后三维来自：
  - `target_event_timing_semantic_sidecar`
    的 frame rasterization

### 当前边界
- 当前仍不包含：
  - `place`
  - `manner`
  - 更细 phone / forced alignment
- 所以这一步应解释为：
  - `teacher_e_evt_v1`
    已接通
- 不能解释成：
  - 最终完整 event contract
    已经完成

## 三、验证

### 1. 静态检查
- 已执行：
```powershell
.\python.exe -m py_compile `
  src/v5vc/event_semantics.py `
  src/v5vc/streaming_student/teacher_labels.py `
  src/v5vc/streaming_student/data.py `
  src/v5vc/streaming_student/losses.py `
  src/v5vc/streaming_student/proxy_acoustic.py `
  src/v5vc/streaming_student/training_data_entry.py
```
- 结果：
  - `py_compile_ok`

### 2. 全量 teacher-label 重导
- 已执行：
```powershell
.\python.exe manage.py build-streaming-student-teacher-labels `
  --data-output-dir data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1 `
  --report-output-dir reports/data/round1_1_streaming_student_teacher_labels_eevt_round1_1 `
  --batch-size 8
```
- 结果：
  - `record_count = 666`
  - `feature_dims.e_evt = 8`
- 产物：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_round1_1/`

### 3. payload 级核对
- 实际单条 payload
  现已包含：
  - `e_evt`
  - `e_evt_meta`
  - `e_evt_summary`
- 示例：
  - `target__archive_firefly_1.pt`
    的
    `e_evt.shape = [3054, 8]`
  - `e_evt_meta.event_contract_version = design_state_e_evt_v1`

### 4. training-data dry-run
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-training-data `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/teacher_label_index.jsonl `
  --output-dir reports/plans/streaming_student_training_data_eevt_round1_1 `
  --batch-size 2
```
- 结果：
  - `teacher_label_required_keys`
    已包含
    `teacher_e_evt`
  - `teacher_shapes.teacher_e_evt = [2, ..., 8]`
  - frame contract
    仍然对齐

### 5. supervision dry-run
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-supervision `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/teacher_label_index.jsonl `
  --output-dir reports/plans/streaming_student_supervision_eevt_round1_1 `
  --batch-size 2
```
- 结果：
  - Stage3 loss
    已在
    `teacher_e_evt`
    合同下跑通
  - 当前 dry-run
    仍保留 semantic/timing weighting，
    但 event 主监督已不再直接吃旧匿名向量

### 6. 1-step train smoke
- 已执行：
```powershell
.\python.exe manage.py run-streaming-student-training-step `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/teacher_label_index.jsonl `
  --output-dir reports/training/streaming_student_eevt_step_smoke_round1_1 `
  --batch-size 2 `
  --experiment-id streaming_student_eevt_step_smoke_round1_1
```
- 结果：
  - 正常完成
  - checkpoint：
    - `checkpoints/streaming_student_eevt_step_smoke_round1_1.step1.pt`

### 7. 12-step short loop
- 已执行：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/teacher_label_index.jsonl `
  --output-dir reports/training/streaming_student_loop_eevt12_round1_1 `
  --batch-size 2 `
  --validation-batch-size 2 `
  --num-steps 12 `
  --validation-interval 6 `
  --checkpoint-interval 6 `
  --validation-batches 1 `
  --experiment-id streaming_student_loop_eevt12_round1_1
```
- 结果：
  - `step1 train loss_total = 23.056263`
  - `step12 train loss_total = 8.215662`
  - `validation step6 loss_total = 10.765154`
  - `validation step12 loss_total = 8.609584`
  - short loop
    运行、验证、checkpoint
    全链路通过

## 四、本轮判断
- 这一步的意义不是：
  - 已经证明 clean voice
    会出现
- 它的意义是：
  1. Stage3
     现在终于有了显式
     `teacher_e_evt`
     合同
  2. `teacher_event_probs`
     不再是唯一事件监督入口
  3. 后续终于可以做：
     - `legacy event_probs`
       vs
       `teacher_e_evt_v1`
       的严格可比短 loop

## 五、下一步
1. 增加一个明确可切换的
   Stage3 event target family
   开关：
   - `legacy_event_probs`
   - `teacher_e_evt_v1`
2. 用它做第一轮严格可比短 loop，
   判断：
   - `teacher_e_evt_v1`
     相比 legacy
     是否真的改善
     Stage3 event supervision
     的可训练性
3. 若短 loop
   证明方向稳定，
   再把这套 event contract
   向更下游的
   Stage5 `C3`
   继续推进

## 一句话结论
- `teacher_e_evt_v1`
  现在已经真实落到
  Stage3 teacher labels / data / loss / train loop
  链上；
  下一步不该再回去讨论“event contract 还没接”，
  而应直接进入：
  - `legacy vs e_evt_v1`
    的严格可比短 loop。
