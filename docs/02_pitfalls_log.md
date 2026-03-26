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

### 18. 不能再用“只有 proxy、还没到真实 decoded.wav”作为拖延 Stage5 fail-fast 的理由
- 现象：
  - 当前 `student_control_packet -> minimal Stage5 adapter` 已经补齐。
  - 新候选如果真的有 Stage5 端到端潜力，现在已经可以快速导出真实 `decoded.wav`。
- 风险：
  - 若还停在 proxy 音频，会把一条其实已经 end-to-end 失败的路线误留太久。
- 正确处理：
  - 一旦某条 packet 线路看起来有 Stage5 端到端潜力，
    就尽快跑最小真实 decoded smoke。
  - 不再把“还没做 Stage5 decode”当成默认状态。

### 19. 但“已经能导出真实 decoded.wav”也不等于这条线值得扩成试听包
- 现象：
  - `vuvbalancedgate48` 已通过最小 adapter 真正导出了 Stage5 `decoded.wav`。
  - 但第一条 smoke 样本就被机器门禁判成 `auto_reject_obvious_buzz`。
- 风险：
  - 很容易因为“终于有 decoded.wav 了”而继续扩到多条样本或人工听审。
- 正确处理：
  - 真实 decoded 只是一条更硬的 fail-fast 工具，不是成功信号。
  - 如果 best-sample decoded 已经 obvious buzz，
    就不默认扩成 3 条包，也不把 adapter 本身当主要调参对象。

### 20. 不能把旧 `v2/event_probs` Stage5 checkpoint 上的 fail-fast 结果误读成“显式 e_evt contract 已被公平验证”
- 现象：
  - 当前 best no-res checkpoint 实际来自 `offline_teacher_vocoder_input_scaffold_v2`
  - noise branch 前 8 维语义家族仍是 `event_probs`
- 风险：
  - 如果拿它去直接否定 `e_evt` 方向，会把“checkpoint 承接层旧”误读成“新 contract 本身错”
- 正确处理：
  - 先确认当前 Stage5 checkpoint 吃的是哪一版 scaffold family
  - 再解释 decoded smoke 的含义
  - 对旧 `v2` checkpoint，更应把它视为保守 fail-fast 工具，而不是新 contract 的最终裁判

### 21. 当前 student packet 与 native teacher package 的主要差异病灶不在 periodic branch，而在 noise 前 8 维 event family
- 现象：
  - `z_art / periodic branch` 与 teacher 已非常接近
  - 但 `event_presence_proxy`、noise first-8、以及其带出的 bright buzz 指标明显更差
- 风险：
  - 若继续把主要精力放在 `F0` 或 adapter 末端，会错过更直接的主病因
- 正确处理：
  - 下一步优先处理 Stage3 generation-side 的 event 维度分布
  - 而不是继续修 Stage5 adapter

### 22. 不能把“adapter 切成 legacy_event_probs 仍没变好”误判成 adapter 已经无信息量
- 现象：
  - 在当前 `vuvbalancedgate48` candidate 上，`e_evt == legacy_event_probs`
  - 所以 adapter 名义切换不会带来任何实际张量变化
- 风险：
  - 若不先核对张量本身，就会把“这条候选本身没有差异”误写成“adapter 路线没有信息量”
- 正确处理：
  - 先核对 packet 内实际导出的控制张量是否不同
  - 再解释 A/B 结果

### 23. local state loss 下降，不等于 handoff / 主监督更好
- 现象：
  - `explicit target acoustic-state supervision`
    能明显压低 `loss_teacher_f0_state`
  - 但 `loss_total` 与 `loss_total_semantic_disabled_reference` 同时变差
- 风险：
  - 很容易把 `F0 / aper / energy` 的局部改善误判成“packet calibration 已经开始转化为整体收益”
- 正确处理：
  - 必须同时检查：
    - `loss_total`
    - `loss_total_semantic_disabled_reference`
    - `loss_teacher_event / event_prior`
    - correction 正则是否异常抬升
  - 若共享主指标更差，应直接停线

### 24. 直接把 deterministic target state 压进现有 Stage3 loss，容易诱导 correction head 作弊
- 现象：
  - 在显式 `teacher_f0_state / vuv_state / aper_state / energy_state` A/B 里，
    `loss_teacher_f0_state` 虽下降，
    但 `loss_log_f0_correction_l1` 从很小值显著抬升
- 风险：
  - 模型可能优先学会“放大 correction head 去追局部 state target”，
    而不是改善更共享的 teacher-event / target-state 主结构
- 正确处理：
  - 不继续扫这组 direct state loss 权重
  - 回到更结构化的 generation-side / contract-side 升级

### 25. `packet 可导出` 不等于 `named controls` 已达到 handoff 最低就绪线
- 现象：
  - `student_control_packet_v1` 已能稳定导出
  - `cheap screen` 也没有明显退化
- 风险：
  - 很容易因此提前开启新的 Stage5 handoff route
- 正确处理：
  - 先过 `named-control readiness negative gate`
  - 当前 gate 已证明：
    - `e_evt / z_art` 可保留
    - `F0 / vuv / aper / E` 仍全部未就绪
  - 所以在 gate 放行前，不开新的 Stage5 adapter/scaffold

### 26. 不应继续让 Stage3 在训练时各处临时重算 target-state
- 现象：
  - 之前 deterministic target acoustic state 虽已可用，
    但主要还是在 Stage3 batch 里临时从 waveform 提取
- 风险：
  - teacher asset、batch contract、packet audit 不同源
  - 后续 generation-side 升级与 handoff 审计容易各用一套 target-state
- 正确处理：
  - 以 teacher asset 内置的
    `target_f0_hz / target_vuv / target_aper / target_energy`
    作为默认来源
  - 仅在旧资产缺字段时才回退重算

