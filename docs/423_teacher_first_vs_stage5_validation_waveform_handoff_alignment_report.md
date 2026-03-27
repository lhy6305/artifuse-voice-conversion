# 2026-03-27 teacher-first 三样本与 Stage5 validation3 waveform handoff 对照报告

## 结论
- 我在跑完 user-line 固定三样本的
  waveform handoff probe
  之后，
  又用同一个 checkpoint
  在 `contractv2_normfix`
  的 validation3 package
  上补跑了
  `analyze-stage5-nores-waveform-handoff`
  做最小对照。
- 当前最关键的新结论是：
  - user-line
    并没有在 handoff stage
    额外出现一个只属于它自己的新 collapse
  - 相反：
    - validation package
      自己也基本处在同样的
      `waveform_frame_logits / waveform_frames`
      模板化坏工作区
- 因而当前更准确的口径应是：
  - user-line
    不是把一个健康 checkpoint
    特殊推坏了
  - 它只是把
    当前 checkpoint-native
    的 waveform handoff collapse
    又复现了一遍

## 一、对照对象

### 1. user-line
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe/`
- 样本：
  - `segment_0001_0000020110_0000021640`
  - `segment_0061_0000300400_0000300910`
  - `peak_011_0002370615_top_peak`

### 2. Stage5 validation
- 目录：
  - `reports/runtime/stage5_waveform_handoff_probe_contractv2_normfix_validation3_round1_1/`
- 命令：
```powershell
.\python.exe manage.py analyze-stage5-nores-waveform-handoff `
  --output-dir reports/runtime/stage5_waveform_handoff_probe_contractv2_normfix_validation3_round1_1 `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --split-name validation `
  --sample-count 3 `
  --device cpu `
  --predicted-activity-gate-smoothing-frames 3
```

## 二、stage 侧 aggregate 对照

### 1. `decoder_hidden`
- `decoder_hidden_template_cosine_mean`
  - user-line: `0.994928`
  - validation: `0.991694`
  - 差值：`+0.003234`
- 解释：
  - user-line
    在更上游 hidden 侧
    略更模板化，
    但量级还不算特别大

### 2. `waveform_frame_logits`
- `waveform_frame_logits_template_cosine_mean`
  - user-line: `0.999641`
  - validation: `0.999573`
  - 差值：`+0.000068`
- `waveform_frame_logits_adjacent_cosine_mean`
  - user-line: `0.999987`
  - validation: `0.999976`
  - 差值：`+0.000011`
- `waveform_frame_logits_fraction_abs_ge_1`
  - user-line: `0.068172`
  - validation: `0.070726`
  - 差值：`-0.002554`

### 3. `waveform_frames`
- `waveform_frames_template_cosine_mean`
  - user-line: `0.999597`
  - validation: `0.999516`
  - 差值：`+0.000081`
- `waveform_frames_adjacent_cosine_mean`
  - user-line: `0.999986`
  - validation: `0.999972`
  - 差值：`+0.000014`
- `logits_to_frames_template_cosine_gap`
  - user-line: `-0.000044`
  - validation: `-0.000057`

## 三、如何解读这些数
- 最关键的不是
  user-line
  比 validation
  高了多少个小数位，
  而是：
  - 两边都已经在
    `0.9995+`
    这一级别
  - 也就是：
    - 还没到 gate，
      `waveform_frame_logits`
      就已经几乎是固定模板
    - 到
      `waveform_frames`
      也没有再发生
      新的一次明显坍塌
- 这说明：
  - 当前坏相位
    不是 user-line
    新发明出来的
  - validation package
    自己也在同一个坏 manifold

## 四、route 侧读法

### 1. 训练包 probe 的正式诊断
- `buzz_before_predicted_activity_gate = true`
- `predicted_activity_gate_changes_auto_reject_status = false`
- `tanh_is_main_new_collapse_site = false`
- `primary_localization = buzz_present_by_waveform_frames_before_gate`

### 2. 这与 user-line probe 的关系
- user-line probe
  给出的结论是：
  - `likely_failure_already_present_by_frames_before_gate = true`
- 两边结论方向一致：
  - 都不是 gate
    才第一次把系统推入坏解
  - 都更像是：
    - gate 前
      就已经坏了

## 五、对当前主线的影响
1. 不能再把用户线现象优先写成：
   - user-line 特有
     control mismatch
   - user-line special decode bug
2. 当前更准确的主线表述应是：
   - Stage5 native teacher
     本体在 validation package
     上就已经处在同类 waveform handoff collapse
   - user-line
     只是把这个坏工作区
     在终端入口上更直接地暴露出来
3. 因而下一步不应优先投入：
   - 只面向 user-line
     的 gate / normalize
     微修
4. 更合理的方向是：
   - 回到 Stage5 native teacher
     本体的
     waveform handoff / projector
     主病灶
   - 把 `user-line` 与 `validation`
     一起视作同类坏 manifold 的两种观测面

## 一句话结论
- user-line 三样本与 Stage5 validation3 的 waveform handoff 形状高度一致；
  当前问题不是“user-line 把健康 checkpoint 推坏”，
  而是“checkpoint 自己就在 native validation 路线上停在同类 waveform collapse”。 
