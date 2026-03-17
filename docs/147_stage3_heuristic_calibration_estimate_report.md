# 147. Stage3 heuristic calibration estimate 报告

## 背景
- `docs/146_stage3_calibration_asset_and_eval_bridge_report.md`
  已经固定了:
  - calibration subset
  - calibration asset template
  - Stage3 eval bridge
- 但那一轮的 calibration asset 仍然是:
  - placeholder zero vectors
  - `alpha = 1.0`

## 本轮目标
- 把 Stage3 conditioning 从“全零占位”
  推进到:
  - 一个可复用的、非 placeholder 的 bootstrap estimate
- 目标不是一步到位做成最终 calibration 算法，
  而是先把真实数据驱动值接进工程链路。

## 本轮实际完成

### 1. 新增 heuristic estimate 命令
- 新增:
  - `.\python.exe manage.py estimate-streaming-student-calibration`

### 2. 新增 estimated asset 产物
- 生成:
  - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json`

### 3. 新增 estimation summary
- 生成:
  - `reports/data/streaming_student_calibration_estimate/streaming_student_calibration_estimate_summary.json`
  - `reports/data/streaming_student_calibration_estimate/streaming_student_calibration_estimate_summary.md`

### 4. 用 estimated asset 重跑 eval bridge
- 当前:
  - `reports/eval/streaming_student_eval_bridge/streaming_student_eval_bridge.md`
  已确认读取:
  - `streaming_student_calibration_asset_estimated.json`
  而不再是 placeholder template

## heuristic estimator 当前做了什么

### 输入
- `target_calibration_records.jsonl`
  中选出的 `11` 条 calibration 记录
- 总时长:
  - `135.964922 sec`

### 核心做法
- 直接读取波形
- 做短窗 frame 分析
- 选取较高能量帧
- 统计:
  - RMS
  - absolute mean
  - zero-crossing
  - spectral centroid
  - low / lowmid / mid / high 频带功率占比
  - low/high ratio
- 再把这些 aggregate feature
  映射成:
  - `s_spk_target`
  - `s_geom_target`
  - `alpha`

### 当前 estimator 名称
- `waveform_feature_bootstrap_v1`

## 当前估计结果

### 1. `s_spk_target`
- `dim = 16`
- `status = heuristic_estimated`
- 当前是一个非零向量，
  用于替代原先的 zero vector placeholder

### 2. `s_geom_target`
- `dim = 8`
- `status = heuristic_estimated`
- 当前同样是一个非零向量，
  用于替代原先的 zero vector placeholder

### 3. `alpha`
- `status = heuristic_estimated`
- 当前值:
  - `1.15`
- 当前是受边界裁剪后的 bootstrap scalar，
  不是通过正式 calibration loss 优化出来的参数

## 与上一轮相比，实际改变了什么

### 已改变
- Stage3 conditioning 不再是全零占位。
- eval bridge 已经能消费 estimated asset。
- 当前 bridge 摘要可以反映:
  - “换了一份真实数据驱动 conditioning”
  之后的输出统计变化。

### 没改变
- 仍没有 dedicated calibration objective。
- 仍没有:
  - formant anchor
  - low-spec warp loss
  - geometry prior optimization
- 因而当前 estimated asset
  仍然不能写成“目标说话人校准已完成”。

## 当前边界

### 1. 这是 bootstrap prior，不是最终 calibration
- 当前值的主要作用是:
  - 让 Stage3 链路摆脱 placeholder
  - 让后续真实训练 / 评估可以在非零 conditioning 上启动

### 2. `alpha` 当前命中上界，不能过度解读
- 当前 `alpha = 1.15`
  是被边界约束裁剪后的值
- 这只能说明:
  - 当前 heuristic feature 映射倾向于把目标往上界推
- 不能直接解释成:
  - 目标说话人真实就一定需要这么强的 warp

### 3. bridge 结果仍然不是模型质量结论
- 即便 bridge 已切到 estimated asset，
  当前它也仍然主要是:
  - plumbing / contract check
- 不是:
  - 真正的 Stage3 训练指标

## 下一步建议
1. 在 heuristic estimate 之上，
   逐步补:
   - 更明确的 low-band / formant proxy
   - 更像 `s_geom_target` 的几何约束
   - 更稳定的 `alpha` 估计逻辑
2. 不要把当前 heuristic asset 固化成最终标准；
   它现在更像:
   - bootstrap prior
3. 以这份 estimated asset 为起点，
   再接 teacher-label 数据与真实 Student 训练入口。

## 一句话结论
- Stage3 现在已经拥有一份非 placeholder、可被 bridge 实际消费的 calibration asset；
  但它仍然只是启发式 bootstrap estimate，
  不是设计稿意义上的正式目标说话人校准器。