### 27. teacher-label generation-side 再次正向，不等于 `student_control_packet` readiness 已同步打开
- 现象：
  - `acoustic_directional_targetstate_bridge_v1`
    在 Stage3 `12-step / 24-step full-validation`
    都继续优于上一版 target-state baseline
- 风险：
  - 很容易因为 Stage3 `loss_total / teacher_event / event_prior` 继续变好，
    就误判 handoff 已经开始成立
- 正确处理：
  - Stage3 正向和 handoff readiness 必须拆开判断
  - 当前 `student_control_packet` 结果仍是：
    - `e_evt_ready = yes`
    - `energy_ready = yes`
    - `F0 / vuv / aper = no`
    - `all_records_auto_reject = true`
  - 因此不能因为新的 generation-side bridge 成功，
    就提前开新的 Stage5 route

### 28. 不能把 `proxy target family` 替换或轻量 `detach` 当作足以完成 named-control handoff 的修复
- 现象：
  - 本轮已验证三条线：
    - `named_control_proxy_target_family = deterministic_target_state_v1`
    - `detach_frontend_named_controls_for_student`
    - `detach_shared_hidden_for_student`
- 风险：
  - 很容易把这种“看起来结构更干净”的局部改动误判成接近解法，
    继续在同一层扫更多小开关
- 正确处理：
  - 这三条都没有打开 readiness gate
  - 下一步应上到更明确的 `frontend/control branch split`
  - 而不是继续在：
    - proxy target family
    - 轻量梯度 stop
    这些同层小变体上消耗预算

### 29. `frontend/control branch split v1` 的 Stage3 正向，也不能直接外推成 handoff 已成立
- 现象：
  - `parallel_control_encoder_v1`
    能继续改善 Stage3 的 `loss_total / event_prior / z_art`
- 风险：
  - 很容易因为“终于做了明确 branch split，而且总 loss 更好”，
    就误判它已经接近可下游消费
- 正确处理：
  - 这版 packet 仍然：
    - `all_records_auto_reject = true`
    - `f0_ready_count = 0`
    - `vuv_ready_count = 0`
    - `aper_ready_count = 0`
    - `energy_ready_count = 0`
  - 更关键的是：
    - `F0` raw proxy correlation 出现稳定反号
  - 所以 branch split v1 只能算“有信息量的失败”，
    不能直接进入新的 Stage5 route

### 30. `F0` 落进物理范围，不等于 `F0` handoff 已经方向正确
- 现象：
  - `bounded_log2_hz_v1`
    能把 `f0_log_proxy_mean` 收进合理的 `log2(Hz)` 区间
- 风险：
  - 很容易因为“数值终于像真的 F0 了”，
    就误判 handoff 已接近可用
- 正确处理：
  - 必须继续看：
    - `f0_proxy_reference_corr`
    - `f0_calibrated_log2_mae`
    - readiness gate
  - 当前事实是：
    - raw correlation 仍稳定为负
    - gate 完全不开
  - 所以 `bounded F0` 只能算量纲修饰，不是当前问题的解法

### 31. 单独再加一层 `explicit F0 branch`，也不等于已经触到 named-control handoff 的主病因
- 现象：
  - `explicit_state_branch_v1`
    相对 `bounded F0` 基本打平
  - `teacher_f0_state` 没有改善
  - `loss_log_f0_correction_l1` 却明显抬升
- 风险：
  - 很容易因为“已经给了 F0 独立支路”，
    就继续在这条单支路上扫层数、delta 上界、小 warmup 权重
- 正确处理：
  - 当前事实是：
    - readiness gate 仍完全不开
    - `F0` raw proxy correlation 仍稳定为负
  - 所以单独 `F0 branch` 不是当前层级的解法
  - 若继续，必须上到更完整的
    `control-specific head family / explicit control-state branch`

### 32. 即使把 `F0 / vuv / aper / energy` 一起放进 control-specific family，也不代表 handoff 病灶就在 student-side correction 层
- 现象：
  - `explicit_named_control_family_v1`
    能继续改善 Stage3 `loss_total`
  - 但 readiness gate 仍完全不开
- 风险：
  - 很容易因为 Stage3 数字继续变好，
    就继续在 student-side correction family 上加层数、加容量、加小限制
- 正确处理：
  - 必须先看更细的相关性诊断
  - 当前已确认：
    - `log_f0_correction` 本身是正相关补偿项
    - 真正负相关的是更上游的 `coarse_log_f0`
  - 所以下一步应转去：
    - `coarse F0 target contract / sign-stable supervision`
  - 而不是继续在 correction family 上追加小修

### 33. `F0 proxy` 从负相关翻正，不等于 handoff 已经打开
- 现象：
  - `coarse_f0_state` 直监督后，
    `F0 proxy` 已从全负翻到全正
- 风险：
  - 很容易因此过早判断
    “F0 已经解决，下一步可以开新 Stage5 route”
- 正确处理：
  - 现在只能说：
    - `sign repair` 方向终于打中了
  - 还不能说：
    - `F0` 已经 ready
- 因为当前仍同时成立：
    - 即使更长 horizon 下 `coarse_log_f0` 本体已经翻正，
      gate 也仍可能不开
    - `f0_proxy_reference_corr` 还没到 gate 阈值
    - `calibrated_log2_mae` 仍偏高
    - 其它 named controls 也还没一起过门

### 34. `F0 sign` 修到位以后，瓶颈会转移到其它 named controls；这时继续加同类 F0 loss 只会浪费时间
- 现象：
  - `24-step` 的 `coarse_f0_state` 已把 `coarse_log_f0` 本体翻成正相关
  - `48-step` 继续改善了 `F0`
  - 但 packet 仍：
    - `f0_ready_count = 0`
    - `vuv_ready_count <= 1`
    - `aper_ready_count = 0`
    - `energy_ready_count = 0`
    - `all_records_auto_reject = true`
