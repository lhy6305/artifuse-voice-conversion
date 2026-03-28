# 456 Stage3 energy-vuv recover short-phase probe report

## 结论
- 我从 `warm3_21.step18` 启动了一条最小修正相位：
  - 目标是只修 `energy / vuv`，不再改 warm-start 结构
  - 配置见 `configs/streaming_student_loss_weights_vuv_balanced_gate_energyvuvrecover_v1.json`
- 结果是否定：
  - `energy` 确实回拉了一截
  - 但 `aper` 明显崩坏
  - validation 也明显退化
- 所以这条 `energy-vuv recover` 短修正线是 no-go，不升级为主线候选

## 试验设置
- 新配置：
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_energyvuvrecover_v1.json`
- 改动：
  - `teacher_energy_proxy = 0.35`
  - `teacher_vuv_proxy = 0.2`
  - `teacher_aper_proxy = 0.08`
  - 其余仍沿用 `vuv_balanced_gate_v1`
- 轨迹：
  - `warm3_21.step18 -> energyvuvrecover6`
- 输出：
  - 训练：
    - `reports/training/streaming_student_loop_timingfocus3warm18_energyvuvrecover6_denseckpt_round1_1/`
  - packet：
    - `reports/runtime/streaming_student_downstream_control_packet_timingfocus3warm18_energyvuvrecover6_step6_round1_1/`

## A. validation
- 起点参考：
  - `warm3_21.step18`
    - `loss_total = 0.774062`
    - `loss_total_semantic_disabled_reference = 0.684734`
    - `loss_teacher_event = 0.338198`
    - `loss_teacher_event_prior = 0.394285`
- 新修正相位：
  - `step3`
    - `loss_total = 1.307572`
    - `loss_total_semantic_disabled_reference = 1.193064`
  - `step6`
    - `loss_total = 0.843071`
    - `loss_total_semantic_disabled_reference = 0.749325`
    - `loss_teacher_event = 0.328271`
    - `loss_teacher_event_prior = 0.386763`
    - `loss_teacher_energy_proxy = 0.261025`
    - `loss_teacher_vuv_proxy = 0.339392`
    - `loss_teacher_aper_proxy = 0.031883`
- 判断：
  - 即使 best checkpoint 是 `step6`
  - 它也明显劣于起点 `warm3_21.step18`

## B. packet cheap screen

### readiness summary
- baseline24
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- warm3 step18
  - `0 / 1 / 3 / 2 / true`
- energyvuvrecover step6
  - `0 / 1 / 1 / 2 / true`

### 三记录平均
- baseline24
  - `avg_vuv_mae = 0.189806`
  - `avg_f0_corr = 0.430536`
  - `avg_f0_mae = 0.325703`
  - `avg_aper_mae = 0.11809`
  - `avg_energy_mae = 0.108172`
- warm3 step18
  - `0.19049 / 0.437627 / 0.323438 / 0.116664 / 0.145751`
- energyvuvrecover step6
  - `0.189094 / 0.412771 / 0.330097 / 0.349659 / 0.122894`

## C. 代表记录
- `target::chapter3_3_firefly_162`
  - warm3 step18
    - `energy_mean = 0.473586`
    - `energy_mae = 0.107506`
    - `aper_mae = 0.092821`
  - energyvuvrecover step6
    - `energy_mean = 0.601386`
    - `energy_mae = 0.095311`
    - `aper_mae = 0.188388`
- `target::chapter3_3_firefly_138`
  - warm3 step18
    - `energy_mean = 0.392035`
    - `energy_mae = 0.142374`
    - `aper_mae = 0.136135`
  - energyvuvrecover step6
    - `energy_mean = 0.517182`
    - `energy_mae = 0.119696`
    - `aper_mae = 0.369018`
- `target::chapter3_4_firefly_106`
  - warm3 step18
    - `energy_mean = 0.320851`
    - `energy_mae = 0.187373`
    - `aper_mae = 0.121035`
  - energyvuvrecover step6
    - `energy_mean = 0.392886`
    - `energy_mae = 0.153676`
    - `aper_mae = 0.49157`

## 判断
- 这条线的真实行为是：
  - `energy` 被拉回
  - `aper` 被明显拉坏
  - `f0` 也没有得到补偿
  - validation 同时回退
- 所以这不是“用少量 validation 换到更好的 packet”：
  - 它只是把问题从 `energy` 转移到了 `aper`

## 最终判断
- `energyvuvrecover_v1` no-go
- 当前主线状态保持不变：
  - packet-facing reference：`vuvbalancedgate24`
  - packet-aware next-best candidate：`warm6_18.step15`
