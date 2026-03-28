# 453 Stage3 warm6 dense checkpoint packet-aware selection report

## 结论
- 对 `warm6_18` 做密集 checkpoint 扫描后，新的 packet-aware 最优点不是 `step18`，而是 `step15`。
- `step18` 仍然是 validation 最优点：
  - `loss_total = 0.716152`
- 但 `step15` 在 packet-facing 平衡性上更好：
  - readiness summary 与 `step18` 同级：
    - `f0=0 / vuv=1 / aper=3 / energy=2 / all_records_auto_reject=true`
  - 三条代表记录中，`step15` 相比 `step18` 在 `vuv_reference_mae`、`aper_calibrated_reference_mae` 上更稳，整体更接近 `baseline24`
- 因此当前更准确的主线状态应是：
  - validation-only best checkpoint：`warm6_18.step18`
  - packet-aware best checkpoint：`warm6_18.step15`

## 试验设置
- 轨迹：
  - `timingfocus6 -> baseline18`
- 新扫描资产：
  - `reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/`
- 配置：
  - `validation_interval = 3`
  - `checkpoint_interval = 3`
- 导出的关键 packet：
  - `step12`
  - `step15`
  - `step18`

## A. validation 轨迹
- `step3`
  - `loss_total = 1.832883`
  - `loss_total_semantic_disabled_reference = 1.691641`
- `step6`
  - `loss_total = 1.292301`
  - `loss_total_semantic_disabled_reference = 1.171323`
- `step9`
  - `loss_total = 0.990997`
  - `loss_total_semantic_disabled_reference = 0.884989`
- `step12`
  - `loss_total = 0.849004`
  - `loss_total_semantic_disabled_reference = 0.753998`
  - `loss_teacher_event = 0.370446`
  - `loss_teacher_event_prior = 0.411357`
- `step15`
  - `loss_total = 0.778303`
  - `loss_total_semantic_disabled_reference = 0.688556`
  - `loss_teacher_event = 0.343485`
  - `loss_teacher_event_prior = 0.391609`
- `step18`
  - `loss_total = 0.716152`
  - `loss_total_semantic_disabled_reference = 0.630345`
  - `loss_teacher_event = 0.323067`
  - `loss_teacher_event_prior = 0.381626`

## B. packet 对比

### readiness summary
- baseline24
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- warm6 step12
  - `f0=0 / vuv=1 / aper=3 / energy=1 / all_records_auto_reject=true`
- warm6 step15
  - `f0=0 / vuv=1 / aper=3 / energy=2 / all_records_auto_reject=true`
- warm6 step18
  - `f0=0 / vuv=1 / aper=3 / energy=2 / all_records_auto_reject=true`

### 代表记录
- `target::chapter3_3_firefly_162`
  - baseline24
    - `vuv_reference_mae = 0.107152`
    - `f0_proxy_reference_corr = 0.495445`
    - `f0_calibrated_log2_mae = 0.17472`
    - `aper_calibrated_reference_mae = 0.095282`
  - step12
    - `0.115915 / 0.429911 / 0.185516 / 0.093152`
  - step15
    - `0.10272 / 0.475353 / 0.177929 / 0.095828`
  - step18
    - `0.107733 / 0.514897 / 0.171179 / 0.093091`
- `target::chapter3_3_firefly_138`
  - baseline24
    - `0.207186 / 0.187293 / 0.431756 / 0.137007`
  - step12
    - `0.22176 / 0.153672 / 0.431375 / 0.138684`
  - step15
    - `0.201397 / 0.177461 / 0.4318 / 0.137165`
  - step18
    - `0.220604 / 0.199807 / 0.432085 / 0.13834`
- `target::chapter3_4_firefly_106`
  - baseline24
    - `0.255081 / 0.608869 / 0.370633 / 0.12198`
  - step12
    - `0.263216 / 0.549034 / 0.409214 / 0.122934`
  - step15
    - `0.244014 / 0.59715 / 0.379002 / 0.122349`
  - step18
    - `0.249854 / 0.62316 / 0.358203 / 0.123861`

## C. `e_evt` 前 8 维观察
- `target::chapter3_4_firefly_106`
- step12
  - `[0.144383, 0.146981, 0.184824, 0.775608, 0.358936, 0.144627, 0.19441, 0.209468]`
- step15
  - `[0.103543, 0.113716, 0.143632, 0.822438, 0.380142, 0.10174, 0.142074, 0.197773]`
- step18
  - `[0.085242, 0.092664, 0.114124, 0.8576, 0.433953, 0.078345, 0.102149, 0.178756]`

## 判断
- 从 `step12 -> step18`：
  - validation 持续改善
  - 但 packet-facing 几何逐步回弹向更高 `dim3 / dim4`
  - `step18` 在 validation 上最强，但不再是 packet 最平衡点
- `step15` 是更合理的折中：
  - 比 `step12` validation 明显更强
  - 比 `step18` packet 更接近 baseline24
  - 尤其 `target::chapter3_3_firefly_138` 与 `target::chapter3_4_firefly_106` 上更稳

## 最终判断
- 当前主线候选更新为：
  - packet-aware next-best candidate：
    - `reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt`
- 当前 packet-facing reference 仍保持：
  - `vuvbalancedgate24`
- 如果继续推进主线，不应再扩 loss 权重搜索，而应围绕 `warm6_18.step15` 做更窄的 downstream-facing 校准或 handoff 前筛查
