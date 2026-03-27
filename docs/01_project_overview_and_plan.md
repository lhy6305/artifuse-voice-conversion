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
48. corrected baseline 主线上的 objective / structure 诊断，
  现在也已对齐到当前真实 gate-off 听审路由：
  - `docs/409_stage5_contractv2_normfix_gateoff_waveform_objective_recheck_report.md`
  - `docs/410_stage5_contractv2_normfix_gateoff_waveform_decoder_structure_recheck_report.md`
  - 当前新结论是：
    - 旧 `293`
      的 gate-on objective probe
      不应再当作当前主听审路由口径
    - 当前 gate-off baseline 的
      `mean_weighted_wave_objective = 0.293871`
      比 gate-on 版更差，
      fixed-template oracle
      仍显著更低
    - 同时 gate-off decoder-structure probe
      仍给出：
      `collapse_not_localized_to_waveform_decoder`
  - 因而当前默认下一步应进一步收紧到：
    - 不再直接重启旧 `acttmpl / delta`
      objective 候选
    - 不再把问题简化成 export gate 开关
    - 直接转向
      `fusion -> fused_hidden`
      与当前 decode semantics 的根因定位
49. 曾在 smoke 上最像“碰到了正确层级”的
  `fused_hidden_branch_mean_weight = 0.25`
  也已在 corrected native-teacher fullsplit24 主线上正式封口：
  - `docs/411_stage5_native_teacher_fusedhidden_branchmean025_fail_fast_report.md`
  - 当前结论是：
    - fullsplit24 training、checkpoint selection、validation3 real decoded
      都已跑通
    - 真实 `decoded.wav`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      三条样本的
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      仍全面更差
  - 因而当前不再继续：
    - `fused_hidden_branch_mean_weight`
      同层 sweep
    - fusion-side `loss`
      家族扩展
  - 当前主线应再收紧一层到：
    - 更强的 `fusion-path structural`
      改路
    - 而不是继续叠
      `fused_hidden`
      penalty
50. 下一条更强的 fusion-path 结构候选已经完成实现与最小真 smoke：
  - `docs/412_stage5_fusion_branchmean_residual_v1_bootstrap_and_smoke_report.md`
  - 当前新候选是：
    - `fusion_mode = branch_mean_residual_v1`
  - 它的语义不是继续叠 loss，
    而是把
    `branch_mean_hidden`
    变成显式主通路，
    fusion 只学习 residual
  - 当前已确认：
    - CLI 入口已接通
    - training summary / export manifest
      都会写回 `fusion_mode`
    - checkpoint state_dict
      可被导出 / probe 端自动反推回正确结构
  - 因而当前默认下一步已进一步具体化为：
    - 直接拿
      `fusion_mode = branch_mean_residual_v1`
      跑 corrected native-teacher fullsplit24 fail-fast
51. `fusion_mode = branch_mean_residual_v1`
  也已完成 corrected native-teacher fullsplit24 fail-fast：
  - `docs/413_stage5_native_teacher_fusion_branchmean_residual_fail_fast_report.md`
  - 当前结论是：
    - `validation3`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      三条样本的
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      仍全部更差
    - 但恶化幅度明显小于多数前序候选，
      当前是第一条在真实 fullsplit24 上
      明显更接近 baseline 的 fusion-path structural 候选
  - 因而当前口径不应写成：
    - `fusion-path structural`
      也已整体封口
  - 更准确的下一步应是：
    - 保持在
      `fusion -> fused_hidden`
      结构改路主线
    - 但不继续扩
      `branch_mean_residual_v1`
      本身，
      而要继续做更强的
      `fusion manifold / handoff-shape`
      候选
52. 更偏 `periodic_hidden` 主骨架的
  `fusion_mode = periodic_residual_v1`
  也已完成 corrected native-teacher fullsplit24 fail-fast：
  - `docs/414_stage5_native_teacher_fusion_periodic_residual_fail_fast_report.md`
  - 当前结论是：
    - `validation3`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对 corrected baseline，
      三条样本的
      `loss_total / spectral_centroid_gap_hz / spectral_high_band_energy_ratio_gap`
      仍全部更差
    - 而且它也明显差于
      `branch_mean_residual_v1`
  - 因而当前可以更明确地排除：
    - `periodic-dominant fusion backbone`
      这一侧 handoff-shape
  - 下一步应进一步收紧到：
    - 留在
      `branch_mean`
      一侧的 fusion manifold
    - 重点处理
      `envelope-following`
      为什么仍被保留
53. 更保守的
  `fusion_mode = branch_mean_contrast_residual_v1`
  也已完成 corrected native-teacher fullsplit24 fail-fast：
  - `docs/415_stage5_native_teacher_fusion_branchmean_contrast_residual_fail_fast_report.md`
  - 当前结论是：
    - `validation3`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 但它是当前第一条真正把
      `spectral_centroid_gap_hz`
      从约 `5.0k`
      压到约 `1.0k`
      的 fusion structural 候选
    - `spectral_high_band_energy_ratio_gap`
      也从约 `0.29 ~ 0.34`
      压到约 `0.01 ~ 0.07`
    - 同时 selector 首次给出了
      `selected_stable_late_stop = step24`
    - 但三条样本的
      `decoded_frame_rms_to_aligned_frame_rms_corr`
      仍稳定在
      `0.89 ~ 0.91`
      一档，
      说明剩余主故障已经收缩成：
      `template-collapse + envelope-following`
  - 因而当前口径应进一步改成：
    - 不再把主线写成“继续修 brightness”
  - 而是：
      在保留
      `branch_mean_contrast`
      这条 backbone 的前提下，
      直接改
      decoder interaction / handoff-shape，
      去打掉 decoder-side template projector
