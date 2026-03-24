# 2026-03-24 Stage5 `contractv2_normfix` waveform decoder 结构探针报告

## 结论
- 已完成：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_contractv2_normfix_round1_1/`
- 当前关键判断是：
  - **主要坍缩不在 `waveform_decoder` 单点内部**
  - **更大的坍缩已经发生在 `fusion -> fused_hidden`**
- 因而：
  - 下一步不该优先做
    `waveform_decoder`
    孤立结构改造
  - 更应转向：
    - `fusion / fused_hidden`
      级别的 objective
      或结构约束
    - 验证如何阻止
      `branch hidden`
      在融合后被压成近固定模板

## 一、探针目的
- 用户已确认：
  - 当前 fixed-record
    听感仍是
    **彻底的 buzz**
    且
    **没有任何人声成分**
- 所以本轮需要回答的不是：
  - 还能不能再训久一点
- 而是：
  - 当前 route
    的短时多样性
    到底是在：
    - `fusion` 前
    - 还是 `waveform_decoder`
      内部
    被压塌

## 二、运行配置
- CLI：
  - `analyze-stage5-nores-waveform-decoder-structure`
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

## 三、probe 设计
- baseline：
  - 原始 checkpoint
    路径
- `periodic_hidden_frame_mean`：
  - 把 periodic encoder
    的帧间动态
    压成包内均值
- `noise_hidden_frame_mean`：
  - 把 noise encoder
    的帧间动态
    压成包内均值
- `fused_hidden_frame_mean`：
  - 把 `fused_hidden`
    压成包内均值
    再送入
    `waveform_decoder`
- `fused_hidden_zero`：
  - 直接把
    `fused_hidden`
    清零

## 四、关键结果

### 1. baseline 各阶段模板化程度
- `periodic_hidden_template_cosine_mean = 0.714140`
- `noise_hidden_template_cosine_mean = 0.811654`
- `fused_hidden_template_cosine_mean = 0.991105`
- `waveform_frames_template_cosine_mean = 0.999462`
- `decoded_frames_template_cosine_mean = 0.993590`

### 2. baseline 各阶段帧间变化幅度
- `periodic_hidden_frame_delta_abs_mean = 0.024629`
- `noise_hidden_frame_delta_abs_mean = 0.018997`
- `fused_hidden_frame_delta_abs_mean = 0.007185`
- `waveform_frames_frame_delta_abs_mean = 0.001350`
- `decoded_frames_frame_delta_abs_mean = 0.001911`

### 3. baseline 的直接结构判断
- `fused_to_waveform_template_cosine_gap = 0.008357`
- `fused_to_waveform_adjacent_cosine_gap = 0.000134`
- probe 自动诊断：
  - `collapse_not_localized_to_waveform_decoder`

这三组数合起来说明：
- `periodic_hidden / noise_hidden`
  还没有完全塌成模板
- 但一到
  `fusion`
  输出的
  `fused_hidden`
  就已经高度模板化
- `waveform_decoder`
  确实还会继续把结果
  往固定模板方向推一点
  但增量很小
- 因此主坍缩点
  更接近：
  - `fusion / fused_hidden`
  而不是：
  - `waveform_decoder`
    单点

## 五、干预结果如何解释

### `fused_hidden_frame_mean`
- `waveform_mean_abs_delta_vs_baseline = 0.003935`
- 解释：
  - 当 `fused_hidden`
    被压成完全 frame mean
    时，
    输出几乎不变
  - 这不是说
    decoder
    完全不吃
    `fused_hidden`
  - 而是说：
    baseline 下的
    `fused_hidden`
    本来就已经非常接近
    常模板

### `fused_hidden_zero`
- `waveform_mean_abs_delta_vs_baseline = 0.153620`
- 解释：
  - `waveform_decoder`
    仍依赖
    `fused_hidden`
    的总体值域
  - 所以它不是
    完全独立于输入的
    常数生成器
  - 但它当前接收到的
    输入状态空间
    已经非常窄

### `periodic_hidden_frame_mean`
- `waveform_mean_abs_delta_vs_baseline = 0.027576`

### `noise_hidden_frame_mean`
- `waveform_mean_abs_delta_vs_baseline = 0.025802`

这说明：
- branch 侧动态
  仍然有作用
- 但这些作用经过
  `fusion`
  后，
  大部分短时差异
  已被压缩掉

## 六、当前最合理的阶段结论
1. 这轮结果不支持：
   - “先改 `waveform_decoder`
     结构就能把 buzz
     拉回 speech”
2. 这轮结果更支持：
   - 当前 route
     在进入
     `waveform_decoder`
     之前，
     就已经落入
     近固定模板的狭窄区域
3. 所以真正该优先处理的不是：
   - decoder-only
     tweak
4. 而是：
   - 如何让
     `fused_hidden`
     保留可用的
     帧间差异

## 七、建议下一步
1. objective 主线继续推进，
   但重心上移到：
   - `fused_hidden`
     的 anti-template
   - `fused_hidden`
     的 frame-delta
   - 或 branch-to-fusion
     的 diversity-preservation
     约束
2. 不建议把下一轮主资源先投到：
   - `waveform_decoder`
     架构替换
   - 或只在 decoder 末端
     做局部修补
3. 若需要做最小验证，
   下一轮更适合：
   - 在当前 recipe 上
     增加
     `fused_hidden`
     级别的结构损失
   - 再看 fixed-record
     是否仍是
     buzz-only

## 一句话结论
- 当前 `contractv2_normfix`
  的 Stage5 no-res
  路线里，
  `waveform_decoder`
  不是唯一也不是主要坍缩点；
  主问题更早发生在
  `fusion -> fused_hidden`，
  因此下一步应优先做
  `fusion / objective`
  级别的反坍缩设计。
