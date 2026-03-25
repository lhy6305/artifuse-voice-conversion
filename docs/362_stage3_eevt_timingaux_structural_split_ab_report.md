# 362. Stage3 `teacher_e_evt_v1` timing-aux structural split 严格可比短 loop 报告

## 结论
- 我把 Stage3 event 主监督里的结构位 supervision 方式做成了显式合同开关：
  - `event_projection_mode = full_e_evt`
  - `event_projection_mode = acoustic_main_plus_timing_aux_v1`
- 新模式的含义不是简单调权重，而是：
  - `teacher_event / teacher_event_prior`
    主头只监督
    `p_frication / p_stop_closure / p_burst / p_voicing / a_aper`
  - `p_pause_boundary / p_terminal_boundary / p_final_clause`
    从主 event 头剥离，
    只走 timing aux heads
- 但在当前 bootstrap 口径下，
  这条“结构位解耦”路线应 fail-fast 判停：
  - baseline
    `full_e_evt`
    step12 validation：
    - `loss_total = 1.952654`
    - `loss_total_semantic_disabled_reference = 1.796829`
  - candidate
    `acoustic_main_plus_timing_aux_v1`
    step12 validation：
    - `loss_total = 2.112254`
    - `loss_total_semantic_disabled_reference = 1.936075`
- 所以当前结论不能再往“loss-side projection 小改”上延伸：
  - 把结构位从主 event 头里剥出去，
    在当前 teacher/bootstrap 质量下并没有带来更好的短程优化行为

## 一、本轮做了什么

### 1. 新增 `event_projection_mode`
- 代码：
  - `src/v5vc/streaming_student/losses.py`
- 新增配置：
  - `event_projection_mode = full_e_evt`
  - `event_projection_mode = acoustic_main_plus_timing_aux_v1`
- 当前行为：
  - `full_e_evt`
    保持主 event 头继续监督 8 维 `teacher_e_evt`
  - `acoustic_main_plus_timing_aux_v1`
    对主 event 头加通道 mask，
    只保留前 5 个 acoustic dims

### 2. BCE 监督现已支持按通道 mask
- 更新：
  - `masked_bce_with_logits(...)`
  - `masked_bce_with_logits_per_sample(...)`
- 当前行为：
  - 除逐帧 `frame_weight`
    外，
    现在还能额外乘：
    - `channel_weight`
- 这让
  `teacher_event / teacher_event_prior`
  可以显式排除：
  - `p_pause_boundary`
  - `p_terminal_boundary`
  - `p_final_clause`

### 3. 新增可复现实验 override
- 新增：
  - `configs/streaming_student_loss_weights_eevt_timingaux_baseline_v1.json`
  - `configs/streaming_student_loss_weights_eevt_timingaux_structuralsplit_v1.json`
- 对照设计：
  - 两边都：
    - 开 timing aux loss
    - 关 timing routing
    - 关 timing bonus
    - 用同一份
      `teacher_e_evt_v1`
      teacher-label index
  - 只切：
    - `event_projection_mode`

## 二、dry-run 验证
- 输出：
  - `reports/plans/streaming_student_supervision_eevt_structuralsplit_round1_1/`
- 关键确认：
  - `teacher_event_projection_mode = acoustic_main_plus_timing_aux_v1`
  - `teacher_event_main_supervised_dim_count = 5`
  - `teacher_event_main_excluded_dims = p_pause_boundary,p_terminal_boundary,p_final_clause`
  - `loss_teacher_timing_pause_boundary`
    已非零，
    说明 timing aux heads
    的 supervision
    在这条线上真实开启

## 三、12-step 严格可比 A/B

### 1. baseline：`full_e_evt`
- 产物：
  - `reports/training/streaming_student_loop_eevt_timingaux_baseline12_round1_1/`
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

### 2. candidate：`acoustic_main_plus_timing_aux_v1`
- 产物：
  - `reports/training/streaming_student_loop_eevt_timingaux_structuralsplit12_round1_1/`
- step12 validation：
  - `loss_total = 2.112254`
  - `loss_total_default_reference = 2.045765`
  - `loss_total_semantic_disabled_reference = 1.936075`
  - `loss_teacher_z_art = 0.066657`
  - `loss_teacher_event = 0.691702`
  - `loss_teacher_event_prior = 0.836328`
  - `loss_teacher_timing_pause_boundary = 0.436899`
  - `loss_teacher_timing_terminal_boundary = 0.352832`
  - `loss_teacher_timing_final_clause = 0.727298`

## 四、当前解释
1. 这次不是：
   - timing aux
     没有接通
   - 或结构位
     还没真正从主头剥离
2. 相反：
   - contract
     已真实切换
   - 但结果仍更差
3. 这说明：
   - 当前 bootstrap
     `teacher_e_evt_v1`
     质量下，
     主 event 头继续背一部分结构位监督，
     反而比“完全交给 timing aux heads”
     更稳
4. 所以下一步不应继续做：
   - `event_projection_mode`
     的 loss-side 细调
   - `main_supervised_dim_count`
     再扫一组
   - timing aux
     小权重再扫一组

## 五、当前阶段判断
1. 这轮不是白做：
   - 它把
     Stage3 event contract
     的“主 event vs timing aux”
     边界做成了可显式 A/B 的合同开关
2. 但作为实验路线，
   当前
   `acoustic_main_plus_timing_aux_v1`
   已被第一轮严格可比短 loop 否定
3. 所以若还保留
   Stage3 主线，
   下一步应继续上收到：
   - teacher-label 生成侧
     的 target shaping
   - 或更高层级的
     `e_evt`
     监督质量升级
4. 不再把：
   - “把结构位从主 event 头里剥出去”
   误解成：
   - 在当前 bootstrap 阶段
     一定更接近设计态
