# 463 Stage5 input-family override probe report

## 结论
- 这轮把主线从“看 drift”推进到了“直接改 fixed Stage5 forward 真正消费的输入族”。
- 结果分三层：
  - `event_family=reference_mean / reference_affine_match` 都是明确 no-go，且比 base 更差。
  - `vuv=reference_mean`、`f0=reference_mean` 都没有打开 route，其中 `f0` 近乎中性，`vuv` 只提高了 `rms_corr` 但让 hidden/template 更差。
  - 最有价值的是 exact teacher counterpart family swap：
    - `acoustic_state_family -> teacher counterpart` 会把 `centroid / high_band / template / fused_hidden_template` 全部往 teacher 方向拉。
    - 在此基础上叠加 `eventzero`，能把 `template_cos` 进一步压到本轮最低。
    - 再叠 `aperzero`，则把 `rms_corr` 拉到本轮最高。
- 但所有路线仍然是 `3/3 auto_reject_obvious_buzz`。
- 所以当前最准确的判断更新为：
  - fixed Stage5 ckpt 确实对输入流形敏感，`student acoustic-state + event` 会把 collapse 推得更坏。
  - 但仅靠 inference-time family override，即便已经把 aggregate 指标拉到接近甚至优于 teacher counterpart，仍然打不开 route。
  - 这意味着下一步如果还要继续主线，不应再停留在“更多推理时输入替换”，而要转向：
    - Stage5 retrain / finetune on corrected manifold
    - 或更深层的 decoder/fusion attractor 机制修复

## 试验对象
- base student package:
  - `reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/streaming_student_stage5_dataset_index.json`
- teacher counterpart package:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_packages_teacher_validation3_counterpart_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- fixed Stage5 checkpoint family:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - `selection_target = best_validation`
- shared records:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

## A. reference-backed single-family overrides

### variant datasets
- `event_family=reference_mean`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_eventrefmean_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_eventrefmean_round1_1/stage5_waveform_handoff_probe.json`
- `event_family=reference_affine_match`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_eventaffine_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_eventaffine_round1_1/stage5_waveform_handoff_probe.json`
- `vuv=reference_mean`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_vuvrefmean_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_vuvrefmean_round1_1/stage5_waveform_handoff_probe.json`
- `f0=reference_mean`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_f0refmean_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_f0refmean_round1_1/stage5_waveform_handoff_probe.json`

### `decoded_post_ola_gate` aggregate
- base
  - `auto_reject = 3/3`
  - `centroid_gap = 9278.554688`
  - `high_band_gap = 0.712497`
  - `template_cos = 0.943517`
  - `adjacent_cos = 0.997297`
  - `rms_corr = 0.900798`
  - `fused_hidden_template = 0.963773`
  - `waveform_frames_template = 0.962746`
- `event_family=reference_mean`
  - `auto_reject = 3/3`
  - `centroid_gap = 9312.401367`
  - `high_band_gap = 0.719466`
  - `template_cos = 0.947940`
  - `rms_corr = 0.896501`
  - `fused_hidden_template = 0.964784`
  - `waveform_frames_template = 0.965418`
- `event_family=reference_affine_match`
  - `auto_reject = 3/3`
  - `centroid_gap = 9329.000977`
  - `high_band_gap = 0.719883`
  - `template_cos = 0.949933`
  - `rms_corr = 0.904643`
  - `fused_hidden_template = 0.966010`
  - `waveform_frames_template = 0.967210`
- `vuv=reference_mean`
  - `auto_reject = 3/3`
  - `centroid_gap = 9265.429688`
  - `high_band_gap = 0.713976`
  - `template_cos = 0.953158`
  - `rms_corr = 0.898089`
  - `fused_hidden_template = 0.970149`
  - `waveform_frames_template = 0.969091`
- `f0=reference_mean`
  - `auto_reject = 3/3`
  - `centroid_gap = 9275.393555`
  - `high_band_gap = 0.712093`
  - `template_cos = 0.943354`
  - `rms_corr = 0.900339`
  - `fused_hidden_template = 0.963299`
  - `waveform_frames_template = 0.962517`

### interpretation
- `event_family` 的全局 reference-backed replacement 不但没救，反而更坏。
  - 说明这里不是“把 student event 拉到 teacher global mean/std”就能复原的分布偏移。
  - 也说明 event 族高度依赖时序与 record-specific shape，不能被全局统计替代。
- `vuv` reference mean 也不是正解。
- `f0` reference mean 基本中性，只证明 coarse `f0` 单独不是当前最强 lever。

## B. exact teacher counterpart family swap

### variant datasets
- `eventswap`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_eventswap_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_eventswap_round1_1/stage5_waveform_handoff_probe.json`
- `vuvswap`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_vuvswap_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_vuvswap_round1_1/stage5_waveform_handoff_probe.json`
- `f0swap`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_f0swap_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_f0swap_round1_1/stage5_waveform_handoff_probe.json`
- `acousticstateswap`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_acousticstateswap_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_acousticstateswap_round1_1/stage5_waveform_handoff_probe.json`

### aggregate
- `eventswap`
  - `auto_reject = 3/3`
  - `centroid_gap = 9309.689453`
  - `high_band_gap = 0.718102`
  - `template_cos = 0.948796`
  - `rms_corr = 0.895695`
  - `fused_hidden_template = 0.966166`
