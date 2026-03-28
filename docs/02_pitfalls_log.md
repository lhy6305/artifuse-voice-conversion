# 开发踩坑记录

## 文档定位
- 本文档只保留当前阶段仍然高频、仍然会误导决策的活跃坑点。
- 历史长版快照已归档：
  - `docs/archive/02_pitfalls_log_snapshot_20260326.md`
  - `docs/archive/02_pitfalls_log_snapshot_20260328.md`
- 新坑点若只是某一轮实验的局部细节，应优先写入对应编号报告；只有会持续影响后续判断的，才进入这里。

## 当前高优先级坑点
### 1. 不能把 Stage3 正向直接外推成当前旧 Stage5 route 也值得重跑
- Stage3 当前最有信息量的层仍是 generation-side。
- 旧 `Stage5 no-res downstream` 已正式停线，不再作为默认回流路线。

### 2. 不能把旧 Stage5 route 停线误写成停止 Stage5 fail-fast
- 停止的是当前默认旧 route，不是停止一切 Stage5 验证。
- 只有真正不同的 handoff family，才值得继续做新的 Stage5 fail-fast。

### 3. contract 接通、summary 有字段，不等于实验已经有效
- 先确认参数和 metadata 是否真实透传到底。
- 解释结果前必须核对最终 package / dataset index / summary。

### 4. machine gate 只能做 negative gate，不能证明成功
- `review_required` 或“没被 auto reject”都不等于已经成功。
- machine gate 只负责自动否定，不负责证明路线成立。

### 5. 人工听审一旦确认 buzz，就必须停掉同层微调线
- 纯 buzz / pure fuzz / 无人声结构不能靠继续扫小参数解决。
- 已被人工定性为错误解收敛的同层路线应立即停线。

### 6. hidden / fused-hidden imitation loss 自己下降，不等于主线更好
- 不能只看局部 imitation 指标下降。
- 必须同时检查 `loss_total`、`loss_total_semantic_disabled_reference`、`loss_teacher_event`、`loss_teacher_event_prior`。

### 7. paired source-target 不能先验当作可直接逐帧监督
- source waveform 与 target teacher frame 不天然对齐。
- 没有 frame bridge / alignment contract 前，不开 paired Stage3 训练。

### 8. 新语义资产必须先完成 metadata / package / index plumbing，再谈 consumer 训练
- plumbing 不清楚时，失败后无法区分接线问题和模型问题。
- 先接 metadata，再做最小 consumer / supervision 验证。

### 9. `student_control_packet_v1` 不能误写成已完成的 Stage5-ready named-control contract
- 当前只有 `e_evt / z_art` 可以按 ready 口径对待。
- `F0 / vuv / aper / E` 仍是 proxy/control status，不能误写成 handoff-ready contract。

### 10. cheap screen 的“基本持平”不能被拔高成“已经值得开新 Stage5 route”
- packet ready 和 loss 改善不等于承接证据已经足够硬。
- 先做 packet/control calibration 与 readiness gate，再决定是否进入新的 Stage5 adapter。

### 11. 不能让 `skip_existing` 的静默复用掩盖真实产物变化
- formal split、packet、audio、checkpoint、calibration、semantic/timing/parity sidecar 都可能受到旧产物复用污染。
- 任何 reuse 都必须先核对身份指纹，不能把旧结果当成本轮新结果。

### 12. 详细实验追记不应再回流进 `01/02`
- `01/02` 只保留持续影响后续判断的索引结论。
- 详细历史继续放在 `docs/archive/` 与对应编号报告。

## 当前维护规则
- 新增坑点前先判断它是否会持续影响未来多轮决策。
- 若只是局部实验结论，写入对应编号报告，不进入本文档。
- 若本文档再次显著膨胀，继续做快照归档，不回到单文件堆历史的模式。

## 关键参考报告
- `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
- `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
- `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
- `docs/374_stage3_student_control_packet_readiness_gate_report.md`
- `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
- `docs/447_repo_health_and_compliance_audit_20260328.md`
