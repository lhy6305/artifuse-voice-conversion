# 389. Stage3 student packet 最小 Stage5 adapter 与真实 decoded smoke 失败报告

## 结论
- `Stage3 student_control_packet -> Stage5 no-res` 的最小 adapter 已真实接通，不再停留在 proxy 音频。
- 当前 best packet 线路 `vuvbalancedgate48` 已成功导出真实 `decoded.wav`，但第一条 smoke 样本就被机器门禁直接判成 `auto_reject_obvious_buzz`。
- 因此这条线路当前的正式状态应是：
  - `adapter ready`
  - `decoded ready`
  - `current packet family still fail-fast negative`
- 基于 fail-fast 原则，不继续把这版 packet 扩成 3 条听审包，也不继续把“已经能出 decoded.wav”误写成“已经接近成功”。

## 一、本轮新增实现

### 1. 新增 `student_control_packet -> Stage5 scaffold/package` 最小桥接
- 新模块：
  - `src/v5vc/streaming_student/stage5_handoff.py`
- 新能力：
  - `build_streaming_student_vocoder_input_scaffold(...)`
  - `build_streaming_student_stage5_dataset_packages(...)`
- 新 scaffold 版本：
  - `streaming_student_vocoder_input_scaffold_v1`
- 设计目标：
  - 不是重写新的 Stage5 decoder
  - 而是把 Stage3 packet 映射成当前 Stage5 best checkpoint 可直接消费的显式控制 `36/36` 语义布局

### 2. 放开现有 Stage5 audio export 的 dataset index 绑定
- 修改：
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/cli.py`
- 新行为：
  - `export-offline-mvp-nores-vocoder-audio` 现在支持 `--dataset-index`
  - 不再被 checkpoint payload 内写死的旧 dataset index 绑住

### 3. Stage5 侧兼容新 scaffold 版本
- 修改：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/offline_vocoder_scaffold.py`
- 结果：
  - `streaming_student_vocoder_input_scaffold_v1` 已被视为显式控制 scaffold
  - 可直接进入现有 no-res package / decode 工具链

## 二、最小 smoke 结果

### 1. scaffold/package smoke 已通过
- synthetic dataset index：
  - `reports/runtime/streaming_student_stage5_dataset_vuvbalancedgate48_smoke_round1_1/streaming_student_stage5_dataset_index.json`
- 关键事实：
  - `source_scaffold_version = streaming_student_vocoder_input_scaffold_v1`
  - `periodic_input_dim = 36`
  - `noise_input_dim = 36`
- 对应 scaffold 摘要：
  - `reports/runtime/streaming_student_stage5_dataset_vuvbalancedgate48_smoke_round1_1/packages/validation/target__chapter3_3_firefly_162/scaffold/streaming_student_vocoder_input_scaffold.json`

### 2. 真实 decoded.wav 已导出
- 导出目录：
  - `reports/runtime/streaming_student_stage5_audio_export_vuvbalancedgate48_smoke_round1_1`
- 关键文件：
  - `target__chapter3_3_firefly_162__decoded.wav`
  - `target__chapter3_3_firefly_162__aligned_target.wav`
  - `nores_vocoder_audio_export.json`
- 使用 checkpoint：
  - `best_validation step72`
  - 来源：
    `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json`

## 三、失败判定

### 1. 第一条真实 decoded smoke 就被自动否定
- 记录：
  - `target::chapter3_3_firefly_162`
- 摘要：
  - `buzz_reject_summary.auto_reject_count = 1`
  - `all_records_auto_reject = true`
- 具体 assessment：
  - `status = auto_reject_obvious_buzz`
  - `decoded_frame_template_cosine_mean = 0.987903`
  - `decoded_frame_adjacent_cosine_mean = 0.991873`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.94424`
  - `spectral_centroid_gap_hz = 5228.478641`
  - `spectral_high_band_energy_ratio_gap = 0.365601`

### 2. 这次 negative 结论比过去更硬
- 过去的问题是：
  - 很多 Stage3 线路只到 proxy 音频
  - 无法快速证明“如果真推到 Stage5 会不会仍是 buzz”
- 这次已经明确：
  - 不是 adapter 没接通
  - 不是没有真实 decoded.wav
  - 而是当前 best Stage3 packet family 推到现有 Stage5 checkpoint 后，仍然直接落入 obvious buzz negative gate

## 四、当前正式口径
- 以后对 `student_control_packet` 这条线，不能再说：
  - “还没真正验证到 Stage5”
- 更准确的说法是：
  - `minimal Stage5 adapter` 已完成
  - `real decoded.wav` 已完成
  - `vuvbalancedgate48` 这版 current best packet 仍然 fail-fast negative

## 五、下一步边界
- 不继续：
  - 把当前这版 packet 扩成 3 条人工听审包
  - 因为第一条 best-sample decoded 已被机器明确判成 obvious buzz
- 不回退到：
  - “只有 proxy、没有 decoded，所以还不能判断”
- 如果后续继续：
  - 应把这个最小 adapter 当成固定 fail-fast 工具
  - 新的 Stage3 named-control candidate 一旦看起来有可能，就优先过这条真实 decoded smoke
  - 当前研发重心仍应留在 `F0 / vuv / named-control generation-side completion`
    而不是继续修当前这版 adapter 本身