54. 在这条最强 backbone 上直接叠
  `use_decoder_branch_condition_adapter = true`
  的组合候选，
  也已完成 corrected native-teacher fullsplit24 fail-fast：
  - `docs/416_stage5_native_teacher_fusion_branchmean_contrast_branchcond_fail_fast_report.md`
  - 当前结论是：
    - `validation3`
      仍是 `3/3 auto_reject_obvious_buzz`
    - 相对纯
      `branch_mean_contrast_residual_v1`
      并没有打掉
      `template-collapse + envelope-following`
    - 反而把已经压下来的 brightness
      明显抬回去：
      - `spectral_centroid_gap_hz`
        从约 `1.0k`
        回升到约 `2.9k`
      - `spectral_high_band_energy_ratio_gap`
        从约 `0.01 ~ 0.07`
        回升到约 `0.47 ~ 0.52`
    - structure probe 也说明：
      fusion 本体基本没坏，
      更差的是 decoder-side hidden conditioning
      把输出重新推向模板投影区
  - 因而当前下一步应继续收紧为：
    - 保留
      `branch_mean_contrast`
      这条 backbone
    - 排除
      hidden-side decoder branch adapter
    - 若还要把 branch dynamics
      重新带回 waveform，
      只能考虑更保守的
      frame-space / residual-shape
      交互
55. 输出侧
  `residualshapecond`
  这条更保守的 waveform handoff
  已经真正接通并完成 corrected native-teacher fullsplit24：
  - `docs/417_stage5_native_teacher_fusion_branchmean_contrast_residualshape_breakthrough_report.md`
  - 当前结论是：
    - 这是第一条把
      `validation3`
      从
      `3/3 auto_reject_obvious_buzz`
      拉到
      `3/3 review_required`
      的 decoder-side structural 候选
    - 但它还不是成功：
      - `selected_stable_late_stop = null`
      - `decoded_frame_rms_to_aligned_frame_rms_corr`
        仍在 `~0.90`
      - 剩余主病灶仍是
        `template-collapse + envelope-following`
  - 因而当前 Stage5 主线应正式改成：
    - 保留
      `branch_mean_contrast`
      backbone
    - 保留输出侧
      `residual-shape`
      handoff
    - 不再回到 hidden-side adapter
56. 这条新 route 的
  scale operating region
  也已继续收紧：
  - `docs/418_stage5_native_teacher_fusion_branchmean_contrast_residualshape_scale_refine_report.md`
  - 当前结论是：
    - `residual_shape_branch_condition_scale = 0.5`
      在 heard-path 指标上更强：
      - `decoded_frame_template_cosine_mean = 0.975055`
      - `spectral_centroid_gap_hz = 3955.47168`
      - `spectral_high_band_energy_ratio_gap = 0.326294`
    - `residual_shape_branch_condition_scale = 0.25`
      在 selector stability 上更强：
      - `selected_stable_late_stop = step24`
      - `decoded_to_target_rms_ratio = 0.992803`
    - 但两者都仍保留：
      - `decoded_frame_rms_to_aligned_frame_rms_corr ~ 0.89`
  - 因而当前下一步不应继续发散到新 family，
    也不应只围绕 brightness 或 selector 做单维 sweep，
    而应在这条已成立的
    `0.25 ~ 0.5 residualshapecond`
    operating region 内，
    直接处理剩余的
    `envelope-following`
    根因。
57. `residual_shape_branch_condition_mode = shape_only_unit_rms_v1`
  也已完成更便宜的
  inference-only route-level probe：
  - `docs/419_stage5_native_teacher_residualshape_unitrms_decode_probe_report.md`
  - 当前结论是：
    - 这条 mode
      在稳定的
      `raw_additive_v1 scale=0.25`
      step24 checkpoint 上，
      仅改 decode 语义后，
      并没有减轻
      `envelope-following`
    - 相反：
      - `decoded_frame_template_cosine_mean`
        从
        `0.975636`
        恶化到
        `0.977393`
      - `decoded_frame_rms_to_aligned_frame_rms_corr`
        从
        `0.891069`
        恶化到
        `0.904674`
      - `spectral_centroid_gap_hz`
        从
        `4036.778076`
        恶化到
        `4302.939941`
      - `spectral_high_band_energy_ratio_gap`
        从
        `0.333024`
        恶化到
        `0.353297`
    - 同时这条 mode
      从随机初始化训练时，
      在最小 smoke 上
      第一步 update 后
      就暴露出明显数值不稳
  - 因而当前 Stage5 主线应进一步写死为：
    - 保留
      `raw_additive_v1 residualshapecond`
    - 暂停
      `unit_rms / shape_only`
      同族归一化假设
    - 继续在
      `scale = 0.25 ~ 0.5`
      这段已成立的 operating region 内，
      直接打
      `envelope-following`
      根因
