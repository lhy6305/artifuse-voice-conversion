# 374 Stage3 Student-Control Packet Readiness Gate Report

## 结论
- 我把 `student_control_packet` 的 named-control readiness 做成了显式 negative gate。
- 这道 gate 的定位和之前的 buzz gate 一样：
  - 只负责自动否定“显然还不够格的 handoff packet”
  - 不负责证明“已经可以开新 Stage5 route”
- 当前 `directional` best checkpoint 的结论是否定：
  - `e_evt / z_art` 可以保留为 `review_required`
  - 但 `F0 / vuv / aper / E` 四条全部 `auto_reject_not_ready`
  - summary 为 `all_records_auto_reject = true`

## 本轮改动
- 文件：
  - `src/v5vc/streaming_student/downstream_control_packet.py`
- 新增：
  - `stage3_student_control_readiness_gate_v1`
  - record-level `named_control_readiness`
  - summary-level `named_control_readiness_summary`
- 当前 gate 规则是保守的 negative gate only：
  - `F0`
    - `reference_voiced_frame_count >= 32`
    - `f0_proxy_reference_corr >= 0.75`
    - `f0_calibrated_log2_mae <= 0.2`
  - `vuv`
    - `vuv_reference_mae <= 0.18`
  - `aper`
    - `aper_reference_mae <= 0.3`
  - `energy`
    - `energy_stage5_norm_reference_mae <= 0.15`
- 这不是“成功阈值”，而是“显然未就绪阈值”。

## 验证
- 使用仓库解释器：
  - `.\python.exe manage.py export-streaming-student-downstream-control-packet ...`
- 产物：
  - `reports/runtime/streaming_student_downstream_control_packet_directional_readinessgate_round1_1/streaming_student_downstream_control_packet.json`

## 结果
- summary：
  - `packet_ready_count = 2`
  - `e_evt_ready_count = 2`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
  - `auto_reject_count = 2`
  - `all_records_auto_reject = true`

### 1. `target::chapter3_3_firefly_162`
- `f0_proxy_reference_corr = 0.535348`
- `f0_calibrated_log2_mae = 0.170376`
- `vuv_reference_mae = 0.247564`
- `aper_reference_mae = 0.503181`
- `energy_stage5_norm_reference_mae = 0.242981`
- 结果：
  - `f0_status = auto_reject_not_ready`
  - `vuv_status = auto_reject_not_ready`
  - `aper_status = auto_reject_not_ready`
  - `energy_status = auto_reject_not_ready`

### 2. `target::chapter3_4_firefly_106`
- `f0_proxy_reference_corr = 0.644668`
- `f0_calibrated_log2_mae = 0.342344`
- `vuv_reference_mae = 0.279193`
- `aper_reference_mae = 0.427093`
- `energy_stage5_norm_reference_mae = 0.182307`
- 结果：
  - `f0_status = auto_reject_not_ready`
  - `vuv_status = auto_reject_not_ready`
  - `aper_status = auto_reject_not_ready`
  - `energy_status = auto_reject_not_ready`

## 判断
- 当前最重要的不是“哪个 control 稍微好一点”，而是：
  - 新 gate 已经明确说明
  - 这条 packet 还不具备新的 Stage5 handoff 基础
- 这也把主线收得更硬：
  - 不再靠“packet 已导出”“cheap screen 没退化”去讨论是否可以开新 Stage5 route
  - 现在必须先过 named-control readiness negative gate

## 结论口径
- 当前可以保留的说法：
  - `e_evt` ready
  - `z_art` ready
- 当前不能保留的说法：
  - `F0 / vuv / aper / E` 已接近 Stage5-ready
  - 当前 packet 已值得进入新 adapter 训练

## 下一步
- 下一步不再是 Stage5 adapter/scaffold smoke。
- 更合理的是继续：
  - `target-state generation / contract completion`
  - 优先修最弱的 named controls
  - 在新的 gate 通过前，不开新的 handoff 训练预算
