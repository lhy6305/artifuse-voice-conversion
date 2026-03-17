# 153. Stage3 短程稳定化对照报告

## 背景
- `docs/152_stage3_training_loop_scaffold_report.md`
  已经证明:
  - Stage3 最小多 step loop 可执行
- 但下一步不能盲目继续放大，
  必须先回答两个更具体的问题:
  - `teacher_confidence` 该不该保留
  - 当前 `learning_rate` 是否要立刻下调

## 本轮目标
- 只做短程对照，
  不扩结构。
- 用可比的 `4 step` loop
  比较:
  - baseline
  - no confidence
  - lower lr

## 本轮实际完成

### 1. 三组短程 loop
- baseline:
  - `streaming_student_stage_loop_scaffold_v2`
  - `lr = 1e-3`
  - `teacher_confidence = on`
- no confidence:
  - `streaming_student_stage_loop_no_conf_v2`
  - `lr = 1e-3`
  - `teacher_confidence = off`
- lower lr:
  - `streaming_student_stage_loop_lr3e4_v2`
  - `lr = 3e-4`
  - `teacher_confidence = on`

### 2. 新增 fuller checkpoint eval 入口
- 新增命令:
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint`

### 3. 修正两类评估陷阱
- checkpoint 现在会保存:
  - `config_path`
  - `training.use_teacher_confidence`
  - `training.loss_weights`
- fuller eval 不再回绕重复样本

## 短程 loop 轨迹对比

### baseline
- `train loss_total`
  - `20.612329 -> 14.973147 -> 12.068747 -> 10.774693`
- `grad_norm`
  - `64.267143 -> 35.93412 -> 21.220259 -> 13.034104`

### no confidence
- `train loss_total`
  - `20.899107 -> 15.594548 -> 12.634779 -> 11.420456`
- `grad_norm`
  - `62.064243 -> 34.331001 -> 20.784277 -> 13.505103`

### lower lr
- `train loss_total`
  - `20.612329 -> 18.587992 -> 16.433231 -> 15.229719`
- `grad_norm`
  - `64.267143 -> 55.542522 -> 45.96698 -> 38.657425`

## fuller checkpoint eval 结果

### target_validation
- baseline:
  - `loss_total = 9.94085`
- no confidence:
  - `loss_total = 10.533068`
- lower lr:
  - `loss_total = 13.962363`

### target_special_eval
- baseline:
  - `loss_total = 9.144604`
- no confidence:
  - `loss_total = 9.372594`
- lower lr:
  - `loss_total = 12.267866`

## 当前结论

### 1. baseline 仍是当前默认短程配置
- 在:
  - `target_validation`
  - `target_special_eval`
  两个 fuller slice 上，
  baseline 都优于另外两组。

### 2. `teacher_confidence` 当前值得保留
- 关闭后并没有换来更好的 fuller eval，
  反而:
  - validation 更差
  - special 更差
- 所以当前不建议把它先关掉。

### 3. `3e-4` 对当前短程 horizon 太慢
- 这组的 train loss、
  grad_norm、
  fuller eval
  都明显落后。
- 当前没有看到足够理由
  立即把默认 lr 切低。

## 当前边界

### 1. 这仍是短程结论，不是长程训练结论
- 当前只观察了:
  - `4 step`
  - 最小 loop
- 不能外推成
  长程训练最终一定同样排序。

### 2. fuller checkpoint eval 仍然是 teacher-supervised proxy loss
- 它比 sampled validation 更可靠，
  但仍不是:
  - 听感结论
  - 最终用户质量结论

## 下一步建议
1. 继续以 baseline:
   - `lr = 1e-3`
   - `teacher_confidence = on`
   作为默认短程训练配置。
2. 下一轮优先调:
   - loss 权重
   - validation 口径
   - 更长一点的短程 horizon
3. 暂不优先再做:
   - `teacher_confidence off`
   - `lr = 3e-4`
   这两条路线

## 一句话结论
- 当前 Stage3 短程稳定化已经把默认方向收窄到:
  - 保留 `teacher_confidence`
  - 保留 `lr = 1e-3`
  然后继续做更长一点的短程训练与 loss 权重细化。
