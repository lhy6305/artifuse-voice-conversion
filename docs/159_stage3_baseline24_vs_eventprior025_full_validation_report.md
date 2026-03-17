# 159. Stage3 baseline24 与 eventprior025 full-validation 对照报告

## 背景
- `docs/157_stage3_full_validation_loop_report.md`
  已把 Stage3 loop
  的 validation
  固定到可正式使用的:
  - `validation_mode = full`
- `docs/158_stage3_energyproxy015_full_validation_report.md`
  已表明:
  - `energyproxy015`
    不是当前更优方向
- 因此下一步最值得做的，
  是把此前最接近 baseline 的:
  - `eventprior025`
  提升到更长一点 horizon，
  并与默认 baseline
  做同口径对照

## 本轮目标
1. 跑一条默认权重的
   - `24-step full-validation baseline`
2. 跑一条只降低
   - `teacher_event_prior = 0.25`
   的
   `24-step full-validation eventprior025`
3. 比较:
   - 两条 run 的训练轨迹
   - loop 内 full validation
   - fuller checkpoint ranking
   - best-checkpoint 外部 eval
4. 明确回答:
   - 更长 horizon
     是否足以让 `eventprior025`
     超过默认 baseline

## 本轮实际完成

### 1. 已完成 baseline24 full-validation run
- 执行:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 24 --validation-interval 8 --checkpoint-interval 8 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_baseline24_fullval_v1`

### 2. 已完成 eventprior025 full-validation run
- 执行:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 24 --validation-interval 8 --checkpoint-interval 8 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_eventprior025_fullval24_v1 --loss-weight-overrides configs/streaming_student_loss_weights_eventprior_light_v1.json`

### 3. 已完成两条 run 的 checkpoint ranking
- 执行:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step8.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step16.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step24.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_baseline24_fullval_v1`
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval24_v1.step8.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval24_v1.step16.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval24_v1.step24.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_eventprior025_fullval24_v1`

### 4. 已完成两条 run 的 best-checkpoint 外部 eval
- 执行:
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step24.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_baseline24_fullval_v1`
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval24_v1.step24.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_eventprior025_fullval24_v1`

## 已生成正式产物
- baseline24 loop summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_baseline24_fullval_v1.summary.md`
- baseline24 ranking:
  - `reports/eval/streaming_student_checkpoint_selection_baseline24_fullval_v1/streaming_student_checkpoint_selection.md`
- baseline24 eval:
  - `reports/eval/streaming_student_checkpoint_eval_baseline24_fullval_v1/streaming_student_stage_loop_baseline24_fullval_v1.checkpoint_eval.md`
- eventprior025 fullval24 loop summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_eventprior025_fullval24_v1.summary.md`
- eventprior025 fullval24 ranking:
  - `reports/eval/streaming_student_checkpoint_selection_eventprior025_fullval24_v1/streaming_student_checkpoint_selection.md`
- eventprior025 fullval24 eval:
  - `reports/eval/streaming_student_checkpoint_eval_eventprior025_fullval24_v1/streaming_student_stage_loop_eventprior025_fullval24_v1.checkpoint_eval.md`

## baseline24 结果

### 训练轨迹
- train `loss_total`
  从:
  - `20.612329`
  降到:
  - `7.315161`
- `grad_norm`
  从:
  - `64.267143`
  降到:
  - `2.901576`

### loop 内 full validation
- `step8`
  - `8.879169`
- `step16`
  - `7.635716`
- `step24`
  - `7.292622`

### ranking / eval
- 当前最优 checkpoint:
  - `step24`
- 外部 eval:
  - `target_validation.loss_total_default_reference = 7.292622`
  - `target_special_eval.loss_total_default_reference = 7.804316`

## eventprior025 fullval24 结果

### 训练轨迹
- train `loss_total`
  从:
  - `19.2505`
  降到:
  - `6.151259`
- train `loss_total_default_reference`
  从:
  - `20.612329`
  降到:
  - `7.33198`
- `grad_norm`
  从:
  - `64.24408`
  降到:
  - `3.003417`

### loop 内 full validation
- `step8`
  - `loss_total = 7.667545`
  - `loss_total_default_reference = 8.913209`