58. `residualshapecond`
  的 decode-time additive delta
  也已完成直接 ablation probe：
  - `docs/420_stage5_native_teacher_residualshape_decode_ablation_probe_report.md`
  - 当前结论是：
    - 固定同一个
      `scale=0.25 raw_additive_v1`
      step24 checkpoint，
      仅把 decode-time
      `residual_shape_branch_condition_scale`
      改成
      `0.0`
      之后，
      route 仍保持：
      - `3/3 review_required`
    - brightness / template-collapse
      还出现了非常轻微的改善：
      - `decoded_frame_template_cosine_mean`
        `0.97723 -> 0.977191`
      - `spectral_centroid_gap_hz`
        `4228.900391 -> 4194.120605`
      - `spectral_high_band_energy_ratio_gap`
        `0.347793 -> 0.344906`
    - 但
      `decoded_frame_rms_to_aligned_frame_rms_corr`
      没有改善：
      - `0.904841 -> 0.904918`
  - 因而当前更准确的主线解释应是：
    - `residualshapecond`
      的收益更像
      training-time handoff shaping
    - 而不是 inference-time
      additive delta
      还在单独扛住当前 route
  - 下一步不应继续：
    - 围绕 decode-time
      `residual_shape_branch_condition_scale`
      做微扫
  - 而应转到：
    - 为什么训练期这条 handoff
      能压低 brightness / collapse，
      却仍留下
      `envelope-following`
59. 用户线已新增专门的
  `waveform handoff probe`
  命令，
  可把
  `decoder_hidden / waveform_frame_logits / waveform_frames / decoded_no_gate / decoded_pre_ola_gate / decoded_post_ola_gate`
  在同一批
  teacher-first case
  上一起导出并汇总：
  - `docs/421_teacher_first_waveform_handoff_probe_bootstrap_report.md`
  - 当前结论是：
    - 这条 probe
      已在单条 user-line smoke 上跑通
    - 每个 case
      会额外落盘：
      - `waveform_frame_logits_stitched.wav`
      - `waveform_frames_stitched.wav`
      - `decoded_no_gate.wav`
      - `decoded_pre_ola_gate.wav`
      - `decoded_post_ola_gate.wav`
      - `teacher_first_vc_waveform_handoff_tensors.pt`
    - 这让后续所有 decode-side 修复
      都能直接回答：
      - 坏相位是从
        `logits`
        就开始，
      - 还是主要在
        `tanh / OLA / gate`
        才放大
  - 当前下一步应直接拿
    已确认 pure buzz
    的固定三条 user-line 样本
    跑这条 probe，
    作为后续每一层修复的统一前后对照基线。
60. 固定三条
  pure buzz
  user-line 样本
  已完成第一轮
  waveform handoff probe：
  - `docs/422_teacher_first_waveform_handoff_probe_triplet_run_report.md`
  - 当前结论是：
    - 三条样本都表现出：
      - `waveform_frame_logits_template_cosine_mean ~ 0.9995 ~ 0.9998`
      - `waveform_frames_template_cosine_mean ~ 0.9994 ~ 0.9998`
      - `logits_to_frames_template_cosine_gap ≈ -0.00006 ~ -0.00003`
    - 也就是说：
      - 坏相位不是
        `tanh`
        才新引入
    - 同时
      `decoded_no_gate`
      已经稳定很坏：
      - aggregate
        `decoded_frame_template_cosine_mean = 0.99358`
      - aggregate
        `decoded_spectral_centroid_hz = 6852.94`
      - aggregate
        `decoded_spectral_high_band_energy_ratio = 0.391782`
    - `pre/post_ola gate`
      主要做的是：
      - 把
        `predicted_activity_to_decoded_frame_rms_corr`
        从
        `-0.0496`
        拉到
        `~0.989`
      - 但只让 brightness / template
        轻微回落，
        没有出现新的大幅恶化
  - 因而当前用户线 decode-side 主线应进一步收紧为：
    - 暂停把主故障继续写成
      `gate semantics`
    - 优先定位
      `waveform_frames`
      之前的 collapse /
      projector operating region /
      handoff source
61. 同 checkpoint 的
  Stage5 validation package
  也已完成最小 waveform handoff 对照：
  - `docs/423_teacher_first_vs_stage5_validation_waveform_handoff_alignment_report.md`
  - 当前结论是：
    - user-line 与 validation package
      在 handoff stage 侧
      并没有出现“只有 user-line 才坏”的新分叉
    - 例如 aggregate 上：
      - user-line
        `waveform_frame_logits_template_cosine_mean = 0.999641`
      - validation
        `waveform_frame_logits_template_cosine_mean = 0.999573`
    - `waveform_frames`
      也同样接近：
      - user-line
        `0.999597`
      - validation
        `0.999516`
    - 这说明当前 user-line
      所暴露的 waveform handoff collapse，
      本质上与 checkpoint-native
      的坏 manifold
      是同一类问题
  - 因而当前更准确的主线表述应改成：
    - 不是
      “user-line 特有 gate 失配”
    - 而是
      “当前 checkpoint
      在 native validation 路线上
      自己就已经停在同类 waveform handoff collapse”
