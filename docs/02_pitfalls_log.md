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

### 65. 不能把“把 residual-shape 分支做成 shape-only / unit-rms 归一化”当作当前 route 下天然正确的 envelope-following 修法
- 现象：
  - 当前稳定主线是：
    - `branch_mean_contrast_residual_v1`
    - `raw_additive_v1 residualshapecond`
    - `scale = 0.25 ~ 0.5`
  - 新增的
    `residual_shape_branch_condition_mode = shape_only_unit_rms_v1`
    在 inference-only decode probe 上表现为：
    - `decoded_frame_template_cosine_mean`
      `0.975636 -> 0.977393`
    - `decoded_frame_rms_to_aligned_frame_rms_corr`
      `0.891069 -> 0.904674`
    - `spectral_centroid_gap_hz`
      `4036.778076 -> 4302.939941`
    - `spectral_high_band_energy_ratio_gap`
      `0.333024 -> 0.353297`
  - 同时它从随机初始化训练时，
    在最小 smoke 上
    第一步 update 后
    就出现：
    - `binary_cross_entropy`
      输入越界
- 风险：
  - 很容易因为这个假设在直觉上“更去振幅、更像 shape-only”，
    就把它当成：
    - 当前 residual-shape route
      的天然下一步
    - 或者值得先投入训练稳定化预算的方向
- 正确处理：
  - 当前事实已经足够说明：
    - 这条 unit-rms 归一化
      没有方向性收益
    - 它不但没减轻
      `envelope-following`，
      还把 collapse / brightness
      一起推差了
  - 因而下一步不应：
    - 围绕
      `shape_only / unit_rms / 归一化 residual-shape`
      同族假设做微扫
    - 也不应先为它投入数值稳定化
  - 当前更合理的口径仍是：
    - 保留
      `raw_additive_v1`
    - 在
      `scale = 0.25 ~ 0.5`
      这段已成立的 route 上
      继续定位
      `envelope-following`

### 66. 不能把当前 `residualshapecond` route 的收益误判成主要由 decode-time additive delta 本身在持续支撑
- 现象：
  - 对同一个
    `scale=0.25 raw_additive_v1`
    step24 checkpoint，
    仅把 decode-time
    `residual_shape_branch_condition_scale`
    改成
    `0.0`
    之后，
    route 仍保持：
    - `3/3 review_required`
  - speech-emergence probe 里：
    - `decoded_frame_template_cosine_mean`
      `0.97723 -> 0.977191`
    - `spectral_centroid_gap_hz`
      `4228.900391 -> 4194.120605`
    - `spectral_high_band_energy_ratio_gap`
      `0.347793 -> 0.344906`
    - 但
      `decoded_frame_rms_to_aligned_frame_rms_corr`
      `0.904841 -> 0.904918`
- 风险：
  - 很容易把当前 route
    首次脱离 `auto_reject`
    的收益，
    继续归因给：
    - decode-time residual-shape 增量
    - inference-time gain 本身
  - 进而继续围绕：
    - `scale`
    - additive delta 大小
    做更多微扫
- 正确处理：
  - 当前更准确的解释应是：
    - 这条 route 的主要收益，
      更像已经被训练过程
      写进了 backbone / decoder operating region
    - 当前 decode-time 那点 additive delta，
      不是主要承载项
  - 因而下一步不应：
    - 继续围绕 decode-time scale
      做微调
  - 而应转到：
    - 为什么 training-time residual-shape handoff
      能压低 brightness / collapse，
      却仍保留
      `envelope-following`

### 67. 复用 `run_offline_mvp_teacher_first_vc_demo` 做用户线诊断时，不能假设 teacher-contract wrapper 会自动跟上下游 contract 新签名
- 现象：
  - 新增
    teacher-first
    `waveform handoff probe`
    的最小 smoke
    首次失败点
    不在 vocoder，
    而在：
    - `teacher_first_vc_demo.py`
      里的
      `export_teacher_contract_with_stage_tracking`
  - 原因是：
    - `offline_teacher_downstream_contract.build_contract_payload`
      与
      `build_tensor_payload`
      已新增：
      - `target_event_semantic_sidecar`
      - `target_event_timing_semantic_sidecar`
      - `source_semantic_parity_sidecar`
      - `teacher_e_evt_bridge_mode`
      - `teacher_e_evt_target_shaping_mode`
    - 但旧 wrapper
      还没同步透传这些参数
- 风险：
  - 很容易把这类报错误读成：
    - 新 probe
      本身写坏了
    - 或 Stage5 vocoder
      又出现新兼容性问题
  - 实际上它会让所有复用
    `run_offline_mvp_teacher_first_vc_demo`
    的用户线诊断命令，
    在进入 waveform handoff 之前
    就被 teacher-contract 阶段提前拦死
