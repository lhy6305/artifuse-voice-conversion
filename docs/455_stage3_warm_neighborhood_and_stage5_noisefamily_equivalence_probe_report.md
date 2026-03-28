# 455 Stage3 warm neighborhood and Stage5 noise-family equivalence probe report

## 结论
- `legacy_event_probs` 不是当前 student -> Stage5 bridge 的真实自由度。
  - 在当前 packet 资产里，`legacy_event_probs` 与 `e_evt` 是逐元素完全相同的 `8D` 张量。
  - 因此切换 `noise_event_family = legacy_event_probs` 不会改变 synthetic Stage5 package，也不会改变 waveform handoff probe 结果。
- 新补的 warm-start 邻域里：
  - validation 最强的新轨迹是 `warm3_21.step21`
    - `loss_total = 0.692153`
    - `loss_total_semantic_disabled_reference = 0.606367`
  - 但 packet cheap screen 仍未打开新门：
    - 新候选都还是 `f0=0 / vuv=1 / aper=3 / energy=2 / all_records_auto_reject=true`
    - 仍然没有超过 `baseline24` 的 `energy_ready_count = 3`
- 我额外对最值得看的 `warm3_21.step18` 做了 Stage5 fail-fast handoff。
  - 结果仍然是 `3/3 auto_reject`
  - 没有比 `warm6_18.step15` 更好的 downstream 证据
- 所以当前主线状态不变：
  - packet-facing reference 仍为 `vuvbalancedgate24`
  - packet-aware next-best candidate 仍保留 `warm6_18.step15`

