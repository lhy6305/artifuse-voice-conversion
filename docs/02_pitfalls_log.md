# 开发踩坑记录

## 文档定位
- 本文档只保留当前阶段仍然高频、仍然会误导决策的“活跃坑点”。
- 历史长版快照已归档：
  - `docs/archive/02_pitfalls_log_snapshot_20260326.md`
- 新坑点若只是某一轮实验的局部细节，应优先写入对应编号报告；只有会持续影响后续判断的，才进入这里。

## 当前高优先级坑点

### 1. 不能把 Stage3 正向直接外推成当前旧 Stage5 route 也值得重跑
- 现象：
  - `teacher_e_evt` generation-side 在 Stage3 连续出现正向 A/B。
- 风险：
  - 很容易形成“上游又变好了，那旧 Stage5 no-res downstream 再试一次”的惯性。
- 正确处理：
  - 停止把新的上游 candidate 机械送回当前已判死的旧 Stage5 route。
  - 先把 Stage3 证据做硬，再决定新的 handoff layer。

### 2. 不能把“停止当前旧 Stage5 route”误写成“以后不再做任何 Stage5 验证”
- 现象：
  - 当前确实已经正式停止旧 `Stage5 no-res downstream` 作为默认承接层。
- 风险：
  - 这句话若写过头，会被误解成不再需要任何下游 fail-fast。
- 正确处理：
  - 停止的是旧 route，不是停止一切 Stage5 验证。
  - 若未来出现真正不同的 handoff layer / contract family，仍应做最小 fail-fast 验证。

### 3. 不能把 Stage5 当前问题简化成“它还只是在吃旧 heuristic 字段”
- 现象：
  - Stage5 已经接通过多条显式 `e_evt` 路线：
    - consumer-side
    - supervision-side
    - downstream contract
- 风险：
  - 若仍把失败原因写成“只是没接上新字段”，会误判问题层级。
- 正确处理：
  - 当前更准确的说法是：
    - 显式 `e_evt` 已接通过多条 route
    - 但当前承接方式仍不成立

### 4. contract 接通、summary 有字段，不等于实验已经有效
- 现象：
  - 新 loss / 新权重 / 新 contract 很容易在 CLI 或 package 层看似存在。
- 风险：
  - 参数可能没有沿真实调用链传到底，或只停在 metadata。
- 正确处理：
  - 解释结果前，必须核对最终 summary / dataset index / package summary。
  - 当前阶段禁止把“字段出现”当成“实验有效”的充分证据。

### 5. machine gate 只能做 negative gate，不能证明成功
- 现象：
  - obvious-buzz 自动门禁对“明确失败样本”很有用。
- 风险：
  - 若把 `review_required` 或“没被 auto reject”误判成成功，会继续浪费人工和训练预算。
- 正确处理：
  - machine gate 只负责自动否定。
  - 不负责证明“已经脱离 buzz”。

### 6. 人工听审一旦给出“纯 buzz / pure fuzz / 无人声结构”，就必须停掉同层微调线
- 现象：
  - 多条线路曾出现量化改善，但人工听感仍是纯 buzz。
- 风险：
  - 若继续扫小权重、小参数、小公式，只会重复消耗预算。
- 正确处理：
  - 一旦人工已把该层路线定性为错误解收敛，就停止同层微调并上收问题层级。

### 7. hidden / fused-hidden imitation loss 自己下降，不等于主线更好
- 现象：
  - `teacher_fused_hidden_projection` 曾显著下降。
- 风险：
  - 容易被误解成 student 更像 teacher，所以主线更接近突破。
- 正确处理：
  - 必须同时检查：
    - `loss_total`
    - `loss_total_semantic_disabled_reference`
    - `loss_teacher_event / event_prior`
  - 若共享主指标更差，应立即停线。

### 8. paired source-target 不能先验当作可直接逐帧监督
- 现象：
  - source parity / paired dry-run 已证明：
    - source waveform 与 target teacher frames 不天然对齐
- 风险：
  - 若直接把 target teacher 硬监督到 source 轴，会把 metadata 问题误当建模问题。
- 正确处理：
  - 没有 frame bridge / alignment contract 前，不开 paired Stage3 训练。

### 9. 新语义资产必须先完成 metadata / package / index plumbing，再谈 consumer 训练
- 现象：
  - target semantic、timing、source parity 几条线都验证过这一点。
- 风险：
  - 若 plumbing 与建模同时变化，失败后无法判断是接线问题还是模型问题。
