# `target_special_eval` 非文本指标补强评估

## 目的
- 评估当前 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
- 若需要，则确认：
  - 哪些指标最有信息量
  - 它们是否真的补上了现有 `loss / text_aux` 口径的盲区

先说人话：
- 这一步是在确认，我们现在看 `special slice`，是不是只看到了“文字上更难”，却还没看清“声音上到底哪里不一样”。

## 当前旧口径的问题
在本次补强前，模型级 `special_eval` 主要输出：
- `loss_total / loss_acoustic / loss_event / loss_text_aux`
- `z_art_abs_mean`
- `event_prob_mean`
- `acoustic_abs_mean`
- `text_aux_abs_mean`

这些统计有两个明显问题：

### 1. `text_aux` 太强，容易盖住更接近运行时的差异
- 当前 `target_special_eval` 本身就是 punctuation-only slice。
- 所以 `loss_text_aux` 高，本来就是预期现象。
- 如果只盯这项，很容易把 special slice 简化成：
  - “文本辅助更难”
- 但这并不能回答运行时真正更关心的问题，例如：
  - 事件激活是更弱还是更尖？
  - 能量是更低还是更乱？
  - `z_art` 的时序变化是否更小？

### 2. `event_prob_mean` 过粗
- 当前 `event_prob_mean` 是所有 event 维度一起平均。
- 它会把：
  - presence
  - delta
  - rise
  - fall
  - energy
  混成一个数。
- 这样即使 special slice 在某个事件子维度上有明显偏移，也可能被总均值冲淡。

## 本轮已补入的非文本指标
本轮已把以下统计接入 `src/v5vc/special_eval.py`，并已对 `EXP-20260314-020-offline-mvp-c1-4-100step-calibration` 重跑：

- `z_art_delta_abs_mean`
- `event_presence_prob_mean`
- `event_delta_prob_mean`
- `event_rise_prob_mean`
- `event_fall_prob_mean`
- `event_energy_prob_mean`
- `event_presence_peak_ratio`
- `acoustic_energy_mean`
- `acoustic_delta_abs_mean`

这些指标的设计原则是：
- 不依赖文本输入
- 更贴近运行态控制链
- 能直接描述：
  - 稀疏度
  - 峰值集中度
  - 动态幅度
  - 能量走势

## `EXP-020` 上的直接结果
实验：
- `EXP-20260314-020-offline-mvp-c1-4-100step-calibration`

### validation vs special 的新非文本差异
- `delta_z_art_delta_abs_mean = -0.001089`
- `delta_event_presence_prob_mean = -0.018956`
- `delta_event_delta_prob_mean = 0.005105`
- `delta_event_rise_prob_mean = -0.003298`
- `delta_event_fall_prob_mean = -0.012558`
- `delta_event_energy_prob_mean = -0.017549`
- `delta_event_presence_peak_ratio = 0.110320`
- `delta_acoustic_energy_mean = -0.564369`
- `delta_acoustic_delta_abs_mean = -0.001511`

## 这些新指标带来的新信息
### 1. special slice 不只是“文本更难”
- `loss_text_aux` 仍然更高，这点没有变。
- 但新指标还显示：
  - `z_art` 的时序变化更小
  - `event presence / fall / energy` 平均值更低
  - `acoustic energy` 更低
  - `acoustic delta` 也更小

这说明：
- special slice 确实更像：
  - 低能量
  - 低持续发声
  - 更平、更稀疏的非完整发声片段
- 这比“只是文字上更难”更贴近运行时理解。

### 2. special slice 不是“更乱”，而是“更稀疏但更尖”
- `event_presence_prob_mean` 更低
- 但 `event_presence_peak_ratio` 反而更高，提升约 `0.110320`

这说明：
- special slice 不是简单的高噪声乱跳。
- 更像是：
  - 平时整体激活更弱
  - 但一旦出现事件峰值，会更集中地顶上去

先说人话：
- 这批样本不是一直都很响、很乱。
- 更像是大部分时间都轻，但会突然冒一下尖。

### 3. `event_prob_mean` 单独看不够
- 总的 `delta_event_prob_mean = -0.009033` 很小。
- 但拆开以后能看到：
  - `presence` 下降
  - `fall` 下降
  - `energy` 下降
  - `delta` 反而微升

这说明：
- 如果只保留原来的总均值，很容易错过真正更有解释力的细节。

## 当前结论
- 结论是明确的：
  - `target_special_eval` 需要保留非文本指标补强；
  - 而且这次新增的指标已经证明自己有信息量。
- 当前最有价值的新增指标是：
  - `event_presence_prob_mean`
  - `event_presence_peak_ratio`
  - `event_fall_prob_mean`
  - `event_energy_prob_mean`
  - `z_art_delta_abs_mean`
  - `acoustic_energy_mean`
  - `acoustic_delta_abs_mean`

## 当前建议
- 后续默认保留这批非文本统计，不再只汇报：
  - `loss_total`
  - `loss_text_aux`
  - `event_prob_mean`
- 若后续继续做 checkpoint 级 special slice 解释，优先扩展：
  - `special_eval_series`
  - 让它也能摘要这批非文本指标的早中晚变化

## 2026-03-14 series 口径固定更新
- 已对以下实验重跑 `special_eval_series`：
  - `EXP-20260314-020-offline-mvp-c1-4-100step-calibration`
  - `EXP-20260314-011-offline-mvp-large-scale-500`
- 当前 series 汇总中已补入：
  - `delta_event_presence_prob_mean`
  - `delta_event_fall_prob_mean`
  - `delta_event_energy_prob_mean`
  - `delta_event_presence_peak_ratio`
  - `delta_z_art_delta_abs_mean`
  - `delta_acoustic_energy_mean`
  - `delta_acoustic_delta_abs_mean`
- 这意味着：
  - 旧实验的早中晚 checkpoint 观察口径已被钉死；
  - 后续切到 `round1.1` 时，旧数据线和新数据线的解释边界会更清楚。

先说人话：
- 这批新指标不是锦上添花。
- 它们第一次把“这批 challenge 样本在声音动态上到底哪里怪”说得更像人能理解的话了。
