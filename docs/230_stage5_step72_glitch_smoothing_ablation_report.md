# 230. Stage5 `step72` glitch smoothing ablation 报告

## 背景
- `docs/229_stage5_low_activity_validation12_spectral_gap_sidecar_report.md`
  已把当前主线收敛为:
  - `72`
    仍是
    最合适的临时锚点
  - 但局部
    glitch / burst
    仍是主问题
- 当前最可疑的机理是:
  - export-side
    `predicted_activity_gate`
    以逐帧标量
    硬乘到 waveform frame
  - 它虽然压低了
    leakage，
    但也可能在
    低活动边界
    引入跳变

## 本轮目标
1. 先不改训练
2. 只在 export-side
   验证:
   - hard gate
     是否真是
     局部毛刺来源
3. 若成立，
   再试:
   - smoothing-only
   - smoothing + floor
   看哪条更健康

## 本轮代码变更

### 1. 修改文件
- `src/v5vc/offline_vocoder_training.py`
- `src/v5vc/nores_vocoder_audio_export.py`
- `src/v5vc/cli.py`

### 2. 新增能力
- `reconstruct_waveform_from_frames(...)`
  现在支持:
  - `frame_gain_floor`
  - `frame_gain_smoothing_frames`
- `export-offline-mvp-nores-vocoder-audio`
  新增参数:
  - `--predicted-activity-gate-floor`
  - `--predicted-activity-gate-smoothing-frames`
- 非默认 export-side
  decode
  设置
  会自动写入
  `branch_label`，
  例如:
  - `__decode_gate_smooth3`
- 新增 GUI 听审脚本:
  - `scripts/launch_stage5_step72_glitch_smoothing_audit.ps1`

## 本轮执行

### 1. 代表性 record
- `target::chapter3_6_firefly_106`
- `target::chapter3_26_firefly_107`
- `target::chapter3_29_firefly_113`

### 2. export-side 变体
- baseline:
  - `use_predicted_activity_gate = true`
  - `smoothing = 0`
  - `floor = 0`
- smoothing-only:
  - `smooth1`
  - `smooth2`
  - `smooth3`
- smoothing + floor:
  - `smooth2 + floor0.05`
  - `smooth2 + floor0.08`
  - `smooth3 + floor0.08`

## 当前结果

### 1. hard gate 确实是 glitch 来源之一，但不能直接拔掉
- 关掉 gate
  后，
  代表性 record
  的
  `decoded_to_target_rms_ratio`
  明显飙高:
  - `chapter3_6_firefly_106`
    - `1.085058 -> 1.911431`
  - `chapter3_26_firefly_107`
    - `0.828752 -> 1.144444`
  - `chapter3_29_firefly_113`
    - `0.991431 -> 1.526051`
- 这说明:
  - gate
    不是可直接删除的多余组件
  - 它在压 leakage
    上
    仍然有价值

### 2. `floor` 路线过度回到了“常亮低电平泄漏”
- smoothing + floor
  虽然能把
  fragmentation
  压到:
  - `0.0`
- 但也会把:
  - `mean_active_fraction`
    推回
    `1.0`
  - `mean_activity_alignment_mae`
    推回
    `0.981209`
- 这更像:
  - 毛刺没了，
    但低活动段又重新
    常亮
- 当前不应把
  `floor`
  作为第一默认修复方向

### 3. `smoothing-only` 是当前更健康的方向
- 正式 probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smoothing_validation3_round1_1/`
- aggregate:
  - baseline
    - `mean_fragmentation_score = 2.453222`
    - `mean_waveform_rms = 0.013321`
    - `mean_sample_delta_peak = 0.139163`
  - `smooth1`
    - `2.403934`
    - `0.012963`
    - `0.095724`
  - `smooth2`
    - `1.703702`
    - `0.013638`
    - `0.081886`
  - `smooth3`
    - `1.543622`
    - `0.014492`
    - `0.077360`
- 当前解释:
  - `smooth3`
    把 fragmentation
    从
    `2.453222`
    压到
    `1.543622`
  - 同时
    `waveform_rms`
    只从
    `0.013321`
    升到
    `0.014492`
  - 属于
    明显更像
    “可接受 tradeoff”
    的方向

### 4. 代表性 top windows 上，`smooth3` 一直是当前最好分支
- 当前 top windows
  中，
  `smooth3`
  连续成为
  最优分支:
  - `chapter3_6_firefly_106 / segment1`
  - `chapter3_26_firefly_107 / segment1`
  - `chapter3_6_firefly_106 / segment2`
  - `chapter3_26_firefly_107 / segment5`
  - `chapter3_26_firefly_107 / segment3`
- 这说明:
  - 改善
    不是只出现在
    单个巧合窗口

### 5. `validation12` 扩样后，`smooth3` 方向仍成立
- 扩样 probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1/`
- aggregate:
  - baseline `72`
    - `mean_fragmentation_score = 1.497705`
    - `mean_waveform_rms = 0.013488`
    - `mean_sample_delta_peak = 0.162141`
    - `mean_activity_alignment_mae = 0.513092`
  - `72__decode_gate_smooth3`
    - `mean_fragmentation_score = 1.196807`
    - `mean_waveform_rms = 0.014613`
    - `mean_sample_delta_peak = 0.079572`
    - `mean_activity_alignment_mae = 0.550197`
- 当前解释:
  - `smooth3`
    不是只在
    `3`
    条代表性 record
    上碰巧有效
  - 放到
    `validation12`
    后，
    仍然保持:
    - 明显更低的
      fragmentation
      与
      sample_delta_peak
    - 同时只付出
      较小的
      leakage /
      alignment
      代价

## 当前判断

### 1. 下一步最值得继续推进的是 smoothing-only，不是 floor
- 当前最合理的 decode-side
  候选是:
  - `predicted_activity_gate_smoothing_frames = 3`
  - `predicted_activity_gate_floor = 0.0`

### 2. 当前还不应直接改写全局默认 decode
- 因为:
  - 虽然已经补到
    `validation12`
  - 但还没有经过
    focused
    人耳复核
- 但它已经足够说明:
  - 后续 focused audit
    不该再只听
    baseline `72`
  - 应该听:
    - baseline `72`
    - `72__decode_gate_smooth3`

## 当前产物
- baseline export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_gateon_validation3_round1_1/`
- smoothing exports:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth1_validation3_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth2_validation3_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3_validation3_round1_1/`
- smoothing probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smoothing_validation3_round1_1/`
- `validation12` 扩样 probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1/`
- GUI 入口:
  - `scripts/launch_stage5_step72_glitch_smoothing_audit.ps1`

## 一句话结论
- 当前 `72`
  的局部毛刺
  更像
  hard predicted-activity gate
  的副作用，
  而不是 gate
  机制本身必须被删掉；
  当前最合理的下一棒是
  继续沿
  `smoothing-only`
  尤其
  `smooth3`
  方向推进，
  再做更宽样本和人耳复核。