- 正确处理：
  - 只要 teacher contract
    新增必填语义参数，
    就必须同步检查：
    - `offline_teacher_downstream_contract` 正式 CLI
    - `teacher_first_vc_demo` 里的 wrapper
    - 所有基于该 wrapper
      的 probe / bundle 命令
  - 当前已修复方式是：
    - 在
      `export_teacher_contract_with_stage_tracking`
      上补齐同名参数及 legacy 默认值，
      并继续向下透传，
    - 先恢复所有用户线 probe
      的可运行性，
      再判断真正的 decoder-side 结论。

### 68. 当 user-line waveform handoff probe 已明确显示 `decoded_no_gate` 本身就坏、且 `logits -> frames` 几乎不再恶化时，不能继续把主故障优先写成 `gate / OLA` 语义
- 现象：
  - 固定三条
    pure buzz
    user-line case
    的 waveform handoff probe
    已给出一致结果：
    - `waveform_frame_logits_template_cosine_mean`
      已在
      `~0.9995 ~ 0.9998`
    - `waveform_frames_template_cosine_mean`
      也仍在
      `~0.9994 ~ 0.9998`
    - `logits_to_frames_template_cosine_gap`
      只有
      `-0.00006 ~ -0.00003`
    - 同时
      `decoded_no_gate`
      已经稳定很坏：
      - template
        `~0.990 ~ 0.996`
      - centroid
        `~6774 ~ 6963 Hz`
      - high_band
        `~0.384 ~ 0.396`
  - `pre/post_ola gate`
    确实会把：
    - `predicted_activity_to_decoded_frame_rms_corr`
      拉到
      `~0.973 ~ 0.997`
    但 brightness / template
    只出现轻微回落，
    没有新的同量级恶化
- 风险：
  - 很容易因为：
    - gated route
      听起来更像“跟包络走”
    - 或 `post_ola`
      在主观上最接近最终导出的坏相位
    就继续优先怀疑：
    - `pre_overlap_add`
    - `post_ola_envelope`
    - smoothing / floor
    - OLA 实现细节
- 正确处理：
  - 当前更准确的写法应是：
    - gate
      主要在放大
      `envelope-following`
      这一层可听表象，
      但不是第一次把系统推入坏 manifold
    - 真正更上游的病灶
      已经在：
      - `waveform_frame_logits`
      - `waveform_frames`
      - 或它们之前的 projector / handoff
      附近形成
  - 因而下一步不应继续优先做：
    - gate apply mode 微扫
    - gate smoothing / floor
    - OLA 语义小修
  - 而应转到：
    - gate 之前的 waveform handoff source
    - projector collapse
    - 为什么 user-line scaffold
      会把 Stage5
      推入这块固定模板区

### 69. 如果同 checkpoint 的 Stage5 validation package 也呈现几乎同样的 waveform handoff collapse，就不能再把 user-line 现象优先解释成“用户输入特有失配”
- 现象：
  - user-line 固定三样本
    与同 checkpoint 的
    validation3 package
    在 handoff stage aggregate
    上非常接近：
    - `waveform_frame_logits_template_cosine_mean`
      - user-line: `0.999641`
      - validation: `0.999573`
    - `waveform_frames_template_cosine_mean`
      - user-line: `0.999597`
      - validation: `0.999516`
    - `logits_to_frames_template_cosine_gap`
      两边都接近 `0`
  - 也就是说：
    - 当前 user-line
      暴露出来的坏工作区，
      并不是一个只在 user-line
      才第一次形成的新 handoff collapse
- 风险：
  - 很容易因为 user-line
    是终端入口、
    试听也更刺耳，
    就继续把主叙事写成：
    - user-line controls
      把健康 checkpoint
      推坏了
    - 或 user-line special mismatch
      才是主故障
- 正确处理：
  - 当前更准确的口径应是：
    - user-line
      只是把已有的
      checkpoint-native waveform collapse
      又复现了一遍，
      并把它听得更直接
  - 若 validation package
    自己也落在同一类 handoff 形状，
    下一步就不应继续优先投入：
    - user-line 特化 normalize
    - user-line gate 小修
    - 只面向终端入口的 decode tweak
  - 而应回到：
    - Stage5 native teacher
      本体的 waveform handoff / projector
      主病灶

### 70. 如果 `fused_hidden_frame_mean` 几乎不改变输出，而 `fused_hidden_from_branch_mean / periodic / noise` 会立刻显著脱模，就不要再把主病灶写成“decoder 已完全死掉”
- 现象：
  - user-line 固定三条 pure buzz
    的 structure probe
    与 validation3 gate-off
    的 structure probe
    都表现出：
    - `fused_hidden_frame_mean`
      的
      `waveform_mean_abs_delta_vs_baseline`
      只有
      `~0.0075`
    - 但 branch bypass
      会立刻带来
      `~0.315 ~ 0.333`
      的大波形变化
    - 同时
      `decoded_template`
      明显下降
