# 371. Stage3 `student_control_packet_v1` bootstrap 与 proxy screen smoke 报告

## 结论
- `Stage3 student-control packet v1` 已经不是文档候选，而是可执行导出物。
- 我新增了 Stage3 packet exporter，能把 checkpoint 的 student outputs 以 named-control candidate 的形式落盘。
- 当前 smoke 使用：
  - `acoustic_directional_transition_bridge_v1`
  - `step24` best checkpoint
- 结果是正向的，但要带一个关键边界：
  - `e_evt` 已经能以 `teacher_e_evt_v1` 口径导出
  - `z_art` 也已稳定落盘
  - 但 `F0 / aper / E` 现在仍是 Stage3 proxy/control status，不应误写成“已完成 Stage5-ready design-state contract”
- 同时我把 cheap screen 也跑通了：
  - Stage3 proxy audio export 已生成
  - 这意味着后续新的 handoff 候选，不必一上来就送进 Stage5

## 一、本轮实现

### 1. 新增 exporter
- 新文件：
  - `src/v5vc/streaming_student/downstream_control_packet.py`
- 新 CLI：
  - `export-streaming-student-downstream-control-packet`
- 相关接线：
  - `src/v5vc/cli.py`
  - `src/v5vc/streaming_student/__init__.py`

### 2. 当前 packet 的含义
- 每条记录会导出：
  - `z_art`
  - `legacy_event_probs`
  - `e_evt`
  - `f0_log_proxy`
  - `vuv_prob`
  - `aper_prob`
  - `energy_log`
  - `energy_norm`
- 当前 contract 明确写死：
  - `r_res` 缺席
  - `e_evt` 仅在 `event_target_family = teacher_e_evt_v1` 时作为 named event candidate 导出
  - `F0` 仍是 `log_domain_proxy_not_calibrated_hz`
  - `aper / E` 仍是 bounded/log proxy

## 二、smoke export 结果

### 1. packet export
- 输出目录：
  - `reports/runtime/streaming_student_downstream_control_packet_directional_smoke_round1_1/`
- 主摘要：
  - `reports/runtime/streaming_student_downstream_control_packet_directional_smoke_round1_1/streaming_student_downstream_control_packet.json`
- 本轮 checkpoint：
  - `reports/training/streaming_student_loop_eevt_directional_fullval24_round1_1/checkpoints/streaming_student_stage_loop_eevt_directional_fullval24_round1_1.step24.pt`
- 关键确认：
  - `packet_version = streaming_student_downstream_control_v1`
  - `event_target_family = teacher_e_evt_v1`
  - `event_projection_mode = full_e_evt`
  - `packet_ready_count = 2 / 2`
  - `r_res_enabled = false`
- 说明：
  - 这不是 metadata-only
  - smoke 里的两个 validation record 都真的导出了 named-control candidate packet

### 2. 两个样本的摘要
- `target::chapter3_3_firefly_162`
  - `frame_count = 167`
  - `packet_ready_for_named_e_evt_handoff = true`
  - `z_art_abs_mean = 0.61706`
  - `e_evt_mean = 0.214285`
- `target::chapter3_4_firefly_106`
  - `frame_count = 5815`
  - `packet_ready_for_named_e_evt_handoff = true`
  - `z_art_abs_mean = 0.464573`
  - `e_evt_mean = 0.215745`

## 三、cheap screen 已接通

### 1. proxy audio export
- 输出目录：
  - `reports/audio/streaming_student_proxy_audio_directional_smoke_round1_1/`
- 主摘要：
  - `reports/audio/streaming_student_proxy_audio_directional_smoke_round1_1/proxy_audio_export.json`
- 当前 bundle 内容：
  - 每个 case 含 `input / teacher_proxy / student_proxy`
  - 当前共 2 个 case

### 2. 当前这一步的意义
- 这不是 final audio，也不是 Stage5 输出
- 它的价值是：
  - 让新的 handoff candidate 在进入 Stage5 前，先经过一个便宜的结构筛选层
- 所以从现在开始，更合理的流程是：
  - `student_control_packet_v1`
  - `proxy_acoustic / proxy_audio` cheap screen
  - 通过后再考虑新的 Stage5 adapter/scaffold

## 四、当前边界条件
1. 不能把 `packet_ready_for_named_e_evt_handoff = true` 误解成“整个 design-state contract 都已完成”。
2. 当前 `e_evt` 是 ready 的，但 `F0` 仍只是 log-domain proxy，不是校准好的 Hz control。
3. 当前 `aper / E` 也仍是 proxy 形式，因此这个 packet 还不该直接冒充最终 Stage5-ready handoff contract。
4. 所以这轮的正确定位是：
   - handoff family 已经从“文档候选”推进到“可导出的 student-side packet”
   - 但还没推进到“可以直接开新 Stage5 adapter 训练”

## 五、下一步
1. 先利用现成 proxy bundle 做 cheap screen 判断，而不是直接开新的 Stage5 route。
2. 若 cheap screen 仍显示结构不足，则优先回到 Stage3 packet/target-state 侧，而不是强行开 Stage5 adapter。
3. 若 cheap screen 显示结构已有明显承接价值，再定义新的 `Stage5 student-control scaffold / adapter v4`。
