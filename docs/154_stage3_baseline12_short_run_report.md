# 154. Stage3 baseline 12-step 短程 run 报告

## 背景
- `docs/153_stage3_short_horizon_stabilization_comparison_report.md`
  已经把默认方向收窄到:
  - `lr = 1e-3`
  - `teacher_confidence = on`
- 但 `4 step`
  仍然太短，
  还不能完全回答:
  - 这条 baseline 是否只是前几步碰巧下降

## 本轮目标
- 不再横向开新路线。
- 直接沿当前 baseline
  做一个更长一点的短程 run。

## 本轮实际完成

### 1. 已完成 baseline 12-step loop
- 执行命令:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 12 --validation-interval 4 --checkpoint-interval 4 --validation-batches 4 --experiment-id streaming_student_stage_loop_baseline12_v1`

### 2. 已完成 `step12` fuller checkpoint eval
- 执行命令:
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step12.pt --batch-size 6`

### 3. 已生成正式产物
- loop summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_baseline12_v1.summary.md`
- checkpoints:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step4.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step8.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline12_v1.step12.pt`
- fuller eval:
  - `reports/eval/streaming_student_checkpoint_eval/streaming_student_stage_loop_baseline12_v1.checkpoint_eval.md`

## 当前轨迹

### train loss
- `step1 = 20.612329`
- `step4 = 10.774693`
- `step8 = 8.774059`
- `step12 = 8.203006`

### grad_norm
- `step1 = 64.267143`
- `step4 = 13.034104`
- `step8 = 7.220087`
- `step12 = 4.994916`

### sampled validation
- `step4 = 10.005472`
- `step8 = 8.914471`
- `step12 = 8.099716`

## fuller checkpoint eval

### `step12`
- `target_validation.loss_total = 8.134648`
- `target_special_eval.loss_total = 8.11794`

### 相比 `4 step baseline v2`
- validation:
  - `9.94085 -> 8.134648`
- special:
  - `9.144604 -> 8.11794`

说明:
- 当前 baseline 在更长一点的短程 horizon 上，
  仍在继续改善。

## 当前能说明什么

### 可以说明
- 当前 baseline 不是只在 `4 step`
  里碰巧下降。
- 在 `12 step` 这个更长一点的短程尺度上，
  它仍然:
  - train loss 持续下降
  - grad_norm 持续回落
  - fuller eval 继续改善

### 不能说明
- 不能说明:
  - 长程训练已经稳定
  - 当前权重就是最终配置
  - 现在就该加 hidden distillation 或 `r_res`

## 下一步建议
1. 继续沿 baseline 做更正式的小规模训练，
   不再优先横向开新低优先级路线。
2. 下一轮优先补:
   - validation 设计
   - best-checkpoint 规则
   - loss 权重细化
3. 在 baseline 长一点的短程训练稳定前，
   不要同时引入:
   - `teacher_confidence off`
   - 更低 lr
   - hidden distillation
   - `r_res`

## 一句话结论
- 当前 Stage3 baseline 已经从“4 step 看起来可行”
  推进到“12 step 仍持续改善”；
  下一步可以更集中地做 baseline 稳定化，
  而不是再回到路线发散。
