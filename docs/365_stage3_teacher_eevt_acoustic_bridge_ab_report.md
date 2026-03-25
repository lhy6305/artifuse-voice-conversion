# 365. Stage3 `teacher_e_evt` acoustic-bridge generation-side A/B 报告

## 结论
- 我把 `teacher_e_evt` 前 5 个 acoustic dims 的 bootstrap bridge 做成了显式合同开关：
  - `legacy_event_probs_v1`
  - `acoustic_guided_event_bridge_v1`
- 这次不再动后三个结构位几何；
  baseline 和 candidate
  都保持：
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
- 新 candidate 的区别是：
  - `p_frication / p_stop_closure / p_burst / p_voicing / a_aper`
    不再只搬 legacy `event_probs`
  - 还引入
    `teacher acoustic_target`
    的 `energy / zero_cross / delta_energy`
    做 acoustic-guided bridge
- 严格可比 12-step validation
  结果继续正向：
  - baseline
    `loss_total = 1.927881`
    `loss_total_semantic_disabled_reference = 1.776346`
  - candidate
    `loss_total = 1.897212`
    `loss_total_semantic_disabled_reference = 1.751405`
- 关键主监督项也同向改善：
  - `loss_teacher_event: 0.570513 -> 0.539711`
  - `loss_teacher_event_prior: 0.737615 -> 0.714994`
- 但 timing aux 不是一起全面变好：
  - `loss_teacher_timing_pause_boundary: 0.403185 -> 0.404393`
  - `loss_teacher_timing_terminal_boundary: 0.342470 -> 0.352758`
- 所以当前结论是：
  - 前 5 维 acoustic bridge
    的 generation-side 升级
    比仅改结构位 shaping
    更值得继续
  - 但它仍只是
    Stage3-level 正向证据，
    不能直接外推出 Stage5 已接近脱离 buzz

## 一、本轮做了什么

### 1. 新增显式 `teacher_e_evt_bridge_mode`
- 代码：
  - `src/v5vc/event_semantics.py`
  - `src/v5vc/streaming_student/teacher_labels.py`
  - `src/v5vc/cli.py`
- 当前支持：
  - `legacy_event_probs_v1`
  - `acoustic_guided_event_bridge_v1`

### 2. 新 bridge 的含义
- `legacy_event_probs_v1`
  维持当前前 5 维的直接桥接：
  - `p_frication`
    主要来自 high-zero-cross 相关 legacy dim
  - `p_stop_closure`
    主要来自 `delta_energy_fall`
  - `p_burst`
    主要来自 `delta_energy_rise`
  - `p_voicing`
    主要来自 low-zero-cross voiced-like dim
  - `a_aper`
    主要来自 high-zero-cross dim
- `acoustic_guided_event_bridge_v1`
  在以上基础上引入：
  - `energy`
  - `zero_cross`
  - `delta_energy`
  - `energy_norm`
  的 acoustic-guided 修正

## 二、teacher-label export

### 1. 全量 candidate teacher-label
- 输出：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_acousticbridge_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_acousticbridge_round1_1/`
- 关键确认：
  - `record_count = 666`
  - `teacher_e_evt_bridge_mode = acoustic_guided_event_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`

### 2. smoke payload 级核对
- 示例：
  - `target::archive_firefly_1`
- 前 5 维均值已真实变化：
  - baseline shaped：
    - `[0.193656, 0.477887, 0.483657, 0.489940, 0.192742]`
  - acoustic bridge：
    - `[0.104178, 0.389510, 0.207877, 0.503101, 0.269473]`
- 说明：
  - 本轮不是 metadata-only
  - generation-side bridge
    确实改了 supervision target 本身

## 三、dry-run
- 输出：
  - `reports/plans/streaming_student_supervision_eevt_acousticbridge_round1_1/`
- 关键确认：
  - 仍是：
    - `event_target_family = teacher_e_evt_v1`
    - `event_projection_mode = full_e_evt`
  - 也就是说：
    - 当前 A/B
      仍只隔离
      generation-side bridge
      变量

## 四、严格可比 12-step A/B

### 1. baseline
- teacher-label index：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_shaped_round1_1/teacher_label_index.jsonl`
- 输出：
  - `reports/training/streaming_student_loop_eevt_acousticbridge_baseline12_round1_1/`
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

### 2. candidate
- teacher-label index：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_acousticbridge_round1_1/teacher_label_index.jsonl`
- 输出：
  - `reports/training/streaming_student_loop_eevt_acousticbridge12_round1_1/`
- step12 validation：
  - `loss_total = 1.897212`
  - `loss_total_default_reference = 1.833316`
  - `loss_total_semantic_disabled_reference = 1.751405`
  - `loss_teacher_z_art = 0.067377`
  - `loss_teacher_event = 0.539711`
  - `loss_teacher_event_prior = 0.714994`
  - `loss_teacher_timing_pause_boundary = 0.404393`
  - `loss_teacher_timing_terminal_boundary = 0.352758`
  - `loss_teacher_timing_final_clause = 0.688776`

## 五、当前解释
1. 这说明：
   - 相比只改结构位几何，
     当前更大的瓶颈
     确实还在
     前 5 个 acoustic event bridge
2. generation-side
   的 acoustic-guided bridge
   已经给出
   比上一轮 shaping
   更强的 Stage3 正向证据
3. 但也要写清楚：
   - `z_art`
     没有一起变好
   - timing aux
     也不是全线改善
4. 所以它的正确定位是：
   - 当前 teacher-label generation-side
     最值得保留的候选方向
   - 但还不是
     “主链已经打通”

## 六、下一步
1. 不再回去做：
   - 纯结构位 shaping
     小扫参
2. 最值钱的动作是：
   - 立刻把这个
     `acoustic_guided_event_bridge_v1`
     推到 Stage5 downstream
     快速链路
   - 检查它是不是仍只停留在 Stage3 正向
