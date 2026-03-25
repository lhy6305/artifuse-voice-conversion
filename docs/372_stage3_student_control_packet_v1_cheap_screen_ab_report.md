# 372. Stage3 `student_control_packet_v1` cheap screen A/B 报告

## 结论
- 我把 `student_control_packet_v1` 的 cheap screen 做成了严格可比 A/B：
  - baseline：
    `acoustic_contextual_event_bridge_v1`
  - candidate：
    `acoustic_directional_transition_bridge_v1`
- 结果是：
  - `directional` 在 Stage3 full-validation loss 上继续更好
  - 但在当前 proxy cheap screen 上，没有出现足够大的结构性跃迁
- 所以当前最合理的决策不是立刻开新的 `Stage5 student-control adapter`，而是：
  - 先把 `student_control_packet` 本身继续做实
  - 重点补齐 `F0 / aper / E` 的 control calibration / contract completion

## 一、为什么这轮要做 cheap screen A/B
- 上一轮已经确认：
  - `student_control_packet_v1` 可导出
  - `e_evt` 与 `z_art` 已能作为 named-control candidate 落盘
- 但是否值得开新的 Stage5 route，不能只看：
  - Stage3 loss 更低
  - packet 已 ready
- 还要看：
  - 在当前最便宜的结构代理层，
    `directional`
    是否真的比上一版
    `contextual`
    更接近 teacher proxy

## 二、本轮对照对象

### 1. directional candidate
- checkpoint：
  - `reports/training/streaming_student_loop_eevt_directional_fullval24_round1_1/checkpoints/streaming_student_stage_loop_eevt_directional_fullval24_round1_1.step24.pt`
- packet：
  - `reports/runtime/streaming_student_downstream_control_packet_directional_smoke_round1_1/streaming_student_downstream_control_packet.json`
- proxy bundle：
  - `reports/audio/streaming_student_proxy_audio_directional_smoke_round1_1/proxy_audio_export.json`

### 2. contextual baseline
- checkpoint：
  - `reports/training/streaming_student_loop_eevt_acousticcontext_fullval24_round1_1/checkpoints/streaming_student_stage_loop_eevt_acousticcontext_fullval24_round1_1.step24.pt`
- packet：
  - `reports/runtime/streaming_student_downstream_control_packet_acousticcontext_smoke_round1_1/streaming_student_downstream_control_packet.json`
- proxy bundle：
  - `reports/audio/streaming_student_proxy_audio_acousticcontext_smoke_round1_1/proxy_audio_export.json`

### 3. cheap screen compare summary
- 汇总：
  - `reports/audio/stage3_student_control_packet_cheap_screen_compare_round1_1.json`
- 采样 record：
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_4_firefly_106`

## 三、Stage3 主指标仍然支持 directional
- `contextual` full-validation step24：
  - `loss_total = 0.975202`
  - `loss_total_semantic_disabled_reference = 0.891887`
  - `loss_teacher_event = 0.417446`
  - `loss_teacher_event_prior = 0.505388`
- `directional` full-validation step24：
  - `loss_total = 0.947703`
  - `loss_total_semantic_disabled_reference = 0.867661`
  - `loss_teacher_event = 0.399819`
  - `loss_teacher_event_prior = 0.486579`
- 所以：
  - generation-side reference 仍应保持 `directional`

## 四、cheap screen 对比结果

### 1. 平均指标
- `directional - contextual`：
  - `rms_mae = -0.000032`
  - `rms_corr = -0.000698`
  - `delta_rms_corr = -0.000713`
  - `zcr_mae = -0.000045`
  - `zcr_corr = +0.008192`
  - `silence_iou = -0.000786`

### 2. 解释
- 这些差值整体都非常小，说明：
  - `directional` 并没有在 proxy cheap screen 上出现“明显高一档”的结构承接
- 更准确地说：
  - 它是 non-regressing
  - 但不是 strong handoff win

### 3. 这意味着什么
- 不能据此说：
  - `student_control_packet_v1`
    已经足以支撑新的 Stage5 adapter 立项
- 但也不能说：
  - 这条 handoff family 没价值
- 当前更合理的定性是：
  - packet v1 已经成立
  - cheap screen 没发现明显坏信号
  - 但 handoff gain 还不够硬，暂不足以直接打开新的下游训练预算

## 五、当前判断
1. `directional` 仍是新的 Stage3 reference。
2. `student_control_packet_v1` 也成立，且不是 metadata-only。
3. 但 cheap screen 只证明了：
   - 这条 route 没有明显退化
   - 还没有证明它已经足够强，值得立即进入新的 Stage5 adapter/scaffold。

## 六、下一步
1. 不直接开新的 `Stage5 student-control adapter`。
2. 下一步最值钱的是：
   - 继续做 `student_control_packet` 的 control calibration / contract completion
3. 当前最该补的是：
   - `F0`
   - `aper`
   - `E`
   这三条从 proxy/control status 向更完整 named control contract 的升级
4. 等这层更完整后，再重做 cheap screen；
   只有出现更明确的结构增益，才值得给它新的 Stage5 route。