- 风险：
  - 很容易因为“F0 终于翻正了”，
    就继续在同一条 `F0 sign repair` 线上追加：
    - 更长 horizon
    - 相关性 loss
    - nof0corr
    - 其它小参数化微调
- 正确处理：
  - `nof0corr` 和 `teacher_coarse_f0_correlation` 都应正式停线
  - `coarse_f0_state` 也不再继续叠同层 horizon
  - 下一步应把问题改写成：
    - 剩余 named controls 的 contract completion
    - 重点是 `vuv / aper / energy`

### 35. raw audit 很差，不等于这个 control 在 contract 上完全不可用
- 现象：
  - `aper / energy` 的 raw MAE 很差，
    但 affine-calibrated audit 后明显下降
  - 当前 best packet 上：
    - `aper_ready_count = 3`
    - `energy_ready_count = 2`
- 风险：
  - 很容易因为 raw MAE 难看，
    就误判 `aper / energy` 还必须继续靠训练主线去救
- 正确处理：
  - 先区分：
    - “模型没有信号”
    - “contract 坐标没对齐”
  - 当前 `aper / energy` 更接近后者
  - 所以后续优先级应下调，
    不再把它们当当前第一主瓶颈

### 36. 当 calibrated audit 已经把瓶颈收紧到 `vuv`，继续做 loss-side completion 仍可能是错层
- 现象：
  - mixed `vuv + aper + energy` state loss：
    - 只把 `energy` 多推进 1 条
    - 主指标更差
  - `vuv-only`：
    - `vuv_ready_count` 没升，
      反而从 `1` 掉到 `0`
    - `F0` 还略回退
- 风险：
  - 很容易因为“现在终于知道是 vuv 了”，
    就继续扫：
    - `teacher_vuv_state` 小权重
    - `vuv-only / vuv+energy` 组合
    - 更长 horizon 的同层 loss 试验
- 正确处理：
  - 到这里应正式判定：
    - loss-side `named-control completion` 整条线停线
  - 下一步不再继续这层小权重，
    而要转去 `vuv contract / representation / target family`

### 37. `vuv_ready_count` 不变，不等于 `vuv contract` 没有真实进展
- 现象：
  - `teacher_e_evt_v1_balanced_vuv_gate_v1` 在 `48-step sample-8` 上，
    `vuv_ready_count` 仍是 `1/8`
  - 但同一批记录里：
    - `vuv_reference_mae` 已经是 `6/8` 改善
- 风险：
  - 如果只看 ready_count，
    很容易把真实的 contract-level 改善误判成“没变化”
- 正确处理：
  - `vuv` 这类接近阈值的问题，
    必须同时看：
    - readiness count
    - per-record MAE
    - wider cheap screen win/loss
  - 当前应表述为：
    - `vuv contract` 已出现真实正向
    - 但还未过 gate

### 38. packet export 的 `semantic_supervision` 元数据当前不会自动反映 loss override 里的 family
- 现象：
  - 用 loss override 改了 `named_control_proxy_target_family` 后，
    training summary / supervision dry-run 会显示新 family
  - 但 packet export json 仍可能回显 checkpoint 基础 config 的旧 family
- 风险：
  - 很容易把 packet metadata 当成最终真相，
    误判“新 contract 没有参与训练”
- 正确处理：
  - 当前阶段应以这些为准：
    - supervision dry-run
    - training loop summary
    - packet 数值结果本身
  - 不应只凭 packet metadata echo 判断这轮 contract 是否生效

### 39. `F0` supervision 覆盖变窄后，Stage3 loss 变好并不自动意味着 handoff-facing `F0` 更好
- 现象：
  - `strong_voiced_gate_v1`
    会明显压低：
    - `loss_teacher_coarse_f0_state`
### 40. `fused_single` 上的轻量 decoder 结构修补，已经连续证明不够强
- 现象：
  - 当前已做过：
    - `decoder_branch_mean_mix_alpha`
    - `use_decoder_branch_condition_adapter`
    - 以及更早的弱 `fused_hidden` penalty
- 风险：
  - 很容易因为它们都“更靠近 decoder 结构”，就继续在 `fused_single` 上堆更多同级 patch
- 正确处理：
  - 这些路线现在应统一视为同层弱修复
  - 不再继续叠加
  - 下一步直接上更强的 `waveform_decoder_mode` 结构变化
### 41. `dual_branch_mix` 在当前 native teacher contract 下会把输出推向更亮、更尖的 harsh buzz
- 现象：
  - `waveform_decoder_mode = dual_branch_mix`
    已完成真实 `validation3 decoded.wav` fail-fast
  - `3/3 auto_reject_obvious_buzz`
  - `spectral_centroid_gap_hz / high_band_energy_ratio_gap` 相对 baseline 明显抬升
- 风险：
  - 很容易把“更强的结构变化”继续理解成“还值得在 branch mixing 这一档细修”
- 正确处理：
  - `dual_branch_mix` 这条线应正式停掉
  - 下一步转去更保守的 residual 型 decoder，而不是继续做 mixing family
### 42. 非 recurrent residual decoder family 在当前 native teacher contract 下也整体不通
- 现象：
  - 当前已做过：
    - `periodic_plus_noise_residual`
    - `periodic_plus_noise_residual_shape`
    - `periodic_plus_noise_factorized_residual`
  - 三条都完成了真实 `validation3 decoded.wav`
  - 三条都 `3/3 auto_reject_obvious_buzz`