62. user-line 固定三条
  pure buzz
  样本
  已完成第一轮
  `waveform decoder structure probe`：
  - `docs/424_teacher_first_waveform_decoder_structure_probe_triplet_report.md`
  - 当前结论是：
    - baseline 下：
      - `fused_hidden_template_cosine_mean = 0.994928`
      - `waveform_frames_template_cosine_mean = 0.999597`
      - 自动诊断仍是
        `collapse_not_localized_to_waveform_decoder`
    - `fused_hidden_frame_mean`
      几乎不改变输出：
      - `waveform_mean_abs_delta_vs_baseline = 0.007526`
    - 但只要直接用
      `periodic / noise / branch_mean`
      绕过 fusion，
      `decoded_template`
      就会从
      `0.993580`
      掉到
      `0.859604 / 0.915412 / 0.901776`
    - 同时 centroid / high-band
      会大幅上冲到
      `10667 ~ 12240 Hz`
      与
      `0.808 ~ 0.852`
  - 因而当前 user-line
    结构层结论应写成：
    - decoder
      不是彻底失去响应能力
    - 更像是：
      - `fusion / decoder input manifold`
        已先坍缩
      - decoder
        围绕这块坏 manifold
        学到了稳定的高模板 buzz 解
63. 同 checkpoint 的
  Stage5 validation3
  gate-off
  `waveform decoder structure probe`
  也已补跑最小对照：
  - `docs/425_teacher_first_vs_stage5_validation_waveform_decoder_structure_alignment_report.md`
  - 当前结论是：
    - user-line 与 validation3
      在结构层的响应形状仍然高度一致：
      - baseline 都是
        `collapse_not_localized_to_waveform_decoder`
      - `fused_hidden_frame_mean`
        都几乎无效
      - branch bypass
        都会把输出显著拉出 baseline 模板区，
        同时推入更亮、更高频的非稳态
  - 因而当前主线应进一步收紧为：
    - 这不是
      user-line 特有结构故障
    - 而是当前 checkpoint-native 的
      `fusion / decoder input manifold`
      问题
64. plain-fusion baseline
  已完成 fusion 子阶段定位：
  - `docs/426_plain_fusion_substage_localization_report.md`
  - 当前结论是：
    - 无论 user-line
      还是 validation3，
      最大模板化跳变都首先发生在：
      - `fusion.0 Linear`
    - 第二个明确跳变点是：
      - `fusion.3 Linear`
    - `GELU / LayerNorm`
      不是主坍缩起点
  - 因而 plain baseline
    的问题现在不应再泛写成：
    - “fusion 之后都坏了”
  - 而应更准确地写成：
    - plain fusion backbone
      的首层与末层线性投影
      正在把 branch dynamics
      压进坏 manifold
65. native-teacher 最强候选
  `branch_mean_contrast_residual_v1 + residualshapecond`
  已完成 user-line 三样本转移验证：
  - `docs/427_teacher_first_candidate_transfer_report.md`
  - 当前结论是：
    - 它不是只在 native validation
      上偶然有效，
      也能稳定把 user-line
      拉离 plain-fusion 的纯 buzz 坏 manifold
    - 最关键的一步：
      - `branch_mean_to_fused_template_cosine_gap`
        `0.073843 -> 0.001379`
    - handoff stage
      也同步改善：
      - `waveform_frame_logits_template_cosine_mean`
        `0.999641 -> 0.994119`
      - `waveform_frames_template_cosine_mean`
        `0.999597 -> 0.993178`
    - `decoded_no_gate template`
      也下降到：
      - `0.984637`
  - 因而当前实验主线应正式切换为：
    - 不再继续围绕
      plain fusion baseline
      做局部修补
    - 直接研究候选线
      为什么仍残留
      `envelope-following`
66. 候选线剩余
  `envelope-following`
  已完成 user-line family-level 归因：
  - `docs/428_teacher_first_candidate_envelope_following_family_attribution_report.md`
  - 当前结论是：
    - 主承载家族不是
      `conditioning_family`
      也不是
      `event_family`
    - 而是：
      - `acoustic_state_family`
    - 在这个家族里：
      - `aper`
        是最强的 residual
        envelope-following 承载项
      - `E_log_rms_norm`
        更偏 brightness / high-band
        杠杆
    - 但直接把
      `aper`
      或
      `aper + energy`
      清零，
      又会把系统往
      更模板化区域
      拉回去
  - 因而当前下一步主线应写成：
    - 不是继续扩大
      family-level zero sweep
    - 而是研究
      `aper / energy`
      的 anti-template 贡献
      与 envelope-following 耦合
      如何被拆开
67. 候选线
  `aper / energy`
  已完成 reference-backed
  去耦对照：
  - `docs/429_teacher_first_candidate_acoustic_reference_backed_decoupling_report.md`
  - 当前结论是：
    - `reference_mean`
      只能通过
      压扁 acoustic-state
      时间动态来压低
      `activity_corr`
    - `reference_affine_match`
      一旦保留时间动态，
      `activity_corr`
      与 brightness
      就会一起回升，
      甚至高于 baseline
    - 因而 residual 主问题
      不能再写成：
      - 静态均值失配
      - 静态方差失配
    - 更准确地应写成：
      - `aper / energy`
        的时间动态本身
        同时承载：
        - anti-template 动态
        - envelope-following 耦合
  - 因而当前下一步主线应进一步收紧为：
    - 不再继续做
      reference-backed
      静态替换扫描
    - 直接研究
      acoustic-state
      时间动态的去耦方式