## A. `legacy_event_probs` 等价性检查
- 对象：
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate24_round1_1/records/target__chapter3_3_firefly_162.pt`
  - `reports/runtime/streaming_student_downstream_control_packet_timingfocus6warm_baseline18_step15_round1_1/records/target__chapter3_3_firefly_162.pt`
- 检查结果：
  - `legacy_event_probs.shape == e_evt.shape == (frames, 8)`
  - `max_abs_diff_all = 0.0`
  - `mean_abs_diff_all = 0.0`
- 进一步比较 synthetic Stage5 package：
  - `timingfocus6warm_baseline18_step15` 的 `e_evt`/`legacy_event_probs` 两套 package
  - `noise_branch_features` 逐元素完全一致：
    - `max_abs_diff noise_branch = 0.0`
    - `mean_abs_diff noise_branch = 0.0`

## B. `legacy_event_probs` handoff probe 结果
- 运行了四条 probe：
  - `baseline24 + e_evt`
  - `baseline24 + legacy_event_probs`
  - `warm6.step15 + e_evt`
  - `warm6.step15 + legacy_event_probs`
- 结果：
  - 所有 aggregate 和 record-level route 指标完全一致
  - 说明当前 Stage5 bridge 中切换 `noise_event_family` 只是标签变化，不是行为变化
- 结论：
  - 这条线已经证伪，不继续投入

## C. 新增 warm-start 邻域
- 为了获得 `step3/step9` 初始化点，先补跑：
  - `reports/training/streaming_student_loop_vuvbalancedgate_timingfocus12_denseckpt_round1_1/`
- 再补两条 24-step 等效邻域：
  - `warm3_21`
    - `timingfocus12.step3 -> baseline21`
    - 输出：
      - `reports/training/streaming_student_loop_timingfocus3warm_baseline21_denseckpt_round1_1/`
  - `warm9_15`
    - `timingfocus12.step9 -> baseline15`
    - 输出：
      - `reports/training/streaming_student_loop_timingfocus9warm_baseline15_denseckpt_round1_1/`

## D. validation 轨迹
- `warm3_21`
  - `step3`
    - `loss_total = 2.407759`
  - `step6`
    - `1.687846`
  - `step9`
    - `1.102678`
  - `step12`
    - `0.952405`
  - `step15`
    - `0.831918`
  - `step18`
    - `0.774062`
    - `loss_total_semantic_disabled_reference = 0.684734`
    - `loss_teacher_event = 0.338198`
    - `loss_teacher_event_prior = 0.394285`
  - `step21`
    - `0.692153`
    - `loss_total_semantic_disabled_reference = 0.606367`
    - `loss_teacher_event = 0.321692`
    - `loss_teacher_event_prior = 0.388329`
- `warm9_15`
  - `step3`
    - `loss_total = 1.649261`
  - `step6`
    - `1.281692`
  - `step9`
    - `0.94791`
  - `step12`
    - `0.843704`
  - `step15`
    - `0.772678`
    - `loss_total_semantic_disabled_reference = 0.683244`
    - `loss_teacher_event = 0.343782`
    - `loss_teacher_event_prior = 0.385714`

## E. packet cheap screen

### readiness summary
- baseline24
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- warm6 step15
  - `0 / 1 / 3 / 2 / true`
- warm3 step18
  - `0 / 1 / 3 / 2 / true`
- warm3 step21
  - `0 / 1 / 3 / 2 / true`
- warm9 step12
  - `0 / 1 / 3 / 2 / true`
- warm9 step15
  - `0 / 1 / 3 / 2 / true`

### 三记录平均
- baseline24
  - `avg_vuv_mae = 0.189806`
  - `avg_f0_corr = 0.430536`
  - `avg_f0_mae = 0.325703`
  - `avg_aper_mae = 0.11809`
  - `avg_energy_mae = 0.108172`
- warm6 step15
  - `0.18271 / 0.416655 / 0.329577 / 0.118447 / 0.143582`
- warm3 step18
  - `0.19049 / 0.437627 / 0.323438 / 0.116664 / 0.145751`
- warm3 step21
  - `0.210239 / 0.450965 / 0.319296 / 0.113728 / 0.137322`
- warm9 step12
  - `0.188312 / 0.389709 / 0.338318 / 0.121576 / 0.139089`
- warm9 step15
  - `0.193218 / 0.431649 / 0.325016 / 0.115945 / 0.140792`

## F. `warm3.step18` Stage5 fail-fast handoff
- synthetic dataset：
  - `reports/runtime/streaming_student_stage5_dataset_packages_timingfocus3warm_baseline21_step18_contractv2_normfix_validation3_round1_1/`
- handoff probe：
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_timingfocus3warm_baseline21_step18_contractv2_normfix_validation3_round1_1/`
- 结果：
  - `decoded_post_ola_gate auto_reject = 3/3`
  - `decoded_post_ola_gate centroid_hz = 10171.095`
  - `decoded_post_ola_gate high_band_energy_ratio = 0.752244`
  - `decoded_post_ola_gate template_cos = 0.949384`
  - `decoded_post_ola_gate rms_corr = 0.894813`
  - `decoder_hidden_template_cosine_mean = 0.970008`
- 相对 `warm6.step15`
  - `high_band_energy_ratio` 略低：
    - `0.752244 < 0.752909`
  - 但 `template_cos` 更高：
    - `0.949384 > 0.945929`
  - `rms_corr` 明显更差：
    - `0.894813 < 0.91044`
  - 仍然落在同一个 `auto_reject_obvious_buzz` 失败族

## 判断
- `warm3_21.step21`
  - 是目前 validation 最强的 24-step 等效 warm-start
  - 但 packet 退化到不值得直接接 Stage5
- `warm3_21.step18`
  - 是这条轨迹里更合理的 packet-facing 截停点
  - 但 handoff fail-fast 仍未优于 `warm6.step15`
- `warm9_15.step15`
  - validation 好于 `warm6.step15`
  - packet 只是另一种 tradeoff，并没有把 `energy_ready_count` 拉回 `3`

## 最终判断
- 当前没有新的候选能同时满足：
  - 比 `warm6.step15` 更强的 packet-aware 表现
  - 比 `warm6.step15` 更强的 Stage5 fail-fast 证据
- 因此主线不更新：
  - packet-facing reference 仍为 `vuvbalancedgate24`
  - packet-aware next-best candidate 仍为 `warm6_18.step15`
