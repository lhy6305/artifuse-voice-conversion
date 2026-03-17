# 173. Stage3 baseline48 默认参数重跑复现确认报告

## 背景
- 在 `docs/172_stage3_proxy_silence_leakage_audit_and_export_fix_report.md`
  之后，
  已确认:
  - proxy 导出链里
    确实存在过
    静音伪底噪
  - 但 warm temporal 候选
    仍保留了
    模型级静音过活跃
- 用户因此提出:
  - 既然问题已经固化到模型上，
    且重训成本不高，
    是否直接按默认参数
    重新跑一遍正式 baseline

## 本次执行
- 训练命令:

```powershell
.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 48 --validation-interval 12 --checkpoint-interval 12 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_baseline48_fullval_rerun_v1
```

- 补充执行:

```powershell
.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step12.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step24.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step36.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step48.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_baseline48_fullval_rerun_v1

.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step48.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_baseline48_fullval_rerun_v1
```

## 产物
- 训练 summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_baseline48_fullval_rerun_v1.summary.md`
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_baseline48_fullval_rerun_v1.summary.json`
- checkpoint:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step12.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step24.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step36.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_rerun_v1.step48.pt`
- checkpoint selection:
  - `reports/eval/streaming_student_checkpoint_selection_baseline48_fullval_rerun_v1/streaming_student_checkpoint_selection.json`
- final checkpoint eval:
  - `reports/eval/streaming_student_checkpoint_eval_baseline48_fullval_rerun_v1/streaming_student_stage_loop_baseline48_fullval_rerun_v1.checkpoint_eval.json`

## 结果
### 1. 训练轨迹与原始 `baseline48_fullval_v1` 完全对齐
- `step_history`
  的条目数一致，
  每步 `record_ids`
  一致，
  每步 `loss_total`
  一致
- `validation_history`
  的条目数一致，
  每次 full-validation
  的 `sampled_record_ids`
  一致，
  每次 `loss_total`
  一致

### 2. rerun 的 checkpoint selection 结果与原始 run 完全一致
- 原始 run:
  - best = `step48`
  - `target_validation_loss_total = 7.141462`
  - `target_special_eval_loss_total = 7.572382`
- rerun:
  - best = `step48`
  - `target_validation_loss_total = 7.141462`
  - `target_special_eval_loss_total = 7.572382`

### 3. rerun 的 final checkpoint eval 与原始 run 完全一致
- 原始 run `step48`:
  - `target_validation loss_total = 7.141462`
  - `target_special_eval loss_total = 7.572382`
- rerun `step48`:
  - `target_validation loss_total = 7.141462`
  - `target_special_eval loss_total = 7.572382`

### 4. checkpoint 文件哈希不同，但模型内容层完全一致
- 直接比较 `.pt`
  文件的 `SHA256`
  时，
  原始 run 与 rerun
  的四个 checkpoint
  哈希都不同
- 进一步按内容拆开后确认:
  - `model_state_dict`
    键集合一致
  - 所有 tensor
    逐元素完全一致
  - `global_step`
    一致
  - 差异主要来自:
    - `experiment_id`
    - 以及随 run 名称变化的
      metadata

## 判断
- 这次“按默认参数直接重跑”
  已经执行完成
- 它提供的不是
  新模型候选，
  而是一次
  复现确认
- 结论是:
  - 当前 Stage3 baseline48
    在现有固定 seed /
    固定数据顺序 /
    固定配置下
    是稳定可复现的
  - 仅靠“同参再跑一遍”
    不会自然解决
    warm 路线上暴露出的
    静音稳定性问题

## 对下一步的意义
- 不需要把这次 rerun
  作为新的默认 checkpoint
- 当前默认 Stage3 checkpoint
  仍保持:
  - `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
- 如果下一步要继续训练，
  题目应明确转到:
  - 静音稳定性 / 静音抑制
  - 或更局部化的 temporal 监督约束
- 不再建议继续做
  “同一默认参数再 rerun 一次”
  这种低信息量动作