68. 候选线
  acoustic-state
  已完成时间对齐去耦 probe：
  - `docs/430_teacher_first_candidate_acoustic_temporal_alignment_decoupling_report.md`
  - 当前结论是：
    - `aper`
      只要做
      `time_roll_half / time_shuffle`
      这类时间对齐打断，
      `activity_corr`
      就会从
      `0.519889`
      明显降到
      `0.243811 / 0.259761`
      而
      `template`
      仍保持在
      `0.983xxx`
    - 更关键的是：
      - `aper + energy = time_shuffle`
        达到
        `decoded_template = 0.981053`
        与
        `activity_corr = 0.101686`
    - 这明显优于：
      - `zero`
        的塌缩倾向
      - `reference_mean`
        的动态压扁
      - `reference_affine_match`
        的包络回升
  - 因而当前主线应进一步收敛为：
    - residual 主故障
      不是静态分布失配
    - 而是
      `aper / energy`
      与当前 activity
      的时间对齐耦合
  - 因而下一步应直接研究：
    - 如何在训练/结构上
      抑制这种时间对齐，
      同时保留
      anti-template 动态
69. user-line source scaffold
  与 Stage5 reference
  的 acoustic temporal alignment
  已完成直接对照：
  - `docs/431_teacher_first_acoustic_temporal_alignment_source_vs_reference_report.md`
  - 当前结论是：
    - 问题不能再写成：
      - teacher/scaffold 完全正常
      - 或全部由 checkpoint 凭空制造
    - 更准确地说：
      - user-line source scaffold
        已经在
        `energy -> frame_rms`
        上表现出
        明显偏高的零延迟耦合
      - `aper*energy -> frame_rms`
        也从 reference 的
        更滞后结构，
        明显向更即时的
        envelope 跟随偏移
      - `aper`
        自身则偏移较弱，
        不如 `energy`
        一致
    - 因而当前 residual 主问题
      应进一步收敛为：
      - source-derived scaffold
        已经把
        `energy / aper*energy`
        的即时包络耦合
        带高
      - checkpoint downstream
        再将其放大成
        可听 residual EF
  - 因而当前下一步主线应直接转向：
    - 如何在训练/结构上
      限制
      `energy`
      尤其
      `aper*energy`
      的即时 envelope 对齐
70. `energy`
  单项时间打断
  已完成最小必要对照：
  - `docs/432_teacher_first_energy_temporal_break_ablation_report.md`
  - 当前结论是：
    - 单独打断
      `energy`
      的时间对齐，
      确实能把
      `activity_corr`
      从
      `0.519889`
      压到
      `0.426418 / 0.367678`
    - 但它仍明显弱于：
      - `aper = time_shuffle`
        的
        `0.259761`
      - `aper + energy = time_shuffle`
        的
        `0.101686`
  - 因而当前训练/结构主线应更准确地写成：
    - `energy`
      是优先的上游异常入口
    - 但最终仍需
      与
      `aper`
      联动去耦，
      不能只改单项
71. `E_log_rms_norm`
  已完成 periodic/noise
  分支级对照：
  - `docs/433_teacher_first_branch_specific_energy_alignment_report.md`
  - 当前结论是：
    - `periodic_E_log_rms_norm = time_shuffle`
      会把
      `activity_corr`
      从
      `0.519889`
      拉高到
      `0.556154`
    - `noise_E_log_rms_norm = time_shuffle`
      则会把它压到
      `0.310713`
    - 更关键的是：
      - `aper + noise_E_log_rms_norm = time_shuffle`
        达到
        `decoded_template = 0.982003`
        与
        `activity_corr = 0.012374`
      - 这比
        `aper + E_log_rms_norm = time_shuffle`
        更强
  - 因而当前最小训练候选应正式收敛为：
    - `noise_E_log_rms_norm`
      为主
    - 与
      `aper`
      联动去耦
  - 当前不再考虑：
    - periodic 支能量约束
    - 整条 energy family
      一刀切处理
72. `noise_E_log_rms_norm + aper`
  的联动去耦
  已经落成可训练候选数据集入口：
  - `docs/434_stage5_noise_energy_aper_alignment_variant_dataset_smoke_report.md`
  - 当前结论是：
    - 新命令
      `materialize-offline-mvp-teacher-first-stage5-input-variant-dataset`
      已可把
      `aper=time_shuffle + noise_E_log_rms_norm=time_shuffle`
      直接写进 Stage5 packages
    - 该变体索引
      已完成：
      - `2 train + 1 validation`
        的小规模物化 smoke
      - 以及
        现有 dataset training loop
        的 `1 step` CPU smoke
  - 因而当前主线已从：
    - 纯诊断
    进入到：
    - 可直接发起训练候选
