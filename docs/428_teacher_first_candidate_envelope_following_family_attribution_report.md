# 2026-03-27 teacher-first 候选线 residual envelope-following 家族归因报告

## 结论
- 我没有回去继续修
  plain baseline，
  而是直接在当前 user-line 主候选：
  - `branch_mean_contrast_residual_v1 + residualshapecond`
  上做了
  family-level inference-only zero probe，
  只问一个问题：
  - 候选线剩余的
    `envelope-following`
    主要是谁在驱动
- 当前最关键的新结论是：
  1. 不是
     `conditioning_family`
     在主导 residual `envelope-following`
  2. 也不是
     `event_family`
     在主导；
     把它清零反而会更像在恶化包络跟随
  3. 当前 residual `envelope-following`
     的主要承载家族是：
     - `acoustic_state_family`
  4. 在这个家族里，
     最强承载项是：
     - `aper`
  5. `E_log_rms_norm`
     则更像 brightness / high-band
     的主要杠杆
  6. 但直接把
     `aper`
     或
     `aper + E_log_rms_norm`
     清零，
     会把系统明显拉回
     更模板化的区域

## 一、probe 入口
- 命令入口：
  - `analyze-offline-mvp-teacher-first-vc-waveform-handoff`
- 本轮新增了：
  - `--control-family-override family=zero`
- 所有 probe
  统一使用当前 user-line 候选 checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- 样本仍固定为三条 pure buzz：
  - `segment_0001_0000020110_0000021640`
  - `segment_0061_0000300400_0000300910`
  - `peak_011_0002370615_top_peak`

## 二、候选 baseline
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs/`
- aggregate：
  - `branch_mean_to_fused_template_cosine_gap = 0.001379`
  - `waveform_frame_logits_template_cosine_mean = 0.994119`
  - `waveform_frames_template_cosine_mean = 0.993178`
  - `decoded_no_gate template = 0.984637`
  - `decoded_no_gate activity_corr = 0.519889`
  - `decoded_no_gate centroid = 6510.052734`
  - `decoded_no_gate high_band = 0.449300`

这就是当前要解释的 residual：
- 它已经明显优于 plain baseline，
  但仍有可见的
  `envelope-following`

## 三、第一层家族归因

### 1. `conditioning_family = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_cond_z/`
- aggregate：
  - `decoded_no_gate template = 0.942887`
  - `decoded_no_gate activity_corr = -0.878048`
  - `decoded_no_gate centroid = 10733.792969`
  - `decoded_no_gate high_band = 0.741368`

读法：
- conditioning family
  不是 residual envelope-following
  的主故障源
- 把它清掉，
  系统不是更正常，
  而是直接冲进更高频、更失控的坏区

### 2. `event_family = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_evt_z/`
- aggregate：
  - `decoded_no_gate template = 0.983436`
  - `decoded_no_gate activity_corr = 0.684000`
  - `decoded_no_gate centroid = 6678.157715`
  - `decoded_no_gate high_band = 0.463281`

读法：
- `event_family`
  不是 residual envelope-following
  的主承载项
- 清零后：
  - `activity_corr`
    反而更高
  - brightness
    也更高

### 3. `acoustic_state_family = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_ac_z/`
- aggregate：
  - `decoded_no_gate template = 0.992915`
  - `decoded_no_gate activity_corr = -0.084735`
  - `decoded_no_gate centroid = 6493.039551`
  - `decoded_no_gate high_band = 0.440090`

读法：
- residual `envelope-following`
  的主承载家族
  明确落在：
  - `acoustic_state_family`
- 但它同时也在承载一部分
  anti-template 动态；
  因为清零后：
  - `activity_corr`
    被压下去了
  - 但 `template`
    又明显回升到
    `0.992915`

## 四、第二层 acoustic 子族拆分

### 1. `E_log_rms_norm = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_e_z/`
- aggregate：
  - `decoded_no_gate template = 0.985994`
  - `decoded_no_gate activity_corr = 0.476136`
  - `decoded_no_gate centroid = 6340.537598`
  - `decoded_no_gate high_band = 0.427833`

读法：
- `energy`
  会推高 brightness / high-band，
  也会推一点
  `activity_corr`
- 但它不是最强的 envelope-following 承载项

### 2. `vuv = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_vuv_z/`
- aggregate：
  - `decoded_no_gate template = 0.986687`
  - `decoded_no_gate activity_corr = 0.455671`
  - `decoded_no_gate centroid = 6780.478516`
  - `decoded_no_gate high_band = 0.472655`

读法：
- `vuv`
  对 residual `activity_corr`
  有一定贡献，
  但同时会把 brightness
  推得更坏，
  方向不如 `energy`
  清晰

### 3. `f0_hz_log_norm = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_f0_z/`
- aggregate：
  - `decoded_no_gate template = 0.983540`
  - `decoded_no_gate activity_corr = 0.562586`
  - `decoded_no_gate centroid = 6537.020996`
  - `decoded_no_gate high_band = 0.451781`

读法：
- `f0`
  不是 residual `envelope-following`
  的主承载项；
  清零后
  `activity_corr`
  反而更高

### 4. `aper = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_aper_z/`
- aggregate：
  - `decoded_no_gate template = 0.988699`
  - `decoded_no_gate activity_corr = 0.217405`
  - `decoded_no_gate centroid = 6507.225098`
  - `decoded_no_gate high_band = 0.448574`

读法：
- `aper`
  是当前 acoustic 家族里
  最强的 residual envelope-following 承载项
- 它几乎单独把
  `activity_corr`
  从
  `0.519889`
  拉到
  `0.217405`
- 但代价也明确：
  - `template`
    回升到
    `0.988699`

### 5. `aper + E_log_rms_norm = zero`
- 目录：
  - `.../rbt_whp_fbmc_rs_aper_e_z/`
- aggregate：
  - `decoded_no_gate template = 0.988933`
  - `decoded_no_gate activity_corr = 0.141311`
  - `decoded_no_gate centroid = 6315.209473`
  - `decoded_no_gate high_band = 0.427246`

读法：
- 这是当前最像
  “同时压低包络跟随与 brightness”
  的组合
- 但它同样把系统往
  更模板化区域
  拉回去了

## 五、当前主线如何更新
1. 当前候选线的 residual 故障，
   不是再回到：
   - conditioning family
   - event family
2. 当前更准确的剩余主线应写成：
   - acoustic-state family
     在继续承载
     residual envelope-following
   - 其中：
     - `aper`
       是主要的包络跟随承载项
     - `E_log_rms_norm`
       更偏 brightness / high-band
3. 但这两项又不是
   “纯坏控制”：
   - 它们同时还在承载一部分
     anti-template 动态
4. 因而下一步不应：
   - 直接把
     `aper / energy`
     硬清零推进训练
5. 更合理的下一步应是：
   - 研究如何在候选 backbone 上，
     保留
     `aper / energy`
     对 anti-template 的贡献
   - 但削弱它们对
     envelope-following
     的直接耦合

## 一句话结论
- 当前 user-line 候选线的 residual `envelope-following`，
  主承载家族已经收敛到
  `acoustic_state_family`，
  且其中以 `aper` 最强，
  `energy` 次之；
  但它们又同时在提供 anti-template 动态，
  所以下一步应做“去耦”，
  不是简单清零。 
