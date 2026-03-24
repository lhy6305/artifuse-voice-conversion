# 325. Stage3 semantic weighting 短程 loop 对比与 proxy audio 导出报告

## 结论
- 本轮完成了：
  1. 修正
     `324`
     首版 semantic weighting
     的 no-op 实现问题
  2. 用同一 subset split
     跑了一组最小
     `on / off`
     4-step Stage3 loop
  3. 跑了对应 checkpoint eval
  4. 已导出
     `target_validation`
     和
     `target_special_eval`
     的 proxy audio
- 当前最重要的判断不是：
  - 语义路线上已经出现明显听感提升
- 当前最重要的判断是：
  - semantic weighting
    现在终于真正进入了损失
  - 而且在同一口径的
    `semantic_disabled_reference`
    下，
    on-checkpoint
    比 off-checkpoint
    有微弱改善

## 一、本轮先修掉的关键问题
- 在准备做
  semantic weighting
  开/关短程对照时，
  发现 `324`
  的首版实现有两个问题：

### 1. override 合并顺序写反
- 现象：
  - `reports/config_overrides/streaming_student_semantic_weighting_disabled.json`
    明明写了：
    - `semantic_supervision.enabled = false`
  - 但 loop summary
    里仍显示：
    - `enabled = true`
- 原因：
  - `resolve_semantic_supervision_config(...)`
    先读 override，
    再读 config，
    导致模板配置把 override
    覆盖回去了
- 处理：
  - 已改成：
    - 默认值
    - config
    - overrides_path
    - overrides
    的顺序

### 2. 首版 semantic weighting 实际接近 no-op
- 现象：
  - 就算 override 生效前后不同，
    只要 batch 内只有一个样本，
    `loss_total`
    轨迹仍然不变
- 原因：
  - 当时把常数 semantic multiplier
    直接乘进了：
    - 每个样本内部已经按分子/分母归一化的
      masked loss
  - 常数会在分子/分母里被抵消
- 处理：
  - 现在改成：
    1. 先算每个样本自己的
       normalized loss
    2. 再对样本级 loss
       做 semantic multiplier
       缩放
  - 同时新增：
    - `loss_total_semantic_disabled_reference`
    用于在不同 semantic 配置之间
    做同口径比较

## 二、本轮代码改动
- 关键修复文件：
  - `src/v5vc/streaming_student/losses.py`
- 当前新增/修正：
  - `resolve_semantic_supervision_config(...)`
    的 override 顺序
  - `masked_*_per_sample(...)`
    一组按样本 loss 计算
  - `reduce_weighted_sample_loss(...)`
  - `loss_total_semantic_disabled_reference`
    指标
- 继续透传：
  - `train_step`
  - `training_loop`
  - `checkpoint_eval`
    都会把
    `semantic_supervision`
    配进来并落盘

## 三、最小对照实验设置

### 1. 关闭 semantic weighting 的 override
- 新增：
  - `reports/config_overrides/streaming_student_semantic_weighting_disabled.json`

### 2. 两条最小短程 loop
- `on`：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --config configs/streaming_student_stage_template.json `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/training/streaming_student_semantic_weighting_on_loop_smoke_fixed `
  --batch-size 1 `
  --validation-batch-size 1 `
  --num-steps 4 `
  --validation-interval 1 `
  --checkpoint-interval 4 `
  --validation-batches 1 `
  --validation-mode full `
  --learning-rate 1e-3 `
  --max-grad-norm 1.0 `
  --experiment-id streaming_student_semantic_weighting_on_loop_smoke_fixed
```
- `off`：
```powershell
.\python.exe manage.py run-streaming-student-training-loop `
  --config configs/streaming_student_stage_template.json `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/training/streaming_student_semantic_weighting_off_loop_smoke_fixed2 `
  --batch-size 1 `
  --validation-batch-size 1 `
  --num-steps 4 `
  --validation-interval 1 `
  --checkpoint-interval 4 `
  --validation-batches 1 `
  --validation-mode full `
  --learning-rate 1e-3 `
  --max-grad-norm 1.0 `
  --experiment-id streaming_student_semantic_weighting_off_loop_smoke_fixed2 `
  --loss-weight-overrides reports/config_overrides/streaming_student_semantic_weighting_disabled.json
