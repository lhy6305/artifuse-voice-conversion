# 459 Stage3 target-blend early-stop and checkpoint-average probe report

## 结论
- `targetblend` correction 路径已经可以整体止损：
  - `step3` packet 不是“更早截停的更优点”
  - 它会直接把 `vuv / energy` 一起拉崩
  - 所以这条线不存在值得继续追的 early-stop 解
- `baseline24 + warm6.step15` 的 checkpoint averaging 出现了一个新的 mixed signal：
  - Stage3 full-validation 明显优于两端
  - packet 也比 `warm6.step15` 更均衡
  - 但接到 Stage5 fail-fast handoff 后，仍然是 `3/3 auto_reject_obvious_buzz`
- 因此本轮主线状态仍不更新：
  - packet-facing reference 仍是 `vuvbalancedgate24`
  - packet-aware next-best candidate 仍保留 `warm6_18.step15`

## 代码修补
- 修了 averaged checkpoint 的 Windows 文件名问题：
  - `src/v5vc/checkpoint_average.py`
    - averaged checkpoint 的 `experiment_id` 不再写成带 `:` 的 `averaged::...`
  - `src/v5vc/streaming_student/checkpoint_eval_entry.py`
    - checkpoint eval 落盘前会清洗非法文件名字符
- 背景：
  - 原先 averaged checkpoint 的 `experiment_id = averaged::...`
  - `evaluate-streaming-student-checkpoint` 会直接拿它拼输出文件名
  - 在 Windows 上会因 `:` 报错

## A. `targetblend.step3` early-stop 检查

### 对象
- 训练轨迹：
  - `reports/training/streaming_student_loop_vuvtargetblend_baseline24corr6_denseckpt_round1_1/`
- 新导 packet：
  - `reports/runtime/streaming_student_downstream_control_packet_vuvtargetblend_baseline24corr6_step3_round1_1/`

### readiness summary
- baseline24
  - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
- targetblend step3
  - `0 / 0 / 3 / 1 / true`
- targetblend step6
  - `0 / 1 / 3 / 2 / true`

### 三记录平均
- baseline24
  - `avg_vuv_mae = 0.189806`
  - `avg_f0_corr = 0.430536`
  - `avg_f0_mae = 0.325703`
  - `avg_aper_mae = 0.11809`
  - `avg_energy_mae = 0.108172`
- targetblend step3
  - `0.416317 / 0.360246 / 0.349258 / 0.143292 / 0.210523`
- targetblend step6
  - `0.175157 / 0.430034 / 0.327024 / 0.136656 / 0.132959`

### 判断
- `step3` 的真实行为是：
  - `vuv` 显著恶化
  - `energy` 大幅恶化
  - `F0` 也回退
- 所以这不是“只需更早截停”：
  - `targetblend` correction 至少要到 `step6` 附近才回到可比较区间
  - 但 `step6` 依然不是主线解

## B. `baseline24 + warm6.step15` checkpoint averaging

### 产物
- averaged checkpoint：
  - `reports/eval/streaming_student_checkpoint_average_baseline24_warm6step15_round1_2/streaming_student_stage_avg_baseline24_warm6step15_round1_2.pt`
- checkpoint eval：
  - `reports/eval/streaming_student_checkpoint_eval_avg_baseline24_warm6step15_round1_2/averaged__streaming_student_stage_avg_baseline24_warm6step15_round1_2.checkpoint_eval.json`
- packet：
  - `reports/runtime/streaming_student_downstream_control_packet_avg_baseline24_warm6step15_round1_2/`

### Stage3 full-validation
- baseline24
  - `loss_total = 0.919927`
  - `loss_total_semantic_disabled_reference = 0.832382`
- warm6 step15
  - `loss_total = 0.778303`
  - `loss_total_semantic_disabled_reference = 0.688556`
- averaged
  - `loss_total = 0.756182`
  - `loss_total_semantic_disabled_reference = 0.668724`
- 判断：
  - averaged 在 teacher-supervised validation 上强于两端

### packet cheap screen
- readiness summary
  - baseline24
    - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
  - warm6 step15
    - `0 / 1 / 3 / 2 / true`
  - averaged
    - `0 / 1 / 3 / 2 / true`
- 三记录平均
  - baseline24
    - `0.189806 / 0.430536 / 0.325703 / 0.11809 / 0.108172`
  - warm6 step15
    - `0.18271 / 0.416655 / 0.329577 / 0.118447 / 0.143582`
  - averaged
    - `0.186788 / 0.424308 / 0.327476 / 0.118243 / 0.129393`
- 判断：
  - averaged 没有追平 baseline24 的 `energy_ready_count = 3`
  - 但它相对 `warm6.step15` 更均衡：
    - `energy` 明显回拉
    - `aper` 更接近 baseline24
    - `F0` 也略好于 warm6.step15

## C. Stage5 fail-fast handoff on averaged checkpoint

### 产物
- synthetic Stage5 dataset：
  - `reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/`
- handoff probe：
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/`
- Stage5 checkpoint family：
  - 与 454 相同：
    - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - `selection_target = best_validation`

### `decoded_post_ola_gate` 聚合对比
- baseline24
  - `auto_reject = 3/3`
  - `centroid = 10171.926`
  - `high_band = 0.752118`
  - `template_cos = 0.942398`
  - `rms_corr = 0.893369`
- warm6 step15
  - `auto_reject = 3/3`
  - `centroid = 10168.383`
  - `high_band = 0.752909`
  - `template_cos = 0.945929`
  - `rms_corr = 0.91044`
- averaged
  - `auto_reject = 3/3`
  - `centroid = 10169.897`
  - `high_band = 0.752179`
  - `template_cos = 0.943517`
  - `rms_corr = 0.900798`

### hidden aggregate
- `decoder_hidden_template_cosine_mean`
  - baseline24: `0.961636`
  - warm6 step15: `0.965892`
  - averaged: `0.963773`

### 判断
- averaged 的 Stage5 行为正好落在 baseline24 和 warm6.step15 中间：
  - `rms_corr` 比 baseline24 高
  - `template_cos` 比 warm6.step15 低
  - `high_band` 也接近 baseline24
- 但最重要的结论没有变：
  - 它仍然是 `3/3 auto_reject_obvious_buzz`
  - 仍然属于同一个 Stage5 template-collapse / harsh-buzz 失败族

## 最终判断
- 当前可便宜验证的两条线都已进一步收口：
  - `targetblend correction` 不存在可用 early-stop
  - `baseline24 + warm6.step15 averaging` 虽然是更好的 Stage3 折中，但还不够打开 Stage5
- 因此本轮主线状态保持不变：
  - packet-facing reference：`vuvbalancedgate24`
  - packet-aware next-best candidate：`warm6_18.step15`