- 风险：
  - 很容易继续在 residual family 内做局部 envelope/gain/shape 细修，误以为只是约束还不够
- 正确处理：
  - 当前应把这整个 non-recurrent residual decoder family 一起判停
  - 下一步不再从 decoder mode 这一层继续横向扫
  - 而应回到 native teacher 的 objective / target / contract 语义层
    - `loss_teacher_f0_state`
  - 同时 `loss_total` 也可能略优
- 风险：
  - 很容易把这解读成：
    - `F0` 真正变好了
    - 应该继续扩到更长 horizon
- 正确处理：
  - 这种 candidate 必须立刻过 packet cheap screen
  - 如果：
    - `f0_proxy_reference_corr`
    - `f0_calibrated_log2_mae`
    没有同步改善，
    就应判定为“只是监督覆盖变窄”，而不是 handoff readiness 真改善

### 40. 当 native teacher route 自己已经在真实 `decoded.wav` 上 `3/3 obvious buzz` 时，不能继续把主故障写成 student 偏差或蒸馏问题
- 现象：
  - 当前 best native `Stage5` checkpoint 在 validation `3-sample` 复核里：
    - `auto_reject_count = 3`
    - `all_records_auto_reject = true`
- 风险：
  - 很容易继续把主要时间花在：
    - `teacher-student` 蒸馏
    - student packet 分布校准
    - adapter 兼容小修
  - 但这些都不是当前第一主故障
- 正确处理：
  - 现阶段先把 native teacher route 的 buzz 当主故障处理
  - student 路线暂停，不再作为默认主线推进

### 41. 在 native teacher 仍明显 buzz 时，引入真实发音的生理传感器数据只会扩大变量数，不会优先解决主问题
- 现象：
  - 当前已存在更低层、证据更硬的故障：
    - `Stage5` 承接层 / waveform decode / template-collapse 假解
- 风险：
  - 容易把“没有 articulatory ground truth”想象成当前核心瓶颈，
    进而过早引入：
    - 采集成本
    - 新对齐问题
    - 新合同设计
    - 新训练变量
- 正确处理：
  - 在现有 acoustic / event / control 链还没稳定产出非 buzz decoded 前，
    不引入生理传感器数据
  - 先把 native teacher route 自身修到至少出现可听人声结构，
    再讨论新模态是否值得

### 42. 只要 teacher 线还没有达到用户可接受质量，就禁止切去 student 蒸馏
- 现象：
  - student 线很容易制造“也许换个 packet / 蒸馏目标就能更好”的错觉
  - 但当前 native teacher route 自己都还在真实 `decoded.wav` 上明显 buzz
- 风险：
  - 若 teacher 线未过关就重开 student，
    会把：
    - teacher 主故障
    - student 继发偏差
    - handoff / adapter 偏差
    混在一起，继续放大变量数
- 正确处理：
  - 把这条规则写成硬门禁：
    - `teacher` 线输出未让用户满意前，
      不允许把 student 蒸馏当作默认下一步
  - 只有在 native teacher 已稳定进入“非明显 buzz、主观可接受”区间后，
    才允许重新评估 student 是否值得恢复

### 43. paired tiny-overfit 上看起来有道理的 objective 组合，不能直接外推到 native teacher fullsplit
- 现象：
  - `active_template_weight = 0.05 + frame_delta_weight = 6.0`
    曾在 paired tiny-overfit 诊断里显得最值得试
  - 但放到 native teacher fullsplit `24-step` 后，
    真实 `decoded.wav` 仍是 `3/3 obvious buzz`
    且频谱亮度明显比 native baseline 更糟
- 风险：
  - 很容易因为它“理论上更针对 template-collapse”，
    就继续扩：
    - 更长 horizon
    - 邻近小权重 sweep
    - 同族 objective 变体
- 正确处理：
  - 这类候选一旦在 native teacher 真 decoded 上明显恶化，
    就应直接停线
  - 不允许把 paired tiny-overfit 的直觉当成 native fullsplit 的默认先验

### 44. 旧版 Stage5 export / probe 默认值若与当前主口径不一致，会直接污染 `decoded.wav / buzz gate / loss_metrics` 结论
- 现象：
  - `export-offline-mvp-nores-vocoder-audio`
    和三条 Stage5 probe CLI
    之前都存在默认 decode 语义与当前主口径不完全一致的问题
  - 同时 export 里的 `loss_metrics`
    也可能没有正确继承 checkpoint 训练时的 gate / objective 语义
- 风险：
  - 很容易把：
    - 旧 decode 默认值下导出的 `decoded.wav`
    - 旧 metric 语义下的 `loss_metrics`
    - 旧 probe 默认值下的诊断
    混成同一条硬结论
  - 进一步污染：
    - `auto_reject_obvious_buzz`
    - baseline/candidate 相对优劣
    - native teacher 是否已被确认 `3/3 obvious buzz`
- 正确处理：
  - 代码修复后，必须先做最小回补重跑，再恢复新实验
  - 当前 active 范围内至少要回补：
    - `391` native teacher baseline validation3 export
    - `392` `acttmpl005_delta6` candidate validation3 export
  - 在此之前：
    - `389~392` 里所有直接依赖旧 export 的
      `decoded.wav / buzz gate / loss_metrics`
      结论都只能按临时结论使用
  - 当前状态更新：
    - `391 -> 392` 的最小回补已完成
    - `391/392` 的主结论已恢复为正式可用
    - 但 `389/390` 里依赖旧 export 的 student 对照部分仍保持临时结论口径，
      除非后续主线重新需要它们

