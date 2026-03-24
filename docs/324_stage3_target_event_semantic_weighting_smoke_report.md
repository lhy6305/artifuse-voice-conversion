# 324. Stage3 `target_event_semantic_sidecar` 第一版 semantic weighting 接线与 smoke 报告

## 结论
- 本轮没有加新的
  semantic head，
  而是先完成了更保守、可回滚的第一步：
  - 用
    `target_event_semantic_sidecar`
    对
    Stage3
    现有
    teacher-supervised loss
    做按样本语义重配
- 当前第一版只作用于：
  - `teacher_event_prior`
  - `teacher_event`
  - `teacher_z_art`
- 当前第一版不作用于：
  - `teacher_energy_proxy`
  - `teacher_vuv_proxy`
  - `teacher_aper_proxy`
  - `teacher_proxy_acoustic`
  - `teacher_proxy_temporal`
- 最小 smoke
  已证明三件事：
  1. semantic weighting
     确实进了 loss
  2. semantic 配置已写入 checkpoint
  3. checkpoint eval
     会按 checkpoint 中同一配置复现

## 一、为什么先做“weighting”而不是新 head
- 当前
  `target_event_semantic_sidecar`
  只具备：
  - target-side
    lexical / punctuation / clause / structure
    语义
- 它仍不具备：
  - phone
  - manner
  - place
  - forced alignment
- 因此现在最安全的第一步不是：
  - 直接引入新的 frame semantic head
- 而是：
  - 只让这份 sidecar
    影响
    “哪些样本更值得强调”
    这一层

## 二、本轮代码改动

### 1. `losses.py` 新增 semantic supervision 配置与样本级权重重配
- 更新：
  - `src/v5vc/streaming_student/losses.py`
- 新增：
  - `build_default_semantic_supervision_config()`
  - `resolve_semantic_supervision_config(...)`
  - `build_semantic_loss_multipliers(...)`
- 当前策略：
  - 仅当：
    - `semantic_contract_version == target_event_semantic_sidecar_v1`
    - 且 `semantic_supervision.enabled = true`
  - 才启用语义重配
- 语义加权信号来源：
  - `clean_text_available`
  - `utterance_structure_type`
  - `clause_count`
  - `pause_boundary_count`
  - `terminal_boundary_count`
  - `nonverbal_only`
- 当前默认参数：
  - `clean_text_bonus = 0.08`
  - `multi_clause_bonus = 0.08`
  - `multi_terminal_bonus = 0.10`
  - `clause_ge4_bonus = 0.08`
  - `pause_multi_bonus = 0.05`
  - `terminal_present_bonus = 0.05`
  - `nonverbal_penalty = 0.20`
  - `min_multiplier = 0.75`
  - `max_multiplier = 1.45`
  - `event_prior_alpha = 1.0`
  - `event_alpha = 0.35`
  - `z_art_alpha = 0.20`

### 2. 当前只重配三类 loss
- 当前行为：
  - `teacher_event_prior`
    直接乘：
    - `semantic_base_multiplier`
  - `teacher_event`
    乘：
    - `1 + (semantic_base_multiplier - 1) * event_alpha`
  - `teacher_z_art`
    乘：
    - `1 + (semantic_base_multiplier - 1) * z_art_alpha`
- 这样做的原因是：
  - 当前 sidecar
    真正可信的是
    utterance structure
  - 还不足以直接声明：
    - `vuv`
    - `aper`
    - `energy`
    的 phonetic / acoustic semantic
    已有更高置信标签

### 3. 训练 / 评估入口已统一接线并持久化
- 更新：
  - `src/v5vc/streaming_student/supervision_entry.py`
  - `src/v5vc/streaming_student/train_step_entry.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `src/v5vc/streaming_student/checkpoint_eval_entry.py`
- 当前行为：
  - supervision dry-run
    会显式写出：
    - `semantic_supervision`
  - train step / training loop
    会把：
    - `semantic_supervision`
    写进 checkpoint 的
    `training`
    段
  - checkpoint eval
    会优先从 checkpoint
    里的
    `training.semantic_supervision`
    复现同一口径

### 4. Stage3 模板配置已默认打开第一版 semantic weighting
- 更新：
  - `configs/streaming_student_stage_template.json`
- 当前默认：
  - `semantic_supervision.enabled = true`

## 三、验证

### 1. 编译验证
- 已执行：
  - `py_compile`
- 覆盖：
  - `src/v5vc/streaming_student/losses.py`
  - `src/v5vc/streaming_student/supervision_entry.py`
  - `src/v5vc/streaming_student/train_step_entry.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `src/v5vc/streaming_student/checkpoint_eval_entry.py`
