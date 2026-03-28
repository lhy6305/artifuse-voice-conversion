# 458 Stage3 vuv contract factor ablation report

## 结论
- 我把上一轮 `vuv transition blend` 拆成了两个单因素：
  - `transition-weight only`
  - `target-blend only`
- 再加上已有的 `target-blend + transition-weight`，本轮形成了完整 factor ablation：
  - baseline `vuvbalancedgate24`
  - `transitionweight_s6`
  - `targetblend_s6`
  - `transitionblend_s6`
- 结论非常清楚：
  - `transition-weight only` 是明确 no-go
    - `vuv` 比 baseline 更差
    - `energy_ready_count` 仍从 `3` 掉到 `2`
  - `target-blend only` 与 `target-blend + transition-weight` 基本等价
    - 两者都能把 `vuv` 拉好一截
    - 但都会同步拖坏 `aper / energy`
  - 所以这条线的有效成分不是 `transition boost`
    - 而是 `target blend` 本身
  - 但 `target blend` 的副作用仍然让它不能进入主线
- 因此本轮主线不更新：
  - packet-facing reference 仍是 `vuvbalancedgate24`
  - packet-aware next-best candidate 仍是 `warm6_18.step15`

## 代码与配置
- 新增 family：
  - `src/v5vc/streaming_student/losses.py`
  - `teacher_e_evt_v1_balanced_vuv_transition_weight_v1`
  - `teacher_e_evt_v1_balanced_vuv_target_blend_v1`
- 新增配置：
  - `configs/streaming_student_loss_weights_vuv_transition_weight_v1.json`
  - `configs/streaming_student_loss_weights_vuv_target_blend_v1.json`

## 试验设置
- 共同起点：
  - `reports/training/streaming_student_loop_vuvbalancedgate24_round1_1/checkpoints/streaming_student_stage_loop_vuvbalancedgate24_round1_1.step24.pt`
- 共同 protocol：
  - `baseline24 -> correction 6`
  - full-validation at `step3 / step6`
  - packet cheap screen on `step6`

### 输出
- transition-weight only
  - train:
    - `reports/training/streaming_student_loop_vuvtransitionweight_baseline24corr6_denseckpt_round1_1/`
  - packet:
    - `reports/runtime/streaming_student_downstream_control_packet_vuvtransitionweight_baseline24corr6_step6_round1_1/`
- target-blend only
  - train:
    - `reports/training/streaming_student_loop_vuvtargetblend_baseline24corr6_denseckpt_round1_1/`
  - packet:
    - `reports/runtime/streaming_student_downstream_control_packet_vuvtargetblend_baseline24corr6_step6_round1_1/`
- 历史对照：
  - baseline24 packet:
    - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate24_round1_1/`
  - target-blend + transition-weight:
    - `reports/runtime/streaming_student_downstream_control_packet_vuvtransitionblend_baseline24corr6_step6_round1_1/`

## A. validation
- baseline24
  - `loss_total = 0.919927`
  - `loss_total_semantic_disabled_reference = 0.832382`
  - `loss_teacher_vuv_proxy = 0.329065`

### transition-weight only
- step6
  - `loss_total = 0.925889`
  - `loss_total_semantic_disabled_reference = 0.832812`
  - `loss_teacher_vuv_proxy = 0.45105`
  - `loss_teacher_energy_proxy = 0.73499`
  - `loss_teacher_aper_proxy = 0.032996`
  - diagnostics:
    - `transition_frame_ratio = 0.046248`
    - `transition_boost_mean = 1.042751`
    - `target_blend_alpha = 0.0`

### target-blend only
- step6
  - `loss_total = 0.948017`
  - `loss_total_semantic_disabled_reference = 0.854848`
  - `loss_teacher_vuv_proxy = 0.525928`
  - `loss_teacher_energy_proxy = 0.777346`
  - `loss_teacher_aper_proxy = 0.033323`
  - diagnostics:
    - `transition_frame_ratio = 0.0`
    - `transition_boost_mean = 1.0`
    - `target_blend_alpha = 0.8`

### target-blend + transition-weight
- step6
  - `loss_total = 0.948547`
  - `loss_total_semantic_disabled_reference = 0.855373`
  - `loss_teacher_vuv_proxy = 0.528562`
  - `loss_teacher_energy_proxy = 0.777735`
  - `loss_teacher_aper_proxy = 0.033313`
  - diagnostics:
    - `transition_frame_ratio = 0.046248`
    - `transition_boost_mean = 1.042751`
    - `target_blend_alpha = 0.8`

## B. packet cheap screen

### readiness summary
- baseline24
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- transition-weight only
  - `0 / 1 / 3 / 2 / true`
- target-blend only
  - `0 / 1 / 3 / 2 / true`
- target-blend + transition-weight
  - `0 / 1 / 3 / 2 / true`

### 三记录平均
- baseline24
  - `avg_vuv_mae = 0.189806`
  - `avg_f0_corr = 0.430536`
  - `avg_f0_mae = 0.325703`
  - `avg_aper_mae = 0.11809`
  - `avg_energy_mae = 0.108172`
- transition-weight only
  - `0.219876 / 0.443576 / 0.323031 / 0.130367 / 0.134125`
- target-blend only
  - `0.175157 / 0.430034 / 0.327024 / 0.136656 / 0.132959`
- target-blend + transition-weight
  - `0.174319 / 0.430513 / 0.326845 / 0.136292 / 0.132971`

## C. 代表记录观察
- `target::chapter3_3_firefly_138`
  - baseline24
    - `vuv_mae = 0.207186`
    - `aper_mae = 0.137007`
    - `energy_mae = 0.109106`
  - transition-weight only
    - `0.244606 / 0.149901 / 0.13109`
  - target-blend only
    - `0.184954 / 0.152369 / 0.130017`
  - target-blend + transition-weight
    - `0.183729 / 0.152122 / 0.130024`
- `target::chapter3_4_firefly_106`
  - baseline24
    - `0.255081 / 0.12198 / 0.130859`
  - transition-weight only
    - `0.281364 / 0.139852 / 0.169255`
  - target-blend only
    - `0.244338 / 0.14995 / 0.167477`
  - target-blend + transition-weight
    - `0.243633 / 0.149343 / 0.167501`

## 判断
- `transition boost` 本身不是有价值的自由度：
  - 单独启用时，`vuv` 反而变差
  - 只保住了部分 `F0` 指标
  - 但没有把 packet gate 打开
- `target blend` 才是让 `vuv` 变好的真正因素：
  - `target-blend only` 和 `target-blend + transition-weight` 几乎重合
  - 两者对 `vuv` 的改善量接近
  - 两者对 `aper / energy` 的副作用也接近
- 这意味着当前问题已经不是：
  - “transition 帧有没有被强调到”
- 更准确的描述应是：
  - 只要把 `vuv target` 从 hard gate 拉向 deterministic target，
    当前 shared representation 就会牺牲 `aper / energy`

## 最终判断
- 本轮这条 `vuv contract-side factor ablation` 到此收口，不继续扩。
- 不做：
  - `transition_boost` 强度 sweep
  - `blend + transition` 的更长步数续跑
  - 在当前 family 上直接接 Stage5
- 当前主线保持不变：
  - packet-facing reference：`vuvbalancedgate24`
  - packet-aware next-best candidate：`warm6_18.step15`