- 风险：
  - 很容易把当前现象误写成：
    - decoder
      无论输入什么都只会吐一个固定 buzz
    - 所以只改 decoder
      就能解释全部问题
- 正确处理：
  - 这组证据更支持：
    - baseline 的
      `fused_hidden`
      自身已经接近常模板
    - decoder
      对 branch-side dynamics
      仍然有响应
    - 但当前响应会落到高频非稳态
  - 因而主病灶优先级应继续放在：
    - `branch_mean -> fused_hidden`
    - `decoder input manifold`
    - 而不是
      “decoder 已完全死掉”

### 71. 如果 user-line 与 validation 的 decoder structure probe 方向一致，就不要继续把 bypass 响应解释成 user-line 特有结构问题
- 现象：
  - user-line 与 validation3
    在同 checkpoint、
    同 gate-off 口径下，
    都表现出：
    - baseline
      `collapse_not_localized_to_waveform_decoder`
    - `fused_hidden_frame_mean`
      几乎无效
    - branch bypass
      会显著脱模，
      但同时把 centroid / high-band
      推到更高频、更刺耳区域
- 风险：
  - 可能因为 user-line
    的可听表现更刺耳，
    就继续把结构问题优先解释成：
    - user-line scaffold mismatch
    - user-line 特有 decoder route 异常
- 正确处理：
  - 当前更准确的表述应是：
    - 这是一类
      checkpoint-native
      的结构响应，
      user-line 与 validation
      只是不同观测面
  - 下一步不应优先投入：
    - 只面向 user-line
      的 decoder 小修
    - 只面向 user-line
      的 structure 解释
  - 而应继续回到：
    - fusion 为何把系统压进坏 manifold
    - 以及这块 manifold
      如何限制后续 decoder handoff

### 72. 对 plain-fusion baseline，主坍缩如果已经定位到 `fusion.0 Linear` 与 `fusion.3 Linear`，就不要再回头抠 `GELU / LayerNorm / gate`
- 现象：
  - user-line 与 validation3
    的 fusion 子阶段 probe
    都表现出：
    - 第一大模板化跳变在
      `fusion.0 Linear`
    - 第二跳变在
      `fusion.3 Linear`
    - `gelu_to_layernorm_template_gap`
      反而接近 `0` 或略负
- 风险：
  - 容易因为
    `LayerNorm`
    会改尺度、
    gate 也会放大听感包络，
    就继续怀疑：
    - `LayerNorm` 小参数
    - `GELU` 细节
    - gate / OLA 局部语义
- 正确处理：
  - 当前更准确的优先级应是：
    - plain fusion backbone
      的首层与末层线性投影
    - 以及结构性替代候选
  - 在这个阶段继续抠
    `GELU / LayerNorm / gate`
    都属于偏离主方向

### 73. 如果更强 backbone 候选已经稳定把 user-line 拉离 plain-fusion 的纯 buzz 坏 manifold，就不要继续把时间花在 plain baseline 局部修补上
- 现象：
  - `branch_mean_contrast_residual_v1 + residualshapecond`
    在 user-line 固定三条 pure buzz
    上已表现出稳定转移：
    - `branch_mean_to_fused_template_cosine_gap`
      `0.073843 -> 0.001379`
    - `waveform_frame_logits_template_cosine_mean`
      `0.999641 -> 0.994119`
    - `decoded_no_gate template`
      `0.993580 -> 0.984637`
- 风险：
  - 可能因为 plain baseline
    已经研究得很多，
    就继续在它上面做：
    - gate tweak
    - decoder tweak
    - 小的 normalization patch
- 正确处理：
  - 一旦更强候选已经证明
    能把 user-line 拉离原坏 manifold，
    主线就应切过去
  - 下一步应直接研究：
    - 候选线剩余的
      `envelope-following`
    - 而不是继续修
      已经确认落后的 plain baseline

### 74. 如果候选线的 residual `envelope-following` 已经收敛到 acoustic-state 家族，就不要再回到 conditioning/event 家族做大把零化试错
- 现象：
  - 在 user-line 候选线的 family-level handoff probe 上：
    - `conditioning_family = zero`
      会把系统直接推向
      更高频、更失控的坏区
    - `event_family = zero`
      会让
      `activity_corr`
      更高
    - `acoustic_state_family = zero`
      才会把
      `activity_corr`
      明显压低
- 风险：
  - 因为旧 native probe
    曾提示
    `conditioning_zero`
    影响很强，
    就继续把 user-line 剩余问题
    误写成：
    - conditioning family 主故障
    - event family 主故障
- 正确处理：
  - 当前 user-line 候选线
    的 residual 主问题
    应收敛到：
    - `acoustic_state_family`
  - 后续若继续零化，
    也应只在这个家族内部
    做最小必要拆分

