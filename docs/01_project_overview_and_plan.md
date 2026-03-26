# 项目总览与实施计划

## 文档定位
- 本文档只保留：
  - 项目目标
  - 当前阶段状态
  - 已确认的主线结论
  - 当前下一步
- 详细实验流水、逐轮追记、旧阶段长历史不再继续堆进这里。
- 2026-03-26 归档快照：
  - `docs/archive/01_project_overview_and_plan_snapshot_20260326.md`

## 项目目标摘要
- 基于 `initial_design.md`，当前目标是构建一个兼顾离线高质量与在线低延迟的工业化变声系统。
- 核心控制链设计态为：
  - `z_art`
  - `e_evt`
  - `F0 / vuv / aper / E`
  - 被严格限权的 `r_res`
- 当前原则保持不变：
  - 无残差主干必须先成立
  - 不允许把系统做成披着可解释外壳的神经编解码器
  - 在线流式闭环晚于离线主干验证

## 当前仓库结构
- `initial_design.md`
  - 主设计稿。
- `initial_design_judg.md`
  - 风险与去魅评估。
- `manage.py`
  - 统一命令入口。
- `python.exe`
  - 项目固定解释器。
- `src/v5vc/`
  - 项目源码。
- `configs/`
  - 配置与模板。
- `reports/`
  - 训练、评估、导出产物。
- `docs/`
  - 主文档、报告和归档。

## 当前阶段总判断

### 1. 上游 `Stage3 / teacher-label / target-state` 仍在产出真实正向信息
- 当前最新、最强的 generation-side reference 是：
  - `teacher_e_evt_bridge_mode = acoustic_directional_targetstate_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
- 依据：
  - `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
- 关键结果：
  - full-validation step12：
    - `loss_total = 1.732503 -> 1.648929`
    - `loss_total_semantic_disabled_reference = 1.57394 -> 1.501041`
    - `loss_teacher_event = 0.504001 -> 0.449996`
    - `loss_teacher_event_prior = 0.728577 -> 0.695983`
  - full-validation step24：
    - `loss_total = 1.157747 -> 1.044122`
    - `loss_total_semantic_disabled_reference = 1.037303 -> 0.939578`
    - `loss_teacher_event = 0.417492 -> 0.332711`
    - `loss_teacher_event_prior = 0.548517 -> 0.489258`

### 2. 当前旧 `Stage5 no-res downstream` 不是有效承接层
- 这不是猜测，而是多轮 fail-fast 结论：
  - `docs/359_stage5_c3_downstream_eevt_overfit24_fail_fast_report.md`
  - `docs/361_stage5_eevt_target_contract_supervision_route_fail_fast_report.md`
  - `docs/366_stage5_teacher_eevt_acoustic_bridge_downstream_fail_fast_report.md`
- 当前旧 route 的稳定现象是：
  - package / contract / supervision 可以接通
  - 但输出仍落入 `template-buzz + envelope-following` 假解
  - automatic buzz gate 长期给出 `all_records_auto_reject = true`

### 3. 当前问题不是“再补一个小参数”
- 当前已正式停止的线包括：
  - Stage5 decode-side 微调
  - waveform/objective 小 sweep
  - target-only static semantic consumer
  - target timing consumer
  - source parity consumer
  - teacher-first inference-only 小修
  - hidden/fused-hidden imitation 小权重线
- 这些线共同说明：
  - 数值改善不等于人声 emergence
  - 当前主问题在 contract / handoff 层级，而不是末端小修

## 当前主线

### 主线 A：继续强化上游 teacher-label / target-state 资产
- 当前参考点：
  - `acoustic_directional_targetstate_bridge_v1`
- 当前优先动作：
  - 继续做 generation-side bridge / target-state 结构升级
  - 不回头扫旧 `acoustic_contextual` 小 patch
  - 不回头扫 loss-side imitation 微调

### 主线 B：重新识别真正有效的 downstream handoff layer
- 当前正式口径：
  - 不再把新的上游 candidate 机械送回当前已判死的旧 `Stage5 no-res downstream`
- 但这不等于：
  - 永久停止一切 Stage5 验证
- 更准确的下一步应是：
  - 先形成 `downstream handoff candidates` 清单
  - 当前最高优先级候选是：
    - `Stage3 student-control packet v1`
  - 这条候选现在已经有最小实现与 smoke export
  - 并把
    - `proxy-acoustic / proxy-audio`
    作为进入新 Stage5 route 前的 cheap screen
  - 当前 cheap screen 结论是：
    - `packet v1` 已成立
    - 但结构增益还不够硬，暂不足以直接开启新的 Stage5 adapter
  - 每个候选都必须写清：
    - 所在层级
    - 预期承接机制
    - 最小验证实验
    - stop rule

