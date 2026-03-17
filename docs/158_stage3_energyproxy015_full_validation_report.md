# 158. Stage3 energyproxy015 full-validation 对照报告

## 背景
- `docs/157_stage3_full_validation_loop_report.md`
  已把 Stage3 loop 内 validation
  升级为可选:
  - `validation_mode = full`
- 这让后续 loss weight sweep
  可以直接在 loop 内
  看到完整 `target_validation`
  轨迹，
  不必先依赖 sampled subset

## 本轮目标
- 基于当前 full-validation loop
  继续做一轮轻量 loss weight 对照
- 只调整:
  - `teacher_energy_proxy`
- 其余权重保持默认，
  观察:
  - 短程训练轨迹
  - full validation
  - 与 baseline12 的统一参考比较

## 本轮实际改动

### 1. 新增 loss weight 配置
- 新增:
  - `configs/streaming_student_loss_weights_energyproxy_light_v1.json`
- 内容:
  - `teacher_energy_proxy`
    从:
    - `0.25`
    调为:
    - `0.15`

### 2. 已完成 smoke test
- 执行:
  - `.\python.exe manage.py prepare-streaming-student-supervision --batch-size 3 --loss-weight-overrides configs/streaming_student_loss_weights_energyproxy_light_v1.json`
- 目的:
  - 确认新权重覆盖
    可被 supervision pipeline
    正常读取

### 3. 已完成 12-step full-validation run
- 执行:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 12 --validation-interval 4 --checkpoint-interval 4 --validation-batches 4 --validation-mode full --experiment-id streaming_student_stage_loop_energyproxy015_fullval_v1 --loss-weight-overrides configs/streaming_student_loss_weights_energyproxy_light_v1.json`

### 4. 已完成 checkpoint ranking
- 执行:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step4.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step8.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step12.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_energyproxy015_fullval_v1`

### 5. 已完成 best checkpoint 外部 eval
- 执行:
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step12.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_energyproxy015_fullval_v1`

## 已生成正式产物
- loop summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_energyproxy015_fullval_v1.summary.md`
- step logs:
  - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_energyproxy015_fullval_v1.step*.json`
- checkpoints:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step4.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step8.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_energyproxy015_fullval_v1.step12.pt`
- checkpoint ranking:
  - `reports/eval/streaming_student_checkpoint_selection_energyproxy015_fullval_v1/streaming_student_checkpoint_selection.md`
- checkpoint eval:
  - `reports/eval/streaming_student_checkpoint_eval_energyproxy015_fullval_v1/streaming_student_stage_loop_energyproxy015_fullval_v1.checkpoint_eval.md`

## 本轮结果

### 训练轨迹
- `loss_total`
  从:
  - `19.314896`
  降到:
  - `7.954313`
- `loss_total_default_reference`
  从:
  - `20.612329`
  降到:
  - `8.263741`
- `grad_norm`
  从:
  - `62.632622`
  降到:
  - `3.887995`

说明:
- 训练过程本身稳定，
  没有出现短程发散迹象

### loop 内 full validation
- `step4`
  - `loss_total = 9.405372`
  - `loss_total_default_reference = 10.037295`
- `step8`
  - `loss_total = 8.459062`
  - `loss_total_default_reference = 8.92416`
- `step12`
  - `loss_total = 7.8875`
  - `loss_total_default_reference = 8.17354`

### checkpoint ranking
- 当前 ranking:
  - `step12`
  - `step8`
  - `step4`
- 说明:
  - 当前短程 run
    仍然是越往后越好，
    没有出现早停型反转

### best checkpoint 外部 eval
- `step12`
  的外部 eval 为:
  - `target_validation.loss_total = 7.8875`
  - `target_validation.loss_total_default_reference = 8.17354`
  - `target_special_eval.loss_total = 8.019549`
  - `target_special_eval.loss_total_default_reference = 8.164811`

## 与 baseline12_fullval_v1 的对照

### baseline12_fullval_v1 参考值
- `target_validation.loss_total_default_reference`
  - `8.134648`
- `target_special_eval.loss_total_default_reference`
  - `8.11794`

### energyproxy015_fullval_v1 对照值
- `target_validation.loss_total_default_reference`
  - `8.17354`
- `target_special_eval.loss_total_default_reference`
  - `8.164811`

### 差值
- 相比 baseline，
  `energyproxy015`
  在统一参考权重下:
  - `target_validation`
    变差:
    - `+0.038892`
  - `target_special_eval`
    变差:
    - `+0.046871`

## 当前最重要的结论

### 1. 只看当前 run 自己的 `loss_total`
   会显得更好，
   但这不代表它赢过 baseline
- 因为本轮直接把:
  - `teacher_energy_proxy`
    权重
    从 `0.25`
    降到了 `0.15`
- 所以:
  - 有效目标函数
    本来就会变小
- 因此:
  - `loss_total`
    下降更快
  - 不能直接解释成
    模型更优

### 2. 用统一参考权重比较时，
   `energyproxy015`
   没有超过 baseline12
- 当前最应该看的不是:
  - 覆盖后权重下的 `loss_total`
- 而是:
  - `loss_total_default_reference`
- 在这个统一标尺下，
  `energyproxy015`
  略差于:
  - `baseline12_fullval_v1`

### 3. `teacher_energy_proxy = 0.15`
   目前不能升级成默认基线
- 它可以保留为:
  - 一条已验证、可复现的候选分支
- 但当前结果不足以支持:
  - 替换默认 baseline

## 当前解释
- `teacher_energy_proxy`
  在短程训练里
  确实占有一定 loss mass，
  所以下调权重后
  训练目标会更轻
- 但目前看来，
  这部分约束并没有“轻一点就更好”
- 至少在当前:
  - 12-step
  - full validation
  - teacher confidence on
  的设定下，
  它更像是:
  - 让优化目标更容易看起来下降
  - 但没有换来更好的统一参考指标

## 下一步建议
1. 默认 full-validation baseline
   继续保留:
   - `streaming_student_stage_loop_baseline12_fullval_v1.step12.pt`
2. 如果下一轮还做权重 sweep，
   优先继续:
   - `eventprior025`
     更长一点 horizon
   - 或只在更长 horizon
     再观察 `energyproxy015`
3. 之后凡是 loss 权重不同的 run，
   正式比较时都优先看:
   - `loss_total_default_reference`
   - 以及各项未加权 component loss

## 一句话结论
- `teacher_energy_proxy`
  从 `0.25`
  降到 `0.15`
  后，
  当前 short-horizon full-validation run
  仍然稳定，
  但在统一参考权重下
  并没有赢过 baseline12；
  所以它是一个有效对照，
  不是新的默认方向。
