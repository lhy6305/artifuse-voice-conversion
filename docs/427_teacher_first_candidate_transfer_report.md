# 2026-03-27 teacher-first user-line 候选 checkpoint 转移验证报告

## 结论
- 我没有继续在
  plain-fusion baseline
  上做局部微修，
  而是直接把当前 native-teacher
  最强候选：
  - `branch_mean_contrast_residual_v1 + residualshapecond`
  接到 user-line 固定三条 pure buzz 样本上，
  跑了同口径的：
  - waveform handoff probe
  - waveform decoder structure probe
- 当前最关键的新结论是：
  1. 这条候选在线上不是单例有效，
     它能稳定把 user-line
     拉离原来的
     plain-fusion 坏 manifold
  2. 最关键的一跳已经明显收缩：
     - `branch_mean_to_fused_template_cosine_gap`
       `0.073843 -> 0.001379`
  3. handoff 侧也同步改善：
     - `waveform_frame_logits_template_cosine_mean`
       `0.999641 -> 0.994119`
     - `waveform_frames_template_cosine_mean`
       `0.999597 -> 0.993178`
  4. decoded route
     不再是原来的纯 buzz 区：
     - `decoded_no_gate template`
       `0.993580 -> 0.984637`
  5. 但它还没有完全转正：
     - `decoded_no_gate`
       的
       `predicted_activity_to_decoded_frame_rms_corr`
       仍为
       `0.519889`
     - 说明仍有明显
       `envelope-following`
       残留

## 一、候选来源
- native-teacher 主线候选：
  - `docs/417_stage5_native_teacher_fusion_branchmean_contrast_residualshape_breakthrough_report.md`
- 对应 selector：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 本轮 user-line probe
  使用：
  - `selection_target = best_validation`

## 二、user-line waveform handoff 对照

### baseline plain fusion
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_waveform_handoff_probe/`
- aggregate：
  - `branch_mean_to_fused_template_cosine_gap = 0.073843`
  - `decoder_to_logits_template_cosine_gap = 0.004712`
  - `waveform_frame_logits_template_cosine_mean = 0.999641`
  - `waveform_frames_template_cosine_mean = 0.999597`
  - `decoded_no_gate template = 0.993580`
  - `decoded_no_gate activity_corr = -0.049617`
  - `decoded_no_gate centroid = 6852.941895`
  - `decoded_no_gate high_band = 0.391782`

### candidate `branch_mean_contrast_residual_v1 + residualshapecond`
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs/`
- aggregate：
  - `branch_mean_to_fused_template_cosine_gap = 0.001379`
  - `decoder_to_logits_template_cosine_gap = 0.013565`
  - `waveform_frame_logits_template_cosine_mean = 0.994119`
  - `waveform_frames_template_cosine_mean = 0.993178`
  - `decoded_no_gate template = 0.984637`
  - `decoded_no_gate activity_corr = 0.519889`
  - `decoded_no_gate centroid = 6510.052734`
  - `decoded_no_gate high_band = 0.449300`

### 读法
- plain baseline
  的第一大坍缩，
  原本是：
  - `branch_mean -> fused`
- 候选线把这一步几乎直接压平了：
  - `0.073843 -> 0.001379`
- 同时
  `waveform_frame_logits / waveform_frames`
  也显著离开
  `0.9995+`
  的固定模板区
- 这说明：
  - 当前候选
    不是只在 native validation
    上偶然逃过 auto-reject
  - 它在 user-line
    也确实改变了 handoff manifold

## 三、user-line structure probe 对照

### baseline plain fusion
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp/`
- aggregate：
  - `fused_hidden_template_cosine_mean = 0.994928`
  - `waveform_frames_template_cosine_mean = 0.999597`
  - `decoded_frames_template_cosine_mean = 0.993580`
  - `branch_mean_to_fused_template_cosine_gap = 0.073843`

### candidate `branch_mean_contrast_residual_v1 + residualshapecond`
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp_fbmc_rs/`
- aggregate：
  - `fused_hidden_template_cosine_mean = 0.980554`
  - `waveform_frames_template_cosine_mean = 0.993178`
  - `decoded_frames_template_cosine_mean = 0.984637`
  - `branch_mean_to_fused_template_cosine_gap = 0.001379`

### 读法
- 这条候选并没有完全消灭模板化，
  但它已经把 user-line baseline
  从：
  - `fused 0.9949 / waveform 0.9996 / decoded 0.9936`
  拉到了：
  - `fused 0.9806 / waveform 0.9932 / decoded 0.9846`
- 这已经不是
  “仍停在同一个坏 manifold 里只做小抖动”
  的量级

## 四、当前主线如何更新
1. plain fusion baseline
   现在可以正式降级为：
   - 已确认主坍缩基线
   - 不再值得继续做局部微修
2. 当前实验主线应切到：
   - `branch_mean_contrast_residual_v1 + residualshapecond`
   这条候选
3. 但下一阶段的目标也要收紧：
   - 不再是证明
     “它能不能离开 pure buzz”
   - 这件事已经基本成立
   - 下一步应直接定位：
     - 为什么 user-line 上
       `envelope-following`
       仍然明显残留

## 一句话结论
- 当前 native-teacher 最强候选
  已能稳定把 user-line
  拉离 plain-fusion 的纯 buzz 坏 manifold；
  下一步主线不该再回头修 plain baseline，
  而应直接转到
  候选线剩余的
  `envelope-following`
  残余故障。 