## 当前推荐下一步
1. 以 `acoustic_directional_targetstate_bridge_v1` 作为新的 Stage3 reference 固定口径。
2. 不再继续重跑当前旧 `Stage5 no-res downstream` 作为默认承接层。
3. 当前新的默认实施顺序是：
   - 先用已实现的 `Stage3 student-control packet v1`
   - 再做 `proxy-acoustic / proxy-audio` cheap screen
   - 然后用 `named-control readiness negative gate` 卡住尚未完成的 named controls
   - 当前 screen 与 gate 的合并结论仍是：
     - Stage3 内部监督继续正向
     - 但 `F0 / vuv / aper` 仍未到 handoff-ready
   - 因此下一步继续补 `target-state / named-control generation-side completion`
     而不是直接进入新的 Stage5 adapter/scaffold smoke
4. 当前候选清单报告：
   - `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
5. 当前实现与 smoke：
   - `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
6. 当前关键边界：
   - `e_evt` 已可按 named-control candidate 导出
   - 但 `F0 / aper / E` 仍是 proxy/control status，不应误写成已完成的 Stage5-ready contract
7. 当前 cheap screen 报告：
   - `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
8. `student_control_packet -> Stage5` 的最小 adapter 现已补齐，而且已经成功导出真实 `decoded.wav`：
   - `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
   - 当前事实不再是“还没到 Stage5”，而是：
     - adapter 已接通
     - best Stage3 packet 已完成真实 decoded smoke
     - 但第一条 smoke 样本就被 `auto_reject_obvious_buzz` 直接否定
   - 因此当前口径应改成：
     - `student packet` 这条线已经具备真实 end-to-end fail-fast 能力
     - 但 `vuvbalancedgate48` 这版 current best packet 仍不值得扩成试听包
9. `packet calibration audit` 已完成，但“直接往 Stage3 loss 注入 deterministic target acoustic state”这条线已失败：
   - `docs/373_stage3_explicit_target_acoustic_state_supervision_ab_fail_report.md`
   - 当前结论是：
     - local state loss 可下降
     - 但共享主指标变差
     - 因此不继续扫 `teacher_f0_state / teacher_vuv_state / teacher_aper_state / teacher_energy_state`
10. `student_control_packet` 现在新增了 named-control negative gate：
   - `docs/374_stage3_student_control_packet_readiness_gate_report.md`
   - 当前最新 target-state bridge checkpoint 的结论是：
     - `e_evt / z_art` 可保留
     - `F0 / vuv / aper / E` 仍全部 auto-reject
     - 因此当前仍不允许开启新的 Stage5 handoff route
11. `teacher_labels` 现在也已完成 `target-state` 合同补齐：
   - `docs/375_stage3_teacher_label_target_state_contract_completion_report.md`
   - 当前新的 teacher asset 基线是：
     - `teacher_labels_eevt_directional_targetstate_round1_1`
   - Stage3 batch 现已优先读取 teacher payload 内置 `target_f0_hz / target_vuv / target_aper / target_energy`
