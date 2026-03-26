# 385 Stage3 named-control calibrated audit and bottleneck relocalization report

## 本轮目的
- 在 `coarse_f0_state` 已经把 `coarse_log_f0` 本体翻成正相关之后，
  先回答一个比继续开训练更值钱的问题：
  - 剩余 named controls 到底是“模型没学到”，
    还是“只是 contract/audit 还没做校准”

## 改动
- `src/v5vc/streaming_student/downstream_control_packet.py`
  - 新增 `aper / energy` 的 analysis-only affine-calibrated audit view
  - packet summary 新增：
    - `aper_calibrated_reference_mae`
    - `energy_stage5_norm_calibrated_reference_mae`
  - readiness gate 对 `aper / energy` 改为优先使用 calibrated audit MAE
  - 保持边界不变：
    - 这只是 audit aid
    - 不是 deployment-ready control contract

## 对照对象
- baseline：
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef048_round1_2/streaming_student_downstream_control_packet.json`
- mixed completion candidate：
  - `reports/training/streaming_student_loop_namedcontrolcompletion24_round1_1/logs/streaming_student_stage_loop_namedcontrolcompletion24_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_namedcontrolcompletion24_round1_2/streaming_student_downstream_control_packet.json`

## 结果

### 1. calibrated audit 后，`aper` 基本不是主瓶颈
- baseline calibrated packet：
  - `aper_ready_count = 3`
- 三条样本：
  - `0.093271 / 0.135341 / 0.119581`
  - 全部低于 gate `0.3`
- 结论：
  - 当前 `aper` 的大部分问题更像坐标/尺度没对齐，
    不是“完全没学到”

### 2. `energy` 也不是主病灶，只剩个别长样本
- baseline calibrated packet：
  - `energy_ready_count = 2`
- 三条样本：
  - `0.104531 / 0.138516 / 0.178734`
- 结论：
  - `energy` 在前两条样本上已经可过门
  - 只剩 `chapter3_4_firefly_106` 这一条长样本仍超阈

### 3. 瓶颈被重新定位成：`vuv`，其次才是 `F0`
- baseline calibrated packet：
  - `vuv_ready_count = 1`
  - `f0_ready_count = 0`
- 当前更准确的瓶颈排序应写成：
  - `vuv`
  - `F0`
  - `energy`
  - `aper`

### 4. mixed named-control completion 候选并不值得继续
- candidate step24 validation：
  - `loss_total = 0.960984`
  - `loss_total_semantic_disabled_reference = 0.873126`
- baseline `coarsef024`：
  - `loss_total = 0.937981`
  - `loss_total_semantic_disabled_reference = 0.8501`
- calibrated packet 对照：
  - baseline：
    - `f0_ready_count = 0`
    - `vuv_ready_count = 0`
    - `aper_ready_count = 3`
    - `energy_ready_count = 2`
  - candidate：
    - `f0_ready_count = 0`
    - `vuv_ready_count = 0`
    - `aper_ready_count = 3`
    - `energy_ready_count = 3`
- 结论：
  - mixed candidate 只在 `energy` 上多推进了 1 条
  - 但共享主指标更差
  - 不值得继续往这条混合 loss 线上追加 48-step

## 判断
- contract-side calibrated audit 这步应保留。
- 它把当前剩余问题从
  “named controls 整体都不行”
  收紧到了
  “真正没过门的是 `vuv`，其次才是 `F0`”
- 同时 mixed `named-control completion` loss route 应停线。

## 下一步
- 不再继续 mixed `vuv + aper + energy` state-loss 组合。
- 下一步只值得做：
  - `vuv` 单独 bottleneck 验证
  - 或更明确的 `vuv contract / representation` 路线
