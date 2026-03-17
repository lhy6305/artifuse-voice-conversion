# 156. Stage3 loss-weight override 与 eventprior025 对照报告

## 背景
- `docs/154_stage3_baseline12_short_run_report.md`
  已经把当前默认短程 baseline
  固定到:
  - `lr = 1e-3`
  - `teacher_confidence = on`
  - default loss weights
- `docs/155_stage3_checkpoint_selection_report.md`
  也已经确认:
  - baseline12 的默认 checkpoint
    先取 `step12`
- 但若继续做 Stage3 loss 权重细化，
  现有实现还缺两件事:
  - 不改源码就能切换 loss weight
  - 跨权重配置时有统一可比口径

## 本轮目标
1. 把 Stage3 loss weight 调整
   改成正式可配置入口。
2. 跑一条最小而明确的权重对照:
   - 只下调 `teacher_event_prior`
3. 明确回答:
   - 这条新配置是否足以替换当前 baseline

## 本轮实际完成

### 1. 新增 Stage3 loss weight override 入口
- 新增 CLI 参数:
  - `--loss-weight-overrides`
- 已接入命令:
  - `.\python.exe manage.py prepare-streaming-student-supervision`
  - `.\python.exe manage.py run-streaming-student-training-step`
  - `.\python.exe manage.py run-streaming-student-training-loop`

### 2. 新增可复现权重配置文件
- 新增配置:
  - `configs/streaming_student_loss_weights_eventprior_light_v1.json`
- 当前 override:
  - `teacher_event_prior = 0.25`

### 3. 新增跨权重统一参考指标
- 当前 loss 输出
  新增:
  - `loss_total_default_reference`

说明:
- `loss_total`
  仍表示:
  - 当前真实训练权重下的有效目标
- `loss_total_default_reference`
  表示:
  - 用默认 Stage3 权重
    回算后的统一参考总 loss
- 后者才适合拿来横向比较
  不同 loss weight 配置

### 4. 已完成 override smoke test
- 执行命令:
  - `.\python.exe manage.py prepare-streaming-student-supervision --batch-size 3 --loss-weight-overrides configs/streaming_student_loss_weights_eventprior_light_v1.json`
  - `.\python.exe manage.py run-streaming-student-training-step --batch-size 3 --experiment-id streaming_student_stage_step_eventprior025_smoketest_v1 --loss-weight-overrides configs/streaming_student_loss_weights_eventprior_light_v1.json`

### 5. 已完成 eventprior025 12-step 对照
- 执行命令:
  - `.\python.exe manage.py run-streaming-student-training-loop --batch-size 3 --validation-batch-size 6 --num-steps 12 --validation-interval 4 --checkpoint-interval 4 --validation-batches 4 --experiment-id streaming_student_stage_loop_eventprior025_v1 --loss-weight-overrides configs/streaming_student_loss_weights_eventprior_light_v1.json`

### 6. 已完成 fuller ranking 与 best checkpoint eval
- 执行命令:
  - `.\python.exe manage.py select-streaming-student-best-checkpoint --checkpoints reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step4.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step8.pt reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_selection_eventprior025_v1`
  - `.\python.exe manage.py evaluate-streaming-student-checkpoint --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt --batch-size 6 --output-dir reports/eval/streaming_student_checkpoint_eval_eventprior025_v1`

## 已生成正式产物
- loop summary:
  - `reports/training/streaming_student_loop/streaming_student_stage_loop_eventprior025_v1.summary.md`
- checkpoints:
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step4.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step8.pt`
  - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt`
- fuller ranking:
  - `reports/eval/streaming_student_checkpoint_selection_eventprior025_v1/streaming_student_checkpoint_selection.md`
- best checkpoint fuller eval:
  - `reports/eval/streaming_student_checkpoint_eval_eventprior025_v1/streaming_student_stage_loop_eventprior025_v1.checkpoint_eval.md`

## eventprior025 当前轨迹

### train effective loss_total
- `step1 = 19.2505`
- `step4 = 9.459835`
- `step8 = 7.566546`
- `step12 = 6.985175`

### grad_norm
- `step1 = 64.24408`
- `step4 = 12.829979`
- `step8 = 7.146733`
- `step12 = 4.958564`

### sampled validation effective loss_total
- `step4 = 8.713638`
- `step8 = 7.703854`
- `step12 = 6.886201`

## eventprior025 内部 ranking 结果

