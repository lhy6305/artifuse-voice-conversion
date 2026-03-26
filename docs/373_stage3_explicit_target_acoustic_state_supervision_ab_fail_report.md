# 373 Stage3 Explicit Target Acoustic-State Supervision A/B Fail Report

## 背景
- 在 `student_control_packet_v1` 的 calibration audit 里，`F0 / vuv / aper / E` 已经能拿到 target-reference 对照。
- 其中 `F0` 相关性不是零，但 `aper / energy` 仍偏弱。
- 这轮的目的不是直接开新 Stage5 route，而是先验证一个更便宜的问题：
  - 把 deterministic target acoustic state 直接接进 Stage3 loss，
  - 是否能在保持共享主指标稳定的前提下改善 `F0 / vuv / aper / E`。

## 代码改动
- batch contract 补充 target acoustic state：
  - `src/v5vc/streaming_student/data.py`
- Stage3 入口补齐 `include_target_acoustic_state=True`：
  - `src/v5vc/streaming_student/train_step_entry.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `src/v5vc/streaming_student/checkpoint_eval_entry.py`
  - `src/v5vc/streaming_student/supervision_entry.py`
- 新增显式 loss，默认权重为 `0`：
  - `src/v5vc/streaming_student/losses.py`
  - `teacher_f0_state`
  - `teacher_vuv_state`
  - `teacher_aper_state`
  - `teacher_energy_state`
- 兼容当前 Python 3.8 运行环境：
  - 去掉当前相关入口中的 `Path.write_text(..., newline=...)`
- candidate override：
  - `configs/streaming_student_loss_weights_explicit_target_acoustic_v1.json`

## Dry-Run 量级探测
- 产物：
  - `reports/plans/streaming_student_supervision_explicitacousticprobe_round1_1/streaming_student_supervision_plan.json`
- `target_validation` 原始量级：
  - `loss_teacher_f0_state = 58.391411`
  - `loss_teacher_vuv_state = 0.717622`
  - `loss_teacher_aper_state = 0.178118`
  - `loss_teacher_energy_state = 1.559344`
- 结论：
  - `F0` 量级明显过大，不能重权直上。
  - 因此 candidate 只用了保守权重：
    - `teacher_f0_state = 0.002`
    - `teacher_vuv_state = 0.05`
    - `teacher_aper_state = 0.05`
    - `teacher_energy_state = 0.02`

## Smoke
- 1-step smoke 已通过：
  - `reports/training/streaming_student_step_explicitacoustic_smoke_round1_1/logs/streaming_student_step_explicitacoustic_smoke_round1_1.step1.json`
- 说明：
  - 新 target-state tensor 已进 batch
  - 新 loss 已真实反传
  - 没有出现立即数值爆炸

## 12-Step Full-Validation A/B
- baseline：
  - `reports/training/streaming_student_loop_directional_explicitacoustic_baseline12_round1_1/logs/streaming_student_stage_loop_directional_explicitacoustic_baseline12_round1_1.summary.json`
- candidate：
  - `reports/training/streaming_student_loop_directional_explicitacoustic_candidate12_round1_1/logs/streaming_student_stage_loop_directional_explicitacoustic_candidate12_round1_1.summary.json`

### step12 validation 对照
- `loss_total`
  - `1.726736 -> 1.936086`
- `loss_total_semantic_disabled_reference`
  - `1.569294 -> 1.777962`
- `loss_teacher_event`
  - `0.504209 -> 0.505376`
- `loss_teacher_event_prior`
  - `0.727416 -> 0.73033`
- `loss_teacher_energy_proxy`
  - `2.578495 -> 2.673196`
- `loss_teacher_f0_state`
  - `69.006061 -> 46.551543`
- `loss_teacher_vuv_state`
  - `0.679986 -> 0.678213`
- `loss_teacher_aper_state`
  - `0.241842 -> 0.225997`
- `loss_teacher_energy_state`
  - `2.162563 -> 1.68863`
- `loss_log_f0_correction_l1`
  - `0.01561 -> 0.81032`
- `loss_aper_correction_l1`
  - `0.063542 -> 0.119833`

## 判断
- 这条线应判为失败，不继续扫权重。
- 原因不是“新 loss 没生效”，而是它生效后带来的净结果更差：
  - 本地 state losses 确实下降了，尤其 `F0`
  - 但共享主指标 `loss_total / loss_total_semantic_disabled_reference` 明显变差
  - `loss_log_f0_correction_l1` 大幅抬升，说明模型开始明显依赖 correction head 去追 state target
- 这说明当前问题不适合用“直接把 deterministic target state 压进现有 Stage3 loss”来解决。

## 结论
- `explicit target acoustic-state supervision` 的 naive loss-side route 正式停线。
- 不继续做：
  - `teacher_f0_state` 小权重 sweep
  - `teacher_vuv_state / teacher_aper_state / teacher_energy_state` 组合微调
  - 再补一个更小 `0.001` 或更大 `0.005` 的机械试验

## 下一步建议
- 回到更结构化的方向，而不是继续加同层 loss：
  - generation-side / contract-side 的 target-state 资产升级
  - 或 `student_control_packet` 的 named-control completion / handoff design
- 当前不应：
  - 因为 local state loss 下降，就提前开启新的 Stage5 adapter
  - 把这轮结果解释成“F0 线快通了”