73. `noise_E_log_rms_norm + aper`
  的 hard-shuffle
  fullsplit 正式训练
  已完成并被否决：
  - `docs/435_stage5_noiseenergy_apershuffle_fullsplit_rejection_report.md`
  - 当前结论是：
    - 把
      `aper=time_shuffle + noise_E_log_rms_norm=time_shuffle`
      直接固化成 full-package
      训练输入，
      虽然会把
      validation loss
      从
      `0.850578`
      压到
      `0.841304`，
      但 user-line 与原始 Stage5 native validation
      都会明显回退到
      更亮、更模板化的高频 buzz
    - user-line aggregate
      已从旧 strongest candidate 的：
      - `template = 0.984637`
      - `activity_corr = 0.519889`
      - `centroid = 6510.052734`
      - `high_band = 0.449300`
      回退到：
      - `template = 0.988341`
      - `activity_corr = 0.543954`
      - `centroid = 13654.723633`
      - `high_band = 0.793869`
    - 原始 `contractv2_normfix`
      validation3
      也同步回退到：
      - `decoded_no_gate auto_reject_count = 3/3`
      - `template = 0.986660`
      - `centroid_gap = 11348.081055`
      - `high_band_gap = 0.737495`
  - 因而当前主线必须更新为：
    - `time_shuffle`
      仍可保留为 probe 诊断工具
    - 但不能再作为
      full-package
      训练输入语义
      直接固化
  - 下一步方向应转向：
    - 保持原始 inference scaffold
      分布不变的
      软约束 / 正则化 / 局部扰动
    - 而不是继续硬写
      shuffle variant
## 2026-03-27 补充更新
- `docs/435_stage5_noiseenergy_apershuffle_fullsplit_rejection_report.md`
  已正式否决把 `aper + noise_E_log_rms_norm = time_shuffle` 直接固化进 fullsplit 训练输入的路线。
- `docs/436_stage5_global_acoustic_corrreg_fullsplit24_rejection_report.md`
  已补完并验证一种“不改 inference scaffold 分布”的训练侧 soft route：
  - 从 `source_scaffold_path` 回填 `aper / E_log_rms_norm`
  - 在 `waveform_frames` 上加全局 `E / aper*E` 超额零延迟相关正则
- 这条 soft route 的当前结论是：
  - 训练 objective 更好：`validation loss_total = 0.850578 -> 0.825239`
  - user-line 某些指标变好：`decoded_no_gate template = 0.984637 -> 0.982265`，`activity_corr = 0.519889 -> 0.414830`
  - 但 native validation3 明确回退：`auto_reject_count = 0 -> 3`，`centroid_gap ≈ 4405.95 -> 5426.24`，`high_band_gap ≈ 0.361477 -> 0.552879`
- 因此当前主线更新为：
  - 不继续扫“全局 `E / aper*E` corrreg”权重
  - 保持 inference scaffold 语义不变
  - 下一阶段转向更贴近 probe 结论的
    `branch-specific / lag-aware / target-relative temporal regularization`
  - 优先围绕 `noise_E_log_rms_norm` 家族，而不是全局 `E`
- `docs/437_stage5_noise_family_lagcorr_fullsplit24_rejection_report.md`
  已补完并验证上述下一阶段中的最小正式候选：
  - 保持原始 `contractv2_normfix` fullsplit 不变
  - strongest backbone 保持不变
  - 训练时只新增 noise-family 的 center-weighted lag-profile excess 正则：
    - `noise_energy_frame_rms_lagcorr_excess`
    - `noise_aper_energy_frame_rms_lagcorr_excess`
- 这条 lag-aware route 的当前结论是：
  - objective 依旧优于 strongest native candidate：`validation loss_total = 0.850578 -> 0.825358`
  - user-line 的 `template / activity_corr` 比上一轮全局 corrreg 再低一小步：
    - `template = 0.982265 -> 0.982206`
    - `activity_corr = 0.414830 -> 0.401372`
  - 但 native validation3 仍然是：
    - `auto_reject_count = 3`
    - `rms_corr = 0.537991 -> 0.509435`
    - `centroid_gap = 5426.24 -> 5462.51`
    - `high_band_gap = 0.552879 -> 0.553493`
- 因此当前主线再次更新为：
  - 不继续围绕 output-side `frame_rms lagcorr` 做局部权重或窗口 sweep
  - `branch-specific / lag-aware / target-relative`
    这个大方向本身提供了方向性证据，但其当前“最终 `waveform_frames` soft regularizer”实现也已被正式否决
  - 下一步必须继续上收到：
    - 更贴近 noise-family 内部表示 / decoder interface 的约束
    - 或更强的 `shape-aware / substage-aware` temporal target
## 2026-03-27 再补充更新
- `docs/438_teacher_first_stage_temporal_coupling_output_head_localization_report.md`
  已补完 strongest candidate 的更上游 stage-wise temporal coupling 定位。
