# 2026-03-27 Stage5 output-head 子阶段 structure probe 报告

## 结论
- 本轮没有继续做新的训练 sweep，
  而是先把当前已失败的
  `bpae01`
  checkpoint
  在 output-head 内部再拆了一层：
  - `baseline_full_output`
  - `waveform_decoder_base_logits_only`
  - `waveform_residual_shape_only`
- 这轮 probe
  已同时在：
  - teacher-first fixed pure-buzz triplet
  - Stage5 native validation3
  两侧跑通，
  并且为每个 variant
  都导出了：
  - `wav`
  - 线性频谱图 `png`
- 当前结论非常硬：
  1. `waveform_decoder_base_logits_only`
     与 baseline
     几乎完全一致
  2. `waveform_residual_shape_only`
     则不是“隐藏的人声结构”，
     而是更亮、更高频、
     更模板化的纯 buzz
  3. 这个方向在 user-line
     与 native validation3
     两边都一致
- 因而当前主线应再次收紧：
  - `residual_shape`
    不是当前缺失语音结构的主要承载者
  - 它更像是在 baseline buzz 之上，
    叠了一层很小但偏高频的
    comb-like / bright-buzz
    修饰
  - 真正缺失的人声结构，
    已经在
    `waveform_decoder_base_logits`
    之前就没有形成，
    或者至少没有在 base logits
    里生成
- 因而下一步不该再优先围绕：
  - residual-shape 同层小调
  - residual-shape penalty 小 sweep
  - residual-shape 是否再换 mode
- 下一步应直接转向：
  - `waveform_decoder(decoder_hidden)` 自身的结构表达
  - 也就是
    base logits
    为什么仍然是稳定 tonal/pure buzz

## 一、本轮新增的 probe 能力
- 现有 structure probe
  已扩成支持 output-head 子变体：
  - `waveform_decoder_base_logits_only`
  - `waveform_residual_shape_only`
- 同时新增：
  - 每个 variant 自动导出 `wav`
  - 每个 variant 自动导出线性频谱图 `png`
- 涉及文件：
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
  - `src/v5vc/stage5_waveform_handoff_probe.py`
  - `src/v5vc/teacher_first_vc_demo.py`

## 二、teacher-first user-line 结果
- 输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_wdsp_outputhead_bpae01_round1_1/`
- baseline：
  - `decoded_template = 0.887733`
  - `centroid = 4163.743652`
  - `high_band = 0.197849`
- `waveform_decoder_base_logits_only`：
  - `decoded_template = 0.887373`
  - `centroid = 4256.501465`
  - `high_band = 0.201769`
  - `waveform_delta_vs_baseline = 0.005684`
- `waveform_residual_shape_only`：
  - `decoded_template = 0.999805`
  - `centroid = 12338.094727`
  - `high_band = 0.833547`
  - `waveform_delta_vs_baseline = 0.080246`
- 读法：
  - baseline
    几乎就是
    `base_logits_only`
  - residual-shape
    单独拿出来听，
    不是语音结构支，
    而是更亮、更规则、
    更直线型的纯 buzz

## 三、native validation3 结果
- 输出目录：
  - `reports/runtime/stage5_waveform_decoder_structure_probe_headstruct_bhb01_bpae01_validation3_round1_1/`
- baseline：
  - `decoded_template = 0.824535`
  - `centroid = 3407.504639`
  - `high_band = 0.151263`
- `waveform_decoder_base_logits_only`：
  - `decoded_template = 0.823982`
  - `centroid = 3470.388672`
  - `high_band = 0.154959`
  - `waveform_delta_vs_baseline = 0.006468`
- `waveform_residual_shape_only`：
  - `decoded_template = 0.999815`
  - `centroid = 11351.418945`
  - `high_band = 0.815930`
  - `waveform_delta_vs_baseline = 0.094926`
- 读法：
  - native validation
    与 user-line
    方向完全一致
  - 所以这不是：
    - user-line 特有听感幻觉
    - 或某一组三条样本的偶然现象

## 四、当前应如何重写 output-head 问题
- 到 `445`
  为止，
  我们已经知道：
  - `bhb01`
    与
    `bpae01`
    主观上都仍是 pure buzz
- 到这轮 `446`
  为止，
  还应进一步明确：
  - 问题不能再写成：
    - residual-shape 没有调好
    - residual-shape 也许还藏着语音结构
  - 更准确的表述应是：
    - baseline 可听输出几乎完全由
      `waveform_decoder_base_logits`
      决定
    - `residual_shape`
      当前只是在其上叠加很小的
      高频模板化 buzz 成分
- 这就解释了为什么：
  - 压亮度
  - 压
    `aper * noise_E`
    jump
  - 主观上仍然只是
    buzz family
    内部变体

## 五、下一步主线
- 当前不再继续做：
  - residual-shape mode 小扫
  - residual-shape penalty 小扫
  - residual-shape 同层听审
- 下一步应直接转向：
  - base logits
    的结构形成问题
- 更具体地说，
  下一条 probe / 训练主线应围绕：
  - `waveform_decoder(decoder_hidden)`
    为什么只生成稳定的
    tonal / pure buzz
  - 而不是去追
    residual-shape
    为什么没把它修好

## 六、一句话结论
- output-head 子阶段 probe 已明确证明：当前可听输出几乎就是 `waveform_decoder_base_logits` 本体，`residual_shape` 单独拿出来只会变成更亮、更直线型的纯 buzz；因此下一步必须从 residual-shape 小修转向 base-logits / waveform-decoder 自身的语音结构形成问题。
