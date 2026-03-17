# 149. Stage3 training-data contract 报告

## 背景
- `docs/148_stage3_teacher_label_export_report.md`
  已经把 Stage3 teacher-label assets
  正式落盘。
- 下一步真正缺的，
  不再只是“有资产”，
  而是:
  - 这些资产怎么与 split / sidecar / conditioning
    一起拼成真实训练 batch

## 本轮目标
- 不直接开始训练。
- 先把 Stage3 训练数据层的 batch contract
  固定成正式 dry-run 产物。

## 本轮实际完成

### 1. 新增 Stage3 数据装载模块
- 新增:
  - `src/v5vc/streaming_student/data.py`

### 2. 新增数据合同 dry-run 入口
- 新增命令:
  - `.\python.exe manage.py prepare-streaming-student-training-data`

### 3. 已生成正式 dry-run 产物
- 生成:
  - `reports/plans/streaming_student_training_data/streaming_student_training_data_plan.json`
  - `reports/plans/streaming_student_training_data/streaming_student_training_data_plan.md`

## 当前 batch contract 实际包含什么

### 输入侧
- `waveform`
- `audio_lengths`
- `speaker_embedding`
- `geom_embedding`
- `alpha`
- `weak_event_hints`
- `target_special_supervision`

### teacher 监督侧
- `teacher_frame_mask`
- `teacher_hidden`
- `teacher_fused_hidden`
- `teacher_z_art`
- `teacher_event_logits`
- `teacher_event_probs`
- `teacher_acoustic`
- `teacher_frame_confidence`

### 元数据
- `record_ids`
- `split_names`
- `teacher_label_paths`
- `teacher_frame_lengths`
- `teacher_confidence_means`
- `teacher_low_confidence_frame_ratios`

## 当前 conditioning 来源
- 使用:
  - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json`
- 当前状态:
  - `asset_status = heuristic_bootstrap_estimated`
  - `speaker_dim = 16`
  - `geom_dim = 8`
  - `alpha = 1.15`

## dry-run 结果

### 当前 sample batch 规模
- 命令:
  - `.\python.exe manage.py prepare-streaming-student-training-data --batch-size 3`
- 当前按 slice 各取 `3` 条样本做 dry-run

### 当前最关键的确认
- `target_train`
  - teacher frame lengths 与 Student frame lengths
    逐样本一致:
    - `[3054, 4735, 4364]`
- `target_validation`
  - 逐样本一致:
    - `[167, 267, 320]`
- `target_special_eval`
  - 逐样本一致:
    - `[128, 188, 581]`

说明:
- 当前 `frame_length = 400`
- 当前 `hop_length = 160`
- 在这套合同下，
  teacher labels 与 Stage3 前端输出
  已确认 frame 对齐。

## 当前边界

### 1. 这是 training-data contract，不是 training loop
- 当前只解决了:
  - 数据怎么读
  - batch 怎么拼
  - 帧怎么对齐
- 还没解决:
  - optimizer
  - checkpoint
  - 真实训练 step

### 2. 当前默认必须读取完整音频
- 之所以能 frame 对齐，
  依赖的是:
  - 不截断 waveform
  - 沿用 teacher 导出时的 frame contract
- 若后续改成截断读取，
  就必须重新定义或重导 teacher labels。

### 3. 当前 hidden 资产虽然已入 batch，
   但还不能直接用于 loss
- 原因不是资产缺失，
  而是:
  - Stage3 `shared_hidden / student_hidden = 96d`
  - offline MVP teacher `hidden / fused_hidden = 64d`
- 目前还没有正式投影桥。

## 下一步建议
1. 基于这份 batch contract
   新建 Stage3 training step scaffold。
2. 在真正训练前，
   先决定 `teacher_frame_confidence`
   到底用于:
   - weighting
   - filtering
   - curriculum
   哪些环节。
3. 若后续仍想引入 hidden distillation，
   先定义维度投影或 adapter contract。

## 一句话结论
- Stage3 现在已经不只是“有 teacher labels”，
  而是已经有了一份经过 dry-run 验证、帧级对齐成立的正式训练 batch contract。