### 第 1 名
- `step12`
- `target_validation.loss_total = 6.919654`
- `target_special_eval.loss_total = 6.845759`

### 第 2 名
- `step8`
- `target_validation.loss_total = 7.667545`
- `target_special_eval.loss_total = 7.188635`

### 第 3 名
- `step4`
- `target_validation.loss_total = 8.651326`
- `target_special_eval.loss_total = 7.825405`

说明:
- 在同一套权重配置内部，
  `step12`
  依然是最好的 checkpoint。

## 与 baseline12 的 apples-to-apples 对照

### 先说一个重要前提
- 不同权重配置之间，
  不能直接比较:
  - `loss_total`
- 因为:
  - `eventprior025`
    本身就把
    `teacher_event_prior`
    权重减半了
- 所以横向对照
  必须看:
  - `loss_total_default_reference`
  - 或各项未加权 component loss

### `step12` fuller eval 的统一参考对照
- baseline12:
  - validation `loss_total_default_reference = 8.134648`
  - special `loss_total_default_reference = 8.11794`
- eventprior025:
  - validation `loss_total_default_reference = 8.150748`
  - special `loss_total_default_reference = 8.115334`

### 直接差值
- validation:
  - `8.134648 -> 8.150748`
  - `+0.0161`
- special:
  - `8.11794 -> 8.115334`
  - `-0.002606`

解释:
- 在统一参考权重下，
  `eventprior025`
  并没有明确超过 baseline12
- 当前更接近的结论是:
  - validation 近乎持平但略差
  - special 近乎持平但略好

## component loss 观察

### validation `step12`
- 更好:
  - `teacher_z_art: 0.060773 -> 0.057108`
  - `teacher_energy_proxy: 2.689745 -> 2.650425`
  - `teacher_vuv_proxy: 0.710879 -> 0.707799`
  - `log_f0_correction_l1: 0.134852 -> 0.128517`
  - `aper_correction_l1: 0.08256 -> 0.071296`
- 略差:
  - `teacher_event: 4.851663 -> 4.853921`
  - `teacher_event_prior: 4.869763 -> 4.924376`
  - `teacher_aper_proxy: 0.060887 -> 0.067569`

### special `step12`
- 更好:
  - `teacher_z_art: 0.068649 -> 0.064556`
  - `teacher_energy_proxy: 1.358571 -> 1.33662`
  - `aper_correction_l1: 0.048218 -> 0.038044`
- 略差:
  - `teacher_event: 5.060087 -> 5.063036`
  - `teacher_event_prior: 5.073026 -> 5.078302`
  - `teacher_vuv_proxy: 0.720992 -> 0.722284`
  - `teacher_aper_proxy: 0.038817 -> 0.050166`
  - `log_f0_correction_l1: 0.053636 -> 0.069707`

更准确地说:
- `eventprior025`
  更像是在:
  - 维持 event 主体大致不变的同时
  - 稍微换了一些 proxy 项之间的平衡
- 目前还看不出
  它已经形成了
  明显更强的统一优势

## 当前结论

### 可以下结论的部分
- Stage3 loss weight sweep
  现在已经具备:
  - 正式 CLI 入口
  - 配置文件复现能力
  - checkpoint / summary 路径追踪
  - 统一参考权重指标
- `eventprior025`
  在它自己的有效训练目标下
  学得更快，
  且内部 best checkpoint
  同样落在 `step12`

### 不能下结论的部分
- 不能因为
  `eventprior025`
  的有效 `loss_total`
  更低，
  就认定它已经优于 baseline12
- 目前按统一参考权重看，
  它与 baseline12
  更接近:
  - 基本打平
  - validation 略差
  - special 略好

## 下一步建议
1. 当前默认 baseline
   仍先保留:
   - baseline12 `step12`
2. 下一轮若继续做权重 sweep，
   必须统一按:
   - `loss_total_default_reference`
   做横向判断
3. 更值得继续试的下一组动作
   已收敛到:
   - 让 `eventprior025`
     再走更长一点 horizon
   - 或追加一个
     `energy_proxy` 更轻的近邻配置
4. 在统一参考口径下，
   再决定是否真的替换默认 baseline

## 一句话结论
- 本轮真正完成的是
  “把 Stage3 loss 权重调参变成可配置、可追踪、可横向比较的流程”；
  `eventprior025`
  目前是一个接近 baseline 的候选，
  但还不足以直接替换当前默认 baseline。
