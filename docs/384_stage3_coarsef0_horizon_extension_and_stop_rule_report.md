# 384 Stage3 coarse F0 horizon extension and stop rule report

## 本轮目的
- 验证 `coarse_f0_state` 这条唯一仍有信息量的 F0 主线，
  到了更长 horizon 后到底会发生哪一种：
  - A. `F0` 相关性继续改善，并把 `coarse_log_f0` 本体翻正
  - B. 只是 12-step 偶然现象，随后回退
  - C. 虽然继续改善，但仍不足以打开 handoff gate

## 范围
- 严格可比 24-step：
  - baseline：
    - `reports/training/streaming_student_loop_controlfamily24_round1_1/logs/streaming_student_stage_loop_controlfamily24_round1_1.summary.json`
    - `reports/runtime/streaming_student_downstream_control_packet_controlfamily24_round1_1/streaming_student_downstream_control_packet.json`
  - candidate：
    - `reports/training/streaming_student_loop_controlfamily_coarsef024_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef024_round1_1.summary.json`
    - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef024_round1_1/streaming_student_downstream_control_packet.json`
- 候选继续延长到 48-step：
  - `reports/training/streaming_student_loop_controlfamily_coarsef048_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef048_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef048_round1_1/streaming_student_downstream_control_packet.json`

## 24-step 结果

### 1. 严格可比 24-step 下，candidate 总指标仍略差
- baseline step24：
  - `loss_total = 0.922773`
  - `loss_total_semantic_disabled_reference = 0.834857`
- candidate step24：
  - `loss_total = 0.937981`
  - `loss_total_semantic_disabled_reference = 0.8501`
- 结论：
  - 到 24-step 为止，
    `coarse_f0_state` 还不能作为 matched A/B 的新 Stage3 reference

### 2. 但 F0 主病灶已经不再是“本体反号”
- baseline packet `F0 proxy corr`：
  - `-0.511958 / -0.193931 / -0.624496`
- candidate packet `F0 proxy corr`：
  - `0.480252 / 0.173097 / 0.59623`
- 对 candidate 24-step `.pt` 的直接诊断：
  - `chapter3_3_firefly_162`
    - `coarse_log_f0_corr = 0.520743`
    - `log_f0_correction_corr = 0.524502`
    - `f0_log_proxy_corr = 0.521843`
  - `chapter3_3_firefly_138`
    - `coarse_log_f0_corr = 0.251993`
    - `log_f0_correction_corr = 0.252924`
    - `f0_log_proxy_corr = 0.252266`
  - `chapter3_4_firefly_106`
    - `coarse_log_f0_corr = 0.812337`
    - `log_f0_correction_corr = 0.818149`
    - `f0_log_proxy_corr = 0.814031`
- 结论：
  - 到 24-step，
    `coarse_log_f0` 本体已经在 3 个样本上全部翻成正相关
  - 所以 `F0 sign repair` 这个结构性问题，
    已经从“没修到”推进到“基本修到”

### 3. 但 handoff gate 仍没打开
- candidate 24-step packet：
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 2`
  - `all_records_auto_reject = true`
- 说明：
  - 问题已经不再只是 `F0` 反号
  - 而是多控制量合同仍未一起达到 handoff 要求

## 48-step 候选延长结果

### 1. 候选自己的 Stage3 数字继续明显改善
- candidate step24：
  - `loss_total = 0.937981`
  - `loss_total_semantic_disabled_reference = 0.8501`
- candidate step48：
  - `loss_total = 0.644372`
  - `loss_total_semantic_disabled_reference = 0.566819`
- 说明：
  - 这条线在更长 horizon 下不是崩掉，
    而是继续收敛

### 2. F0 继续改善，但 improvement 不足以打开 gate
- step48 packet `F0 proxy corr`：
  - `0.523969 / 0.202658 / 0.633974`
- 相比 step24：
  - `0.480252 / 0.173097 / 0.59623`
- 结论：
  - 相关性仍在缓慢上升
  - 但离 gate 的 `0.75` 仍明显不足，
    尤其是 `chapter3_3_firefly_138`

### 3. 其余 named controls 反而暴露出新的瓶颈
- step48 packet：
  - `f0_ready_count = 0`
  - `vuv_ready_count = 1`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
  - `all_records_auto_reject = true`
- 说明：
  - F0 在继续变好
  - 但 `vuv / aper / energy` 没有同步完成
  - 特别是 energy 相对 step24 没有保住

## stop rule 判断
- 本轮预设的 stop rule 是：
  - 如果 48-step 仍 `gate closed`
  - 且相关性没有出现足够大的新跃迁
  - 就停止继续在同一条 `F0 sign` 线上堆 horizon / loss
- 当前结果满足 stop 条件：
  - gate 仍完全不开
  - `F0` 只是在原有正相关基础上小幅继续上升
  - 新瓶颈已经转移到剩余 named controls 的合同完成度

## 最终判断
- `coarse_f0_state` 这条线不是失败实验。
- 它已经给出两个有效结论：
  - `coarse_log_f0` 本体可以被拉成正相关
  - 更长 horizon 确实能继续改善 F0
- 但它也已经给出明确边界：
  - 继续在同一条 `F0 sign repair` 线上叠 horizon / 小 loss，
    不能单独把 packet 推到 handoff-ready

## 下一步
- 不再继续：
  - `coarse_f0_state` 同层 horizon 追加
  - `teacher_coarse_f0_correlation`
  - `nof0corr`
  - 其它同层 `F0` 小参数化微调
- 下一步主线应改成：
  - 以当前 repaired `coarse_f0` 候选为 F0 参考
  - 转去剩余 named controls 的 contract completion
  - 重点是 `vuv / aper / energy`
  - 不再把问题继续表述成“F0 还没翻正”
