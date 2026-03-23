# 2026-03-23 Stage5 no-res speech-emergence temporal-structure 补充报告

## 结论
- 当前 `Stage5 no-res`
  的 speech-emergence
  问题，
  现在已经不只是：
  - “控制 family
    哪个更重要”
- 本轮补充后的更强结论是：
  - baseline route
    本身就表现出
    极强的
    frame-template collapse
  - 同时它又对
    aligned target
    的帧级能量包络
    保持较高相关
- 更贴近人话的解释是：
  - 当前 route
    不是在持续生成
    语音结构丰富的短时帧
  - 而更像是：
    - 先学出一个几乎固定的 buzz 模板
    - 再让 gate / energy
      去跟着目标包络起伏
- 这也解释了为什么：
  - 粗粒度频谱统计
    看起来不一定极端坏
  - 但人耳仍稳定听成
    buzzing / 非语音

## 背景
- `docs/256_stage5_speech_emergence_root_cause_probe_report.md`
  已完成首轮 family-level
  root-cause probe：
  - `conditioning`
    最强
  - `z_art`
    次强
  - `event_probs`
    与
    noise-side proxies
    次级但真实
- 但当时仍缺一层关键解释：
  - 为什么 baseline
    的 coarse spectral summary
    不算特别坏，
    人耳却仍听成
    非语音 buzzing

## 本轮代码补充
- 文件：
  - `src/v5vc/stage5_speech_emergence_probe.py`
- 新增的不是新 family，
  而是 temporal-structure
  指标：
  - `waveform_frames_adjacent_cosine_mean`
  - `waveform_frames_template_cosine_mean`
  - `decoded_frame_adjacent_cosine_mean`
  - `decoded_frame_template_cosine_mean`
  - `aligned_frame_adjacent_cosine_mean`
  - `aligned_frame_template_cosine_mean`
  - `decoded_frame_adjacent_cosine_gap_vs_aligned`
  - `decoded_frame_template_cosine_gap_vs_aligned`
  - `predicted_activity_to_aligned_frame_rms_corr`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`

## 当前关键结果

### 1. baseline 的 `waveform_frames`
  几乎是固定模板
- baseline aggregate:
  - `waveform_frames_adjacent_cosine_mean = 0.999994`
  - `waveform_frames_template_cosine_mean = 0.999649`
  - `waveform_frames_rms_cv = 0.001093`
- 这说明：
  - 模型输出到
    `waveform_frames`
    这一层时，
    帧形状几乎不变
  - 连帧内 RMS
    变化都非常小

### 2. OLA 后的 decoded
  仍保持极强模板一致性
- baseline aggregate:
  - `decoded_frame_adjacent_cosine_mean = 0.997967`
  - `decoded_frame_template_cosine_mean = 0.994838`
  - `decoded_frame_rms_cv = 0.694692`
- 这说明：
  - 重建后的 decoded
    在短时帧层面，
    仍然极度相似
  - 变化主要体现在：
    - 帧级振幅
    - 而不是
      帧内结构多样性

### 3. aligned target
  与 decoded
  在短时结构上完全不是一回事
- aligned aggregate:
  - `aligned_frame_adjacent_cosine_mean = 0.121139`
  - `aligned_frame_template_cosine_mean = 0.022486`
  - `aligned_frame_rms_cv = 1.037555`
- 对比 gap:
  - `decoded_frame_adjacent_cosine_gap_vs_aligned = 0.876828`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.972352`
- 这说明：
  - 真实语音的短时帧
    结构变化很大
  - 当前 decoded
    却几乎始终贴着
    同一个模板

### 4. 但它确实在跟目标包络走
- baseline aggregate:
  - `predicted_activity_to_aligned_frame_rms_corr = 0.816000`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.825703`
- 这说明：
  - 当前 route
    并不是完全乱响
  - 它确实在跟着
    目标的粗粒度能量轮廓
    起伏
- 所以更准确的解释不是：
  - “什么都没学到”
- 而是：
  - 学到的是
    envelope-following
    假解，
    不是 speech emergence

## family probe 在这一层上的新解释

### 1. `conditioning_zero`
  与 `z_art_zero`
  会显著改输出，
  但不会打破模板塌缩
- `conditioning_zero`
  aggregate:
  - `decoded_frame_template_cosine_mean = 0.964012`
- `z_art_zero`
  aggregate:
  - `decoded_frame_template_cosine_mean = 0.977341`
- 它们都比 baseline
  低，
  说明确实会改短时结构
- 但仍然远高于
  aligned target
  的
  `0.022486`
- 这说明：
  - 这些 family
    会改变
    buzz 的样子
  - 但没有把 route
    从“模板 buzz”
    推进成
    “真实语音结构”

### 2. `event_probs_zero`
  与 `noise_proxies_zero`
  也没有扭转结构塌缩
- `event_probs_zero`
  aggregate:
  - `decoded_frame_template_cosine_mean = 0.988150`
- `noise_proxies_zero`
  aggregate:
  - `decoded_frame_template_cosine_mean = 0.985433`
- 同时：
  - `predicted_activity_to_aligned_frame_rms_corr`
    仍高于
    `0.87`
  - `decoded_frame_rms_to_aligned_frame_rms_corr`
    也仍高于
    `0.87`
- 这说明：
  - 噪声侧控制更像在调：
    - 包络强弱
    - buzz 的亮度/粗糙度
  - 而不是解除
    “固定模板 + 包络跟随”
    这个主问题

## 当前判断
- 当前最接近事实的根因表述应改成：
  - `Stage5 no-res`
    当前并不是单纯没用控制量
  - 而是：
    - waveform head
      已塌到近固定模板
    - controls
      主要在驱动
      包络和粗强弱
    - 没有形成足够的
      短时语音结构多样性
- 所以当前更像是：
  - `template-buzz + envelope-following`
    假解
- 不是：
  - “单个 family
    配错了”

## 下一步建议
1. 当前不优先继续扩：
   - family-level
     `zero/frame_mean`
     小变体
2. 下一题更值得做的是：
   - 沿训练步长比较
     `step24 / step48 / step60 / step72`
     的 frame-template collapse
     是否始终存在
   - 直接验证这是不是
     整条 no-res route
     的训练级假解
3. 如果后续继续改代码或实验，
   优先怀疑：
   - waveform reconstruction target / loss
   - waveform head
     的表达与约束
   - 而不是先怀疑
     decode-side
     小参数

## 一句话结论
- 当前最强的实验线解释已经从
  “哪个 control family
  更重要”
  推进到：
  - `Stage5 no-res`
    baseline
    几乎是在输出固定短时模板，
    再让包络去跟着目标能量起伏；
    这正是当前
    buzzing / 非语音
    听感最贴切的工程解释。
