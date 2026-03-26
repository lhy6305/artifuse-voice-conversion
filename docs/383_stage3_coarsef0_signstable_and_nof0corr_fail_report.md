# 383 Stage3 coarse F0 signstable and nof0corr fail report

## 本轮目的
- 在 `coarse_f0_state` 首次把 `F0 proxy` 从负相关翻正之后，
  先排掉两条最容易误入的小分支：
  - `nof0corr`：关掉 `log_f0_correction`，强迫 `coarse_log_f0` 独自扛住方向
  - `signstable`：继续给 `coarse_log_f0` 叠相关性型 loss

## 对照对象
- baseline：
  - `reports/training/streaming_student_loop_controlfamily_coarsef012_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef012_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef012_round1_1/streaming_student_downstream_control_packet.json`
- nof0corr：
  - `reports/training/streaming_student_loop_controlfamily_nof0corr12_round1_1/logs/streaming_student_stage_loop_controlfamily_nof0corr12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_nof0corr12_round1_1/streaming_student_downstream_control_packet.json`
- signstable：
  - `reports/training/streaming_student_loop_controlfamily_coarsef0sign12_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef0sign12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef0sign12_round1_1/streaming_student_downstream_control_packet.json`

## 结果

### 1. `nof0corr` 证明 correction 不是主病因，反而是当前必要补偿项
- step12 validation：
  - baseline：
    - `loss_total = 1.558948`
    - `loss_total_semantic_disabled_reference = 1.439009`
  - nof0corr：
    - `loss_total = 1.591727`
    - `loss_total_semantic_disabled_reference = 1.471673`
- packet：
  - baseline `F0 proxy corr`：
    - `0.297515 / 0.071034 / 0.360725`
  - nof0corr `F0 proxy corr`：
    - `-0.435446 / -0.203175 / -0.537061`
- 结论：
  - 关掉 correction 以后，
    `F0` 直接退回负相关
  - 所以当前不能把 correction 当作主要病因

### 2. `signstable` 这版相关性 loss 也没有打到点
- step12 validation：
  - signstable：
    - `loss_total = 1.619039`
    - `loss_total_semantic_disabled_reference = 1.499102`
- packet：
  - signstable `F0 proxy corr`：
    - `-0.390018 / -0.183692 / -0.522718`
- 对 `chapter3_3_firefly_162` 的 `.pt` 诊断：
  - baseline：
    - `coarse_log_f0_corr = -0.338234`
    - `log_f0_correction_corr = 0.516655`
    - `f0_log_proxy_corr = 0.400702`
  - signstable：
    - `coarse_log_f0_corr = -0.550337`
    - `log_f0_correction_corr = 0.514222`
    - `f0_log_proxy_corr = -0.195866`
- 结论：
  - 这版相关性 loss 没有把 `coarse_log_f0` 拉正，
    反而把它推得更负
  - correction 仍在做正向补偿，
    但已经补不过来

## 判断
- `nof0corr` 应正式停线：
  - 不能再用“强迫 coarse 独扛方向”这种方式继续试
- `signstable` 这版相关性 loss 也应正式停线：
  - 不能再继续扫 `teacher_coarse_f0_correlation` 小权重

## 当前含义
- 到这里可以更硬地写死：
  - 当前阶段的关键不是“去掉 correction”
  - 也不是“再叠一个相关性 loss”
  - 真正留下来的有效信号，
    仍只有 `coarse_f0_state` 那条最直接的 voiced-frame state supervision

## 下一步
- 不再继续：
  - `nof0corr`
  - `teacher_coarse_f0_correlation`
  - 这两条线上的小权重或小参数化微调
- 下一步只保留：
  - `coarse_f0_state` 主线是否能在更长 horizon 下把 `coarse_log_f0` 本体真正翻正