12. 在这套 target-state-complete teacher asset 之上，当前 generation-side 最新 reference 已升级为：
   - `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
   - 当前结论是：
     - Stage3 `12-step / 24-step full-validation` 都继续正向
     - 但 `student_control_packet` 的 readiness gate 仍然不给放行
     - 所以这版收益暂时仍停留在 Stage3 内部监督层
13. 在新的 handoff family 通过更强 cheap screen 前，不再新增：
  - Stage5 同层 decode 小实验
  - Stage5 同层 semantic/timing consumer 小实验
  - 同类 objective / weight 微扫
14. 当前新的默认下一步改为：
  - 不继续做 naive direct state loss injection
  - 基于新的 `teacher_labels_eevt_directionaltargetstatebridge_round1_1`
    继续做更结构化的 `target-state / named-control generation-side completion`
  - 并以 `named-control readiness negative gate` 作为新的下游前置门禁
  - 尤其避免把“packet 可导出”或“local state MAE 下降”误判成“已经值得开新 Stage5 route”
15. 当前新的 Stage5 fail-fast 顺序已经改成：
  - 先过 `named-control readiness negative gate`
  - 若仍有端到端潜力，再走 `student_control_packet -> minimal Stage5 adapter -> real decoded.wav smoke`
  - 若第一条 best-sample decoded 已经 `auto_reject_obvious_buzz`，
    就不再默认扩成多条试听包
16. `minimal Stage5 adapter` 这条线本轮也已进一步定准：
  - `docs/390_stage5_adapter_contract_mismatch_diagnosis_and_next_route_report.md`
  - 当前 best Stage5 checkpoint 实际是旧 `v2/event_probs` 承接层，不是显式 `e_evt` checkpoint
  - 更关键的是，student 与 native teacher 的差异主病灶不在 periodic branch，
    而在 noise branch 前 8 维 event family 的分布错位
  - 因此下一步不再修 adapter 本身，而转回 Stage3 generation-side 的 event 维度分布校准
17. 本轮又新增了一层更硬的负结论：
  - `docs/377_stage3_named_control_handoff_ablation_fail_report.md`
  - 当前已证伪：
    - `named_control_proxy_target_family = deterministic_target_state_v1`
    - `detach_frontend_named_controls_for_student`
    - `detach_shared_hidden_for_student`
  - 所以下一步不再扫这些轻量开关，而是上到更明确的
    `frontend/control branch split`
15. `frontend/control branch split v1` 也已做过 fail-fast：
  - `docs/378_stage3_parallel_control_branch_fail_fast_report.md`
  - 当前结论是：
    - Stage3 主指标可以继续改善
    - 但 packet readiness 仍不开
    - `F0` 甚至出现 raw proxy correlation 反号
  - 因此这条线不能直接升格为新的 reference
  - 如果继续，只能上到更强的
    `control-specific head family / bounded F0 parameterization`
16. `bounded F0 parameterization` 也已做过同层 fail-fast：
  - `docs/379_stage3_parallel_control_branch_bounded_f0_fail_report.md`
  - 当前结论是：
    - 它能把 `F0` 数值收进物理边界
    - 但不能修掉 raw proxy correlation 反号
    - readiness gate 依然完全不开
  - 所以下一步不再扫 `bounded/unbounded` 小变体，
    而只能上到更强的 `control-specific head family / explicit F0 control-state branch`
17. `explicit F0 control-state branch` 也已完成 fail-fast：
  - `docs/380_stage3_explicit_f0_control_state_branch_fail_report.md`
  - 当前结论是：
    - 相对 `bounded F0` 基本打平
    - `teacher_f0_state` 没有变好
    - `loss_log_f0_correction_l1` 明显变差
    - packet readiness 仍完全不开
    - `F0` raw proxy correlation 继续稳定为负
  - 所以下一步不再扫单独 `F0 branch` 的层数、delta 上界或小权重，
    而只能上到更完整的 `control-specific head family / explicit control-state branch`
18. 更完整的 `control-specific head family` 也已完成 fail-fast：
  - `docs/381_stage3_control_specific_head_family_fail_and_coarse_f0_sign_diagnosis_report.md`
  - 当前结论是：
    - Stage3 主指标继续改善
    - 但 packet readiness 仍完全不开
    - `vuv / energy` 有局部改善，`aper / F0` 仍拖后腿
    - 更关键的是：`F0` 反号病灶不在 correction head，
      而在更上游的 `coarse_log_f0`
  - 所以下一步不再继续 student-side correction family 微调，
    而要转去 `coarse F0 target contract / sign-stable supervision`
19. `coarse_log_f0` 直监督已给出第一条有效恢复信号：
  - `docs/382_stage3_coarse_f0_state_supervision_partial_recovery_report.md`
  - 当前结论是：
    - Stage3 主指标略差，不能升格为新 reference
    - 但 `F0 proxy` 已首次从稳定负相关翻到正相关
    - gate 仍不开，说明这只是部分恢复
  - 因此下一步应继续留在
    `coarse_log_f0 sign-stable supervision / parameterization`
    这一层，而不是回到 student-side correction family
20. `coarse_f0` 线的分支和 horizon 已经继续收干净：
  - `docs/383_stage3_coarsef0_signstable_and_nof0corr_fail_report.md`
  - `docs/384_stage3_coarsef0_horizon_extension_and_stop_rule_report.md`
  - 当前结论是：
    - `nof0corr` 和 `teacher_coarse_f0_correlation` 都应正式停线
    - `coarse_f0_state` 到 `24-step` 已把 `coarse_log_f0` 本体翻成正相关
    - 到 `48-step`，`F0` 继续改善，但 handoff gate 仍完全不开
    - 当前瓶颈已从“F0 反号”转移到剩余 named controls 的合同完成度
  - 因此下一步不再继续同层 `F0 sign repair` 微调，
    而要转去 `vuv / aper / energy` 的 contract completion
21. `named-control` 的 calibrated audit 已把剩余瓶颈重新定位：
  - `docs/385_stage3_named_control_calibrated_audit_and_bottleneck_relocalization_report.md`
  - 当前结论是：
    - `aper` 经过 calibrated audit 后已 `3/3 ready`
    - `energy` 已 `2/3 ready`
    - 真正主瓶颈是 `vuv`，其次才是 `F0`
  - 因此后续不再把问题写成“所有 named controls 都没学到”
22. loss-side `named-control completion` 整条线应正式停线：
  - `docs/385_stage3_named_control_calibrated_audit_and_bottleneck_relocalization_report.md`
  - `docs/386_stage3_vuv_completion_loss_route_fail_report.md`
  - 当前结论是：
    - mixed `vuv + aper + energy` state loss 不值得继续
    - `vuv-only` 也不值得继续
    - 它们都没有打开 `vuv`
  - 因此下一步应转去
    `vuv contract / representation / target family`
    而不是继续扫 loss-side 小权重
23. `vuv contract / representation` 这条线上，第一条真正正向的结构候选已经出现：
  - `docs/387_stage3_vuv_balanced_gate_contract_positive_ab_report.md`
  - 当前新候选是：
    - `teacher_e_evt_v1_balanced_vuv_gate_v1`
  - 当前结论是：
    - `12-step / 24-step` full-validation 都优于 `coarse_f0_state` 基线
    - `48-step` 上总 loss 基本持平略优
    - packet cheap screen 在 `3-sample` 上连续改善
    - 扩到 `8-sample` 后，`vuv_reference_mae` 仍是 `6/8` 改善
    - 但 `vuv_ready_count` 仍只有 `1/8`，`f0_ready_count` 仍是 `0/8`
  - 因此这条线现在应升级为：
    - `vuv contract` 的新工作 reference
  - 但还不能升级为：
    - 新 Stage5 handoff route 的放行依据
24. 当前瓶颈已再次收紧：
  - `vuv balanced gate` 证明 `vuv` 方向不是死线
  - 但 handoff gate 仍不开
  - 当前更准确的说法是：
    - `vuv` 已出现真实 contract-level 正向
    - 剩余主要瓶颈重新回到 `F0`
    - 外加少量 `vuv` 长尾失败样本
  - 所以下一步不再回到：
    - `teacher_vuv_state` 小权重
    - `vuv-only` loss completion
  - 而应在固定 `balanced_vuv_gate` 的前提下，
    继续排查剩余 `F0` handoff readiness
25. 一个最小 `F0 supervision mask` 候选已经做过，并在最小 packet screen 上被判停：
  - `docs/388_stage3_f0_strong_voiced_mask_minimal_ab_and_proxy_export_report.md`
  - 当前候选是：
    - `f0_supervision_mask_family = strong_voiced_gate_v1`
  - 当前结论是：
    - `12-step` Stage3 shared 指标略优
    - 但 `3-sample` packet cheap screen 上
      `f0_proxy_reference_corr / calibrated_log2_mae`
      没有改善，整体持平略差
    - 因此这条线不进入 `24-step / 48-step`
  - 所以下一步不再继续：
    - `strong voiced` 阈值线
    - “少监督一点 F0 帧”这类 mask 微变体
  - 而要继续回到更上层的
    `F0 handoff representation / contract`
26. `teacher-student` 蒸馏现阶段已暂停，主问题先切回 native teacher 的真实 buzz：
  - `docs/391_stage5_native_teacher_buzz_recheck_and_physiology_data_assessment.md`
  - 新复核已确认：
    - 当前 best native `Stage5` checkpoint 在 validation `3-sample` 上
      `decoded.wav` 的旧 export 结论指向 `3/3 auto_reject_obvious_buzz`
    - 因此当前 buzz 不是 student 才引入的问题
    - 当前第一主故障是 native teacher route 本身
  - 但需注意：
    - `391` 已完成按修正后 export 语义的最小回补重跑
    - 统一修正口径见：
      `docs/393_stage5_export_semantics_correction_scope_and_rerun_requirements.md`
    - 回补确认见：
      `docs/394_stage5_export_semantics_rerun_confirmation_report.md`
27. 对“是否需要真实发音的生理传感器数据”的当前正式判断已固定为：
  - `不需要`
  - 原因是：
    - native teacher 当前控制链自己都还没脱离 obvious buzz
    - 当前主病灶仍在现有 `Stage5` 承接层 / waveform decode / template-collapse 假解
    - 不是“缺 articulatory ground truth”这一层
28. 因此当前主线再次收紧为：
  - 暂停 `teacher-student` 蒸馏
  - 不引入新生理数据模态
  - 优先修 `Stage5 native teacher buzz`
  - 后续最小候选应围绕：
    - waveform decoder structure
    - template-collapse 假解
    - 现有 objective / decode semantics
    而不是继续扩上游变量数
29. 当前新增一条硬门禁：
  - 若 `teacher` 线的真实输出质量仍未让用户满意，
    禁止尝试 `student` 线蒸馏
  - 只有在 native teacher 路线已经稳定摆脱明显 buzz、
    且用户确认其主观质量达到可接受区间后，
    才允许重新讨论 student 蒸馏是否值得恢复
30. native teacher 的第一条最小修复候选 `acttmpl005_delta6` 已完成 fail-fast：
  - `docs/392_stage5_native_teacher_acttmpl005_delta6_fail_fast_report.md`
  - 当前结论是：
    - 旧 export 结论指向：
      `decoded.wav` 仍然 `3/3 auto_reject_obvious_buzz`
    - 且旧 export 对照里相对当前 native baseline 明显更差，
      `spectral_centroid_gap_hz` 与 `high_band_energy_ratio_gap`
      都接近翻倍恶化
  - 因此这条 objective 组合不继续扩 horizon，
    当前 native teacher buzz 修复应改走别的更保守候选
  - 但同样需注意：
    - `392` 已完成按修正后 export 语义的最小回补重跑
    - 其相对恶化结论现已恢复为正式可用
    - 回补确认见：
      `docs/394_stage5_export_semantics_rerun_confirmation_report.md`

31. 当前主线进入新实验前，必须先完成 export/probe 语义修正后的最小回补：
  - `docs/393_stage5_export_semantics_correction_scope_and_rerun_requirements.md`
  - 当前这组最小回补已完成，确认报告见：
    - `docs/394_stage5_export_semantics_rerun_confirmation_report.md`
  - 当前正式口径是：
    - `391` 与 `392` 已恢复为当前可直接引用结论
    - `389/390` 中依赖旧 export 的部分仍只按临时结论使用，
      除非后续主线再次需要 student 对照时再补跑
32. native teacher 新补的一条 `recurrent + temporal + periodic_rms_floor=0.05`
    fullsplit24 候选也已完成 fail-fast：
  - `docs/395_stage5_native_teacher_recurrent_temporal_periodicrmsfloor005_fail_fast_report.md`
  - 当前结论是：
    - 训练 summary 虽显示这条线在动，
      但真实 `decoded.wav` 仍然 `3/3 auto_reject_obvious_buzz`
    - 而且相对当前 native baseline，
      `spectral_centroid_gap_hz`
      和 `spectral_high_band_energy_ratio_gap`
      都显著恶化
  - 因此当前不再继续：
    - `recurrent + temporal`
      同分支上的 local RMS floor / high-band / 小权重补丁
  - 下一步应先回到修正后的 native teacher baseline probes，
    再选择更保守的 teacher-side 候选
33. probe 指向的 `acttmpl005 + zero_target_flux_jitter=4.0`
    也已完成 native teacher fullsplit24 fail-fast：
  - `docs/396_stage5_native_teacher_acttmpl005_zerojitter4_fail_fast_report.md`
  - 当前结论是：
    - 新增 loss 已真实接通，并通过 1-step smoke
    - 但真实 `decoded.wav` 仍然 `3/3 auto_reject_obvious_buzz`
    - 而且相对 corrected native baseline 明显更差
  - 因此当前不再继续：
    - `zero_target_flux_jitter`
    - `active_template + zero_target_flux_jitter`
      同族小权重或同族 objective 变体
34. 指向 `fusion -> fused_hidden` 的弱正则候选
    `fused_hidden_template=0.05 + fused_hidden_delta=2.0`
    也已完成 native teacher fullsplit24 fail-fast：
  - `docs/397_stage5_native_teacher_fusedhidden_t005_d2_fail_fast_report.md`
  - 当前结论是：
    - 它比 `acttmpl005 + zerojitter4` 更接近 baseline，
      但仍然 `3/3 auto_reject_obvious_buzz`
    - 因此也不值得继续扩成同族小权重 sweep
  - 当前下一步应升级为：
    - 更直接的 `forward-path structural` native teacher 候选
    - 而不是继续叠弱 `objective-side` 或弱 `fused_hidden` penalty
35. 更直接的 `forward-path structural` 轻量候选
    `decoder_branch_mean_mix_alpha=0.25`
    也已完成 native teacher fullsplit24 fail-fast：
  - `docs/398_stage5_native_teacher_branchmix025_fail_fast_report.md`
  - 当前结论是：
    - 它与 `fused_hidden_t005_d2` 大致同量级，
      虽好于 `zerojitter4`，
      但真实 `decoded.wav` 仍然 `3/3 auto_reject_obvious_buzz`
    - 因此当前不再继续：
      - `decoder_branch_mean_mix_alpha`
        小范围 sweep
      - 同级别轻量 operating-point mix 变体
  - 当前下一步应继续上收到：
    - 更强的 `forward-path structural` native teacher 候选
    - 例如真正改变 fusion / branch-conditioned decoder 形态

## 关键参考报告
- `docs/355_post_buzz_fail_main_scheme_reevaluation_and_v2core_gap_report.md`
- `docs/356_stage3_teacher_eevt_v1_bootstrap_plumbing_and_short_loop_report.md`
- `docs/357_stage3_teacher_eevt_v1_vs_legacy_event_target_ab_short_loop_report.md`
- `docs/365_stage3_teacher_eevt_acoustic_bridge_ab_report.md`
- `docs/366_stage5_teacher_eevt_acoustic_bridge_downstream_fail_fast_report.md`
- `docs/367_stage3_teacher_fused_hidden_projection_ab_fail_report.md`
- `docs/368_stage3_teacher_eevt_directional_transition_bridge_ab_report.md`
- `docs/369_oneoff_evaluation_of_1md_recommendations.md`
- `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
- `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
- `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
- `docs/373_stage3_explicit_target_acoustic_state_supervision_ab_fail_report.md`
- `docs/374_stage3_student_control_packet_readiness_gate_report.md`
- `docs/375_stage3_teacher_label_target_state_contract_completion_report.md`
- `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
- `docs/377_stage3_named_control_handoff_ablation_fail_report.md`
- `docs/378_stage3_parallel_control_branch_fail_fast_report.md`
- `docs/379_stage3_parallel_control_branch_bounded_f0_fail_report.md`
- `docs/380_stage3_explicit_f0_control_state_branch_fail_report.md`
- `docs/381_stage3_control_specific_head_family_fail_and_coarse_f0_sign_diagnosis_report.md`
- `docs/382_stage3_coarse_f0_state_supervision_partial_recovery_report.md`
- `docs/383_stage3_coarsef0_signstable_and_nof0corr_fail_report.md`
- `docs/384_stage3_coarsef0_horizon_extension_and_stop_rule_report.md`
- `docs/385_stage3_named_control_calibrated_audit_and_bottleneck_relocalization_report.md`
- `docs/386_stage3_vuv_completion_loss_route_fail_report.md`
- `docs/387_stage3_vuv_balanced_gate_contract_positive_ab_report.md`
- `docs/388_stage3_f0_strong_voiced_mask_minimal_ab_and_proxy_export_report.md`
- `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
- `docs/390_stage5_adapter_contract_mismatch_diagnosis_and_next_route_report.md`
- `docs/391_stage5_native_teacher_buzz_recheck_and_physiology_data_assessment.md`
- `docs/392_stage5_native_teacher_acttmpl005_delta6_fail_fast_report.md`
- `docs/393_stage5_export_semantics_correction_scope_and_rerun_requirements.md`
- `docs/394_stage5_export_semantics_rerun_confirmation_report.md`
- `docs/395_stage5_native_teacher_recurrent_temporal_periodicrmsfloor005_fail_fast_report.md`
- `docs/396_stage5_native_teacher_acttmpl005_zerojitter4_fail_fast_report.md`
- `docs/397_stage5_native_teacher_fusedhidden_t005_d2_fail_fast_report.md`
- `docs/398_stage5_native_teacher_branchmix025_fail_fast_report.md`
 - `docs/399_stage5_native_teacher_branchcondadapter_fail_fast_report.md`
 - `docs/400_stage5_native_teacher_dualbranchmix_fail_fast_report.md`
