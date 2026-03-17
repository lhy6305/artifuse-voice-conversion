# 155. Stage3 checkpoint selection 报告

## 背景
- `docs/154_stage3_baseline12_short_run_report.md`
  已经确认 baseline12
  在 `step12` 时继续改善。
- 但要把默认 checkpoint
  正式固定下来，
  还需要一个明确的 ranking 规则，
  而不是只看 loop 曲线。

## 本轮目标
- 对 baseline12 已产出的多个 checkpoint
  做正式 fuller ranking。

## 本轮实际完成

### 1. 新增 checkpoint ranking 入口
- 新增命令:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint`

### 2. 已对 baseline12 三个 checkpoint 排名
- 执行命令:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step4.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step8.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step12.pt --batch-size 6`

### 3. 已生成正式产物
- `reports/eval/streaming_student_checkpoint_selection/streaming_student_checkpoint_selection.json`
- `reports/eval/streaming_student_checkpoint_selection/streaming_student_checkpoint_selection.md`

## 当前 ranking 规则
- `lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)`

说明:
- 先比:
  - `target_validation.loss_total`
- 若接近或并列，
  再看:
  - `target_special_eval.loss_total`

## baseline12 排名结果

### 第 1 名
- `step12`
- `target_validation.loss_total = 8.134648`
- `target_special_eval.loss_total = 8.11794`

### 第 2 名
- `step8`
- `target_validation.loss_total = 8.879169`
- `target_special_eval.loss_total = 8.446648`

### 第 3 名
- `step4`
- `target_validation.loss_total = 9.94085`
- `target_special_eval.loss_total = 9.144604`

## 当前结论
- 当前 baseline12 的正式默认选点
  可以先固定为:
  - `step12`
- 当前没有看到:
  - `step8`
  在 special 上反超 validation
  的情况
- 也没有看到:
  - “更晚 checkpoint validation 继续变好、
    但 special 明显恶化”
  这种当前阶段最担心的反向信号

## 当前边界

### 1. 这仍然是 teacher-supervised proxy ranking
- 当前 ranking 的依据
  仍是 Stage3 proxy losses，
  不是最终听感评价。

### 2. sampled loop `best_checkpoint`
   仍不能代替 fuller ranking
- loop summary 里的 `best_checkpoint`
  只是快速参考。
- 真正的正式默认选点
  仍应以后验 fuller ranking 为准。

## 下一步建议
1. 以 `step12`
   作为当前 baseline12 的默认 checkpoint。
2. 若下一轮 run 产生更多 checkpoint，
   继续复用这套 fuller ranking 机制。
3. 继续把主要时间投入到:
   - loss 权重细化
   - validation 设计
   - 更长一点的短程 horizon

## 一句话结论
- baseline12 当前的正式默认 checkpoint
  已可先固定为 `step12`；
  之后不必再手工回看 `step4/8/12` 去猜哪个更好。
