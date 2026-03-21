# 2026-03-21 用户线 gate 隔离试验与 runtime 风险告警报告

## 结论
- 本轮已把用户线短期计划中的两项工作落地：
  1. decoder-side gate 隔离试验
  2. runtime summary 风险告警
- 当前最重要的新结论是：
  - `post_ola_envelope`
    与
    `pre_overlap_add`
    在 buzzing 问题上几乎没有本质差异
  - 关闭 predicted activity gate
    后，
    输出整体幅度会上升，
    但高频占比、centroid、rolloff
    仍继续维持在异常高位
- 因而当前判断进一步收敛为：
  - buzzing
    不是主要由
    predicted activity gate
    的 apply mode
    放大出来的
  - 更像是：
    当前 user-line control / conditioning
    对 Stage5 checkpoint
    本身就不在健康适用范围内

## 本轮代码变更

### 1. decoder behavior probe 现已支持 gate 隔离
- CLI：
  - `analyze-offline-mvp-teacher-first-vc-decoder-behavior`
- 新增参数：
  - `--use-predicted-activity-gate`
  - `--disable-predicted-activity-gate`
  - `--predicted-activity-gate-apply-mode`

### 2. 用户线 summary 现已带风险告警
- `run-offline-mvp-teacher-first-vc-demo`
  导出的
  `teacher_first_vc_demo.json/.md`
  现新增：
  - `applicability_risk`
  - `waveform_decode.decoded_spectral_summary`
- 当前风险启发式版本：
  - `teacher_first_runtime_risk_v1`
- 当检测到明显高风险频谱行为时，
  summary 会直接给出：
  - `status = high_risk`
  - 风险信号
  - 推荐动作

## 本轮隔离试验

### 固定输入
- `segment_0001_0000020110_0000021640.wav`
- `segment_0061_0000300400_0000300910.wav`
- `peak_011_0002370615_top_peak.wav`

### 方案 A：gate on + `post_ola_envelope`
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_decoder_behavior_postenv_probe/`

### 方案 B：gate on + `pre_overlap_add`
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_decoder_behavior_preola_probe/`

### 方案 C：gate off
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_decoder_behavior_nogate_probe/`

## 关键结果

### 1. `postenv` vs `pre_overlap_add` 几乎不反转
- 以常规 segment
  为例：
  - postenv:
    `HF=0.479510`
  - pre_overlap_add:
    `HF=0.479940`
- 高静音 case：
  - postenv:
    `HF=0.477566`
  - pre_overlap_add:
    `HF=0.480087`
- peak case：
  - postenv:
    `HF=0.477874`
  - pre_overlap_add:
    `HF=0.478144`
- 说明：
  - apply mode
    只带来很小扰动，
    不能解释 buzzing

### 2. 关闭 gate 后异常高频分布依旧存在
- 常规 segment：
  - gate off:
    `HF=0.478479`
    `centroid=3299.43`
    `rolloff95=22799.35`
- 高静音 case：
  - gate off:
    `HF=0.473941`
    `centroid=3302.87`
    `rolloff95=22798.03`
- peak case：
  - gate off:
    `HF=0.477796`
    `centroid=3286.86`
    `rolloff95=22799.29`
- 说明：
  - 不依赖 predicted gate，
    当前 decoded 行为
    仍系统性偏向高频

### 3. gate off 主要改变的是幅度，不是频谱异常方向
- gate off
  会明显抬高 RMS，
  尤其对高静音 case：
  - postenv:
    `RMS=0.027716`
  - gate off:
    `RMS=0.165188`
- 这说明：
  - predicted gate
    主要起到了幅度压制作用
  - 但没有把“高频 buzzing 根因”
    消掉

## runtime 风险告警 smoke

### 命令
```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --output-dir tmp/teacher_first_vc_demo_risk_smoke `
  --max-audio-sec 0.1 `
  --device cpu `
  --no-save-intermediates `
  --skip-full-pass-verify
```

### 结果
- summary 路径：
  - `tmp/teacher_first_vc_demo_risk_smoke/teacher_first_vc_demo.json`
- 关键字段：
  - `applicability_risk.status = high_risk`
  - `decoded_spectral_high_band_energy_ratio = 0.472851`
  - `decoded_spectral_centroid_hz = 3334.621699`
  - `decoded_spectral_rolloff95_hz = 22789.830078`

## 当前推荐的下一步
1. 当前不建议再继续扫
   gate apply mode
   周边小题。
2. 若继续用户线，
   下一题应转向：
   - user-line control / conditioning
     如何贴近 Stage5 训练内分布
   - 或如何在用户线入口前
     增加更强的 applicability guard
3. 在缓解策略落地前，
   当前用户线输出更适合：
   - 工程通路验证
   - 诊断排障
   不适合直接当成终端用户质量展示样本

## 一句话结论
- 本轮隔离试验已经把“是不是 predicted gate 造成 buzzing”
  这个问题基本排掉了；
  当前更像是
  Stage5 checkpoint
  对 user-line control
  的整体适用性失配，
  而 runtime summary
  现在已经能直接把这类高风险状态写出来。