### 75. 如果 `aper / energy` 清零既能压低 `activity_corr`，又会把系统拉回更模板化区域，就不要把下一步误写成“直接去掉这两个控制”
- 现象：
  - `aper = zero`
    会把
    `decoded_no_gate activity_corr`
    从
    `0.519889`
    拉到
    `0.217405`
  - `aper + E_log_rms_norm = zero`
    还能把它进一步拉到
    `0.141311`
  - 但同时：
    - `decoded_no_gate template`
      会回升到
      `0.988699 / 0.988933`
- 风险：
  - 很容易把这组结果误解成：
    - 这两个控制就是坏的
    - 训练上直接删掉就行
- 正确处理：
  - 这组结果更说明：
    - `aper / energy`
      同时在承载：
      - residual envelope-following
      - 一部分 anti-template 动态
  - 因而下一步应追求：
    - 去耦
  - 而不是：
    - 直接硬清零

### 76. 如果 `reference_mean` 能压低 `activity_corr`，而 `reference_affine_match` 一保留时间动态就把 `activity_corr` 和 brightness 一起抬回来，就不要把问题继续误写成静态分布失配
- 现象：
  - 在候选线 user-line handoff probe 上：
    - `aper = reference_mean`
      把
      `activity_corr`
      压到
      `0.297761`
    - 但
      `aper = reference_affine_match`
      又把它抬到
      `0.535281`
    - `energy = reference_affine_match`
      甚至到
      `0.602283`
    - `aper + energy = reference_affine_match`
      到
      `0.604880`
- 风险：
  - 很容易因为
    `reference_mean`
    看起来有效，
    就把下一步误写成：
    - 调静态均值
    - 调静态尺度
    - 做更多 reference replacement
- 正确处理：
  - 这组结果更说明：
    - acoustic-state
      的时间动态本身
      在驱动 residual
      envelope-following
    - 静态 replacement
      只是通过抹掉动态
      暂时压住问题
  - 因而下一步应优先追：
    - 动态去耦
    - 时序形状约束
  - 而不是继续扩大
    静态 reference 对照

### 77. 如果 `time_shuffle` 能在保住 anti-template 的同时明显压低 `activity_corr`，就不要再把 residual 主故障写成“需要去掉 acoustic-state”
- 现象：
  - 在候选线 user-line handoff probe 上：
    - `aper = time_shuffle`
      达到：
      - `decoded_template = 0.983125`
      - `activity_corr = 0.259761`
    - `aper + energy = time_shuffle`
      达到：
      - `decoded_template = 0.981053`
      - `activity_corr = 0.101686`
  - 而对照组：
    - `aper + energy = zero`
      是
      `0.988933 / 0.141311`
    - `aper + energy = reference_mean`
      是
      `0.990502 / 0.050668`
- 风险：
  - 很容易因为
    `zero / reference_mean`
    也能压
    `activity_corr`，
    就继续把下一步写成：
    - 去掉 acoustic-state
    - 或把 acoustic-state 压成静态常量
- 正确处理：
  - `time_shuffle`
    更说明：
    - 问题核心是
      `aper / energy`
      与当前 activity
      的时间对齐
    - 不是这些控制本身
      必须被删除
  - 因而下一步应优先研究：
    - 对齐约束
    - 动态去耦
    - 而不是控制删除

### 78. 如果 source scaffold 自己就已经在 `energy / aper*energy` 上带有偏高的零延迟 envelope 耦合，就不要再把问题简化成“checkpoint 独自制造了一切”
- 现象：
  - 在 user-line vs Stage5 reference 的
    acoustic temporal alignment probe 上：
    - `energy -> frame_rms`
      的 user-line 均值
      从
      `0.787623`
      抬到
      `0.872423`
    - `aper*energy -> frame_rms`
      的 user-line 均值
      从
      `-0.317557`
      推到
      `-0.030862`
- 风险：
  - 很容易因为
    waveform handoff / decode
    的坏听感最后出现在
    checkpoint downstream，
    就把整个根因都写成：
    - checkpoint 单独失控
- 正确处理：
  - 当前更准确的写法应是：
    - source-derived scaffold
      已经把一部分
      危险的即时 envelope 耦合
      带高了，
      尤其是
      `energy`
      与
      `aper*energy`
    - checkpoint downstream
      再把这条耦合
      放大成可听残差
  - 因而下一步应追：
    - 上游对齐约束
    - 而不是只在下游
      做消费侧补丁

### 79. 如果 `energy = time_shuffle` 只能拿到部分收益，而 `aper + energy = time_shuffle` 明显更强，就不要把下一步误写成“只修 energy 就够了”
- 现象：
  - `energy = time_shuffle`
    只能把
    `activity_corr`
    从
    `0.519889`
    压到
    `0.367678`
  - 但：
    - `aper = time_shuffle`
      到
      `0.259761`
    - `aper + energy = time_shuffle`
      到
      `0.101686`