- 新 probe：
  - `analyze-offline-mvp-teacher-first-vc-stage-temporal-coupling`
  - 已在 fixed pure buzz triplet 上跑通：
    - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_stcp_fbmc_rs/`
- 当前结论是：
  - 剩余 `envelope-following`
    的主放大点已经不在
    `noise_hidden -> branch_mean -> fused -> decoder_hidden`
    这条上游链路。
  - 三个 noise-family controls
    的最大绝对零延迟耦合跳变，
    都主要落在：
    - `decoder_hidden -> waveform_decoder_base_logits`
  - 再拆 output head 后可以更准确地写成：
    - `aper`
      和
      `aper * noise_E`
      更像 raw waveform head 自身在放大
    - `noise_E_log_rms_norm`
      的峰值则更高地落在
      `waveform_residual_shape_delta`
- 因而当前主线再次更新为：
  - 不再回到：
    - fusion regularizer
    - `decoder_hidden` 之前的局部小修
    - output-side `frame_rms corrreg`
  - 下一步应直接转向：
    - output head / residual-shape injection interface
    - 也就是
      `waveform_decoder(decoder_hidden)`
      与
      `residual_shape_branch_condition_delta`
      这两个子阶段的结构约束或训练目标
## 2026-03-27 晚间补充更新
- `docs/440_stage5_output_head_headstruct_raw_edb_dual_route_rejection_report.md`
  已补完 interruption 前未落盘的 stronger headstruct 双候选结果。
- 当前结论是：
  - 在 `docs/439`
    否决较弱的
    output-head lagcorr route
    后，
    已实际跑过更强的：
    - active-template
    - base_logits `aper/noise_E` abs-zero-lag corr
    - residual-shape `noise_E` abs-zero-lag corr
  - 同时比较了：
    - `raw_additive_v1`
    - `shape_only_energy_debiased_v1`
  - 这两条 stronger headstruct route
    都已完成：
    - smoke
    - fullsplit24
    - user-line 回投
    - native validation3 回投
  - 且都被正式否决：
    - native 仍是 `auto_reject = 3/3`
    - `shape_only_energy_debiased_v1`
      比 raw 版更差
- `docs/441_stage5_output_head_headstruct_high_band_candidate_breakthrough_report.md`
  已补完下一条显式 anti-brightness 候选。
- 当前结论更新为：
  - 已补齐
    `waveform_decoder_base_logits_high_band_excess_weight`
    的 CLI 接线
  - 新候选：
    - 保持 raw headstruct 路线
    - 在 `waveform_decoder_base_logits`
      上新增直接
      `high_band_excess`
  - 当前结果和 `439/440`
    已有本质差异：
    - native validation3
      从
      `auto_reject = 3/3`
      恢复到
      `0/3`
    - `centroid_gap / high_band_gap`
      已显著优于旧 strongest candidate
    - `waveform_handoff`
      首次显示：
      - `likely_failure_already_present_by_frames_before_gate = false`
  - 因而当前主线再次更新为：
    - `headstruct + base_logits high_band_excess`
      升格为新的可继续治理主候选
    - 下一步优先：
      - 人工听审治理
      - 与继续收缩
        `aper * noise_E`
        在
        `decoder_hidden -> waveform_decoder_base_logits`
        的残余 jump
## 2026-03-27 深夜补充更新
- `docs/442_teacher_first_output_head_high_band_compare_bundle_and_audio_audit_contract_report.md`
  已把
  `441`
  的新主候选整理成正式人工听审交付物。
- 当前已固定的主听审对比为：
  - 旧 strongest native candidate
  - 对比
  - 新 `output_head_high_band_bhb01`
- 已落盘的正式入口：
  - compare bundle：
    `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/`
  - 主听 wav 目录：
    `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/listening/`
  - GUI 输出目录：
    `reports/audio/audio_audit_gui_outputhead_highband_vs_strongest_round1_1/`
- 当前 bundle
  已验证：
  - `case_count = 3`
  - `variant_count = 2`
  - `variant_runs_succeeded = 6 / 6`
  - `positive_controls_ready = 3 / 3`
- GUI
  也已通过一次自动关闭 smoke，
  因而当前状态不是
  “理论上可听审”，
  而是：
  - 命令
  - bundle
  - GUI 入口
  都已实际跑通
- 当前下一步维持不变：
  - 先拿这份 bundle
    做人工听审收口
  - 再根据听感决定：
    - 继续保留
      `high_band` 主线并治理
    - 还是回到
      `aper * noise_E`
      residual jump
      的更强结构收缩
## 2026-03-27 深夜再次更新
- `docs/443_stage5_output_head_high_band_human_audit_fail_and_gui_demote_report.md`
  已补完
  `441/442`
  之后的正式人工听审结论。
- 当前结论已更新为：
  - `output_head_high_band_bhb01`
    虽然量化上相对旧 strongest
    有明显 anti-brightness 改善，
    也不再是
    `440`
    那种 native 直接坏死路线，
    但人工听审仍明确判为：
    - 纯 buzz
    - 只是变成了
      带一点明显音调变化的 buzz
- 因而当前主线再次收紧为：
  - 不再继续围绕
    `bhb01`
    做同层微调或再发一轮同类听审
  - `high_band` route
    正式记为：
    - 量化改善成立
    - 主观听感失败
      的候选
  - 下一步应回到：
    - 为什么压亮度以后，
      仍只得到
      tonal buzz
    - 以及
      `aper * noise_E`
      在
      `decoder_hidden -> waveform_decoder_base_logits`
      的残余 jump
- 听审交付策略也同步更新为：
  - 对这类
    pure-buzz / non-pure-buzz
    快速判别实验，
    默认直接交：
    - wav 目录
  - 不再默认交
    GUI
    量化打分
## 2026-03-27 深夜继续更新
- `docs/444_stage5_output_head_bpae01_relocalization_and_minimal_listening_contract_report.md`
  已补完在
  `bhb01`
  基础上继续加入
  `waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr`
  的新候选结果。
- 当前结论更新为：
  - `bpae01`
    不是假接线，
    也不是简单回退：
    - native validation3
      仍保持
      `auto_reject = 0/3`
    - `decoded_post_ola_gate`
      的
      `centroid_gap / high_band_gap`
      继续从
      `3211.714111 / 0.198100`
      改善到
      `2516.162109 / 0.111581`
  - 但它也不能升格为新主候选：
    - user-line
      `decoded_post_ola_gate template`
      从
      `0.870602`
      回升到
      `0.887733`
    - 更像
      “继续变暗，
      但没有明确离开
      tonal pure buzz”
- stage temporal coupling
  的正式解释也进一步收紧为：
  - `aper * noise_E`
    在
    `decoder_hidden -> waveform_decoder_base_logits`
    的旧大 jump
    已被压平
  - 但 residual 没有消失，
    而是重定位到：
    - `waveform_residual_shape_delta`
  - 同时
    `aper`
    和
    `noise_E`
    单项在
    `waveform_decoder_base_logits`
    上反而更强
- 因而当前主线更新为：
  - 不把
    `bpae01`
    直接 promoted
  - 先做最小
    wav
    听审，
    只判它是否仍在
    pure-buzz
    区间
  - 如果听感仍只是更暗的
    tonal buzz，
    下一步就应继续上收到：
    - residual-shape interface
    - 与单项
      `aper / noise_E`
      在 output head
      的重新放大
- 当前已落盘的最小听审入口：
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_bpae01_vs_bhb01_vs_strongest_round1_1/listening/`
## 2026-03-27 深夜最终更新
- `docs/445_stage5_output_head_bpae01_human_audit_fail_and_spectrogram_corroboration_report.md`
  已补完
  `bpae01`
  的人工听审收口。
