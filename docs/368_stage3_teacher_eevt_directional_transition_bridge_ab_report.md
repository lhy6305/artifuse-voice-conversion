# 368. Stage3 `teacher_e_evt` directional transition bridge A/B 报告

## 结论
- 我把 `teacher_e_evt` 前 5 个 acoustic dims 的 bridge 再往前推进了一层：
  - 旧最优：
    `acoustic_contextual_event_bridge_v1`
  - 新 candidate：
    `acoustic_directional_transition_bridge_v1`
- 这次不是再调 threshold 或 weight，
  而是把 `closure -> burst`
  的时序先后关系显式写进 generation-side bridge：
  - `closure`
    只看后续 burst 支持
  - `burst`
    只看先前 closure 支持
- 结果是正向，而且不是只在一个短点上成立：
  - full-validation step12：
    - baseline
      `loss_total = 1.65222`
      `loss_total_semantic_disabled_reference = 1.54467`
    - candidate
      `loss_total = 1.635463`
      `loss_total_semantic_disabled_reference = 1.529686`
  - full-validation step24：
    - baseline
      `loss_total = 0.975202`
      `loss_total_semantic_disabled_reference = 0.891887`
    - candidate
      `loss_total = 0.947703`
      `loss_total_semantic_disabled_reference = 0.867661`
- `loss_teacher_event / loss_teacher_event_prior`
  在 step12 和 step24
  都同向更低，
  所以这不是偶然一跳；
  当前可以把
  `acoustic_directional_transition_bridge_v1`
  升格为新的 Stage3 generation-side reference。
- 但这不等于：
  - 当前 Stage5 no-res downstream
    已值得再重跑
- 那条 handoff route
  已被前几轮反复证明不是承接突破口，
  所以这轮正确动作是先在 Stage3 把证据做硬，
  而不是又把同一上游改动送回旧失败路线。

## 一、本轮做了什么

### 1. 新增显式 directional bridge mode
- 代码：
  - `src/v5vc/event_semantics.py`
- 新 mode：
  - `acoustic_directional_transition_bridge_v1`

### 2. 这次改动的核心含义
- `acoustic_contextual_event_bridge_v1`
  已经把局部上下文引进来了，
  但 `closure / burst`
  仍主要看对称邻域
- 新 candidate
  进一步加入了方向性 transition 假设：
  - `future_burst_support`
    只从当前帧右侧聚合
  - `past_closure_support`
    只从当前帧左侧聚合
  - `closure`
    由
    `closure_region * future_burst_support * past_quiet_support`
    强化
  - `burst`
    由
    `burst_region * past_closure_support * future_energy_support`
    强化
- 也就是说：
  - 这轮不是再做
    symmetric smoothing
  - 而是把
    stop-like transition
    的方向性
    真正引进 teacher-label generation-side

### 3. 新增单侧 pooling helper
- 新 helper：
  - `pool_teacher_e_evt_bridge_channel(...)`
- 用它支持：
  - 左上下文 only
  - 右上下文 only
  - mean / max
- 原来的
  `smooth_teacher_e_evt_bridge_channel(...)`
  现在只是对称窗口的 wrapper

## 二、smoke export 与几何确认

### 1. smoke export
- 输出：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directional_smoke_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directional_smoke_round1_1/`
- 关键确认：
  - `teacher_e_evt_bridge_mode = acoustic_directional_transition_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
  - `record_count = 6`

### 2. 不是 metadata-only
- 示例记录：
  - `target::archive_firefly_1`
- 与旧最优 `acoustic_contextual_event_bridge_v1`
  对比前 5 维均值：
  - contextual：
    `[0.091919, 0.17395, 0.101624, 0.503418, 0.27124]`
  - directional：
    `[0.083618, 0.129761, 0.08252, 0.503418, 0.27124]`
- 绝对差：
  - `[0.008301, 0.044189, 0.019104, 0.0, 0.0]`
