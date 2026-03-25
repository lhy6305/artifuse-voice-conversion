# 370. Stage3-to-Stage5 downstream handoff candidates 报告

## 结论
- 当前最应该采纳的动作，不是再把新的 `teacher_e_evt` 上游 candidate 送回旧 `Stage5 no-res downstream`，而是先定义新的 downstream handoff family。
- 候选里优先级最高的，不是再补一个 Stage5 consumer 或 gate 公式，而是：
  - `Stage3 student-control packet v1`
- 这条线的核心含义是：
  - 不再让 Stage5 继续围绕 teacher-runtime packet 做“语义字段升级”
  - 而是让 Stage5 开始接收真正更接近设计稿的 student predicted named controls：
    - `z_art`
    - `e_evt`
    - `F0 / vuv / aper / E`
  - 且继续保持：
    - `r_res = off`
- 在这条主候选落地前，必须先加一个便宜的前置门禁：
  - `proxy-acoustic / proxy-audio` handoff screen
- 当前旧 route 的正式口径也需要写死：
  - 可以保留作历史兼容和反证参考
  - 但不再作为默认承接层反复重跑

## 一、当前证据基线

### 1. 上游 Stage3 正向已经足够明确
- 当前 generation-side 新 reference：
  - `teacher_e_evt_bridge_mode = acoustic_directional_transition_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
- 依据：
  - `docs/368_stage3_teacher_eevt_directional_transition_bridge_ab_report.md`
- 当前判断：
  - 上游 `teacher-label / target-state` 资产仍在持续产出真实正向信息

### 2. 当前旧 Stage5 route 的失败也已经足够明确
- 反证链已经连续成立：
  - `docs/359_stage5_c3_downstream_eevt_overfit24_fail_fast_report.md`
  - `docs/361_stage5_eevt_target_contract_supervision_route_fail_fast_report.md`
  - `docs/366_stage5_teacher_eevt_acoustic_bridge_downstream_fail_fast_report.md`
- 这些失败不是“没接上新字段”：
  - 显式 `e_evt` 的 consumer-side
  - supervision-side
  - downstream contract-side
  都已经接通过
- 更准确的结论是：
  - 当前承接方式本身不成立

### 3. 代码事实支持“换 handoff family”，而不是继续小修旧 route
- `src/v5vc/streaming_student/model.py`
  已经能稳定输出：
  - `coarse_log_f0`
  - `vuv_logits`
  - `aperiodicity`
  - `energy`
  - `z_art`
  - `event_logits / event_probs`
  - `log_f0_correction`
  - `aper_correction`
- `src/v5vc/streaming_student/proxy_acoustic.py`
  已经能从 Stage3 输出构建低成本 proxy acoustic packet：
  - `energy_log`
  - `abs_mean`
  - `zero_cross`
  - `delta_energy`
- `src/v5vc/streaming_student/proxy_audio_export.py`
  已有 cheap proxy audio 导出能力
- 相比之下，当前 `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  的 `v3` scaffold 虽然已经优先消费显式 `e_evt`，
  但本质仍是 teacher-runtime packet 的延长线，
  而不是新的 student-control downstream family

## 二、候选分级

### A. 应优先推进

#### A1. `Stage3 student-control packet v1`
- 层级：
  - `Stage3 outputs -> downstream packet`
- 为什么它是第一优先级：
  - 当前真正持续变好的层在 Stage3 generation-side
  - 设计稿里的主控制链本来就是：
    - `z_art + e_evt + F0 / vuv / aper / E`
  - 旧 Stage5 route 失败的一个核心问题，是它一直在承接 teacher-runtime semantics 的变体，而不是直接承接 student control state
- 建议的 packet 含义：
  - `z_art`
  - `e_evt`
  - `coarse_log_f0 + log_f0_correction -> F0`
  - `sigmoid(vuv_logits) -> vuv`
  - `aperiodicity + aper_correction -> aper`
  - `energy -> E`
  - `r_res` 继续缺席
- 最小验证实验：
  1. contract export / dry-run
  2. eval bridge 指标检查
  3. proxy acoustic / proxy audio 导出
  4. `zero_z_art / zero_e_evt` 正负控制检查