- `docs/401_stage5_native_teacher_nonrecurrent_residual_decoder_family_fail_fast_report.md`
- `docs/402_stage5_native_teacher_gatemasked_spectral_target_fail_fast_report.md`
- `docs/403_stage5_native_teacher_activitygate00_nogatedrecon_fail_fast_report.md`
- `docs/404_stage5_dataset_split_builder_processpool_takeover_report.md`
- `docs/405_stage5_native_teacher_aperenergyonly_target_contract_fail_fast_report.md`
- `docs/406_stage5_native_teacher_eevttargetcontract_target_contract_fail_fast_report.md`

## 维护规则
- 新实验细节默认写入独立编号报告，不再整段追加到本文档。
- 本文档只在以下情况更新：
  - 主线判断改变
  - 当前 best reference 改变
  - 下一步策略改变
  - 文档口径需要统一修正
- 若后续再次出现超长追记，应继续归档，不回到单文件堆历史的做法。
33. native teacher 的 `fused_single + use_decoder_branch_condition_adapter`
    也已完成真实 `validation3 decoded.wav` fail-fast：
  - `docs/399_stage5_native_teacher_branchcondadapter_fail_fast_report.md`
  - 当前结论是：
    - `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline 三条样本都更差
    - 因此这条 `branchcondadapter` 结构候选也应正式停线
34. 当前 native teacher buzz 主线已连续否掉的同层弱修复包括：
  - `active_template + frame_delta`
  - `active_template + zero_target_flux_jitter`
  - `fused_hidden_template + fused_hidden_delta`
  - `decoder_branch_mean_mix_alpha`
  - `fused_single + decoder_branch_condition_adapter`
  - 因此下一步不再做同层小 penalty / 小 mix / 小 adapter 叠加
35. 当前更合理的下一条 native teacher 结构候选应是：
  - 直接改变 `waveform_decoder_mode`
  - 优先 `dual_branch_mix`
  - 并继续保持“24-step -> checkpoint selection -> validation3 real decoded.wav” 的 fail-fast 顺序
36. `waveform_decoder_mode = dual_branch_mix` 也已完成真实 `validation3 decoded.wav` fail-fast：
  - `docs/400_stage5_native_teacher_dualbranchmix_fail_fast_report.md`
  - 当前结论是：
    - `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline 三条样本都更差
    - 高频亮度恶化更明显