### 45. 历史 smoke 上“最接近有效信号”的 `recurrent + temporal`，放到当前 native teacher fullsplit 真 decoded 上也可能直接变成更亮、更尖的坏 buzz
- 现象：
  - 历史 `smoke` 曾表明：
    - `recurrent + explicit temporal loss`
      是第一条能继续压
      `adjacent cosine`
      的路线
  - 但当前 fullsplit24 native teacher 候选
    `recurrent + temporal + periodic_rms_floor=0.05`
    在真实 `decoded.wav` 上：
    - `3/3 auto_reject_obvious_buzz`
    - 相对当前 baseline，
      `spectral_centroid_gap_hz`
      与 `spectral_high_band_energy_ratio_gap`
      都显著恶化
- 风险：
  - 很容易把 smoke 上的局部结构信号外推成：
    - “只要再补一点 RMS floor / high-band restraint 就会成”
  - 进而继续在同一 recurrent 分支上烧：
    - horizon
    - local RMS floor
    - high-band restraint
    - 同族小权重 sweep
- 正确处理：
  - 一旦当前 fullsplit native teacher 的真实 `decoded.wav`
    已把这类 recurrent 分支判成更糟的 harsh buzz，
    就应直接停整条同分支小修线
  - 后续先回到修正后的 baseline probe，
    再选更保守、且不重复历史死线的 teacher-side 候选
### 46. probe 里看起来强的 `active_template + zero-target flux-jitter` 组合，也不能直接外推成 native teacher fullsplit 上值得继续扩的 objective 线
- 现象：
  - waveform-objective-collapse probe 里，
    `active_template + zero-target flux-jitter`
    在 probe ranking 上是强信号
  - 但 native teacher fullsplit24 候选
    `acttmpl005 + zero_target_flux_jitter=4.0`
    在真实 `decoded.wav` 上仍然：
    - `3/3 auto_reject_obvious_buzz`
    - 且相对 corrected baseline 明显更差
- 风险：
  - 很容易因为它比 `acttmpl005_delta6` 更“保守”，
    就继续扫：
    - `zerojitter=1/2/4`
    - `acttmpl + zerojitter`
      的同族小权重
- 正确处理：
  - 当前不再继续这组 waveform frame objective 族
  - 应把问题上收到更结构化的 forward-path / fusion 层

### 47. `fusion -> fused_hidden` 确实是有信息量的病灶层，但弱 `fused_hidden template/delta` penalty 仍不足以把 native teacher 拉出 buzz 假解
- 现象：
  - decoder-structure probe 明确显示：
    - 更大的 collapse 已发生在 `fusion -> fused_hidden`
  - 但 native teacher fullsplit24 候选
    `fused_hidden_template=0.05 + fused_hidden_delta=2.0`
    在真实 `decoded.wav` 上仍然：
    - `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline 仍更差
- 风险：
  - 很容易把“病灶定位对了”误读成“只差再扫一点 template/delta 小权重”
- 正确处理：
  - 停止：
    - `fused_hidden_template`
    - `fused_hidden_delta`
      同族小权重 sweep
  - 下一步应升级到更直接的
    `forward-path structural`
    native teacher 候选
### 48. 即使 probe 显示 `branch_mean` 方向最有反应，轻量 `decoder_branch_mean_mix_alpha` 也不等于足够强的结构改路
- 现象：
  - decoder-structure probe 里，
    `fused_hidden_from_branch_mean`
    是影响最大的变体之一
  - 但 native teacher fullsplit24 候选
    `decoder_branch_mean_mix_alpha = 0.25`
    在真实 `decoded.wav` 上仍然：
    - `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline 仍更差
- 风险：
  - 很容易把“方向上有响应”误读成
    “只要再扫 `alpha=0.1/0.2/0.3` 就会成”
- 正确处理：
  - 停止：
    - `decoder_branch_mean_mix_alpha`
      小范围 sweep
    - 同级别轻量 operating-point mix
  - 下一步应继续升级到更强的
    `fusion / branch-conditioned decoder`
    结构候选