- 正确处理：
  - 先接 metadata，再做最小 consumer / supervision 验证。

### 10. teacher-first / reference-relative 风险指标不能替代听审
- 现象：
  - `reference_shift` 之类指标能修正旧的误报，但不能证明出现人声。
- 风险：
  - 容易把“比 reference 更接近一些”误判成“快成功了”。
- 正确处理：
  - 若听感仍是纯 buzz，立即停止 inference-only 小修线。

### 11. 新增权重或新损失后，必须先确认真实透传到底
- 现象：
  - `MRSTFT short weight` 曾出现“CLI 有参数但实际没生效”的情况。
- 风险：
  - 会把假实验当成真实结论。
- 正确处理：
  - 先核对：
    - CLI
    - training loop
    - final summary 中的 `training.loss_weights`
  - 再解释实验结果。

### 12. 当前最有价值的层是 teacher-label / target-state generation-side，不是 Stage5 同层末端
- 现象：
  - `target shaping -> acoustic bridge -> directional transition bridge`
    连续给出 Stage3 正向。
- 风险：
  - 若仍把时间花在 Stage5 decode/objective/consumer 小修上，会错过真正有信息量的层。
- 正确处理：
  - 当前默认优先级：
    - generation-side 资产升级
    - handoff layer 识别
    - 最后才是下游末端小修

### 13. 不能把“新 handoff layer”做成旧 teacher-runtime route 的换皮
- 现象：
  - 当前 `offline_teacher_downstream_control_v3 -> scaffold v3`
    已经接过显式 `e_evt`
  - 但它仍主要是 teacher-runtime packet 的延长线
- 风险：
  - 很容易把“字段更像设计稿”误判成“承接层已经换了”
- 正确处理：
  - 真正新的 handoff family
    必须开始显式承接
    `Stage3 student-control state`
  - 不能只是旧 route 上的字段替换或 gate 公式替换

### 14. 不应跳过 cheap screen，直接把每个新上游 candidate 送进 Stage5
- 现象：
  - 当前仓库已具备：
    - `eval_bridge`
    - `proxy_acoustic`
    - `proxy_audio_export`
- 风险：
  - 若仍然每次都先开 Stage5 fail-fast，
    会重复消耗训练预算和人工精力
- 正确处理：
  - 新 handoff candidate
    先过 proxy-acoustic / proxy-audio cheap screen
  - 只有 screen 过关，才允许进入新的 Stage5 adapter/scaffold smoke

### 15. 不能把 `student_control_packet_v1` 误写成已完成的 Stage5-ready design-state contract
- 现象：
  - 当前 packet v1 已能导出：
    - `z_art`
    - `e_evt`
    - `f0_log_proxy`
    - `vuv_prob`
    - `aper_prob`
    - `energy_log / energy_norm`
- 风险：
  - 容易把“已有 named-control packet”误解成“F0 / aper / E 都已完成可直接下游消费的最终合同”
- 正确处理：
  - 当前只能说：
    - `e_evt` 已 ready
    - `z_art` 已 ready
    - `F0 / aper / E` 仍是 proxy/control status
  - 在这层没说明白前，不开新的 Stage5 adapter 训练

### 16. cheap screen 的“基本持平”不能被拔高成“已经值得开新 Stage5 route”
- 现象：
  - `directional` 相比 `contextual`
    在 Stage3 主指标上更好
  - 但在当前 proxy cheap screen 上只表现为近乎持平、没有明显结构跃迁
- 风险：
  - 很容易因为 packet 已 ready、loss 已改善，就提前开启新的 Stage5 adapter 训练
- 正确处理：
  - 当前只可下结论为：
    - handoff family 有效
    - 但承接证据还不够硬
  - 下一步应先补 packet/control calibration，
    而不是直接开新下游 route

### 17. 详细实验追记不应再回流进本文档
- 现象：
  - 旧版 `02` 已膨胀成超长历史流水账。
- 风险：
  - 主文档失去“活跃坑点清单”的功能，接班成本反而更高。
- 正确处理：
  - 新实验细节写入独立编号报告。
  - 只有会持续影响后续决策的坑点，才进入本文档。

## 当前维护规则
- 新增坑点前先判断：
  - 它是否会影响未来多轮决策，而不是只影响一轮实验。
- 若只是局部实验结论：
  - 写入对应编号报告，不进入本文档。
- 若本文档再次显著膨胀：
  - 继续做快照归档，不回到单文件堆历史的模式。