37. 因此当前 native teacher buzz 主线继续收紧为：
  - 不再做 `fused_single` 同层 patch
  - 不再做 `dual_branch_mix` 同层扩展
  - 下一条更合理的结构候选改为更保守的 `periodic_plus_noise_residual`
38. 更保守的非 recurrent residual decoder family 也已整族 fail-fast：
  - `docs/401_stage5_native_teacher_nonrecurrent_residual_decoder_family_fail_fast_report.md`
  - 覆盖：
    - `periodic_plus_noise_residual`
    - `periodic_plus_noise_residual_shape`
    - `periodic_plus_noise_factorized_residual`
  - 当前结论是：
    - 三条都 `3/3 auto_reject_obvious_buzz`
    - 三条都比 corrected baseline 更差
    - 因而当前 native teacher 主故障不只是“缺一个更保守的 residual decoder”
39. 因此下一步不再继续试当前这组 non-recurrent decoder mode 变体，而应回到：
  - native teacher objective / target / contract 语义
  - 尤其是 noise/periodic 解码含义本身
40. 更上游的 `spectral target` 乘 gate 也已经被证伪：
  - `docs/402_stage5_native_teacher_gatemasked_spectral_target_fail_fast_report.md`
  - `spectral_target_mode = gate_masked_halfsplit_v1`
    虽然真实接通了 package / training / export 全链路，
    但真实 `decoded.wav` 仍是 `3/3 auto_reject_obvious_buzz`，
    且比 corrected baseline 明显更差
  - 因此当前不再继续：
    - `spectral_target_mode` 同族 gate-masking 变体
    - `harmonic/noise target * gate_target`
      这种简单乘法式 target 收窄
