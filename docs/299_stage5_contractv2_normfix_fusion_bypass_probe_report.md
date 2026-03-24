# 2026-03-24 Stage5 `contractv2_normfix` fusion-bypass 结构探针报告

## 结论
- 本轮已在现有
  `waveform decoder structure probe`
  上扩展并完成一轮新的
  **fusion-bypass / branch-substitution**
  诊断：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_bypass_round1_1/`
- 当前最关键的结论是：
  1. **decoder 不是“只能输出固定 buzz”的纯常模板器件**
  2. **只要直接喂它 branch-side hidden 动态，decoded template 化会明显下降**
  3. 但这些 bypass 输出会同时出现：
     - 幅度比明显失控
     - 高频重心大幅上冲
  4. 所以当前更准确的系统判断是：
     - 主坍缩仍然首先发生在
       `fusion -> fused_hidden`
     - 但 decoder
       也已经被当前
       collapsed fused manifold
       “驯化”了；
       一旦直接喂入更动态的 hidden，
       它会响应，
       但会落到
       **高频、过响、非语音**
       的非稳态区域

## 一、探针目的
- 前一轮
  `docs/296`
  已确认：
  - baseline 下
    `periodic_hidden / noise_hidden`
    尚未完全坍缩
  - 但
    `fusion -> fused_hidden`
    已高度模板化
- 当前真正需要回答的新问题是：
  - 如果绕过当前
    `fusion`
    的坏输出，
    直接给 decoder
    更有动态的 hidden，
    它能不能用起来？

## 二、运行配置
- 代码入口：
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
- runtime 目录：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_bypass_round1_1/`
- checkpoint selection：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json`
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 运行设置：
  - `selection_target = best_validation`
  - `split_name = validation`
  - `sample_count = 12`
  - `device = cpu`
  - `use_predicted_activity_gate = true`
  - `predicted_activity_gate_smoothing_frames = 3`
  - `predicted_activity_gate_apply_mode = post_ola_envelope`

## 三、本轮新增 probe 设计
- baseline：
  - 原始 checkpoint
- 旧结构探针保留：
  - `periodic_hidden_frame_mean`
  - `noise_hidden_frame_mean`
  - `fused_hidden_frame_mean`
  - `fused_hidden_zero`
- 本轮新增 bypass：
  - `fused_hidden_from_periodic_hidden`
    - 直接把
      `periodic_hidden`
      送入
      `waveform_decoder`
  - `fused_hidden_from_noise_hidden`
    - 直接把
      `noise_hidden`
      送入
      `waveform_decoder`
  - `fused_hidden_from_branch_mean`
    - 直接把
      `0.5 * (periodic_hidden + noise_hidden)`
      送入
      `waveform_decoder`

## 四、baseline 重申
- baseline aggregate：
  - `fused_hidden_template_cosine_mean = 0.991105`
  - `waveform_frames_template_cosine_mean = 0.999462`
  - `decoded_frames_template_cosine_mean = 0.993590`
  - `decoded_frames_adjacent_cosine_mean = 0.998107`
  - `decoded_spectral_centroid_hz = 5857.393066`
  - `decoded_to_aligned_rms_ratio = 0.928302`
- 自动诊断仍为：
  - `collapse_not_localized_to_waveform_decoder`

## 五、关键结果

### 1. `fused_hidden_frame_mean` 仍几乎无影响
- `waveform_mean_abs_delta_vs_baseline = 0.003935`
- `decoded_frames_template_cosine_mean`
  反而略升：
  - `0.993590 -> 0.997058`
- 这继续支持：
  - baseline 下的
    `fused_hidden`
    本来就非常接近常模板

### 2. 直接 branch bypass 会大幅降低 decoded template 化

#### `fused_hidden_from_periodic_hidden`
- `waveform_mean_abs_delta_vs_baseline = 0.164701`
- `decoded_frames_template_cosine_mean`
  - `0.993590 -> 0.588111`
  - `delta = -0.405479`
- `decoded_frames_adjacent_cosine_mean`
  - `0.998107 -> 0.993629`
  - `delta = -0.004478`

#### `fused_hidden_from_noise_hidden`
- `waveform_mean_abs_delta_vs_baseline = 0.174454`
- `decoded_frames_template_cosine_mean`
  - `0.993590 -> 0.700063`
  - `delta = -0.293527`
- `decoded_frames_adjacent_cosine_mean`
  - `0.998107 -> 0.995398`
  - `delta = -0.002709`

#### `fused_hidden_from_branch_mean`
- `waveform_mean_abs_delta_vs_baseline = 0.174871`
- `decoded_frames_template_cosine_mean`
  - `0.993590 -> 0.675008`
  - `delta = -0.318582`
- `decoded_frames_adjacent_cosine_mean`
  - `0.998107 -> 0.994636`
  - `delta = -0.003471`

### 3. 但 bypass 输出会明显失真到高频、过响区域

#### `fused_hidden_from_periodic_hidden`
- `decoded_spectral_centroid_hz`
  - `5857.393066 -> 10701.847656`
  - `delta = +4844.454590`
- `decoded_to_aligned_rms_ratio`
  - `0.928302 -> 1.888971`
  - `delta = +0.960669`

#### `fused_hidden_from_noise_hidden`
- `decoded_spectral_centroid_hz`
  - `5857.393066 -> 10586.281250`
  - `delta = +4728.888184`
- `decoded_to_aligned_rms_ratio`
  - `0.928302 -> 1.921502`
  - `delta = +0.993200`

#### `fused_hidden_from_branch_mean`
- `decoded_spectral_centroid_hz`
  - `5857.393066 -> 10263.575195`
  - `delta = +4406.182129`
- `decoded_to_aligned_rms_ratio`
  - `0.928302 -> 1.960894`
  - `delta = +1.032592`

## 六、当前该如何解释
1. 这轮结果明确反对一个旧假设：
   - “decoder 自身已经坏到无论输入什么都只会输出固定 buzz”
2. 更符合当前数据的解释是：
   - decoder
     仍然有能力对 hidden 动态作出响应
   - 但 baseline 下
     它长期只见到
     坍缩后的
     `fused_hidden`
     狭窄工作区
3. 所以：
   - 当直接喂入
     `periodic / noise / branch_mean`
     这类更动态 hidden
   - 输出确实脱离了原来的极强模板化
   - 但并没有自然转成 speech，
     而是掉进了
     更亮、更响、更尖的非稳态区域
4. 换句话说：
   - 当前问题不是
     “只要把 fusion 修开，decoder 就会自然说话”
   - 更像是：
     - 先被
       `fusion`
       压成坏 manifold
     - decoder 再围绕这个坏 manifold
       学到一个稳定的 buzz 解

## 七、当前阶段判断更新
1. `fusion / fused_hidden`
   仍然是第一坍缩点，
   这个判断没有变
2. 但 decoder
   并非完全不重要：
   - 它不是主坍缩起点
   - 却已经对
     collapsed fused manifold
     产生了明显适配
3. 因而后续不应做两种极端误判：
   - 误判 A：
     - 只改 decoder
       就能救回来
   - 误判 B：
     - 只要强行把
       fused_hidden
       变得更动态，
       现有 decoder
       就会自然转正

## 八、当前最值钱的下一步
### 推荐的最小训练实验
- 在当前
  `contractv2_normfix`
  recipe
  上做一轮新的
  **fusion-side minimal smoke**
- 目标不是再加
  decode-side
  quant-only loss，
  而是：
  - 让
    `fused_hidden`
    更接近 branch-side
    的动态结构
  - 同时保留
    waveform / stft / rms_guard
    作为输出稳定锚点

### 更具体的优先级
1. 首先新增：
   - `fused_hidden`
     向
     `0.5 * (periodic_hidden + noise_hidden)`
     靠拢的
     activity-masked
     表征约束
2. 保留：
   - 当前
     `waveform / stft / rms_guard`
     基础项
3. 先不要继续加：
   - `active_template`
   - `frame_adjacent_cosine`
   - `frame_delta`
   这类 decode-side
   quant-only
   约束

### 为什么这是下一步
- 因为当前 probe
  已经回答清楚：
  - decoder
    不是完全没能力
  - 真正缺的是：
    如何把更有用的 hidden
    以“不过载、不爆高频”的方式
    送到 decoder

## 一句话结论
- 本轮 bypass probe
  已正式说明：
  - 现有 decoder
    在拿到更动态的 branch hidden 时，
    确实会脱离原来的极强模板化；
  - 但它会同时掉进
    高频、过响、非语音区域；
  因此下一步最该投的不是
  decoder-only
  或 decode-side 小 loss，
  而是带输出稳定锚点的
  `fusion / fused_hidden`
  侧最小训练实验。
