# 150. Stage3 minimal teacher supervision 报告

## 背景
- `docs/149_stage3_training_data_contract_report.md`
  已经确认:
  - Stage3 batch contract 成立
  - teacher labels 与 Student 前端逐帧对齐
- 下一步如果还停在“只有 batch 没 loss”，
  下次恢复时仍然会卡在监督定义上。

## 本轮目标
- 不直接开始真实训练。
- 先给 Stage3 定一个最小可计算的 teacher-supervised loss dry-run。

## 本轮实际完成

### 1. 新增最小 supervision loss 模块
- 新增:
  - `src/v5vc/streaming_student/losses.py`

### 2. 新增 supervision dry-run 入口
- 新增命令:
  - `.\python.exe manage.py prepare-streaming-student-supervision`

### 3. 已生成正式 dry-run 产物
- 生成:
  - `reports/plans/streaming_student_supervision/streaming_student_supervision_plan.json`
  - `reports/plans/streaming_student_supervision/streaming_student_supervision_plan.md`

## 当前最小 loss 包含什么

### 直接 teacher 对齐项
- `teacher_z_art`
- `teacher_event`
- `teacher_event_prior`

### frontend proxy 项
- `teacher_energy_proxy`
- `teacher_vuv_proxy`
- `teacher_aper_proxy`

### 轻量 regularization
- `log_f0_correction_l1`
- `aper_correction_l1`

### 当前默认权重
- `teacher_z_art = 1.0`
- `teacher_event = 1.0`
- `teacher_event_prior = 0.5`
- `teacher_energy_proxy = 0.25`
- `teacher_vuv_proxy = 0.15`
- `teacher_aper_proxy = 0.1`
- `log_f0_correction_l1 = 0.01`
- `aper_correction_l1 = 0.01`

### 当前 frame weighting
- 默认:
  - `use_teacher_confidence = true`
- 即:
  - `teacher_frame_mask`
    与
  - `teacher_frame_confidence`
  共同构成有效 frame weight

## dry-run 结果

### 执行命令
- `.\python.exe manage.py prepare-streaming-student-supervision --batch-size 3`

### 当前结果摘要
- `target_train`
  - `loss_total = 16.015551`
  - `loss_teacher_z_art = 3.473783`
  - `loss_teacher_event = 5.781376`
  - `loss_teacher_event_prior = 5.751039`
  - `loss_teacher_energy_proxy = 14.93887`
- `target_validation`
  - `loss_total = 14.957625`
  - `loss_teacher_z_art = 4.186419`
  - `loss_teacher_event = 5.72887`
  - `loss_teacher_event_prior = 5.716`
  - `loss_teacher_energy_proxy = 8.133447`
- `target_special_eval`
  - `loss_total = 14.195153`
  - `loss_teacher_z_art = 2.321452`
  - `loss_teacher_event = 5.816716`
  - `loss_teacher_event_prior = 5.759247`
  - `loss_teacher_energy_proxy = 12.106345`

说明:
- 当前这些数值的意义是:
  - loss contract 已可计算
  - 不是性能好坏结论

## 当前刻意没做什么

### 1. 没做 hidden distillation
- 当前没有直接对齐:
  - `shared_hidden`
  - `student_hidden`
  到
  - `teacher hidden`
  - `teacher fused_hidden`
- 原因:
  - Stage3 是 `96d`
  - offline MVP teacher 是 `64d`
  - 当前没有投影桥

### 2. 没把 frontend proxy 项写死成最终语义
- 当前:
  - `vuv`
  - `aperiodicity`
  - `energy`
  的 teacher 监督
  只是最小 proxy
- 目的是先让训练入口有基础可算监督，
  不是现在就宣告这些 proxy
  等价于最终设计稿语义。

## 当前边界

### 1. 这是 dry-run supervision，不是真实训练结果
- 当前没有:
  - optimizer
  - backward
  - checkpoint
  - 多 step 训练轨迹

### 2. `teacher_frame_confidence` 还只是 bootstrap weighting
- 当前能说明:
  - 这份权重可被 loss 正常消费
- 还不能说明:
  - 真实训练里它最适合做 weighting、filtering 还是 curriculum

## 下一步建议
1. 在这份最小 supervision 基础上，
   新建真正的 Stage3 training step。
2. 补一个小规模单 step / 少 step 训练 dry-run，
   验证:
   - backward
   - optimizer
   - checkpoint
   - loss 落盘
3. 等基本训练入口稳定后，
   再决定是否加:
   - hidden distillation
   - 更严格的 frontend supervision

## 一句话结论
- Stage3 现在已经不只是“知道要学 teacher labels”，
  而是已经有一份真正能算出数值的最小监督定义；
  下一步可以进入真实训练 step scaffold，
  但还不能把当前 proxy losses 当成最终理论结论。