41. “activity gate 自身是主 bug” 这条解释也已被最小否证：
  - `docs/403_stage5_native_teacher_activitygate00_nogatedrecon_fail_fast_report.md`
  - `activity_gate_weight = 0.0`
    且训练期 `use_predicted_activity_gate = false`
    仍然没有把 native teacher 拉出 buzz
  - 当前可以更明确地说：
    - 不是单纯关掉 activity-gate 监督或 gated reconstruction，
      就能摆脱当前 template-collapse 假解
42. 因此当前 native teacher 主线再次收紧为：
  - 不再扫 decoder mode family
  - 不再扫简单 gate-masked spectral target
  - 不再扫 `activity_gate` 同层微调
  - 下一步只值得继续做更上游的：
    - noise/periodic target family
    - target contract semantics
    - objective meaning
43. Stage5 dataset package export 的工程入口已补齐并行 split builder：
  - `docs/404_stage5_dataset_split_builder_processpool_takeover_report.md`
  - 当前结论是：
    - `--worker-processes`
      已真实透传到底层 split builder
    - `worker_processes == 1`
      保留原串行路径
    - `worker_processes > 1`
      已切到 `ProcessPoolExecutor`
    - 进度现在统一由主进程按 future 完成数打点
    - dataset index 也已回写 `worker_processes`
  - 但当前只完成了 `1 train + 1 validation`
    的最小真 smoke，
    尚未完成 full-split 吞吐实测
