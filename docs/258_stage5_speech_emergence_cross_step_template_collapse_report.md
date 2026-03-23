# 2026-03-23 Stage5 no-res cross-step template-collapse 对照报告

## 结论
- 当前 `Stage5 no-res`
  的主问题，
  现在可以进一步收紧为：
  - `template collapse`
    不是
    `step72`
    才出现的后期副作用
  - 而是从
    `step24`
    开始就已经贯穿：
    `step24 / step48 / step60 / step72`
    整条当前训练路线
- 当前训练的真实演化更像是：
  - 一直停留在
    同一类
    `template-buzz + envelope-following`
    假解里
  - 只是在假解内部，
    高频比例逐步下降，
    包络跟随逐步更稳
- 所以当前最重要的事实不是：
  - `step72`
    选错了
- 而是：
  - 当前这整条 no-res
    waveform route
    还没有发生过
    speech emergence

## 背景
- `docs/257_stage5_speech_emergence_temporal_structure_report.md`
  已确认：
  - `step72`
    baseline
    几乎是在输出固定短时模板，
    再跟着目标包络起伏
- 但当时仍有一个可能的误判风险：
  - 会不会这只是后期 checkpoint
    的局部塌缩，
    更早 checkpoint
    其实出现过更健康的结构

## 本轮对照范围
- 当前对同一批
  `validation12`
  record ids，
  用完全相同的 probe
  口径，
  分别跑了：
  - `step24`
  - `step48`
  - `step60`
  - `step72`
- 统一口径：
  - predicted gate on
  - smoothing `3`
  - `post_ola_envelope`

## 关键结果

### 1. `waveform_frames`
  级模板塌缩从头到尾都存在
- `waveform_frames_adjacent_cosine_mean`
  - `step24 = 0.999986`
  - `step48 = 0.999993`
  - `step60 = 0.999994`
  - `step72 = 0.999994`
- `waveform_frames_template_cosine_mean`
  - `step24 = 0.999101`
  - `step48 = 0.999604`
  - `step60 = 0.999606`
  - `step72 = 0.999649`
- 这说明：
  - waveform head
    从早期开始
    就几乎在输出固定模板
  - 后续训练
    没有把它从模板塌缩里拉出来

### 2. reconstructed decoded
  的短时模板塌缩也一直存在
- `decoded_frame_adjacent_cosine_mean`
  - `step24 = 0.998545`
  - `step48 = 0.998496`
  - `step60 = 0.998220`
  - `step72 = 0.997967`
- `decoded_frame_template_cosine_mean`
  - `step24 = 0.996672`
  - `step48 = 0.996885`
  - `step60 = 0.995927`
  - `step72 = 0.994838`
- 对照：
  - `aligned_frame_template_cosine_mean = 0.022486`
- 这说明：
  - 即便到了
    `step72`
    有轻微下降，
    decoded
    仍然远远停留在
    “固定模板”
    区间
  - 没有任何一步
    接近真实语音的
    短时结构多样性

### 3. 高频比例在下降，
  但这只是“假解内部改善”
- `decoded_spectral_high_band_energy_ratio`
  - `step24 = 0.455890`
  - `step48 = 0.162925`
  - `step60 = 0.118253`
  - `step72 = 0.064479`
- 这说明：
  - 高频塌穿确实在逐步收敛
- 但结合上面的模板塌缩结果，
  更准确的解释不是：
  - 训练从噪音逐步变成语音
- 而是：
  - 训练在同一类
    buzz 模板
    里逐步变得没那么亮、
    没那么刺

### 4. 包络跟随从头到尾都存在
- `predicted_activity_to_aligned_frame_rms_corr`
  - `step24 = 0.827138`
  - `step48 = 0.814499`
  - `step60 = 0.807014`
  - `step72 = 0.816000`
- `decoded_frame_rms_to_aligned_frame_rms_corr`
  - `step24 = 0.831330`
  - `step48 = 0.819282`
  - `step60 = 0.815368`
  - `step72 = 0.825703`
- 这说明：
  - 从早期开始，
    模型就已经在学
    target-like
    的粗能量轮廓
  - 但这种学习
    并没有自然长成
    语音结构

## 当前判断
- 当前整条训练路线
  最贴切的演化描述应写成：
  1. 很早就收敛到
     固定短时模板
  2. 后续训练主要在调：
     - 包络跟随
     - RMS
     - 高频比例
  3. 但从未跨过
     speech emergence
     这条线
- 所以当前不应再把问题理解成：
  - `best_validation`
    选错
  - 或
    `step72`
    后期退化
- 更准确的理解应是：
  - 当前 waveform route
    的训练目标 / 结构
    允许并稳定维持
    这种假解

## 下一步建议
1. 当前不再优先做：
   - 更晚 checkpoint
     排名
   - decode-side
     小 tweak
2. 下一题更值得直接转向：
   - waveform head
     / reconstruction loss
     的假解诊断
   - 为什么固定模板
     能持续满足当前训练目标
3. 若后续继续做 probe，
   优先方向应是：
   - 对齐训练步长的
     waveform-head
     输出多样性
   - 或直接比较
     target / decoded
     的短时帧结构约束缺口

## 一句话结论
- 当前 `Stage5 no-res`
  的问题已经可以从
  “当前 route
  为什么听成 buzzing”
  进一步升级成：
  - 这整条当前训练路线
    从早期开始就稳定停在
    `template-buzz + envelope-following`
    假解里，
    只是后续在假解内部变得没那么刺耳。
