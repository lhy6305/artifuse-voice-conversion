# 152. Stage3 training loop scaffold 报告

## 背景
- `docs/151_stage3_training_step_scaffold_report.md`
  已经把 Stage3 单步训练闭环跑通。
- 下一步如果还停在单步，
  就看不到:
  - loss 轨迹
  - grad_norm 变化
  - 周期 validation
  - checkpoint 节点

## 本轮目标
- 不直接上大规模训练。
- 先把 Stage3 扩成最小多 step 训练循环。

## 本轮实际完成

### 1. 新增多 step 训练循环入口
- 新增命令:
  - `.\python.exe manage.py run-streaming-student-training-loop`

### 2. 已完成一个最小短程 loop
- 执行命令:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 3 --num-steps 4 --validation-interval 2 --checkpoint-interval 2 --validation-batches 2 --experiment-id streaming_student_stage_loop_scaffold_v1`

### 3. 已生成正式产物
- summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_scaffold_v1.summary.md`
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.summary.json`
- step logs:
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.step1.json`
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.step2.json`
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.step3.json`
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.step4.json`
- checkpoints:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_scaffold_v1.step2.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_scaffold_v1.step4.pt`

## 当前 loop 实际做了什么

### train side
- 每 step:
  - 取一个 target_train batch
  - forward
  - teacher-supervised loss
  - backward
  - grad clip
  - optimizer step
  - 写 step log

### validation side
- 每 `2` step
  - 从 `target_validation`
    抽 `2` 个 batch
  - 对这 `2` 个 batch
    的 loss 求平均

### checkpoint side
- 每 `2` step
  写一次 checkpoint

## 当前短程轨迹

### train loss
- `step1 = 20.612329`
- `step2 = 14.973147`
- `step3 = 12.068747`
- `step4 = 10.774693`

### grad_norm
- `step1 = 64.267143`
- `step2 = 35.93412`
- `step3 = 21.220259`
- `step4 = 13.034104`

### sampled validation
- `step2 = 13.13162`
- `step4 = 9.656614`

## 当前能说明什么

### 可以说明
- Stage3 现在已经具备:
  - 多 step 训练
  - 周期 validation
  - 周期 checkpoint
  - step 级日志
  的最小训练循环能力

### 不能说明
- 不能说明:
  - 当前 loss 已稳定收敛
  - 当前 validation 已代表全量 validation slice
  - 当前 learning rate / 权重已经最优

原因:
- 当前 loop 很短
- validation 仍是 sampled batches
- train batch 仍按记录顺序顺推

## 当前边界

### 1. validation 还是 sampled subset
- 当前 `validation_batches = 2`
- 它更像:
  - 快速体检
- 不是:
  - 正式 full validation

### 2. 当前短程曲线仍受样本顺序影响
- 本轮 `4` step
  只覆盖了训练集前缀一小段样本
- 所以当前曲线主要回答:
  - loop 通不通
  - 数值有没有炸

### 3. 当前依然保持基础策略
- 继续保持:
  - `r_res = false`
  - 无 hidden distillation
  - teacher confidence 仅做 weighting

## 下一步建议
1. 把当前最小 loop
   扩成更像真实小规模训练的短程 run。
2. 先明确 validation 口径:
   - sampled validation
   还是
   - fuller validation pass
3. 再基于短程轨迹调:
   - learning rate
   - loss weights
   - teacher confidence 用法

## 一句话结论
- Stage3 已经从“单步训练能跑”
  推进到“最小多 step 训练循环能跑”；
  下一步该做的是短程稳定化，
  而不是再回到只搭接口。