44. 更保守的 `target_contract_mode = v2core_aper_energy_only_v1`
  也已完成 fullsplit24 fail-fast：
  - `docs/405_stage5_native_teacher_aperenergyonly_target_contract_fail_fast_report.md`
  - 当前结论是：
    - full-split package、24-step training、checkpoint selection、validation3 real decoded
      都已跑通
    - 真实 `decoded.wav`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      都明显更差
  - 因而当前不再值得继续扫：
    - `target_contract_mode`
      现有这几条 gate 公式变体
    - `aper / energy / event_presence`
      的简单加减法式 contract 改写
  - 下一步必须继续上收到：
    - noise/periodic target family
    - objective meaning
    - template-collapse 的更根本诱因
45. 显式 `target_contract_mode = teacher_e_evt_gate_targets_v1`
  也已完成 corrected native-teacher fullsplit24 fail-fast：
  - `docs/406_stage5_native_teacher_eevttargetcontract_target_contract_fail_fast_report.md`
  - 当前结论是：
    - full-split package、24-step training、checkpoint selection、validation3 real decoded
      都已跑通
    - 真实 `decoded.wav`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      三条样本的
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      仍明显更差
  - 因而当前 `target_contract_mode`
    家族已在 native-teacher corrected 主线上完成封口：
    - `legacy_proxy`
    - `v2core_aper_energy_only_v1`
    - `teacher_e_evt_gate_targets_v1`
  - 下一步若继续留在这条主线，
    只能继续上收到：
    - 更根本的 noise/periodic target family
    - objective meaning
    - template-collapse 的诱因定位
