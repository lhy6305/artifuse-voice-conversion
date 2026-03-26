# 393. Stage5 export/probe 语义修正影响范围与回补重跑要求

## 结论
- 当前代码侧已修复一组会影响 `Stage5 decoded.wav / buzz gate / loss_metrics` 解释口径的问题。
- 这些问题不会改写旧训练出的 checkpoint 本身，但会影响一部分旧导出与 probe 结论。
- 当前应把以下仍在主线判断中被引用的报告视为 `需回补重跑确认`：
  - `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
  - `docs/390_stage5_adapter_contract_mismatch_diagnosis_and_next_route_report.md`
  - `docs/391_stage5_native_teacher_buzz_recheck_and_physiology_data_assessment.md`
  - `docs/392_stage5_native_teacher_acttmpl005_delta6_fail_fast_report.md`
- 在完成修正后的最小回补重跑前：
  - 这些报告里的 `decoded.wav / auto_reject_obvious_buzz / loss_metrics` 相关结论，只能按 `临时结论` 使用。
  - 不能再把它们当成已经按当前预期行为验证过的最终事实。

## 一、这次修复了什么

### 1. `export-offline-mvp-nores-vocoder-audio` 的 decode 默认值与当前主口径曾不一致
- 之前风险：
  - CLI 若未显式传 `--use-predicted-activity-gate`，会默认走 `False`
  - 但当前推广中的听审主口径是：
    - `use_predicted_activity_gate = true`
    - `predicted_activity_gate_apply_mode = post_ola_envelope`
- 当前修复后：
  - export 侧 decode 默认与当前主口径对齐
  - 并支持显式 `--disable-predicted-activity-gate`

### 2. export 里的 `loss_metrics` 与实际 `decoded.wav` 之前可能不是同一语义
- 之前风险：
  - export 记录会同时写：
    - 实际导出的 `decoded.wav`
    - 以及一次重新计算的 `loss_metrics`
  - 但这套 `loss_metrics` 默认可能没有继承 checkpoint 当时的训练权重与 gate 配置
- 当前修复后：
  - export 会优先解析 checkpoint 对应 training summary
  - `loss_metrics` 默认继承训练时的：
    - `activity_gate`
    - `active_template`
    - `frame_delta`
    - `use_predicted_activity_gate`
    - `reconstruction_frame_gain_apply_mode`
  - summary 中新增：
    - `loss_metrics_semantics`
    - 明确标出它是否与实际 `decoded.wav` 完全同语义

### 3. 三个 Stage5 probe 的 CLI decode 默认值也曾有同类风险
- 受影响命令：
  - `analyze-stage5-nores-speech-emergence`
  - `analyze-stage5-nores-waveform-decoder-structure`
  - `analyze-stage5-nores-waveform-objective-collapse`
- 当前修复后：
  - 默认 decode 路线统一改为：
    - predicted gate on
    - `post_ola_envelope`

## 二、哪些旧结论不会被推翻
- 不受这次问题直接影响的：
  - 已经发生过的训练过程
  - checkpoint 本体
  - training loop summary
  - package/index/scaffold 合同是否接通
- 因此：
  - 这不是“所有旧实验作废”
  - 而是“旧 export/probe 口径需要校正”

## 三、当前 active 报告的修正口径

### 1. `389`
- 仍可保留的事实：
  - `student_control_packet -> Stage5` 最小 adapter 已接通
  - 真实 `decoded.wav` 导出链已存在
- 需回补确认的部分：
  - 旧 smoke 样本的 `auto_reject_obvious_buzz`
  - 旧 `loss_metrics`
  - 旧 decoded 与 native teacher 的相对差距

### 2. `390`
- 仍可保留的事实：
  - 当前 best Stage5 checkpoint 的 scaffold family 核对
  - `e_evt == legacy_event_probs` 的张量核对
  - 主要差异病灶位于 noise first-8 的方向性诊断
- 需回补确认的部分：
  - student/native teacher decoded compare
  - 基于旧 export 的 `centroid_gap / high_band_gap / loss_total`

### 3. `391`
- 这是当前最关键、且必须优先回补的一份。
- 原因：
  - 它直接承载了“native teacher validation3 已经 `3/3 obvious buzz`”这一主判断
  - 其报告中可见导出命令没有显式传 gate 开关
- 所以：
  - 在修正后的 export 语义下，必须优先重跑 native teacher baseline validation3

### 4. `392`
- 这份也必须跟着回补。
- 原因：
  - 它的“candidate 比 native baseline 更差”建立在旧 export 对照之上
  - 若 baseline 与 candidate 的 export 语义曾未被当前代码正确约束，
    那么这份相对比较也必须在新口径下重做

## 四、回补重跑的最小顺序
1. 先重跑 `391` 对应的 native teacher baseline validation3 export。
2. 再重跑 `392` 对应的 `acttmpl005_delta6` candidate validation3 export。
3. 若两者仍保持同方向结论，再恢复新的 native teacher 实验。
4. `389/390` 可在 native teacher baseline/candidate 回补之后，再视是否仍需要 student 对照而补跑。

## 五、历史文档如何处理
- 当前不机械回刷全部旧长历史报告。
- 处理原则是：
  - 当前仍被主线引用、仍会影响下一步决策的报告，必须修正口径。
  - 更早期、已脱离当前决策面的旧报告，允许保留原文，但不再作为当前事实依据。

## 六、当前正式口径
- 代码现在应按当前预期行为工作。
- 但在完成 `391 -> 392` 的最小回补重跑前：
  - 当前 native teacher 的 `decoded.wav obvious buzz` 结论
  - 以及 `acttmpl005_delta6` 相对 baseline 更差的结论
  都应视为：
  - `高概率仍成立`
  - 但 `尚待按修正后 export 语义确认`

## 七、状态更新（2026-03-26）
- `391 -> 392` 的最小回补重跑现已完成，见：
  - `docs/394_stage5_export_semantics_rerun_confirmation_report.md`
- 当前关闭的待确认项：
  - native teacher baseline `validation3` 仍是 `3/3 auto_reject_obvious_buzz`
  - `acttmpl005_delta6` candidate 仍是 `3/3 auto_reject_obvious_buzz`
  - candidate 相对 baseline 仍明显更差
- 因此：
  - `393` 仍作为影响范围与修正原则报告保留
  - 但其中针对 `391/392` 的“尚待确认”状态已经结束