- `step16`
  - `loss_total = 6.443347`
  - `loss_total_default_reference = 7.651951`
- `step24`
  - `loss_total = 6.124982`
  - `loss_total_default_reference = 7.30326`

### ranking / eval
- 当前最优 checkpoint:
  - `step24`
- 外部 eval:
  - `target_validation.loss_total_default_reference = 7.30326`
  - `target_special_eval.loss_total_default_reference = 7.803009`

## 12-step 到 24-step 的变化

### baseline
- validation:
  - `8.134648 -> 7.292622`
  - 改善:
    - `-0.842026`
- special:
  - `8.11794 -> 7.804316`
  - 改善:
    - `-0.313624`

### eventprior025
- validation:
  - `8.150748 -> 7.30326`
  - 改善:
    - `-0.847488`
- special:
  - `8.115334 -> 7.803009`
  - 改善:
    - `-0.312325`

说明:
- 两条路线都从更长 horizon
  中获益明显
- 但获益幅度非常接近，
  没有出现:
  - `eventprior025`
    借更长 horizon
    明显拉开默认 baseline
  的现象

## 24-step apples-to-apples 对照

### baseline24
- validation:
  - `7.292622`
- special:
  - `7.804316`

### eventprior025 fullval24
- validation:
  - `7.30326`
- special:
  - `7.803009`

### 直接差值
- validation:
  - `7.292622 -> 7.30326`
  - `+0.010638`
- special:
  - `7.804316 -> 7.803009`
  - `-0.001307`

解释:
- 到了 `24-step`
  以后，
  当前结论仍然是:
  - validation 上
    `eventprior025`
    略差
  - special 上
    `eventprior025`
    略好
- 但两边差值都非常小，
  仍然属于:
  - 接近持平
  - 没有形成明确反转

## 当前最重要的结论

### 1. 更长 horizon
   继续有效，
   且 baseline24 已明显优于 baseline12
- 默认权重 baseline
  的 `target_validation`
  已从:
  - `8.134648`
    降到
  - `7.292622`
- 说明:
  - 当前 Stage3 主线
    还远没到 12-step
      就触顶

### 2. `eventprior025`
   在 24-step 仍未超过 baseline
- 它不是坏路线，
  反而是目前最接近 baseline 的 override
- 但按照当前正式规则:
  - validation-first
  - special 作次级排序
- 24-step 默认基线
  仍应保留在:
  - `baseline24_fullval_v1.step24`

### 3. 当前默认 best checkpoint
   应更新为 baseline24 step24
- 在已经完成的 full-validation run 里，
  当前 validation-first
  的最好结果是:
  - `streaming_student_stage_loop_baseline24_fullval_v1.step24.pt`
- 它优于:
  - baseline12 fullval
  - energyproxy015 fullval
  - eventprior025 fullval24

## 当前解释
- `eventprior025`
  目前更像是:
  - 与 baseline 非常接近的候选
  - 在 special 上偶尔略占便宜
  - 在 validation 上仍略落后
- 更长 horizon
  没有把这种关系改写成
  明确的主从反转
- 因此最稳妥的推进方式是:
  - 默认训练继续沿 baseline24
  - 若要保留 `eventprior025`
    就把它视作
    近似平手的备选分支，
    而不是新的正式默认

## 下一步建议
1. 默认基线
   更新为:
   - `streaming_student_stage_loop_baseline24_fullval_v1.step24.pt`
2. 之后若继续扩 horizon，
   默认权重与 `eventprior025`
   仍可并行跟一轮，
   但优先级先放在:
   - baseline 主线
3. 若下一轮继续做 loss weight sweep，
   先不要再做更轻微近邻，
   因为:
   - `eventprior025`
     已经是最接近 baseline 的候选
   - 现在更值得回答的是:
     - 更长 horizon 是否继续稳定
     - 以及何时开始接更接近成品的后续链路

## 一句话结论
- 把 horizon
  从 `12-step`
  提到 `24-step`
  后，
  baseline 和 `eventprior025`
  都继续明显变好；
  但 `eventprior025`
  仍然只是:
  - validation 略差
  - special 略好
  的近似持平候选，
  还没有足以替换
  `baseline24 step24`
  成为新的默认基线。