46. 更显式的 package-level `spectral_target_mode = f0_harmonicity_split_v1`
  也已完成 corrected native-teacher fullsplit24 fail-fast：
  - `docs/407_stage5_native_teacher_f0harmonicity_spectral_target_fail_fast_report.md`
  - 当前结论是：
    - full-split package、24-step training、checkpoint selection、validation3 real decoded
      都已跑通
    - `spectral_target_contract`
      已真实切换到
      `harmonic_bins_from_f0_hz_and_vuv`
      / `spectral_complement_of_harmonic_mask`
    - 真实 `decoded.wav`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      三条样本的
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      仍全面更差
  - 因而当前不再继续：
    - `spectral_target_mode`
      的 package-level target family 微扫
    - 把 `F0 / vuv`
      显式编码进 harmonic/noise spectral target
      的近邻变体
47. 对这条 `f0_harmonicity` 线路补做 objective-collapse probe 后，
  当前口径还要再收紧一层：
  - `docs/408_stage5_native_teacher_f0harmonicity_objective_collapse_probe_report.md`
  - 当前结论是：
    - baseline decode route
      `mean_weighted_wave_objective = 0.240339`
    - 两个 fixed-template oracle
      仍显著更低：
      - `0.141467`
      - `0.147455`
    - `active_template + delta`
      在这条更差 target family 上
      也只做到 `20 / 24`
      而不是先前 probe 里的完整压制
  - 因而当前默认下一步不再是继续扫
    Stage5 package target/contract family，
    而应转去：
    - corrected baseline 主线上的 objective meaning
    - template-collapse 的更根本诱因定位
    - 以及为什么 fixed-template counterexample
      仍能稳定压过 baseline objective
