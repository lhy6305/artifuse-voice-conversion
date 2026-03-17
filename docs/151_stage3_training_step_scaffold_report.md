# 151. Stage3 training step scaffold 报告

## 背景
- `docs/150_stage3_minimal_teacher_supervision_report.md`
  已经把最小 teacher-supervised loss
  定成正式 dry-run。
- 但在真正把:
  - backward
  - optimizer
  - checkpoint
  接起来之前，
  Stage3 仍然不算进入训练入口阶段。

## 本轮目标
- 不直接上多 step 训练。
- 先把 Stage3 最小训练闭环跑通一次。

## 本轮实际完成

### 1. 新增单步训练 scaffold 入口
- 新增命令:
  - `.\python.exe manage.py run-streaming-student-training-step`

### 2. 已完成一次真实单步训练
- 执行命令:
  - `.\python.exe manage.py run-streaming-student-training-step --batch-size 3 --experiment-id streaming_student_stage_step_scaffold_v1`

### 3. 已生成正式产物
- checkpoint:
  - `reports/training/streaming_student/checkpoints/streaming_student_stage_step_scaffold_v1.step1.pt`
- 日志:
  - `reports/training/streaming_student/logs/streaming_student_stage_step_scaffold_v1.step1.json`
- markdown:
  - `reports/training/streaming_student/streaming_student_stage_step_scaffold_v1.step1.md`

## 当前单步训练实际做了什么

### train step
- 读取 `target_train` 首个 dry-run batch
- forward Stage3 scaffold
- 计算最小 teacher-supervised loss
- backward
- `clip_grad_norm_`
- `optimizer.step()`

### validation step
- 再读取 `target_validation` 首个 dry-run batch
- 仅 forward + loss
- 不做参数更新

## 当前关键结果

### 训练配置
- `batch_size = 3`
- `learning_rate = 0.001`
- `max_grad_norm = 1.0`
- `use_teacher_confidence = true`

### train step
- `loss_total = 20.612329`
- `loss_teacher_z_art = 8.814978`
- `loss_teacher_event = 5.720385`
- `loss_teacher_event_prior = 5.447319`
- `loss_teacher_energy_proxy = 12.97434`

### validation step
- `loss_total = 14.115878`
- `loss_teacher_z_art = 4.63012`
- `loss_teacher_event = 5.536524`
- `loss_teacher_event_prior = 5.374236`
- `loss_teacher_energy_proxy = 4.587865`

### 梯度
- `grad_norm = 64.267143`

## 当前能说明什么

### 可以说明
- Stage3 训练主干最小闭环已打通:
  - forward
  - loss
  - backward
  - optimizer
  - checkpoint

### 不能说明
- 不能说明:
  - 当前 learning rate 已经稳定
  - 当前 loss 权重已合理
  - 当前监督设计已经适合长期训练

原因:
- 当前只有单步结果，
  还没有多 step 轨迹。

## 当前边界

### 1. checkpoint 是 wiring artifact，不是训练里程碑
- 当前 checkpoint 的价值是:
  - 验证 Stage3 训练产物能落盘
- 不是:
  - 可用于模型选择的正式训练 checkpoint

### 2. 当前仍保持最小化策略
- 仍然保持:
  - `r_res_enabled = false`
  - 不引入 hidden distillation
  - teacher confidence 仅作为 weighting

## 下一步建议
1. 把当前 one-step scaffold
   扩成最小多 step 训练循环。
2. 对:
   - `learning_rate`
   - loss weights
   - grad_norm
   做小规模轨迹观察，
   再决定是否需要调整。
3. 在多 step 稳定前，
   不要同时引入:
   - hidden distillation
   - `r_res`
   - 更多 proxy 头监督

## 一句话结论
- Stage3 现在已经正式进入“训练入口可执行”阶段；
  下一步不该再停留在接线，
  而应进入最小多 step 训练循环与策略稳定化。