```

## 四、对照结果

### 1. train loop 轨迹
- `on`
  的 train loss：
  - step1 `23.375328`
  - step2 `17.282442`
  - step3 `14.499185`
  - step4 `12.930013`
- `off`
  的 train loss：
  - step1 `21.081259`
  - step2 `15.340199`
  - step3 `12.715452`
  - step4 `11.231480`
- 解释：
  - 这是预期内现象
  - 因为 `on`
    把结构化 lexical target
    的样本权重抬高了，
    raw training loss
    理应更重，
    不能直接拿它和 `off`
    的 raw total
    比谁更低

### 2. checkpoint eval 应看同口径参考值
- `on`
  checkpoint eval：
  - `target_validation`
    - `loss_total = 9.591149`
    - `loss_total_semantic_disabled_reference = 9.006555`
  - `target_special_eval`
    - `loss_total = 7.526979`
    - `loss_total_semantic_disabled_reference = 8.423156`
- `off`
  checkpoint eval：
  - `target_validation`
    - `loss_total = 9.037385`
    - `loss_total_semantic_disabled_reference = 9.037385`
  - `target_special_eval`
    - `loss_total = 8.452121`
    - `loss_total_semantic_disabled_reference = 8.452121`

### 3. 当前可比结论
- 若按
  `loss_total`
  比，
  结论会混入
  semantic weighting
  本身的度量口径变化，
  不适合直接比较
- 若按统一口径的
  `loss_total_semantic_disabled_reference`
  比：
  - `target_validation`
    - `on = 9.006555`
    - `off = 9.037385`
    - `on` 微弱更好
  - `target_special_eval`
    - `on = 8.423156`
    - `off = 8.452121`
    - `on` 也微弱更好
- 这说明：
  - 至少在这个极小 subset
    和 4-step horizon
    下，
    semantic weighting
    不是纯负收益
  - 但它现在还只是：
    - 极弱
    - 极早期
    的信号

## 五、proxy audio 已导出

### 1. validation
- `on`：
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_on_validation/semantic_on_val__target__chapter3_3_firefly_162__input.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_on_validation/semantic_on_val__target__chapter3_3_firefly_162__teacher_proxy.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_on_validation/semantic_on_val__target__chapter3_3_firefly_162__student_proxy.wav`
- `off`：
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_off_validation/semantic_off_val__target__chapter3_3_firefly_162__input.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_off_validation/semantic_off_val__target__chapter3_3_firefly_162__teacher_proxy.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_off_validation/semantic_off_val__target__chapter3_3_firefly_162__student_proxy.wav`

### 2. special_eval
- `on`：
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_on_special/semantic_on_special__target__no_text_voice_chapter3_17_firefly_106__input.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_on_special/semantic_on_special__target__no_text_voice_chapter3_17_firefly_106__teacher_proxy.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_on_special/semantic_on_special__target__no_text_voice_chapter3_17_firefly_106__student_proxy.wav`
- `off`：
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_off_special/semantic_off_special__target__no_text_voice_chapter3_17_firefly_106__input.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_off_special/semantic_off_special__target__no_text_voice_chapter3_17_firefly_106__teacher_proxy.wav`
  - `reports/audio/streaming_student_proxy_audio_semantic_weighting_off_special/semantic_off_special__target__no_text_voice_chapter3_17_firefly_106__student_proxy.wav`

### 3. 导出波形差异检查
- 已做快速数值校验，
  `on/off`
  的 student proxy
  不是同一份波形：
  - validation：
    - `l2_rms_diff = 0.00180065`
  - special：
    - `l2_rms_diff = 0.00161462`
- 说明：
  - semantic weighting
    已经不只是日志层变化，
    它确实改变了导出的代理波形

## 六、当前判断
- 这一轮可以先给出一个保守正面判断：
  1. semantic weighting
     现在真的生效了
  2. 在统一参考口径下，
     `on`
     比
     `off`
     有微弱改善
  3. 音频导出已经具备，
     可以开始最小人工听审
- 但不能夸大成：
  - semantic 路线已经证明可听收益成立

## 七、下一步
1. 先听：
   - validation
     `on/off`
   - special
     `on/off`
   这四组 student proxy
2. 同时下一轮实验继续保持最小化：
   - 把短程 loop
     放大到
     更合理的 subset
     或更多 batch 内样本
   - 继续比较
     `semantic_disabled_reference`
3. 如果听感和 reference
   都没有出现坏方向，
   下一步再考虑：
   - semantic warmup schedule
   - 或 utterance-level semantic head