### 49. 不能把“给 spectral target 乘上 gate”想当然地当作 native teacher 的更正确 contract
- 现象：
  - `spectral_target_mode = gate_masked_halfsplit_v1`
    已真实接通 package / training / export 全链路
  - 但真实 `decoded.wav` 结果是：
    - `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline 明显更差
- 风险：
  - 很容易因为它“更像显式 contract”，就继续扫：
    - `harmonic_target * periodic_gate_target`
    - `noise_target * noise_gate_target`
    的同族 target 变体
- 正确处理：
  - 当前应把这条线视为已证伪：
    - 简单乘法式 gate-masked spectral target
      不会修好 native teacher buzz
  - 下一步应改查：
    - noise/periodic target family 的语义本身
    - 而不是再给现有 target 叠 mask

### 50. 不能把“关掉 training-side activity gate”误当作当前 native teacher buzz 的主解法
- 现象：
  - `activity_gate_weight = 0.0 + use_predicted_activity_gate = false`
    的 fullsplit24 候选已经完成真实 `decoded.wav` fail-fast
  - 结果仍是：
    - `3/3 auto_reject_obvious_buzz`
    - 且相对 corrected baseline 更差
- 风险：
  - 很容易继续围绕：
    - `activity_gate_weight`
    - training-side gated reconstruction
    - 同层 gate 开关
    做微扫
- 正确处理：
  - 当前应把“activity gate 自身就是主 bug”这条解释降级
  - 后续不再继续：
    - `activity_gate_weight` 同层 sweep
    - `use_predicted_activity_gate` 的 training-side 微变体
  - 应转去更根本的：
    - noise/periodic target semantics
    - objective meaning

### 51. `worker_processes` 这种导出参数，不能只加到 CLI 和顶层函数签名就当作已经生效
- 现象：
  - 本轮 Stage5 dataset package builder
    一开始已经有：
    - CLI `--worker-processes`
    - 顶层 `build_offline_mvp_nores_vocoder_dataset_packages(..., worker_processes=...)`
  - 但核心 `build_dataset_packages_for_split(...)`
    的真实调用链还没收到这个参数，
    实际行为仍是串行。
- 风险：
  - 很容易把“参数入口已接好”
    误判成“并行导出已经成立”。
  - 也容易在并行改造后继续让子进程各自打印日志，
    导致进度信息乱序、不可解释。
- 正确处理：
  - 必须继续核对：
    - 顶层调用是否把参数真正传入核心 split builder
    - `worker_processes == 1`
      是否保留原串行语义
    - `worker_processes > 1`
      是否真实走 `ProcessPoolExecutor`
    - 进度是否由主进程按 future 完成数统一打点
    - dataset index / summary
      是否写回 `worker_processes`
  - 在产物里看到这些证据之前，
    不能把它写成“并行路径已完成”。

### 52. 不能把“把 noise gate 收窄成纯 `aper * E`”想当然地当作更干净、更安全的 native teacher contract
- 现象：
  - `target_contract_mode = v2core_aper_energy_only_v1`
    已完成 full-split package、fullsplit24 training、checkpoint selection、validation3 real decoded 全链路
  - 真实结果仍然是：
    - `3/3 auto_reject_obvious_buzz`
    - 且相对 corrected baseline，
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      全面更差
- 风险：
  - 很容易因为它“看起来更保守、更物理”，
    就继续围绕：
    - `aper`
    - `energy`
    - `event_presence_proxy`
      的加减法小修
  - 把这类同层 gate 公式改写误当成当前 Stage5 主解法
- 正确处理：
  - 当前应把这条解释降级：
    - native teacher 的主故障
      不是只要把 noise gate 改成纯 `aper * E` 就会自然变好
  - 后续不再继续：
    - `v2core_aper_energy_only_v1` 同层扩展
    - `aper / energy / event_presence`
      的简单门公式微扫
  - 应继续上收到：
    - 更根本的 noise/periodic target family
    - objective meaning
    - template-collapse 的诱因定位

### 53. 不能把“把 Stage5 gate supervision 显式换成 `e_evt` 公式”想当然地当作当前 native teacher buzz 的主解法
- 现象：
  - `target_contract_mode = teacher_e_evt_gate_targets_v1`
    已在 corrected native-teacher fullsplit24 主线上完成：
    - full-split package
    - 24-step training
    - checkpoint selection
    - validation3 real decoded
  - 真实结果仍然是：
    - `3/3 auto_reject_obvious_buzz`
    - 且相对 corrected baseline，
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      全面更差
- 风险：
  - 很容易因为它“终于显式用了 `e_evt`”，
    就继续围绕：
    - `p_voicing`
    - `p_frication`
    - `p_stop_closure`
    - `p_burst`
    - `pause / terminal boundary`
    的 gate 公式做同层微扫
  - 把 supervision-side `e_evt gate target`
    误判成当前 Stage5 主突破口
- 正确处理：
  - 当前应把这条解释降级：
    - native teacher 的主故障
      不是只要把 gate supervision 显式改写成 `e_evt` 公式就会自然变好
  - 后续不再继续：
    - `teacher_e_evt_gate_targets_v1` 同层扩展
    - 现有 `target_contract_mode`
      家族里的语义 gate 公式微扫
  - 应继续上收到：
    - 更根本的 noise/periodic target family
    - objective meaning
    - template-collapse 的诱因定位

### 54. 不能把“按 `F0 / vuv` 显式构造 harmonic/noise spectral target”想当然地当作当前 native teacher 的更正确 target family
- 现象：
  - `spectral_target_mode = f0_harmonicity_split_v1`
    已完成 corrected native-teacher fullsplit24 主线的：
    - full-split package
    - 24-step training
    - checkpoint selection
    - validation3 real decoded
  - 单包 `spectral_target_contract`
    已真实切换到：
    - `harmonic_mask_formula = harmonic_bins_from_f0_hz_and_vuv`
    - `noise_mask_formula = spectral_complement_of_harmonic_mask`
  - 真实结果仍然是：
    - `3/3 auto_reject_obvious_buzz`
    - 且相对 corrected baseline，
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      全面更差
- 风险：
  - 很容易因为它“更像谐波结构、更像设计态”，
    就继续围绕：
    - `F0`
    - `vuv`
    - harmonic mask 宽度
    - harmonic/noise spectral complement
    做 package-level target family 微扫
- 正确处理：
  - 当前应把这条解释降级：
    - native teacher 的主故障
      不是只要把 half-split 换成 `F0 / vuv`
      驱动的 spectral target family 就会自然变好
  - 后续不再继续：
    - `f0_harmonicity_split_v1` 同层扩展
    - `spectral_target_mode`
      的近邻 package-level 变体
  - 应继续上收到：
    - objective meaning
    - template-collapse 的诱因定位

### 55. 不能在已经更差的 package target family 上继续叠 objective-side penalty，误把它当作主线
- 现象：
  - 对 `f0_harmonicity_split_v1`
    补做 waveform-objective collapse probe 后，
    baseline decode route 的
    `mean_weighted_wave_objective = 0.240339`
    仍显著输给：
    - `oracle_active_frame_target_rms = 0.141467`
    - `oracle_sine_target_rms = 0.147455`
  - 同时：
    - `active_template + delta`
      在这条线上最好也只做到
      `20 / 24`
    - 没有回到先前 corrected baseline probe
      那种更强的压制形态
- 风险：
  - 很容易因为“objective 还没修好”，
    就继续在一个已经更差的 target family 上：
    - 叠更多 waveform/frame penalty
    - 反复开 fullsplit24
    - 把 package target family
      和 objective root cause
      混在一起做
- 正确处理：
  - objective-side 根因分析
    应回到 corrected baseline 主线来做，
    不应默认继续在更差 target family 上叠 penalty
  - 当前新的默认顺序应是：
    - 先停止 Stage5 package target/contract family 微扫
    - 再在 corrected baseline 主线上做
      objective meaning / collapse 诱因定位

### 56. 不能把 gate-on 的旧 objective probe 结果，直接当成当前 corrected baseline 听审主路由的口径
- 现象：
  - 旧 `docs/293_stage5_contractv2_normfix_waveform_objective_recheck_report.md`
    用的是：
    - predicted gate `on`
    - `post_ola_envelope`
  - 但当前 corrected baseline 的真实听审主路由
    已经是 gate-off
  - 本轮 gate-off 复核后，
    baseline 的
    `mean_weighted_wave_objective = 0.293871`
    明显差于旧 gate-on probe 的
    `0.149037`
- 风险：
  - 很容易继续把：
    - `acttmpl005_delta6`
    - 旧 `frame_delta flip threshold`
    - 旧 `active_template + delta`
      排名
    直接拿来当当前默认训练候选
- 正确处理：
  - 当前 objective-side 判断
    必须优先参考
    gate-off 复核结果
  - 不再把 gate-on probe
    当作当前主听审路由的最终口径

### 57. 不能把“gate-off 听起来更差”误判成主病灶已经转到 export gate 开关本身
- 现象：
  - gate-off 听审路由下的 corrected baseline
    objective probe 确实更差
  - 但同语义 decoder-structure probe
    仍给出：
    - `collapse_not_localized_to_waveform_decoder`
    - 主坍缩点仍在
      `fusion -> fused_hidden`
- 风险：
  - 很容易把问题写成：
    - “主要是 export gate 开关选错了”
    - “只要回到 gate-on 就是主修复方向”
- 正确处理：
  - gate-on / gate-off
    现在更适合作为症状显影方式，
    不是主病灶本身
  - 当前主线仍应优先定位：
    - `fusion -> fused_hidden`
      为什么先塌
    - 以及它如何和 decode semantics
      一起放大当前 buzz

### 58. 不能把 smoke 上“第一个碰到 fusion 有效层级”的候选，误判成理应继续做 full sweep 的主线
- 现象：
  - `fused_hidden_branch_mean_weight = 0.25`
    在最小 smoke 上曾出现：
    - `loss_fused_hidden_to_branch_mean_unit_rms_l1`
      明显下降
    - `loss_active_template`
      同时下降
    - `waveform / rms_guard`
      没有明显恶化
  - 但 corrected native-teacher fullsplit24
    真实 `decoded.wav`
    结果仍是：
    - `3/3 auto_reject_obvious_buzz`
    - 且相对 corrected baseline，
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      全面更差
- 风险：
  - 很容易因为它是第一条 smoke 上“看起来真正碰到了 fusion 层”的候选，
    就继续围绕：
    - `branch_mean_weight = 0.1 / 0.25 / 0.4`
    - 其它 fusion-side `loss`
      小权重
    做 sweep
  - 把“局部层命中感”误判成“已经足够接近真实解”
- 正确处理：
  - smoke 只能说明：
    - 这条候选在诊断层面有信息量
  - 不能说明：
    - 它值得自动升级成 fullsplit sweep 主线
  - 一旦真实 fullsplit24 decoded
    已把这条线判成更差的同类 buzz，
    就应把整个现有 fusion-side `loss`
    家族一起降级
  - 后续若继续推进
    `fusion -> fused_hidden`
    主线，
    应直接转向更强的
    `forward-path structural / fusion manifold`
    改路，
    而不是继续叠 penalty

### 59. 不能把“比多数旧候选更接近 baseline”误写成“当前 fusion 结构已经转正”
- 现象：
  - `fusion_mode = branch_mean_residual_v1`
    是当前第一条在真实 fullsplit24 上，
    明显比多数旧候选更接近 corrected baseline 的
    fusion-path structural 候选
  - 但真实 `validation3 decoded.wav`
    结果仍然是：
    - `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      仍全部更差