- 说明：
  - 这轮确实主要改动了
    `closure / burst`
    相关通道
  - `voicing / aper`
    基本保持旧最优几何

## 三、全量 teacher-label 与 dry-run

### 1. 全量 export
- 输出：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directional_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directional_round1_1/`
- 关键确认：
  - `teacher_e_evt_bridge_mode = acoustic_directional_transition_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`

### 2. supervision dry-run
- 输出：
  - `reports/plans/streaming_student_supervision_eevt_directional_round1_1/`
- 关键确认：
  - 仍是：
    - `event_target_family = teacher_e_evt_v1`
    - `event_projection_mode = full_e_evt`
- 所以本轮 A/B
  仍只隔离 generation-side bridge 变量，
  没混入 loss-side 变化

## 四、严格可比 full-validation A/B

### 1. 12-step 对照
- baseline：
  - `reports/training/streaming_student_loop_eevt_acousticcontext_fullval12_round1_1/`
- candidate：
  - `reports/training/streaming_student_loop_eevt_directional_fullval12_round1_1/`
- step12 validation：
  - baseline
    - `loss_total = 1.65222`
    - `loss_total_semantic_disabled_reference = 1.54467`
    - `loss_teacher_event = 0.49421`
    - `loss_teacher_event_prior = 0.677806`
  - candidate
    - `loss_total = 1.635463`
    - `loss_total_semantic_disabled_reference = 1.529686`
    - `loss_teacher_event = 0.482419`
    - `loss_teacher_event_prior = 0.669148`

### 2. 24-step 对照
- baseline：
  - `reports/training/streaming_student_loop_eevt_acousticcontext_fullval24_round1_1/`
- candidate：
  - `reports/training/streaming_student_loop_eevt_directional_fullval24_round1_1/`
- step24 validation：
  - baseline
    - `loss_total = 0.975202`
    - `loss_total_semantic_disabled_reference = 0.891887`
    - `loss_teacher_event = 0.417446`
    - `loss_teacher_event_prior = 0.505388`
  - candidate
    - `loss_total = 0.947703`
    - `loss_total_semantic_disabled_reference = 0.867661`
    - `loss_teacher_event = 0.399819`
    - `loss_teacher_event_prior = 0.486579`

### 3. 其他项
- `z_art`
  在 step24
  也略好：
  - `0.034814 -> 0.034481`
- `energy_proxy`
  基本持平略好：
  - `0.545835 -> 0.544777`
- timing aux
  不是一起全面更好：
  - `terminal_boundary`
    略差
  - `final_clause`
    略差
- 但共享主指标
  与
  `teacher_event / event_prior`
  已足够支撑本轮结论

## 五、当前解释
1. 这说明：
   - 现在真正有效的增益层，
     仍然是
     `teacher-label / target-state`
     generation-side
2. 而且比上一轮
   `acoustic_contextual_event_bridge_v1`
   更进一步的是：
   - 不是单纯“更多上下文”
   - 而是
     transition 的方向性假设
     本身
3. 当前最合理的更新是：
   - 把
     `acoustic_directional_transition_bridge_v1`
     作为新的 Stage3 best reference
4. 但必须同时写清楚：
   - 这不构成
     当前 Stage5 no-res downstream
     值得再次重跑的理由
   - 因为我们已经有充分反证说明：
     当前 handoff layer
     不是这些上游正向的承接突破口

## 六、下一步
1. 不回去做：
   - `acoustic_contextual`
     的小系数补丁
   - `directional`
     的同层小阈值 sweep
   - 把当前 candidate
     又投回旧的
     Stage5 no-res downstream route
2. 下一步更值钱的是：
   - 以
     `acoustic_directional_transition_bridge_v1`
     作为新的 Stage3 generation-side reference
   - 继续做更上游的
     teacher-label / target-state
     资产升级
   - 或重新识别
     哪个 downstream handoff layer
     才真正能承接
     这些上游正向改动
