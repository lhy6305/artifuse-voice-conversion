# 452 Stage3 warm-start refinement and packet-aware selection report

## 结论
- `warm6_18` 是到目前为止最强的两阶段候选：
  - validation 远好于 `baseline24`
  - packet 明显好于上一轮 `warm12`
  - 同一条轨迹内，`step18` 同时优于 `step12`
- 但它仍未全面超过 `baseline24`：
  - readiness summary 仍是 `f0=0 / vuv=1 / aper=3`
  - `energy_ready_count` 只有 `2`，低于 baseline24 的 `3`
- 因此：
  - 当前仍不切换 packet-facing reference，继续保持 `vuvbalancedgate24`
  - 但后续主线 warm-start 试验应以 `warm6_18.step18` 为新的起点，而不是继续回到 `warm12`

## 本轮试验设计
- 目标：
  - 继续收窄两阶段 warm-start
  - 验证“short warm phase + baseline phase2”是否比“long warm phase + baseline phase2”更稳
  - 并在同一条轨迹内做 packet-aware checkpoint selection
- 候选：
  - `warm12_lr5e4`
    - `timingfocus12.step12 -> baseline 12 steps @ lr=5e-4`
  - `warm6_18`
    - `timingfocus12.step6 -> baseline 18 steps @ lr=1e-3`
  - `warm6_18_lr5e4`
    - `timingfocus12.step6 -> baseline 18 steps @ lr=5e-4`

## A. validation 对比

### 基线与上一轮 warm-start
- baseline24 final
  - `loss_total = 0.919927`
  - `loss_total_semantic_disabled_reference = 0.832382`
  - `loss_teacher_event = 0.325852`
  - `loss_teacher_event_prior = 0.392491`
- warm12 final
  - `loss_total = 0.833233`
  - `loss_total_semantic_disabled_reference = 0.741754`
  - `loss_teacher_event = 0.340539`
  - `loss_teacher_event_prior = 0.388945`

### 新候选
- warm12_lr5e4 final
  - `loss_total = 0.855612`
  - `loss_total_semantic_disabled_reference = 0.762795`
  - `loss_teacher_event = 0.356668`
  - `loss_teacher_event_prior = 0.409074`
- warm6_18 final
  - `loss_total = 0.716152`
  - `loss_total_semantic_disabled_reference = 0.630345`
  - `loss_teacher_event = 0.323067`
  - `loss_teacher_event_prior = 0.381626`
- warm6_18_lr5e4 final
  - `loss_total = 0.832626`
  - `loss_total_semantic_disabled_reference = 0.739283`
  - `loss_teacher_event = 0.357071`
  - `loss_teacher_event_prior = 0.414424`

### 判断
- `warm12_lr5e4` 不如 `warm12`
- `warm6_18_lr5e4` 不如 `warm6_18`
- `warm6_18` 明显是这一轮唯一值得继续看的候选

## B. `warm6_18` packet 对比

### 与 baseline24 / warm12 对比
- baseline24 summary
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- warm12 summary
  - `f0=0 / vuv=1 / aper=3 / energy=1 / all_records_auto_reject=true`
- warm6_18 summary
  - `f0=0 / vuv=1 / aper=3 / energy=2 / all_records_auto_reject=true`

### 代表记录
- `target::chapter3_3_firefly_162`
  - baseline24
    - `vuv_reference_mae = 0.107152`
    - `f0_proxy_reference_corr = 0.495445`
    - `f0_calibrated_log2_mae = 0.17472`
    - `aper_calibrated_reference_mae = 0.095282`
  - warm12
    - `0.106564 / 0.432845 / 0.186373 / 0.103936`
  - warm6_18
    - `0.107733 / 0.514897 / 0.171179 / 0.093091`
- `target::chapter3_3_firefly_138`
  - baseline24
    - `0.207186 / 0.187293 / 0.431756 / 0.137007`
  - warm12
    - `0.20369 / 0.144777 / 0.429963 / 0.148242`
  - warm6_18
    - `0.220604 / 0.199807 / 0.432085 / 0.13834`
- `target::chapter3_4_firefly_106`
  - baseline24
    - `0.255081 / 0.608869 / 0.370633 / 0.12198`
  - warm12
    - `0.248215 / 0.555656 / 0.4098 / 0.140709`
  - warm6_18
    - `0.249854 / 0.62316 / 0.358203 / 0.123861`

### 判断
- 相对 warm12，`warm6_18` 明显更稳
- 相对 baseline24，`warm6_18` 呈现 mixed 结果：
  - `target::chapter3_3_firefly_162` 明显更好
  - `target::chapter3_4_firefly_106` 大多更好，仅 aper 略差
  - `target::chapter3_3_firefly_138` 略差
- 这已经说明 short warm phase 比 long warm phase 更符合 packet-facing 需求

## C. `warm6_18` 的 packet-aware checkpoint 选择

### validation
- `step12`
  - `loss_total = 0.849004`
  - `loss_total_semantic_disabled_reference = 0.753998`
  - `loss_teacher_event = 0.370446`
  - `loss_teacher_event_prior = 0.411357`
- `step18`
  - `loss_total = 0.716152`
  - `loss_total_semantic_disabled_reference = 0.630345`
  - `loss_teacher_event = 0.323067`
  - `loss_teacher_event_prior = 0.381626`

### packet
- `step12` summary
  - `f0=0 / vuv=1 / aper=3 / energy=1`
- `step18` summary
  - `f0=0 / vuv=1 / aper=3 / energy=2`

### 代表记录
- `target::chapter3_3_firefly_162`
  - step12
    - `vuv_reference_mae = 0.115915`
    - `f0_proxy_reference_corr = 0.429911`
    - `f0_calibrated_log2_mae = 0.185516`
    - `aper_calibrated_reference_mae = 0.093152`
  - step18
    - `0.107733 / 0.514897 / 0.171179 / 0.093091`
- `target::chapter3_3_firefly_138`
  - step12
    - `0.22176 / 0.153672 / 0.431375 / 0.138684`
  - step18
    - `0.220604 / 0.199807 / 0.432085 / 0.13834`
- `target::chapter3_4_firefly_106`
  - step12
    - `0.263216 / 0.549034 / 0.409214 / 0.122934`
  - step18
    - `0.249854 / 0.62316 / 0.358203 / 0.123861`

### 判断
- `step18` 同时优于 `step12`：
  - validation 更强
  - energy readiness 更高
  - 代表记录整体更好
- 所以 `warm6_18.step18` 是这条 warm-start 轨迹里的最佳 checkpoint

## 最终判断
- 当前最值得继续推进的主线候选已经明确：
  - `reports/training/streaming_student_loop_timingfocus6warm_baseline18_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_round1_1.step18.pt`
- 但它还没有足够强到替换 `baseline24`
- 更准确的主线状态应是：
  - packet-facing reference 仍是 `vuvbalancedgate24`
  - warm-start next-best candidate 改为 `warm6_18.step18`
- 下一步如果继续做实验，不应再盲试更多 loss 权重，而应围绕这个 candidate 做更窄的 downstream-facing 校准或 checkpoint 选择策略