- 风险：
  - 很容易因为这次恶化幅度终于没有那么大，
    就把它误写成：
    - “结构方向已经对了”
    - “只差再跑长一点或做小 sweep”
  - 进而过早围绕：
    - `branch_mean_residual_v1`
      horizon
    - 同族小变体
    做扩展
- 正确处理：
  - 当前只能说：
    - 这条线比多数旧候选更有信息量
    - 说明主线继续留在
      `fusion -> fused_hidden`
      结构改路
      是合理的
  - 不能说：
    - 这一个具体结构已经值得扩 sweep
  - 下一步应继续做更强的
    `fusion manifold / handoff-shape`
    候选，
    而不是直接围绕
    `branch_mean_residual_v1`
    做延长或邻域微扫

### 60. 不能把 bypass 里“`periodic_hidden` 去模板化更强”直接外推成“periodic 主骨架会是更好的 fusion handoff”
- 现象：
  - gate-off decoder-structure probe 里，
    `fused_hidden_from_periodic_hidden`
    的确比 `branch_mean`
    展现出更强的去模板化响应
  - 但真实 fullsplit24 候选
    `fusion_mode = periodic_residual_v1`
    在 `validation3 decoded.wav` 上：
    - 仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline 更差
    - 相对 `branch_mean_residual_v1` 也更差
- 风险：
  - 很容易把 probe 里的 bypass 响应，
    误判成：
    - “应该继续让 periodic branch 当 fusion 主骨架”
    - “只差 periodic residual 再调小一点”
  - 进而继续往
    periodic-dominant handoff
    这条更亮、更尖的方向扩展
