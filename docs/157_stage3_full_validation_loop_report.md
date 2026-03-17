# 157. Stage3 full-validation loop 集成报告

## 背景
- `docs/152_stage3_training_loop_scaffold_report.md`
  已明确:
  - loop 内 validation
    仍只是 sampled batches
- `docs/153_stage3_short_horizon_stabilization_comparison_report.md`
  与
  `docs/154_stage3_baseline12_short_run_report.md`
  又都表明:
  - sampled validation
    适合快速观察
  - 但更正式的判断
    仍要依赖外部 fuller checkpoint eval

## 本轮目标
- 不改训练轨迹本身。
- 只把 Stage3 loop 内 validation
  从:
  - sampled subset
  扩成可选:
  - full-slice sequential pass
- 并验证:
  - loop 内 full validation
  与
  - 外部 fuller checkpoint eval
  的 `target_validation`
  口径一致。

## 本轮实际完成

### 1. 新增 loop 内 validation 模式开关
- `run-streaming-student-training-loop`
  现支持:
  - `--validation-mode sampled`
  - `--validation-mode full`

### 2. full validation 当前行为
- 当 `--validation-mode full` 时:
  - validation 不再使用
    `select_streaming_student_batch_records`
  - 改为对 `target_validation`
    做:
    - 顺序
    - 不回绕
    - 不重复
    的整 slice 切片
- 当前 summary / checkpoint training metadata
  也会记录:
  - `validation_mode`

### 3. 已完成 baseline12 fullval 对照 run
- 执行命令:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 12 --validation-interval 4 --checkpoint-interval 4 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_baseline12_fullval_v1`

### 4. 已完成 step12 外部 checkpoint eval 对齐复核
- 执行命令:
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_fullval_v1.step12.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_baseline12_fullval_v1`

## 已生成正式产物
- loop summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_baseline12_fullval_v1.summary.md`
- step logs:
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_baseline12_fullval_v1.step*.json`
- checkpoints:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_fullval_v1.step4.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_fullval_v1.step8.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_fullval_v1.step12.pt`
- external eval:
  - `reports/eval/streaming_student_checkpoint_eval_baseline12_fullval_v1/streaming_student_stage_loop_baseline12_fullval_v1.checkpoint_eval.md`

## full-validation 结果

### 训练轨迹
- train `loss_total`
  与原 baseline12 保持一致:
  - `20.612329 -> 8.203006`
- `grad_norm`
  也保持一致:
  - `64.267143 -> 4.994916`

说明:
- 本轮改的是 validation 口径，
  不是训练轨迹本身。

### loop 内 full validation
- `step4`
  - `validation_mode = full`
  - `validation_batches = 11`
  - `record_count = 66`
  - `loss_total = 9.94085`
- `step8`
  - `loss_total = 8.879169`
- `step12`
  - `loss_total = 8.134648`

### step12 外部 checkpoint eval
- `target_validation.loss_total = 8.134648`
- `target_special_eval.loss_total = 8.11794`

## 当前最重要的结论

### 1. loop 内 full validation
   已与外部 fuller checkpoint eval 对齐
- `step12`
  在 loop summary 里的:
  - `target_validation.loss_total = 8.134648`
- 与外部 checkpoint eval 的:
  - `target_validation.loss_total = 8.134648`
  完全一致

这说明:
- 当前 Stage3 training loop
  已经可以直接在循环内部
  提供正式的 `target_validation`
  full-slice 口径

### 2. 当前 full-validation loop 内默认 best checkpoint
   仍为 `step12`
- 当前 loop summary 内
  `best_checkpoint`
  已更新为:
  - `selection_rule = min_validation_loss_total_over_recorded_checkpoints`
  - `validation_mode = full`
  - `step = 12`

### 3. 后续短程对照
   可以更少依赖 sampled validation
- sampled validation
  仍适合快检
- 但若本轮目的是:
  - 正式比较 baseline / weight sweep
  - 判断短程 checkpoint 走势
  则 `full`
  已更适合作为默认 loop validation 口径

## 当前边界

### 1. 当前 full validation
   仍只覆盖 `target_validation`
- 它没有在 loop 内
  直接加入:
  - `target_special_eval`
- 因此 special 维度的正式判断，
  仍建议保留:
  - 外部 checkpoint eval
  - 或 fuller checkpoint ranking

### 2. 这仍是 teacher-supervised proxy loss
- 即使 validation 口径变硬了，
  当前指标仍然是:
  - teacher-supervised proxy losses
- 不是:
  - 最终听感
  - 最终 runtime 质量

### 3. 不等于长程训练已稳定
- 本轮只是把:
  - loop 内 validation
  做得更正式
- 不是:
  - 已经证明更长 horizon
    必然稳定

## 下一步建议
1. 后续凡是正式比较 Stage3 短程 run，
   优先使用:
   - `--validation-mode full`
2. 下一轮 loss weight 对照，
   可继续围绕:
   - `eventprior025` 更长一点 horizon
   - `energy_proxy` 轻量化
   并统一改用 full validation。
3. 在 `target_special_eval`
   也需要并入 loop 级判断前，
   继续保留:
   - 外部 checkpoint eval
   - checkpoint ranking
   作为 special 侧正式口径。

## 一句话结论
- Stage3 训练 loop
  现在已经不只是“带 sampled validation 的短程脚手架”，
  而是已经能在循环内部
  直接跑完整 `target_validation`
  并给出与外部 fuller eval 对齐的数值；
  这让下一轮 baseline 与权重对照
  的 validation 口径明显更硬了。
