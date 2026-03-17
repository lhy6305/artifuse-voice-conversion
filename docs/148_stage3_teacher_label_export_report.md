# 148. Stage3 teacher-label 导出报告

## 背景
- `docs/147_stage3_heuristic_calibration_estimate_report.md`
  已经把 Stage3 conditioning
  从 zero placeholder
  推进到 heuristic bootstrap prior。
- 下一步真正缺的，
  不再只是“Student 以后学什么”，
  而是:
  - 现阶段拿什么监督它
  - 这些监督资产怎样正式落盘

## 本轮目标
- 不直接开始真实 Student 训练。
- 先把 formal offline MVP anchor
  导出的 teacher pseudo labels
  固定成 Stage3 可复用资产。

## 本轮实际完成

### 1. 新增 Stage3 teacher-label CLI 入口
- 新增命令:
  - `.\python.exe manage.py build-streaming-student-teacher-labels`

### 2. teacher-label 导出已正式接入默认 route handoff anchor
- 当前默认从:
  - `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json`
  解析 teacher anchor
- 当前实际落到:
  - `EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration`
  - checkpoint:
    - `reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt`

### 3. 已完成全量导出
- 执行命令:
  - `.\python.exe manage.py build-streaming-student-teacher-labels --batch-size 4`
- 成功生成:
  - `data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl`
  - `data_prep/round1_1/streaming_student_teacher_labels/records/*.pt`
  - `reports/data/streaming_student_teacher_labels/streaming_student_teacher_label_summary.json`
  - `reports/data/streaming_student_teacher_labels/streaming_student_teacher_label_summary.md`

## 当前 teacher-label 资产格式

### 每条记录包含
- `frame_mask`
- `hidden`
- `fused_hidden`
- `z_art`
- `event_logits`
- `event_probs`
- `acoustic`
- `frame_confidence`

### 当前附带索引字段包括
- `record_id`
- `split_name`
- `audio_path`
- `duration_sec`
- `frame_count`
- `teacher_label_path`
- `confidence_mean / min / max`
- `low_confidence_frame_ratio`
- `utterance_structure_type`
- `final_terminal_type`
- `special_proximity_score`
- `pool_memberships`

### 当前 feature dims
- `hidden = 64`
- `fused_hidden = 64`
- `z_art = 8`
- `event_logits = 8`
- `acoustic = 4`
- `confidence = 1`

## 全量导出结果

### 总量
- `record_count = 666`
- `frame_count = 1118127`
- `records/*.pt count = 666`

### 各 slice
- `target_train`
  - `record_count = 592`
  - `duration_mean_sec = 6.158126`
  - `frame_count_mean = 1695.342905`
  - `confidence_mean = 0.489846`
  - `low_confidence_frame_ratio_mean = 0.319015`
- `target_validation`
  - `record_count = 66`
  - `duration_mean_sec = 6.173509`
  - `frame_count_mean = 1699.530303`
  - `confidence_mean = 0.486753`
  - `low_confidence_frame_ratio_mean = 0.338887`
- `target_special_eval`
  - `record_count = 8`
  - `duration_mean_sec = 1.057291`
  - `frame_count_mean = 289.375`
  - `confidence_mean = 0.489138`
  - `low_confidence_frame_ratio_mean = 0.177271`

## 当前 teacher-label 是怎么来的

### 当前来源
- 先加载 formal offline MVP anchor checkpoint
- 再对:
  - `target_train`
  - `target_validation`
  - `target_special_eval`
  三个 slice
  做 forward
- 同时结合 frame target
  计算启发式:
  - `frame_confidence`

### 当前 `frame_confidence` 组成
- event certainty
- acoustic reconstruction consistency
- `z_art` 时序稳定性
- energy gate

说明:
- 这只是 `bootstrap_v1` 权重估计，
  不是最终 confidence 设计。

## 当前边界

### 1. teacher-label 不是 ground truth
- 当前产物本质上是:
  - pseudo-label training assets
- 它们继承了:
  - Teacher 偏差
  - formal route anchor 偏差
  - confidence heuristic 偏差

### 2. 当前只是把监督资产正式接好
- 这一步解决的是:
  - Stage3 将来训练时“从哪里读监督”
- 还没有解决:
  - 真实 Student loss 定义
  - loss weighting / filtering policy
  - Stage3 训练循环

### 3. 仍不能直接复用 `offline_mvp` 训练循环
- 当前可复用的是:
  - formal teacher anchor
  - split
  - 伪标签资产
- 不能直接复用的是:
  - `offline_mvp` 训练 step
  - loss 组合
  - 整个 runtime contract

## 下一步建议
1. 基于:
   - `teacher_label_index.jsonl`
   - `records/*.pt`
   新建 Stage3 Student 数据层与 batch collator。
2. 明确 `frame_confidence`
   在 Stage3 中究竟用于:
   - sample weighting
   - frame masking
   - curriculum
   哪些环节，
   不要默认三者一起开。
3. 把 teacher-label contract
   接到真实 Student loss 定义，
   但继续保持:
   - `r_res` 关闭
   - `frame_length / hop_length` 对齐
4. 后续若补人工分析或额外派生资产，
   不要混放到 teacher-label 命令的 managed 输出目录，
   因为重跑会重建目录。

## 一句话结论
- Stage3 现在已经同时拥有:
  - scaffold
  - calibration asset
  - eval bridge
  - teacher-label assets
- 也就是说，
  下一步终于可以从“接口准备”进入“真实 Student 训练入口设计”，
  但仍要明确这些监督来自 pseudo labels，
  不是最终真值。
