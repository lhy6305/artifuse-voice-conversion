# 171. Stage3 `proxytemporal20 + warmup6` schedule probe 报告

## 背景
- `docs/170_stage3_baseline48_vs_proxytemporal50_human_review_report.md`
  已确认:
  - `proxytemporal50`
    不是完全无效
  - 但它不足以替代 baseline48
- 当时更合理的下一步
  已收敛到:
  - 更温和的 temporal 权重
  - 更细的 schedule
  - 不直接拉长 horizon

## 本轮目标
1. 先补 Stage3 training loop
   对 loss-weight schedule 的正式支持
2. 再跑一条
   比 `50.0` 更温和的 temporal 候选
3. 判断它是否能:
   - 保留一部分稳定性收益
   - 同时减少 validation 侧副作用

## 本轮新增实现

### 1. training loop 现已支持 loss-weight schedule
- 文件:
  - `src/v5vc/streaming_student/losses.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`

新增能力:
- 从原有
  `--loss-weight-overrides`
  对应的 JSON 中
  额外读取:
  - `loss_weight_schedule`
- 当前已支持:
  - `linear_warmup_hold`

说明:
- 这样不需要新增另一套 CLI 参数
- 现有 override 文件
  仍可继续使用
- 只有在 JSON 中显式写入
  `loss_weight_schedule`
  时，
  training loop
  才会按 step
  动态调整实际权重

### 2. 每一步有效权重现已正式落盘
- training loop summary
- validation history
- checkpoint training metadata
  现在都会记录:
  - 当前 step
    实际生效的 loss weights

## 本轮新增配置
- `configs/streaming_student_loss_weights_proxytemporal20_warmup6_v1.json`

当前配置:
- 最终目标权重:
  - `teacher_proxy_temporal = 20.0`
- schedule:
  - `start_weight = 0.0`
  - `warmup_steps = 6`
  - 类型:
    - `linear_warmup_hold`

对应实际轨迹:
- `step1 = 0`
- `step2 = 4`
- `step3 = 8`
- `step4 = 12`
- `step5 = 16`
- `step6+ = 20`

## 本轮执行

### 1. schedule smoke test
- 执行:

```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --batch-size 2 `
  --validation-batch-size 2 `
  --num-steps 1 `
  --validation-interval 1 `
  --checkpoint-interval 1 `
  --validation-batches 1 `
  --validation-mode sampled `
  --experiment-id streaming_student_stage_loop_proxytemporal20warm6_smoketest_v1 `
  --loss-weight-overrides configs/streaming_student_loss_weights_proxytemporal20_warmup6_v1.json
```

结果:
- 命令通过
- `step1`
  记录到的
  `teacher_proxy_temporal`
  生效权重为:
  - `0.0`

### 2. 正式 12-step full-validation run
- experiment:
  - `streaming_student_stage_loop_proxytemporal20warm6_fullval12_v1`

### 3. checkpoint ranking 与 fuller eval
- best checkpoint:
  - `step12`
- eval 目录:
  - `reports/eval/streaming_student_checkpoint_selection_proxytemporal20warm6_fullval12_v1/`
  - `reports/eval/streaming_student_checkpoint_eval_proxytemporal20warm6_fullval12_v1/`

## 数值结果

### 当前 run 内部 best checkpoint
- `step12`
- `target_validation.loss_total = 8.231539`
- `target_special_eval.loss_total = 8.189151`

### 统一参考权重对照
- baseline12:
  - validation:
    - `8.134648`
  - special:
    - `8.11794`
- `proxytemporal50`:
  - validation:
    - `8.105292`
  - special:
    - `8.107188`
- `proxytemporal20 + warmup6`:
  - validation:
    - `8.131792`
  - special:
    - `8.117062`

### 与 baseline12 的差值
- validation:
  - `8.134648 -> 8.131792`
  - 改善:
    - `-0.002856`
- special:
  - `8.11794 -> 8.117062`
  - 改善:
    - `-0.000878`

### 与 `proxytemporal50` 的差值
- validation:
  - `8.105292 -> 8.131792`
  - 变差:
    - `+0.0265`
- special:
  - `8.107188 -> 8.117062`
  - 变差:
    - `+0.009874`

## 当前判断

### 1. 这条 warmup 线达成了“更温和”
- 它没有像
  `proxytemporal50`
  那样把数值推得那么激进
- 统一参考权重下，
  它几乎贴着 baseline12
  轻微改善

### 2. 但它也没有形成明确的自动指标突破
- 如果只看数值，
  `proxytemporal50`
  仍更强
- 说明:
  - warmup 的确在收副作用
  - 但也一起收掉了
    一部分收益

### 3. 当前最合理的解释
- 这条线不是“已经赢了”
- 更像是:
  - 把 temporal supervision
    从
    “过猛但有信号”
    推到
    “更可控、值得继续人耳核对”

## 本轮后续动作

### 已导出新的试听包
- validation:
  - `reports/audio/streaming_student_proxy_audit_proxytemporal20warm6_step12_v1/`
- special:
  - `reports/audio/streaming_student_proxy_audit_proxytemporal20warm6_step12_special_v1/`

### 已创建新的 A/B 听审会话
- 会话目录:
  - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session/`

启动方式:

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --output-dir reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session
```

## 一句话结论
- 本轮已经把
  Stage3 temporal supervision
  从“只能试固定权重”
  推进到“可做 step-level warmup schedule”；
  第一条温和 schedule 候选
  在自动指标上
  接近 baseline12 且略好于它，
  没有直接赢过
  `proxytemporal50`，
  但已经足够值得进入下一轮
  baseline48 对照复听。
