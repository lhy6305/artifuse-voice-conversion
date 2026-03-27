# 2026-03-27 plain fusion 子阶段定位报告

## 结论
- 我没有继续做
  gate / decoder 小扫，
  而是把当前 plain-fusion baseline
  的 fusion 块内部再拆成：
  - `fusion.0 Linear`
  - `fusion.1 GELU`
  - `fusion.2 LayerNorm`
  - `fusion.3 Linear`
- 然后分别在：
  - user-line 固定三条 pure buzz 样本
  - Stage5 validation3 package
  上做同口径统计。
- 当前最关键的新结论是：
  1. 两边最大的模板化跳变，
     都首先发生在
     `fusion.0 Linear`
  2. 第二个明确跳变点，
     是最后一层
     `fusion.3 Linear`
  3. `GELU / LayerNorm`
     不是主坍缩起点；
     它们更多是在重排尺度，
     不是第一次把系统推入坏 manifold

## 一、user-line 结果
- 产物：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp/fusion_substage_probe_summary.json`

### template 侧
- `branch_mean_hidden_template_cosine_mean = 0.920910`
- `fusion_linear0_template_cosine_mean = 0.976164`
- `fusion_gelu_template_cosine_mean = 0.980961`
- `fusion_layernorm_template_cosine_mean = 0.979663`
- `fused_hidden_template_cosine_mean = 0.994767`

### 关键 gap
- `branch_mean_to_linear0_template_gap = +0.055254`
- `linear0_to_gelu_template_gap = +0.004797`
- `gelu_to_layernorm_template_gap = -0.001298`
- `layernorm_to_fused_template_gap = +0.015104`
- `branch_mean_to_fused_template_gap = +0.073857`

### temporal delta 比例
- `branch_mean_to_linear0_delta_ratio = 0.751390`
- `linear0_to_gelu_delta_ratio = 0.475185`
- `gelu_to_layernorm_delta_ratio = 2.871049`
- `layernorm_to_fused_delta_ratio = 0.500120`
- `branch_mean_to_fused_delta_ratio = 0.512676`

读法：
- user-line 上，
  第一大压缩发生在：
  - `branch_mean -> fusion.0 Linear`
- 最后一层
  `fusion.3 Linear`
  又补了一次明显模板化
- `LayerNorm`
  会把 delta 幅度重新拉起来一点，
  但并没有把模板化拉回去

## 二、validation3 结果
- 产物：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_validation3_gateoff_round1_1/fusion_substage_probe_summary.json`

### template 侧
- `branch_mean_hidden_template_cosine_mean = 0.804829`
- `fusion_linear0_template_cosine_mean = 0.946709`
- `fusion_gelu_template_cosine_mean = 0.964400`
- `fusion_layernorm_template_cosine_mean = 0.963044`
- `fused_hidden_template_cosine_mean = 0.991426`

### 关键 gap
- `branch_mean_to_linear0_template_gap = +0.141880`
- `linear0_to_gelu_template_gap = +0.017691`
- `gelu_to_layernorm_template_gap = -0.001356`
- `layernorm_to_fused_template_gap = +0.028382`
- `branch_mean_to_fused_template_gap = +0.186597`

### temporal delta 比例
- `branch_mean_to_linear0_delta_ratio = 0.727474`
- `linear0_to_gelu_delta_ratio = 0.445368`
- `gelu_to_layernorm_delta_ratio = 2.997511`
- `layernorm_to_fused_delta_ratio = 0.508786`
- `branch_mean_to_fused_delta_ratio = 0.494121`

读法：
- validation3
  与 user-line
  方向一致，
  只是幅度更大：
  - 第一大跳变仍是
    `fusion.0 Linear`
  - 第二跳变仍是
    `fusion.3 Linear`

## 三、当前应如何解释
1. plain fusion 的主问题，
   已经不是一个抽象的
   “fusion 之后坏掉”
2. 更准确的结构定位应是：
   - `branch_mean / concat hidden`
     进入
     `fusion.0 Linear`
     后，
     先被大幅压向模板区
   - 最后一层
     `fusion.3 Linear`
     再把它推向更固定的
     `fused_hidden`
3. 这意味着：
   - 下一步不应回头抠：
     - gate
     - `tanh`
     - `GELU / LayerNorm` 局部参数
   - 应继续优先看：
     - plain fusion backbone
       是否需要结构性替代
     - 以及已经存在的
       `branch_mean_contrast_residual_v1 + residualshapecond`
       候选
       是否真的把 user-line
       也带离这块坏 manifold

## 一句话结论
- plain fusion 的主坍缩点，
  在 `fusion.0 Linear` 与 `fusion.3 Linear`，
  不是 gate，
  也不是 `GELU / LayerNorm`；
  当前主线应继续转向
  fusion backbone 结构替代。 
