# 2026-03-21 `teacher-first / single-target` 终端用户线 bootstrap 报告

## 结论
- 当前终端用户线第一条真实入口已经落地：
  - `run-offline-mvp-teacher-first-vc-demo`
- 这条命令已经能把：
  - source audio
  - teacher runtime / downstream contract
  - consumer-side scaffold
  - Stage5 no-res vocoder checkpoint
  串成一条真正的
  `source audio -> decoded.wav`
  最小闭环
- 当前默认仍沿正式 decode 主线：
  - `use_predicted_activity_gate = true`
  - `predicted_activity_gate_smoothing_frames = 3`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`
- 待审实验分支
  `postenv`
  没有被写死成默认，
  但已通过显式参数保留切换能力

## 本轮目标
1. 不依赖
   `aligned_target`
2. 不依赖 validation package
3. 用现有 teacher-first 与 Stage5 资产，
   先交付一条终端用户可调用的最小入口
4. 同时保留中间 contract / scaffold，
   便于后续排障

## 本轮代码变更

### 1. 新增模块
- `src/v5vc/teacher_first_vc_demo.py`

### 2. 新增 CLI
- `run-offline-mvp-teacher-first-vc-demo`

### 3. 入口能力
- 输入：
  - `--input-audio`
- 中间步骤：
  - 导出
    `teacher_downstream_control_contract.pt`
  - 构建
    `teacher_vocoder_input_scaffold.pt`
  - 加载 Stage5 no-res vocoder checkpoint
  - 直接前向生成
    `waveform_frames`
  - 用现有 OLA 重建逻辑导出
    `decoded.wav`
- 输出：
  - `decoded.wav`
  - `teacher_first_vc_demo.json`
  - `teacher_first_vc_demo.md`
  - 可选保留中间 contract / scaffold

## 当前默认参数口径

### 1. teacher
- 默认 route handoff：
  - `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json`

### 2. conditioning
- 默认 calibration asset：
  - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json`

### 3. vocoder checkpoint
- 默认 checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json`
- 默认 selection target：
  - `best_validation`

### 4. decode
- 默认 predicted activity gate：
  - 开启
- 默认 smoothing：
  - `3`
- 默认 apply mode：
  - `post_ola_envelope`

## 为什么当前默认不是 `stable_late_stop`
- 当前最新正式 selection payload
  并不是每份都含有：
  - `selected_stable_late_stop`
- 但
  `best_validation`
  当前仍稳定落到：
  - `step72`
- 所以终端用户线第一版默认应优先保证：
  - 命令开箱即用
- 不应因为某份 selection payload
  缺少
  `stable_late_stop`
  就让默认入口直接失败

## smoke test

### 命令
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_convert/dataset_ly65_raw.wav `
  --output-dir tmp/teacher_first_vc_demo_smoke `
  --max-audio-sec 2.0 `
  --device cpu
```

### 结果
- exit code:
  `0`
- 输出目录：
  - `tmp/teacher_first_vc_demo_smoke/`
- 主输出：
  - `decoded.wav`
- 中间资产：
  - `teacher_contract/teacher_downstream_control_contract.pt`
  - `teacher_vocoder_input_scaffold/teacher_vocoder_input_scaffold.pt`
- summary 关键字段：
  - `decoded_audio_sec = 1.998333`
  - `decoded_waveform_rms = 0.046524`
  - `selection_target = best_validation`
  - `branch_label = stage5_best_validation_step72__decode_gate_smooth3_postenv`

## 当前边界
- 这条命令当前仍不是：
  - final product runtime
  - many-to-many
  - final pitch-correct output
- 当前仍不支持：
  - `aligned_target` 参考下的 pitch-match
  - validation-side `audit_proxy`
  - target-relative loss / RMS 报告
- 它回答的是：
  - “现在能不能从源音频真的跑到目标音频”
- 它还没有回答：
  - “质量是否已达到成品标准”

## 与实验线的关系
- 当前实验线仍停在：
  - `postenv`
    已完成人工听审且不反转
- 所以终端用户线当前默认已同步提升为：
  - `post_ola_envelope`
- 若需旧行为复现，
  仍可显式传：
  - `--predicted-activity-gate-apply-mode pre_overlap_add`

## 当前建议的下一步
1. 用这条命令对更多真实源音频做 smoke
2. 观察：
   - 是否存在明显 sample-rate / 时长 / 静音输入边界问题
3. 若命令稳定，
   下一步可补：
   - 更清晰的失败分类
   - 更适合终端用户的输出目录契约
   - 一个对应的 PowerShell 包装脚本

## 一句话结论
- 当前终端用户线已经不再停留在设计稿，
  而是正式拥有一条
  `teacher-first / single-target`
  的真实最小闭环命令；
  它现在能把源音频直接跑成
  `decoded.wav`，
  但默认仍严格沿当前正式 decode 主线，
  等待实验线对
  `postenv`
  听审收口后再决定是否升级默认。
