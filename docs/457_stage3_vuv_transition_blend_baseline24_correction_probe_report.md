# 457 Stage3 vuv transition-blend baseline24 correction probe report

## 结论
- 我对当前 packet-facing reference `vuvbalancedgate24` 做了一条最小 `vuv contract-side` 修正：
  - 不再改 loss 权重
  - 不再加 `teacher_vuv_state`
  - 只把 `named_control_proxy_target_family` 换成新的 `teacher_e_evt_v1_balanced_vuv_transition_blend_v1`
- 新 family 的行为是：
  - 保留当前 `balanced_vuv_gate` 的 unvoiced reweight
  - 用 `teacher_target_vuv` 和 hard voiced gate 做 `0.8 / 0.2` 混合 target
  - 对 `teacher_target_vuv` 变化较快的 transition 帧额外加权
- 结果仍然是否定：
  - validation 比 `baseline24` 更差
  - packet 上 `vuv` 的确改善了一截
  - 但 `aper / energy` 同时明显回退，`energy_ready_count` 从 `3` 掉到 `2`
- 因此这条 `vuv transition blend` 线不能升级为主线候选。
  - 当前 packet-facing reference 继续保持 `vuvbalancedgate24`
  - 当前 packet-aware next-best candidate 继续保持 `warm6_18.step15`

## 代码与配置
- 新增 target family：
  - `src/v5vc/streaming_student/losses.py`
  - `teacher_e_evt_v1_balanced_vuv_transition_blend_v1`
- 新增配置：
  - `configs/streaming_student_loss_weights_vuv_transition_blend_v1.json`
- 顺手修了一个实验入口缺口：
  - `src/v5vc/cli.py`
  - `run-streaming-student-training-step` 现在也接受 `--init-checkpoint`

## 试验设置
- 起点 checkpoint：
  - `reports/training/streaming_student_loop_vuvbalancedgate24_round1_1/checkpoints/streaming_student_stage_loop_vuvbalancedgate24_round1_1.step24.pt`
- 修正轨迹：
  - `baseline24 -> vuvtransitionblend correction 6`
- 训练输出：
  - `reports/training/streaming_student_loop_vuvtransitionblend_baseline24corr6_denseckpt_round1_1/`
- packet 输出：
  - `reports/runtime/streaming_student_downstream_control_packet_vuvtransitionblend_baseline24corr6_step6_round1_1/`

## A. validation
- baseline24
  - `loss_total = 0.919927`
  - `loss_total_semantic_disabled_reference = 0.832382`
  - `loss_teacher_vuv_proxy = 0.329065`
  - `loss_teacher_energy_proxy = 1.177872`
  - `loss_teacher_aper_proxy = 0.051589`
- transition-blend correction
  - `step3`
    - `loss_total = 1.374925`
    - `loss_total_semantic_disabled_reference = 1.27913`
    - `loss_teacher_vuv_proxy = 0.780964`
  - `step6`
    - `loss_total = 0.948547`
    - `loss_total_semantic_disabled_reference = 0.855373`
    - `loss_teacher_vuv_proxy = 0.528562`
    - `loss_teacher_energy_proxy = 0.777735`
    - `loss_teacher_aper_proxy = 0.033313`
- 判断：
  - 这条线能把 `energy / aper proxy loss` 压低
  - 但 shared validation 仍然回退
  - `teacher_vuv_proxy` 在 validation 上也没有拿到优势

## B. 新 family 是否真实生效
- 训练 metrics 已确认不是空跑：
  - `teacher_named_control_proxy_target_family = teacher_e_evt_v1_balanced_vuv_transition_blend_v1`
  - `teacher_vuv_proxy_target_blend_alpha = 0.8`
  - full-validation
    - `teacher_vuv_proxy_transition_frame_ratio = 0.046248`
    - `teacher_vuv_proxy_transition_boost_mean = 1.042751`
- 说明：
  - 这次结果可以解释为新 VUV family 的真实行为
  - 不是配置未穿透或无效训练

## C. packet cheap screen

### readiness summary
- baseline24
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- transition-blend step6
  - `0 / 1 / 3 / 2 / true`

### 三记录平均
- baseline24
  - `avg_vuv_mae = 0.189806`
  - `avg_f0_corr = 0.430536`
  - `avg_f0_mae = 0.325703`
  - `avg_aper_mae = 0.11809`
  - `avg_energy_mae = 0.108172`
- transition-blend step6
  - `0.174319 / 0.430513 / 0.326845 / 0.136292 / 0.132971`

## D. 代表记录
- `target::chapter3_3_firefly_162`
  - baseline24
    - `vuv_mae = 0.107152`
    - `aper_mae = 0.095282`
    - `energy_mae = 0.08455`
  - transition-blend step6
    - `0.095594 / 0.107412 / 0.101388`
- `target::chapter3_3_firefly_138`
  - baseline24
    - `vuv_mae = 0.207186`
    - `aper_mae = 0.137007`
    - `energy_mae = 0.109106`
  - transition-blend step6
    - `0.183729 / 0.152122 / 0.130024`
- `target::chapter3_4_firefly_106`
  - baseline24
    - `vuv_mae = 0.255081`
    - `aper_mae = 0.12198`
    - `energy_mae = 0.130859`
  - transition-blend step6
    - `0.243633 / 0.149343 / 0.167501`

## 判断
- 这条线的真实效果很明确：
  - `vuv` 在三条代表记录上都变好
  - 但 `aper / energy` 三条都同步回退
  - `f0` 基本原地踏步
- 所以它不是主线需要的“打开新门”：
  - 它只是把当前 bottleneck 从 `vuv` 再次转移回 `energy / aper`

## 最终判断
- `teacher_e_evt_v1_balanced_vuv_transition_blend_v1` 暂停，不继续扩成更长步数或 Stage5 handoff。
- 当前主线状态保持不变：
  - packet-facing reference：`vuvbalancedgate24`
  - packet-aware next-best candidate：`warm6_18.step15`
