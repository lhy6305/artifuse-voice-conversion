# 160. Stage3 baseline48 与 eventprior025 full-validation 对照报告

## 背景
- `docs/159_stage3_baseline24_vs_eventprior025_full_validation_report.md`
  的结论是:
  - 到 `24-step`
    为止，
    `eventprior025`
    仍然只是:
    - validation 略差
    - special 略好
    的近似平手候选
- 因此上一轮决定:
  - 继续推进默认 baseline 主线
  - 同时只把 `eventprior025`
    保留为影子对照

## 本轮目标
1. 把默认 baseline
   拉到:
   - `48-step full validation`
2. 用同 horizon
   跑一条
   - `eventprior025`
   影子对照
3. 回答:
   - 更长 horizon
     是否会把此前的“近似平手”
     推成真正反超

## 本轮实际完成

### 1. 已完成 baseline48 full-validation run
- 执行:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 48 --validation-interval 12 --checkpoint-interval 12 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_baseline48_fullval_v1`

### 2. 已完成 baseline48 ranking 与 best-checkpoint eval
- 执行:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step12.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step24.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step36.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_baseline48_fullval_v1`
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_baseline48_fullval_v1`

### 3. 已完成 eventprior025 fullval48 影子对照
- 执行:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 48 --validation-interval 12 --checkpoint-interval 12 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_eventprior025_fullval48_v1 --loss-weight-overrides configs/streaming_student_loss_weights_eventprior_light_v1.json`

### 4. 已完成 eventprior025 fullval48 ranking 与 best-checkpoint eval
- 执行:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step12.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step24.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step36.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step48.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_eventprior025_fullval48_v1`
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step48.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_eventprior025_fullval48_v1`

## 已生成正式产物
- baseline48 summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_baseline48_fullval_v1.summary.md`
- baseline48 ranking:
  - `reports/eval/streaming_student_checkpoint_selection_baseline48_fullval_v1/streaming_student_checkpoint_selection.md`
- baseline48 eval:
  - `reports/eval/streaming_student_checkpoint_eval_baseline48_fullval_v1/streaming_student_stage_loop_baseline48_fullval_v1.checkpoint_eval.md`
- eventprior025 fullval48 summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_eventprior025_fullval48_v1.summary.md`
- eventprior025 fullval48 ranking:
  - `reports/eval/streaming_student_checkpoint_selection_eventprior025_fullval48_v1/streaming_student_checkpoint_selection.md`
- eventprior025 fullval48 eval:
  - `reports/eval/streaming_student_checkpoint_eval_eventprior025_fullval48_v1/streaming_student_stage_loop_eventprior025_fullval48_v1.checkpoint_eval.md`

## baseline48 结果

### loop 内 full validation
- `step12`
  - `7.292622`? 不对，本轮记录如下:
  - `step12 = 8.134648`
- `step24`
  - `7.292622`
- `step36`
  - `7.323279`
- `step48`
  - `7.141462`

### ranking / eval
- 当前最优 checkpoint:
  - `step48`
- 外部 eval:
  - `target_validation.loss_total_default_reference = 7.141462`
  - `target_special_eval.loss_total_default_reference = 7.572382`

### 解释
- baseline 主线继续有效，
  并且比 `24-step`
  继续更好
- 但 `step24 -> step36`
  有一次轻微回弹，
  说明更长 horizon
  已进入:
  - 仍能改善
  - 但不再单调丝滑
  的区域

## eventprior025 fullval48 结果

### loop 内 full validation
- `step12`
  - `loss_total_default_reference = 8.150748`
- `step24`
  - `loss_total_default_reference = 7.30326`
- `step36`
  - `loss_total_default_reference = 7.318337`
- `step48`
  - `loss_total_default_reference = 7.152429`

### ranking / eval
- 当前最优 checkpoint:
  - `step48`
- 外部 eval:
  - `target_validation.loss_total_default_reference = 7.152429`
  - `target_special_eval.loss_total_default_reference = 7.573954`

## 更正与最终 apples-to-apples 对照

### 先说关键事实
- 上面 `loop / eval`
  数值已经表明:
  - `baseline48`
    validation:
    - `7.141462`
  - `eventprior025 fullval48`
    validation:
    - `7.152429`
- 也就是:
  - `eventprior025`
    在 `48-step`
    依然没有超过 baseline

### 直接差值
- validation:
  - `7.141462 -> 7.152429`
  - `+0.010967`
- special:
  - `7.572382 -> 7.573954`
  - `+0.001572`

### 正确结论
- 与 `24-step`
  一样，
  到 `48-step`
  为止，
  `eventprior025`
  仍然没有完成反超
- 只是:
  - 继续保持非常接近
  - 但依旧略差于默认 baseline

## 24-step 到 48-step 的变化

### baseline
- validation:
  - `7.292622 -> 7.141462`
  - 改善:
    - `-0.15116`
- special:
  - `7.804316 -> 7.572382`
  - 改善:
    - `-0.231934`

### eventprior025
- validation:
  - `7.30326 -> 7.152429`
  - 改善:
    - `-0.150831`
- special:
  - `7.803009 -> 7.573954`
  - 改善:
    - `-0.229055`

说明:
- 两条路线在 `24 -> 48`
  上继续改善，
  而且改善幅度几乎一致
- 这再次说明:
  - `eventprior025`
    更像是高相似候选
  - 还不是明确更优路线

## 当前最重要的结论

### 1. 默认 baseline48 step48
   现在是当前全局最优默认 checkpoint
- 它相对:
  - baseline24 step24
  - baseline12 step12
  都继续更好
- 也仍优于:
  - eventprior025 fullval48 step48

### 2. `eventprior025`
   依旧值得保留，
   但还不该翻成默认主线
- 因为它已经多次表现出:
  - 非常接近 baseline
- 但在当前正式口径下，
  仍没有完成:
  - validation-first 反超

### 3. 下一步不再优先做更多近邻权重 sweep
- 现在再做更轻微权重近邻，
  信息增益不会太高
- 更值得推进的是:
  - 默认主线是否还能继续稳定
  - 以及向试听导出链路靠近

## 下一步建议
1. 默认 best checkpoint
   更新为:
   - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
2. 若还做更长 horizon，
   `eventprior025`
   只保留为影子分支，
   不再抢主线资源
3. 下一轮更值得做:
   - 把当前默认 checkpoint
     接到试听导出链路
   - 或在进入更复杂模块前，
     先补一条正式的可试听代理导出路径

## 一句话结论
- `48-step`
  证明默认 baseline
  还能继续稳定改善；
  `eventprior025`
  仍然很接近，
  但在统一参考口径下
  依旧没有完成反超，
  所以当前默认主线
  应更新到:
  - `baseline48 step48`