- 风险：
  - 因为 source-vs-reference
    probe 已经显示
    `energy`
    是更稳定的上游异常项，
    就把下一步直接收缩成：
    - 只改 energy
- 正确处理：
  - 当前更合理的写法应是：
    - `energy`
      是优先入口
    - 但 residual EF
      的最终主承载
      仍需要和
      `aper`
      联动处理
  - 所以下一步应追：
    - `energy`
      为主、
      `aper`
      联动的去耦方案

### 80. 如果 `periodic_E_log_rms_norm` 打断会更坏，而 `noise_E_log_rms_norm` 打断会明显变好，就不要把下一步再泛写成“整条 energy family 约束”
- 现象：
  - `periodic_E_log_rms_norm = time_shuffle`
    会把
    `activity_corr`
    从
    `0.519889`
    拉到
    `0.556154`
  - `noise_E_log_rms_norm = time_shuffle`
    则把它压到
    `0.310713`
  - `aper + noise_E_log_rms_norm = time_shuffle`
    还能进一步压到
    `0.012374`
- 风险：
  - 很容易因为旧结论里
    写的是
    `energy`
    这个家族名，
    就把训练候选继续泛写成：
    - 改 energy family
    - 周期支和噪声支一起动
- 正确处理：
  - 当前应明确区分：
    - periodic 支能量
      不是当前优先入口
    - 真正该优先约束的是：
      - `noise_E_log_rms_norm`
  - 所以下一步应直接写成：
    - `noise energy + aper`
      联动去耦

### 81. 如果候选已经能被 package 物化并被现有 training loop smoke 跑通，就不要再把它停留在“只有 probe 结论”的状态描述上
- 现象：
  - 新命令
    `materialize-offline-mvp-teacher-first-stage5-input-variant-dataset`
    已经能物化：
    - `aper=time_shuffle`
    - `noise_E_log_rms_norm=time_shuffle`
  - 且现有
    `run-offline-mvp-nores-vocoder-dataset-training-loop`
    已在该变体索引上
    跑通了
    `1 step`
    CPU smoke
- 风险：
  - 继续把主线写成：
    - 还在纯分析阶段
    - 还没有训练入口
- 正确处理：
  - 当前更准确的状态应是：
    - 候选已进入
      “可直接发起训练”
      阶段
  - 下一步应优先考虑：
    - 小规模正式训练候选
    - 而不是继续只做文档化分析

### 82. 如果某个 `time_shuffle` family 在 probe 里显著压低 residual EF，不要直接把它固化成 full-package 训练输入
- 现象：
  - `aper + noise_E_log_rms_norm = time_shuffle`
    在 user-line probe
    上曾把
    `activity_corr`
    压到
    `0.012374`
  - 但把这件事
    直接写成
    fullsplit package 输入后，
    正式训练得到的新 checkpoint
    虽然 validation loss
    略优，
    却在：
    - user-line fixed triplet
    - 原始 Stage5 native validation3
    两侧一起回退成
    更亮、更模板化的明显 buzz
- 风险：
  - 容易把
    probe 中的
    “打断某个坏耦合”
    误判成：
    - 这个打断后的分布
      就应该成为训练输入真分布
- 正确处理：
  - `time_shuffle`
    目前更适合作为：
    - 诊断工具
    - 上限参考
    - 或训练时的软约束启发
  - 不应直接被固化成：
    - 全量 package 输入替换
    - inference-time 真实语义
  - 下一步更合理的是：
    - 保持原始 scaffold
      分布，
    - 改做
      正则化、
      软扰动、
      或只作用于内部表示的去耦
### 2026-03-27 补充坑点：全局 acoustic corrreg 不能因 user-line 局部改善就直接升格
- 现象：
  - 在原始 fullsplit 数据集上加入
    `waveform_frames -> E`
    和
    `waveform_frames -> aper*E`
    的超额零延迟相关正则以后，
    objective 会变好，
    user-line 的 `template / activity_corr`
    也会局部下降。
- 风险：
  - 很容易把这类结果误写成
    “主方向已确定，只差继续调权重”。
  - 但当前真实回投结果是：
    - user-line 亮度变坏
    - Stage5 native validation3 重新回到 `auto_reject 3/3`
- 正确处理：
  - 这条线只能保留为“方向性证据”，不能保留为当前主训练路线。
  - 在大方向未定前，禁止继续围绕
    `global E / global aper*E corrreg`
    做局部小 sweep。
  - 下一步必须上收到
    `branch-specific / lag-aware / target-relative`
    级别，而不是继续在全局 zero-lag 权重上抠细节。