- stop rule：
  - 如果 packet 最终仍只是旧 `event_probs + teacher packet` 的换皮
  - 或 proxy 层已经表现出明显 envelope-following / template-buzz 假解
  - 就不进入 Stage5 训练

#### A2. `proxy-acoustic / proxy-audio` handoff screen
- 层级：
  - `Stage3 outputs -> cheap structural screen`
- 为什么必须前置：
  - 当前最大浪费点之一，是每个上游 candidate 都太快被送进 Stage5
  - 但 Stage3 这边已经有足够好的 cheap screen 基础设施
- 这条线不是新的训练主线：
  - 它是承接层筛选器
- 最小验证实验：
  1. 用新的 `Stage3 student-control packet v1` 导出 proxy acoustic
  2. 导出 teacher / student proxy audio 对照
  3. 在 full validation 上做 summary
- stop rule：
  - 若 proxy 音频仍然只有包络跟随、没有结构分化
  - 或 eval bridge 指标显示 `z_art / F0 / aper / E` 的稳定性不足
  - 则停止该 handoff 候选

### B. 条件推进

#### B1. `Stage5 student-control scaffold / adapter v4`
- 层级：
  - `new downstream packet -> Stage5 no-res adapter`
- 为什么不是第一步：
  - 它依赖 A1 先成立
  - 否则只是在新的 Stage5 scaffold 上重复旧 route 的错误
- 它和当前 `v3` scaffold 的本质区别应当是：
  - 不再只做 `event_probs -> e_evt` 字段替换
  - 而是显式围绕 design-state controls 重组特征家族
  - 必须让 `z_art`、`e_evt`、`F0/vuv/aper/E` 的职责边界更接近设计稿
- 最小验证实验：
  1. 1+1 package smoke
  2. scaffold summary / dataset index 核对
  3. 只有在 A1 和 A2 都通过后，才允许 overfit24 fail-fast
- stop rule：
  - 如果实现后仍然只是沿用旧 `36/36` scaffold 语义、只换几个字段名
  - 或 target contract 仍主要靠旧 gate 公式兜底
  - 则不继续扩成 fullsplit

### C. 当前不应作为主候选

#### C1. 当前旧 `offline_teacher_downstream_control_v3 -> scaffold v3 -> Stage5 no-res`
- 定性：
  - 已有充分 fail-fast 反证
- 当前用途：
  - 历史兼容
  - 反证参考
  - 不再是默认承接层

#### C2. hidden / fused-hidden 直接 handoff
- 定性：
  - 暂不作为主候选
- 原因：
  - `teacher_fused_hidden_projection` 线已经证明：
    - 局部 imitation loss 可下降
    - 但共享主指标更差
  - 当前不应再回到 state-space imitation 主线

#### C3. paired source-target 监督 handoff
- 定性：
  - 当前不立项
- 原因：
  - paired dry-run 已证明 source / target teacher frame 不天然对齐
  - 没有 frame bridge 前，不应把它当主承接路线

## 三、当前最合理的实施顺序
1. 先把 `acoustic_directional_transition_bridge_v1` 固定为新的 Stage3 reference。
2. 定义 `Stage3 student-control packet v1`。
3. 用 `eval_bridge + proxy_acoustic + proxy_audio_export` 做 cheap handoff screen。
4. 只有 cheap screen 过关后，才进入 `Stage5 student-control scaffold / adapter v4` 的 smoke。
5. 只有在新的 scaffold/adapter 明显不同于旧 route 后，才允许一次 overfit24 fail-fast。

## 四、当前不该做什么
- 不该继续：
  - 把新的 Stage3 candidate 再送回旧 `Stage5 no-res downstream`
  - 给旧 `semantic_consumer_mode`
    再加一个新变体
  - 给旧 `target_contract_mode`
    再补一个新 gate 公式
  - 再开 hidden / fused-hidden 小权重 sweep
  - 再拿 paired source-target 做逐帧监督假设

## 五、一句话决策
- 下一步不是“继续修旧 Stage5”，而是：
  - 先定义一个真正新的 `Stage3 student-control -> downstream` handoff family，
  - 用便宜 proxy screen 先筛，
  - 通过后再决定是否值得给它一个新的 Stage5 adapter/scaffold。
