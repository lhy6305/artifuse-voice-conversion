# 363. Stage3 `teacher_e_evt` generation-side target shaping 严格可比短 loop 报告

## 结论
- 我把 `teacher_e_evt_v1` 的 generation-side label geometry 做成了显式合同开关：
  - `hard_box_v1`
  - `center_weighted_boundary_progressive_final_clause_v1`
- 这次不是 loss routing，也不是 aux/head 职责重分配，而是直接改 teacher-label 生成侧：
  - `pause / terminal boundary`
    从固定硬窗改成 center-weighted
  - `final_clause`
    从整段全 1
    改成 progressive ramp
- 在当前严格可比 12-step A/B 下，
  shaped labels
  首次给出了正向结果：
  - baseline
    `loss_total = 1.952654`
    `loss_total_semantic_disabled_reference = 1.796829`
  - shaped
    `loss_total = 1.927881`
    `loss_total_semantic_disabled_reference = 1.776346`
- 其他关键项也同向变好：
  - `loss_teacher_event: 0.590488 -> 0.570513`
  - `loss_teacher_event_prior: 0.755913 -> 0.737615`
  - `loss_teacher_timing_pause_boundary: 0.412537 -> 0.403185`
  - `loss_teacher_timing_final_clause: 0.705116 -> 0.697581`
- 所以当前结论是：
  - generation-side `teacher_e_evt` shaping
    比前面的 Stage3 loss-side 微调
    更有价值
  - 但它目前仍只是
    Stage3-level 正向证据，
    还不能直接宣称下游 Stage5 会因此脱离 buzz

## 一、本轮做了什么

### 1. 新增显式 shaping mode
- 代码：
  - `src/v5vc/event_semantics.py`
  - `src/v5vc/streaming_student/teacher_labels.py`
  - `src/v5vc/cli.py`
- 当前支持：
  - `hard_box_v1`
  - `center_weighted_boundary_progressive_final_clause_v1`

### 2. shaping 含义
- `pause_boundary_window / terminal_boundary_window`
  不再整个窗口直接填 `1.0`
  而是按 `center_frame_index`
  生成中心高、两侧低的权重
- `final_clause`
  不再整个 final/single clause
  全段填 `1.0`
  而是按 clause 内帧位置
  生成从前到后的渐进 ramp

### 3. teacher-label export 现在会显式落盘 shaping mode
- CLI 新增：
  - `--teacher-eevt-target-shaping-mode`
- summary / index / payload
  现都包含：
  - `teacher_e_evt_target_shaping_mode`

## 二、teacher-label 重导与 smoke 核对

### 1. 全量 shaped teacher-label
- 输出：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_shaped_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_shaped_round1_1/`
- 关键确认：
  - `record_count = 666`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`

### 2. payload 级核对
- shaped smoke export
  已确认：
  - index row
  - `e_evt_meta`
  - `e_evt_summary`
  三处都带同一 shaping mode

### 3. 几何变化核对
- 示例记录：
  - `target::archive_firefly_1`
    - `timing_final_clause_frame_ratio: 0.200393 -> 0.100360`
    - `timing_pause_frame_ratio: 0.006549 -> 0.003929`
  - `target::archive_firefly_10`
    - `timing_final_clause_frame_ratio: 0.034002 -> 0.017107`
    - `timing_pause_frame_ratio: 0.005913 -> 0.003590`
- 说明：
  - 这轮不是 metadata-only
  - 标签几何确实变窄、变软了

## 三、dry-run
- 输出：
  - `reports/plans/streaming_student_supervision_eevt_targetshaping_round1_1/`
- 关键确认：
  - 仍是：
    - `event_target_family = teacher_e_evt_v1`
    - `event_projection_mode = full_e_evt`
  - 也就是：
    - 本轮 A/B
      不再混入
      loss-side projection
      变量

## 四、严格可比 12-step A/B

### 1. baseline
- teacher-label index：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/teacher_label_index.jsonl`
- 输出：
  - `reports/training/streaming_student_loop_eevt_targetshaping_baseline12_round1_1/`
- step12 validation：
  - `loss_total = 1.952654`
  - `loss_total_default_reference = 1.888852`
  - `loss_total_semantic_disabled_reference = 1.796829`
  - `loss_teacher_z_art = 0.062956`
  - `loss_teacher_event = 0.590488`
  - `loss_teacher_event_prior = 0.755913`
  - `loss_teacher_timing_pause_boundary = 0.412537`
  - `loss_teacher_timing_terminal_boundary = 0.340636`
  - `loss_teacher_timing_final_clause = 0.705116`

### 2. shaped candidate
- teacher-label index：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_shaped_round1_1/teacher_label_index.jsonl`
- 输出：
  - `reports/training/streaming_student_loop_eevt_targetshaping12_round1_1/`
- step12 validation：
  - `loss_total = 1.927881`
  - `loss_total_default_reference = 1.864597`
  - `loss_total_semantic_disabled_reference = 1.776346`
  - `loss_teacher_z_art = 0.063701`
  - `loss_teacher_event = 0.570513`
  - `loss_teacher_event_prior = 0.737615`
  - `loss_teacher_timing_pause_boundary = 0.403185`
  - `loss_teacher_timing_terminal_boundary = 0.342470`
  - `loss_teacher_timing_final_clause = 0.697581`

## 五、当前解释
1. 这轮正向信号来自：
   - teacher-label 生成侧
     label geometry
     本身
   - 不是：
     - head 解耦
     - routing bonus
     - aux 权重微调
2. 这说明：
   - 当前更值得继续投资的层
     确实是
     `teacher-label / target shaping`
     生成侧
3. 但收益幅度目前仍是：
   - 小幅、一致性正向
   - 不是已经压出巨大 margin
4. 所以它的正确解读是：
   - 这是目前少数站住的上游正向证据
   - 不是已经证明 Stage5 emergence 会自然出现

## 六、下一步
1. 不回去做：
   - Stage3 loss-side projection
   - timing aux 小扫参
2. 最值钱的下一步是：
   - 立刻把 shaped `teacher_e_evt`
     推到现有 Stage5 downstream fail-fast 链
   - 检查它是否只是
     Stage3 自己变好，
     还是能真实往人耳样本方向推进