### 2026-03-27 补充坑点：把 zero-lag corrreg 升级成最终输出上的 lag-aware corrreg，仍不足以成为主线
- 现象：
  - 在 strongest backbone 上把上一轮
    `global zero-lag excess`
    升级为
    `noise-family center-weighted lag-profile excess`
    以后，
    objective 仍然很好，
    user-line 的 `template / activity_corr`
    还会继续小幅下降。
- 风险：
  - 很容易把这种结果写成：
    - “大方向已经确定，只差继续调 lag window / 权重”
  - 但当前正式回投结果是：
    - user-line brightness 仍未回到 strongest candidate
    - Stage5 native validation3 依旧 `auto_reject = 3/3`
    - 相比上一轮全局 corrreg，
      native `rms_corr / centroid_gap / high_band_gap`
      甚至略差
- 正确处理：
  - 不能继续围绕
    `noise_energy_frame_rms_lagcorr_excess`
    和
    `noise_aper_energy_frame_rms_lagcorr_excess`
    做局部 sweep。
  - 这说明问题不只是：
    - “最终输出的 frame-RMS 与 acoustic-state 的近零延迟曲线过强”
  - 下一步必须继续上收到：
    - noise-family 内部表示
    - decoder interface / handoff substage
    - 或更强的 `shape-aware / substage-aware` temporal target
### 2026-03-27 补充坑点：不要把剩余 envelope-following 继续归因到 fusion 或 decoder_hidden 之前
- 现象：
  - strongest candidate 上新补的
    `stage temporal coupling probe`
    已经把 noise-family controls
    沿着：
    - `noise_hidden`
    - `branch_mean_hidden`
    - `fused_hidden`
    - `decoder_hidden`
    - `waveform_decoder_base_logits`
    - `waveform_residual_shape_delta`
    - `waveform_frame_logits`
    - `waveform_frames`
    - `decoded_no_gate`
    做了统一的绝对零延迟耦合定位。
  - 当前最大 jump
    已稳定落在：
    - `decoder_hidden -> waveform_decoder_base_logits`
  - 其中：
    - `aper` / `aper * noise_E`
      更像 raw waveform head 自身在放大
    - `noise_E`
      的峰值则更高地落在
      `waveform_residual_shape_delta`
- 风险：
  - 如果还把剩余故障继续写成：
    - fusion 残留没修干净
    - `decoder_hidden` manifold 本体还在主导
    - 或 output-side `frame_rms corrreg` 再调一下就能解决
  - 后续实验就会重新退回：
    - 上游小修
    - 末端输出损失小 sweep
    - 而错过真正的 output-head / residual-shape 接口
- 正确处理：
  - 当前应把主落点更新为：
    - `waveform_decoder(decoder_hidden)`
    - `residual_shape_branch_condition_delta`
  - 后续训练/结构实验要优先围绕：
    - output head 自身的 acoustic-state 放大
    - residual-shape delta 对 `noise_E`
      的进一步峰值放大
  - 在没有新证据前，禁止再把主时间花回
    `fusion`、`decoder_hidden` 之前，
    或最终输出上的 corrreg 小权重扫描。
### 2026-03-27 晚间补充坑点：更强的 output-head active-template 与 abs-zero-lag 约束，不等于已经补上 anti-brightness
- 现象：
  - 在 `docs/439`
    否决较弱的
    output-head lagcorr route
    之后，
    已继续跑过更强的
    headstruct 候选：
    - `waveform_decoder_base_logits_active_template`
    - `waveform_decoder_base_logits_aper_abs_zero_lag_corr`
    - `waveform_decoder_base_logits_noise_energy_abs_zero_lag_corr`
    - `waveform_residual_shape_delta_noise_energy_abs_zero_lag_corr`
  - 但无论是：
    - `raw_additive_v1`
    还是：
    - `shape_only_energy_debiased_v1`
    最终都仍然回到
    native `auto_reject = 3/3`
- 风险：
  - 很容易把“已经直接约束到 output head”
    误写成：
    - 这条线只差再调点权重
  - 但当前事实是：
    - 如果没有显式 anti-brightness，
      它仍然会以别的形态坏掉
- 正确处理：
  - 当前不能继续围绕
    `active-template`
    与
    `abs-zero-lag`
    单独做小 sweep
  - 下一步必须显式补上：
    - brightness / high-band
      这类直接 target

### 2026-03-27 晚间补充坑点：`shape_only_energy_debiased_v1` 不是当前 residual-shape consumer 的默认优选
- 现象：
  - 在完全相同的 stronger headstruct loss 组合下，
    把 residual-shape consumer
    从：
    - `raw_additive_v1`
    换成：
    - `shape_only_energy_debiased_v1`
    并没有转正，
    反而让：
    - user-line
    - native validation3
    一起更差
- 风险：
  - 因为它名字上更像“更受限、更合理”，
    很容易被写成默认更优结构