- 结果：
  - `py_compile_ok`

### 2. supervision smoke
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-supervision `
  --config configs/streaming_student_stage_template.json `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/plans/streaming_student_supervision_semantic_weighting_smoke `
  --batch-size 1
```
- 关键结果：
  - `target_train`
    - `semantic_base_multiplier_mean = 1.36`
    - `semantic_event_prior_multiplier_mean = 1.36`
    - `semantic_event_multiplier_mean = 1.126`
    - `semantic_z_art_multiplier_mean = 1.072`
  - `target_validation`
    - `semantic_base_multiplier_mean = 1.13`
    - `semantic_event_prior_multiplier_mean = 1.13`
    - `semantic_event_multiplier_mean = 1.0455`
    - `semantic_z_art_multiplier_mean = 1.026`
  - `target_special_eval`
    - `semantic_base_multiplier_mean = 0.8`
    - `semantic_event_prior_multiplier_mean = 0.8`
    - `semantic_event_multiplier_mean = 0.93`
    - `semantic_z_art_multiplier_mean = 0.96`
- 解释：
  - lexical / structured
    target
    被温和上调
  - nonverbal
    special_eval
    被温和下调

### 3. training step smoke
- 已执行：
```powershell
.\python.exe manage.py run-streaming-student-training-step `
  --config configs/streaming_student_stage_template.json `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/training/streaming_student_semantic_weighting_smoke `
  --batch-size 1 `
  --learning-rate 1e-3 `
  --max-grad-norm 1.0 `
  --experiment-id streaming_student_semantic_weighting_smoke
```
- 关键结果：
  - checkpoint 已生成：
    - `reports/training/streaming_student_semantic_weighting_smoke/checkpoints/streaming_student_semantic_weighting_smoke.step1.pt`
  - checkpoint 对应 step log
    已写出：
    - `training.semantic_supervision`
  - `train_step.loss_metrics`
    中也可看到：
    - `semantic_supervision_enabled = true`
    - `semantic_base_multiplier_mean = 1.36`

### 4. checkpoint eval smoke
- 已执行：
```powershell
.\python.exe manage.py evaluate-streaming-student-checkpoint `
  --checkpoint reports/training/streaming_student_semantic_weighting_smoke/checkpoints/streaming_student_semantic_weighting_smoke.step1.pt `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/eval/streaming_student_checkpoint_eval_semantic_weighting_smoke `
  --batch-size 1
```
- 关键结果：
  - checkpoint eval
    摘要里已成功复现：
    - `training.semantic_supervision`
  - `target_validation`
    仍然显示：
    - `semantic_base_multiplier_mean = 1.13`
  - `target_special_eval`
    仍然显示：
    - `semantic_base_multiplier_mean = 0.8`
- 说明：
  - 评估口径现在不会因为重新读模板或遗漏配置
    而漂移

## 四、当前判断
- 这一步已经证明：
  1. semantic sidecar
     已不只是“存在于 batch 里”
  2. 它已经能真实改变
     Stage3 loss
  3. 而且这种改变
     已能跨：
     - supervision dry-run
     - train step
     - checkpoint eval
     保持一致
- 这一步还没有证明：
  1. 这种 weighting
     一定会带来更好听感
  2. 它已经等价于真正的 semantic auxiliary head

## 五、下一步
1. 先不要急着加新 semantic head。
2. 下一步更合理的是：
   - 先跑一个很短的
     Stage3 training loop
     对比：
     - semantic weighting 开
     - semantic weighting 关
3. 如果短程轨迹显示：
   - weighting 稳定
   - validation / special_eval
     口径可解释
   再决定是否加：
   - utterance-level semantic auxiliary head
   - 或 semantic warmup schedule

## 六、更正
- 2026-03-24
  后续在
  `325`
  中已确认：
  - 本报告对应的首版实现
    虽然完成了
    `semantic_supervision`
    的配置透传、
    checkpoint 持久化、
    checkpoint eval 复现
  - 但当时把常数 multiplier
    直接乘进了
    “按样本内部归一化”的
    masked loss
    里，
    会被分子/分母抵消，
    因而实际接近
    no-op
- 因此：
  - `324`
    主要应被视为：
    - semantic weighting
      wiring smoke
  - 真正“会改变损失”的
    修正版结果，
    以后续
    `325`
    为准