- `vuvswap`
  - `auto_reject = 3/3`
  - `centroid_gap = 9284.949219`
  - `high_band_gap = 0.713039`
  - `template_cos = 0.943863`
  - `rms_corr = 0.915923`
  - `fused_hidden_template = 0.963162`
- `f0swap`
  - `auto_reject = 3/3`
  - `centroid_gap = 9276.845703`
  - `high_band_gap = 0.712296`
  - `template_cos = 0.943816`
  - `rms_corr = 0.899028`
  - `fused_hidden_template = 0.963106`
- `acousticstateswap`
  - `auto_reject = 3/3`
  - `centroid_gap = 9235.940430`
  - `high_band_gap = 0.709033`
  - `template_cos = 0.940647`
  - `rms_corr = 0.900905`
  - `fused_hidden_template = 0.957698`
  - `waveform_frames_template = 0.959608`
- teacher counterpart
  - `auto_reject = 3/3`
  - `centroid_gap = 9266.612305`
  - `high_band_gap = 0.713724`
  - `template_cos = 0.941868`
  - `rms_corr = 0.893252`
  - `fused_hidden_template = 0.957539`
  - `waveform_frames_template = 0.960643`

### interpretation
- `eventswap` 继续证明 event 族不是“直接换成 teacher 就会好”的简单问题，单换 event 仍更差。
- `vuvswap` 主要改善 envelope follow，但对 collapse 没什么帮助。
- `f0swap` 几乎中性。
- `acousticstateswap` 是本轮最重要的新信号：
  - 它明显降低了 `centroid/high_band/template`
  - 也把 `fused_hidden_template` 拉到了 teacher counterpart 附近
  - 说明真正能把 fixed ckpt 从更坏 attractor 往外拉的是整组 acoustic-state family，而不是单独 `f0` 或 `vuv`

## C. narrow combo follow-up

### variants
- `acousticstateswap + eventzero`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_acousticstateswap_eventzero_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_acousticstateswap_eventzero_round1_1/stage5_waveform_handoff_probe.json`
- `acousticstateswap + eventzero + aperzero`
  - dataset:
    - `reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_acousticstateswap_eventzero_aperzero_round1_1/streaming_student_stage5_dataset_index.json`
  - handoff:
    - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_acousticstateswap_eventzero_aperzero_round1_1/stage5_waveform_handoff_probe.json`

### aggregate
- `acousticstateswap + eventzero`
  - `auto_reject = 3/3`
  - `centroid_gap = 9116.155273`
  - `high_band_gap = 0.711012`
  - `template_cos = 0.936230`
  - `adjacent_cos = 0.997429`
  - `rms_corr = 0.909780`
  - `fused_hidden_template = 0.957994`
  - `waveform_frames_template = 0.958754`
- `acousticstateswap + eventzero + aperzero`
  - `auto_reject = 3/3`
  - `centroid_gap = 9098.527344`
  - `high_band_gap = 0.710473`
  - `template_cos = 0.940648`
  - `adjacent_cos = 0.997393`
  - `rms_corr = 0.938132`
  - `fused_hidden_template = 0.961777`
  - `waveform_frames_template = 0.961693`

### best-case read
- 如果优先看 collapse/template：
  - 最佳是 `acousticstateswap + eventzero`
  - 它把 `template_cos` 压到 `0.936230`
  - 比 base `0.943517` 明显更低
  - 也优于 teacher counterpart `0.941868`
- 如果优先看 envelope follow：
  - 最佳是 `acousticstateswap + eventzero + aperzero`
  - `rms_corr = 0.938132`
  - 远高于 base `0.900798`
  - 也高于 teacher counterpart `0.893252`

### record-level for `acousticstateswap + eventzero + aperzero`
- `target::chapter3_3_firefly_162`
  - `template = 0.951860`
  - `rms_corr = 0.936262`
  - `high_band_gap = 0.731730`
  - `centroid_gap = 9002.243365`
- `target::chapter3_3_firefly_138`
  - `template = 0.945598`
  - `rms_corr = 0.936041`
  - `high_band_gap = 0.689288`
  - `centroid_gap = 9026.142912`
- `target::chapter3_4_firefly_106`
  - `template = 0.924485`
  - `rms_corr = 0.942094`
  - `high_band_gap = 0.710402`
  - `centroid_gap = 9267.195354`

## 当前最准确的判断
- fixed Stage5 ckpt 的失败已经不能简单表述成“student packet 太差”。
- 这轮证明了：
  - 通过 input-family override，fixed ckpt 的 hidden geometry 和 waveform metrics 可以被明显推向更好的区域
  - 甚至某些 aggregate 指标已经优于 teacher counterpart
  - 但最终 `auto_reject_obvious_buzz` 仍然不松口
- 这意味着问题不是“还差一点点输入修正”。
- 更像是：
  - 当前 ckpt 自己就在一个错误 attractor 周围形成了宽容但失败的 basin
  - inference-time family surgery 只能在 basin 内移动位置，不能把 decode 拉出失败族

## 下一步
- 不建议继续扩更多 inference-time family overrides。
- 更合理的主线只剩两条：
  1. 以 `acousticstateswap + eventzero` 或 `acousticstateswap + eventzero + aperzero` 的方向，构建 corrected-manifold Stage5 package，然后做小规模 finetune / retrain
  2. 继续做更深层 decoder/fusion attractor probe，确认是否需要结构或损失上的约束，而不是继续手工替换输入族