- 正确处理：
  - 在没有新证据前，
    不要再把
    `shape_only_energy_debiased_v1`
    当成当前 output-head 主线的默认 consumer
  - 当前更合理的策略是：
    - 回到 raw 版
    - 再补更直接的
      anti-brightness target

### 2026-03-27 晚间补充坑点：当 decode 默认已经提升为 `post_ola_envelope` 时，不要只看 `decoded_no_gate` 就匆忙否决候选
- 现象：
  - 新的
    `headstruct + base_logits high_band_excess`
    候选上，
    `decoded_no_gate`
    仍然不是最终听感等价物，
    但：
    - native validation3
      已从
      `auto_reject = 3/3`
      恢复到
      `0/3`
    - `waveform_handoff`
      也首次显示：
      - `likely_failure_already_present_by_frames_before_gate = false`
- 风险：
  - 如果还沿用旧阶段那种
    “先看 no-gate，
    no-gate 不顺眼就直接否掉”
    的习惯，
    会把已经进入可治理状态的候选
    过早丢掉
- 正确处理：
  - 在当前 promoted decode 语义下，
    需要联合看：
    - `decoded_post_ola_gate`
    - native `auto_reject`
    - `waveform_handoff diagnosis`
  - 只有当这些信号一起坏时，
    才应直接否决

### 2026-03-27 深夜补充坑点：`launch-audio-audit-gui` 对 compare bundle 不能只传目录，必须传 summary json
- 现象：
  - 本轮给
    `launch-audio-audit-gui`
    直接传：
    `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/`
    时，
    GUI
    会去找：
    `proxy_audio_export.json`
    并直接报错
  - 但把参数改成：
    `teacher_first_vc_audible_compare_bundle.json`
    本体后，
    GUI
    可以正常启动并完成 smoke
- 风险：
  - 很容易误把这个现象写成：
    - compare bundle
      不支持 GUI
    - 或当前听审入口损坏
- 正确处理：
  - 对 teacher-first audible compare bundle，
    应传：
    `--bundle <...>/teacher_first_vc_audible_compare_bundle.json`
  - 不要只传 bundle 目录本身

### 2026-03-27 深夜再次补充坑点：量化改善成“带音调变化的 buzz”时，不能继续把它当可治理主候选
- 现象：
  - `output_head_high_band_bhb01`
    在量化上确实比旧 strongest
    更暗，
    也摆脱了直接坏死型 native auto-reject，
    但人工听审仍明确给出：
    - 纯 buzz
    - 只是多了一点明显音调变化
- 风险：
  - 因为它相对前序候选
    的确“看起来更好”，
    很容易继续沿这条线做：
    - 同层权重微调
    - 再发一轮听审
    - 或默认进入 GUI 打分
- 正确处理：
  - 一旦主观结论仍是
    pure buzz，
    即使 buzz
    变成了
    tonal buzz，
    也应把这条线记为失败
  - 下一步应上收到：
    - 为什么只压亮度，
      还不够产生人声结构
    - 为什么 residual jump
      仍停在
      `decoder_hidden -> waveform_decoder_base_logits`

### 2026-03-27 深夜再次补充坑点：pure-buzz 判别实验不该默认走 GUI 量化打分
- 现象：
  - 本轮这类实验真正需要用户回答的，
    只是：
    - 还是不是 pure buzz
  - 并不需要一套完整的 GUI 分项打分
- 风险：
  - 如果默认把这类实验都包装成 GUI 打分，
    一方面会增加操作成本，
    另一方面也容易让流程看起来比结论本身更重
- 正确处理：
  - 对 pure-buzz / non-pure-buzz
    的快速门槛判别，
    默认直接交：
    - 最小 wav 目录
    - 简短对比说明
  - 只有在已经确认
    “不再是 pure buzz”
    之后，
    才值得升级到更细的 GUI 听审
### 2026-03-27 深夜继续补充坑点：把 `aper * noise_E` 的 base-logits jump 压平，不等于 output-head residual 已被解决
- 现象：
  - 新候选
    `output_head_bpae01`
    直接在
    `waveform_decoder_base_logits`
    上新增
    `aper * noise_E`
    的
    `abs_zero_lag_corr`
    约束后，
    旧的 product jump
    确实被压平了：
    - `decoder_hidden -> base_logits`
      从
      `0.270616 -> 0.696298`
      变成
      `0.376493 -> 0.391278`
- 风险：
  - 很容易把这个结果误写成：
    - output-head 主病灶已经修掉
    - 剩下只是听感收口
  - 但当前正式 probe 同时显示：
    - `aper * noise_E`
      的新峰值转到了
      `waveform_residual_shape_delta = 0.434913`
    - `aper`
      和
      `noise_E`
      单项在
      `waveform_decoder_base_logits`
      上反而更强
    - user-line
      `template`
      还从
      `0.870602`
      回升到
      `0.887733`
