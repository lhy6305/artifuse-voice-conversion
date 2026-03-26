# 375 Stage3 Teacher-Label Target-State Contract Completion Report

## 结论
- 我已经把 deterministic `target acoustic state` 正式并入 `Stage3 teacher_labels` 资产，而不是继续让 Stage3 在训练时各处临时从 waveform 重算。
- 当前 `teacher_labels` payload 现在除了：
  - `e_evt`
  - `acoustic`
  - `frame_confidence`
  之外，还正式带：
  - `target_f0_hz`
  - `target_vuv`
  - `target_aper`
  - `target_energy`
  - `target_acoustic_state_meta`
- `streaming_student.data` 也已改成：
  - 优先读取 teacher payload 内置 target-state
  - 只有旧资产缺字段时，才回退到 waveform 提取

## 为什么这步值得做
- 之前虽然已经能在 Stage3 batch 里拿到 deterministic target state，
  但来源是运行时临时重算。
- 这种做法的问题是：
  - contract 不显式
  - teacher asset 与 Stage3 batch 不同源
  - downstream packet audit 与 Stage3 training 也不共享同一份命名 target-state
- 当前补齐后，teacher-side target-state 终于成为可复用资产，而不是一次性的训练时 helper。

## 代码改动
- teacher label export：
  - `src/v5vc/streaming_student/teacher_labels.py`
- Stage3 data loader：
  - `src/v5vc/streaming_student/data.py`

## 本轮验证

### 1. smoke export
- 输出：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directional_targetstate_smoke_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directional_targetstate_smoke_round1_1/`
- 单条 payload 核对：
  - `target__archive_firefly_1.pt`
  - 已包含：
    - `target_f0_hz`
    - `target_vuv`
    - `target_aper`
    - `target_energy`
    - `target_acoustic_state_meta`
- 示例：
  - `target_acoustic_state_meta.version = source_acoustic_state_extraction_v1`
  - `target_acoustic_state_meta.aper_version = aper-v1`
  - `target_f0_hz.shape = [3054, 1]`

### 2. 全量 export
- 输出：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directional_targetstate_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directional_targetstate_round1_1/`
- 摘要：
  - `record_count = 666`
  - `frame_count = 1118127`
  - `feature_dims` 已包含：
    - `target_f0_hz = 1`
    - `target_vuv = 1`
    - `target_aper = 1`
    - `target_energy = 1`

### 3. index metadata
- `teacher_label_index.jsonl` 已新增：
  - `target_acoustic_state_version`
  - `target_acoustic_state_aper_version`
  - `target_acoustic_state_voiced_ratio`

### 4. Stage3 data loader 复用确认
- 我用新全量 index 直接调用了：
  - `load_streaming_student_target_examples_from_records(..., include_target_acoustic_state=True)`
- 对 `target::chapter3_3_firefly_162` 做了 payload 一致性检查：
  - `example.target_f0_hz == payload['target_f0_hz']`
  - `example.target_vuv == payload['target_vuv']`
  - `example.target_aper == payload['target_aper']`
  - `example.target_energy == payload['target_energy']`
- 四项均为 `True`
- 说明：
  - Stage3 现在确实优先吃 teacher asset 内置 target-state，
  - 不是继续临时重算。

### 5. supervision dry-run
- 输出：
  - `reports/plans/streaming_student_supervision_eevt_directional_targetstate_round1_1/`
- 结果：
  - dry-run 正常通过
  - 新 full index 与当前 Stage3 supervision contract 兼容

## 当前判断
- 这一步不是“新 loss 更好了”，也不是“已经可以开新 Stage5 route”。
- 它的价值在于：
  - teacher-side target-state contract 终于资产化了
  - 后续 generation-side target-state 升级、named-control audit、以及 handoff 讨论
    都可以基于同一份 teacher asset，而不是不同地方各算一遍

## 结论
- `teacher_labels_eevt_directional_targetstate_round1_1`
  现在应作为新的 Stage3 teacher asset 基线保留。
- 当前仍不做：
  - direct state loss injection 小权重 sweep
  - 新的 Stage5 handoff route 开训

## 下一步
- 后续更合理的动作是：
  - 在这份新 teacher asset 基线之上继续做 generation-side / target-state contract 升级
  - 或继续收紧 `student_control_packet` 的 named-control readiness
- 而不是回到“训练时临时提取 target state”的旧模式。
