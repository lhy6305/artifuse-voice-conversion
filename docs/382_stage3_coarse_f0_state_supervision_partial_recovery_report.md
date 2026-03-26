# 382 Stage3 coarse F0 state supervision partial recovery report

## 本轮目的
- 针对上一轮已确认的病灶：
  - `F0` 反号的主病因不在 correction head
  - 而在更上游的 `coarse_log_f0`
- 这轮不再改 student-side branch 结构，
  只验证：
  - 直接给 `coarse_log_f0` 增加 voiced-frame target supervision，
    能否把当前 `F0` handoff 从“稳定负相关”拉回到更接近可用的状态

## 改动
- `src/v5vc/streaming_student/losses.py`
  - 新增 loss key：
    - `teacher_coarse_f0_state`
  - 新增指标：
    - `loss_teacher_coarse_f0_state`
  - 监督目标：
    - `outputs["coarse_log_f0"]`
    - 对齐 `log2(target_f0_hz)`
    - 仅在 voiced target frames 上生效
- 新 override：
  - `configs/streaming_student_loss_weights_coarse_f0_state_warmup_v1.json`
  - 本轮只试单一候选：
    - `teacher_coarse_f0_state = 0.05`
    - `teacher_f0_state = 0.02`
    - 二者都做 `6-step warmup`

## 验证范围
- 使用仓库解释器：
  - `python.exe`
- 完成：
  - `py_compile`
  - 1-step smoke
  - 严格可比 `12-step full-validation`
  - `student_control_packet` export
  - `coarse / correction / proxy` 相关性对照

## 对照对象
- baseline：
  - `reports/training/streaming_student_loop_controlfamily12_round1_1/logs/streaming_student_stage_loop_controlfamily12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily12_round1_1/streaming_student_downstream_control_packet.json`
- candidate：
  - `reports/training/streaming_student_loop_controlfamily_coarsef012_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef012_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef012_round1_1/streaming_student_downstream_control_packet.json`

## 结果

### 1. Stage3 主指标略变差，不适合直接升格为新 reference
- baseline step12：
  - `loss_total = 1.545674`
  - `loss_total_semantic_disabled_reference = 1.425769`
- candidate step12：
  - `loss_total = 1.558948`
  - `loss_total_semantic_disabled_reference = 1.439009`
- 同时：
  - `loss_teacher_event = 0.441407 -> 0.441284`
  - `loss_teacher_event_prior = 0.511271 -> 0.510728`
- 判断：
  - 主指标基本持平但略差
  - 这条线当前不能直接升格为新的 Stage3 reference

### 2. `coarse_f0_state` 本地监督确实生效
- validation step12：
  - `loss_teacher_coarse_f0_state = 0.351731`
  - `loss_teacher_f0_state = 0.357171`
- 说明：
  - 新监督不是空转
  - 它确实在改写 F0 这条链

### 3. 关键新信号：`F0 proxy` 已从稳定负相关翻到正相关
- baseline：
  - `target::chapter3_3_firefly_162`
    - `proxy_corr = -0.525194`
  - `target::chapter3_3_firefly_138`
    - `proxy_corr = -0.203372`
  - `target::chapter3_4_firefly_106`
    - `proxy_corr = -0.63891`
- candidate：
  - `target::chapter3_3_firefly_162`
    - `proxy_corr = 0.297515`
  - `target::chapter3_3_firefly_138`
    - `proxy_corr = 0.071034`
  - `target::chapter3_4_firefly_106`
    - `proxy_corr = 0.360725`
- 判断：
  - 这是当前 `named-control handoff` 线上第一次看到
    `F0 proxy` 从全负翻到全正
  - 说明“sign 修复方向”终于打中了问题层级

### 4. 但 `coarse_log_f0` 本体仍未翻正
- candidate：
  - `target::chapter3_3_firefly_162`
    - `coarse_corr = -0.50578`
    - `corr_corr = 0.470287`
  - `target::chapter3_4_firefly_106`
    - `coarse_corr = -0.598053`
    - `corr_corr = 0.582866`
- 说明：
  - 这次把 `proxy` 拉回正相关的，
    主要还是更强的 correction 补偿
  - `coarse_log_f0` 本体仍没有真正翻正

### 5. readiness gate 仍完全不开
- summary 仍是：
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
  - `all_records_auto_reject = true`
- `F0` 仍不过门的直接原因是：
  - 虽然相关性已翻正
  - 但还没达到 gate 的 `0.75`
  - 且 `calibrated_log2_mae` 也仍偏高
- 同时其它 named controls 仍未同步改善到可放行

## 判断
- 这条 `coarse_f0_state supervision` 线不能直接判成功。
- 但它也不是普通负结果。
- 当前更准确的判断是：
  - 它首次证明了 `F0 sign repair` 是可以在现有 Stage3 contract 内被打中的
  - 但当前这版只是“部分恢复”，还不足以打开 handoff gate

## 当前含义
- 不应把这轮写成：
  - “还是没用”
- 更准确的写法应是：
  - Stage3 主指标略差
  - 但 `F0 proxy` 已从负相关翻正
  - 因此当前最该继续追的，
    不再是 student-side branch family，
    而是更直接的
    `coarse_log_f0 sign-stable target / parameterization`

## 下一步
- 不开新的 Stage5 route。
- 不回头扫：
  - correction family 层数
  - `vuv / aper / energy` 小修
- 下一条主线应是：
  - 围绕 `coarse_log_f0` 本体做更强的
    `sign-stable supervision / parameterization / target contract`
  - 目标不是再让 correction 去补，
    而是让 `coarse_log_f0` 自己翻正。