- 当前结论再次收紧为：
  - `bpae01`
    虽然量化上继续压低 brightness，
    也压平了旧的
    `aper * noise_E`
    base-logits jump，
    但人工听审已明确：
    - 与
      `bhb01`
      几乎完全一致
    - `segment_0061`
      仍完全是 buzz
    - `peak_011`
      仍完全是 pure buzz
- 用户本轮还提供了线性频谱图，
  并已归档到：
  - `reports/audio/outputhead_bpae01_human_audit_spectrograms_round1_1/`
- 当前频谱图层面的辅助结论也与听审一致：
  - `1 ~ 3`
    的
    `bpae01 / bhb01`
    交替片段仍表现为
    等距直线型稳定 buzz
  - 对照 target
    则明显存在：
    - unvoice 的宽带砂状区
    - voice 的低频共振峰
- 因而当前 output-head 主线应再更新为：
  - 不再继续围绕
    `bhb01`
    或
    `bpae01`
    做同层治理
  - 当前已正式确认：
    - 仅靠
      `high-band`
      压亮度
      或
      `aper * noise_E`
      product penalty
      压 jump，
      都只能得到 pure buzz 家族内部的变化
  - 下一步必须继续上收到：
    - residual-shape interface
    - 以及单项
      `aper / noise_E`
      在 output head
      的重新放大
## 2026-03-27 深夜继续补充
- `docs/446_stage5_output_head_substage_structure_probe_base_vs_residual_report.md`
  已把 output-head
  再拆成：
  - `baseline_full_output`
  - `waveform_decoder_base_logits_only`
  - `waveform_residual_shape_only`
  并在：
  - teacher-first 三条 pure-buzz 样本
  - Stage5 native validation3
  两侧都跑通了
  `wav + 线性频谱图`
  导出。
- 当前新结论比
  `445`
  更进一步：
  - baseline
    几乎等于
    `waveform_decoder_base_logits_only`
  - `waveform_residual_shape_only`
    不是隐藏的人声结构，
    而是更亮、更高频、
    更模板化的纯 buzz
- 量化上在 user-line：
  - baseline：
    `template / centroid / high_band = 0.887733 / 4163.743652 / 0.197849`
  - `base_logits_only`：
    `0.887373 / 4256.501465 / 0.201769`
  - `residual_shape_only`：
    `0.999805 / 12338.094727 / 0.833547`
- native validation3
  也完全同向：
  - baseline：
    `0.824535 / 3407.504639 / 0.151263`
  - `base_logits_only`：
    `0.823982 / 3470.388672 / 0.154959`
  - `residual_shape_only`：
    `0.999815 / 11351.418945 / 0.815930`
- 因而当前主线必须再次更新为：
  - 不再优先围绕
    `residual_shape`
    做同层解释和小修
  - 当前可听输出几乎就是
    `waveform_decoder_base_logits`
    本体
  - 下一步必须转向：
    - `waveform_decoder(decoder_hidden)`
      为什么只生成稳定
      tonal/pure buzz
    - 而不是继续问
      residual-shape
      为什么没把它修好
- 当前新增 probe 产物目录：
  - user-line：
    `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp_outputhead_bpae01_round1_1/`
  - native validation3：
    `reports/runtime/stage5_waveform_decoder_structure_probe_headstruct_bhb01_bpae01_validation3_round1_1/`