- 正确处理：
  - bypass probe
    只能说明：
    - 该隐藏态里有可用动态
  - 不能说明：
    - 把它直接升格为 fusion 主骨架
      就会自然变好
  - 当前真实 fail-fast 已证明：
    - periodic-dominant fusion
      会重新拉高 harsh buzz
  - 下一步应留在
    `branch_mean`
    一侧继续做 fusion manifold 改路，
    而不是继续增强 periodic dominance

### 61. 不能把“brightness 明显变好、selector 也稳定了”误写成 Stage5 native teacher 已经接近可用
- 现象：
  - `fusion_mode = branch_mean_contrast_residual_v1`
    是当前第一条真正把
    `spectral_centroid_gap_hz`
    从约 `5.0k`
    压到约 `1.0k`
    的 fusion structural 候选
  - `spectral_high_band_energy_ratio_gap`
    也被压到约
    `0.01 ~ 0.07`
  - selector 还第一次给出了
    `selected_stable_late_stop = step24`
- 风险：
  - 很容易因此把当前口径写成：
    - “只差一点点了”
    - “brightness 修好了就说明主问题已经解决”
  - 进而继续围绕：
    - brightness restraint
    - high-band penalty
    - periodic dominance
    这些已经降级的方向消耗预算
- 正确处理：
  - 当前仍必须优先看：
    - `auto_reject_obvious_buzz`
    - `decoded_frame_template_cosine_mean`
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
  - 当前事实是：
    - 三条样本仍 `3/3 auto_reject_obvious_buzz`
    - `decoded_frame_template_cosine_mean`
      仍在 `0.99` 左右
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
      仍稳定在 `0.89 ~ 0.91`
  - 因而这条线只能说明：
    - brightness 症状被压下来了
    - 剩余主病灶已收缩成
      `template-collapse + envelope-following`
  - 下一步应直接打：
    - decoder-side template projector
    - branch dynamics 到 waveform handoff 的保真
  - 不应再把“亮度明显变好”误判成已经值得回到同层 brightness 微扫

### 62. 不能把“主病灶已经收缩到 decoder-side”误判成“直接把 branch-conditioned hidden adapter 插回 decoder 就会自然变好”
- 现象：
  - `branch_mean_contrast_residual_v1`
    已把 brightness 明显压下来了，
    剩余主故障主要收缩成
    `template-collapse + envelope-following`
  - 但在这条 backbone 上直接叠
    `use_decoder_branch_condition_adapter = true`
    后，
    fullsplit24 真 decoded 结果仍然：
    - `3/3 auto_reject_obvious_buzz`
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
      仍稳定在 `0.89 ~ 0.90`
    - brightness 还明显回升：
      - `spectral_centroid_gap_hz`
        回到 `~2.9k`
      - `spectral_high_band_energy_ratio_gap`
        回到 `0.47 ~ 0.52`
- 风险：
  - 很容易因为“病灶就在 decoder 附近”、
    “adapter 也是最现成的 decoder 补丁”，
    就继续围绕：
    - hidden-side branch adapter
    - decoder hidden additive conditioning
    - 同族小 gate / 小 projection
    做微扫
- 正确处理：
  - 当前应把这条解释降级：
    - decoder-side 仍是问题层，
      但“直接改 decoder hidden”
      不是当前正确的改法
  - 结构 probe 说明：
    - fusion backbone 基本没坏
    - 更差的是 hidden-side conditioning
      把 waveform projector 又推回模板区
  - 下一步若继续把 branch dynamics
    带回 waveform，
    应优先考虑：
    - frame-space residual
    - residual-shape
    - 输出侧更受限的 handoff
  - 不应再继续：
    - hidden-side decoder branch adapter
      同族变体

### 63. 不能把第一次从 `auto_reject` 进入 `review_required` 误写成 Stage5 已经脱离 buzz
- 现象：
  - `branch_mean_contrast_residual_v1 + residualshapecond`
    是当前第一条把
    validation3
    从 `3/3 auto_reject_obvious_buzz`
    拉到
    `3/3 review_required`
    的 route
- 风险：
  - 很容易把“终于不是 auto reject 了”
    误写成：
    - 已经出现可用人声
    - 下一步只要做人工听审收尾
- 正确处理：
  - 当前仍必须同时看：
    - `decoded_frame_template_cosine_mean`
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
  - 这条线当前只能说明：
    - 从 obvious buzz 假解
      进入了更有信息量的
      `review_required` operating region
  - 不能说明：
    - 已经脱离
      `template-collapse + envelope-following`

### 64. 不能把 selector 稳定性重新变好，误判成当前 residual-shape route 的 heard-path 指标也更优
- 现象：
  - `residual_shape_branch_condition_scale = 0.25`
    重新拿回了
    `selected_stable_late_stop = step24`
    且
    `decoded_to_target_rms_ratio = 0.992803`
    更接近 `1.0`
  - 但在同一路由上，
    `scale = 0.5`
    的：
    - `decoded_frame_template_cosine_mean`
    - `spectral_centroid_gap_hz`
    - `spectral_high_band_energy_ratio_gap`
    反而更优
- 风险：
  - 很容易因为 selector 和 RMS ratio
    更好看，
    就把 `0.25`
    直接当作当前最优 route
- 正确处理：
  - 当前要把这两档分开解释：
    - `0.5`
      是 heard-path collapse / brightness
      更优的一档
    - `0.25`
      是 selector / RMS stability
      更优的一档
  - 下一步不应只围绕：
    - selector
    - RMS ratio
    做单维优化
  - 而应直接处理：
    - 两档都没动到的
      `envelope-following`