- 正确处理：
  - 当前应把这类结果写成：
    - residual coupling
      被重分配了，
      不是被消灭了
  - 下一步不能直接围绕
    `bpae01`
    做 promoted 或 GUI 化，
    也不能把它当成
    “只差一点点”的新主候选
  - 必须继续联合看：
    - residual-shape interface
    - 单项
      `aper / noise_E`
      在 output head
      的重新放大
    - 以及最小人工听感
      是否仍是
      pure buzz
### 2026-03-27 深夜最终补充坑点：如果新候选主观上与已失败候选几乎无差别，就不要因为量化继续变好而保留它
- 现象：
  - `output_head_bpae01`
    相比
    `bhb01`
    在量化上继续压低了：
    - centroid
    - high-band
    - native validation3
      的 brightness gap
  - 但本轮人工听审已明确给出：
    - 两者几乎完全一致
    - `segment_0061`
      完全是 buzz
    - `peak_011`
      完全是 pure buzz
- 风险：
  - 很容易因为
    “数值还在继续变好”
    就把这类候选继续写成：
    - 值得 promoted
    - 值得再听一轮
    - 或值得继续扫同层权重
  - 这会让主线长期停留在
    pure-buzz 家族内部打转
- 正确处理：
  - 一旦用户明确给出：
    - 新旧候选几乎无差别
    - 且仍然完全是 pure buzz
  - 就应把该候选直接记为失败，
    不再因为量化继续改善而保留
  - 后续应上收到：
    - 为何这些量化改善
      不能转化为 voice structure
    - 而不是继续做
      same-family
      微调

### 2026-03-27 深夜最终补充坑点：线性频谱图可作为 pure-buzz 判停的辅证，但不能替代听审
- 现象：
  - 本轮用户补充的线性频谱图里，
    `bpae01 / bhb01`
    交替播放片段表现为
    等距直线型稳定结构，
    而 target
    明显同时存在：
    - unvoice 的宽带砂状区
    - voice 的低频共振峰
- 风险：
  - 可能走向两个极端：
    - 完全不看频谱，
      失去一种便宜的辅助证据
    - 或把频谱图当成
      可以替代听审的最终裁判
- 正确处理：
  - 对
    pure-buzz / non-pure-buzz
    的快速门槛判别，
    线性频谱图可以作为：
    - 听审后的辅助佐证
  - 但最终 stop/go
    仍以人工听感为准
  - 当听感已经明确失败，
    且频谱图也显示候选仍是
    稳定直线型 buzz，
    就不再保留该路线
### 2026-03-27 深夜继续补充坑点：如果 `base_logits_only` 已几乎等于 baseline，就不要继续把 residual-shape 写成当前主承载层
- 现象：
  - output-head 子阶段 structure probe
    已经在 user-line
    与 native validation3
    两边都显示：
    - `waveform_decoder_base_logits_only`
      与 baseline
      几乎重合
    - `waveform_residual_shape_only`
      则变成更亮、更高频、
      更模板化的纯 buzz
- 风险：
  - 很容易沿着之前
    `438/444`
    的定位，
    继续把问题写成：
    - residual-shape interface
      仍是主病灶
    - 或 residual-shape
      里也许还藏着没听出来的语音结构
- 正确处理：
  - 当前更准确的说法应是：
    - residual-shape
      当然还在放大某些坏成分，
      但它不是当前可听结构的主要承载者
    - baseline
      几乎就是
      `base_logits`
      本体
  - 后续主线应转向：
    - `waveform_decoder(decoder_hidden)`
      自身为什么只形成
      tonal/pure buzz
    - 而不是继续优先修
      residual-shape

### 2026-03-27 深夜继续补充坑点：如果 `residual_shape_only` 单独听起来是更亮、更直线型的 pure buzz，就不要把它当作“潜在语音结构支”
- 现象：
  - 在两侧 structure probe
    里，
    `waveform_residual_shape_only`
    都稳定表现为：
    - `decoded_template ≈ 0.9998`
    - `centroid ≈ 11k ~ 12k`
    - `high_band ≈ 0.81 ~ 0.83`
  - 这说明它本身更像：
    - 高频模板化 buzz 支
  - 而不是：
    - 被主分支埋住的语音结构支
- 风险：
  - 容易因为它名字上像
    residual shape，
    就继续假设：
    - 这里面也许有 formant/noise shape
    - 只是混合方式不对
- 正确处理：
  - 在没有新证据前，
    不再把当前 residual-shape
    默认视为潜在的 speech-structure carrier
  - 若未来还要继续用它，
    也必须把目标改写成：
    - 显式 shape-aware
      结构目标
  - 而不是继续假设
    它自己天然就带着语音结构
