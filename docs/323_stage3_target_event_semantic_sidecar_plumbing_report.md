# 323. Stage3 `target_event_semantic_sidecar` 接线与最小闭环 smoke 报告

## 结论
- 本轮已把
  `target_event_semantic_sidecar`
  从 bootstrap 资产，
  真正接入
  Stage3 的：
  - teacher-label export
  - training-data contract
  - supervision dry-run
  - calibration/tagging
  - scaffold plan / offline_mvp training plan
- 当前完成的是：
  - 资产透传
  - 语义摘要
  - 旧 checkpoint 兼容消费
- 当前还没有做的是：
  - 基于这份 sidecar
    新增 semantic loss
    或 target-side 监督权重策略

## 一、本轮要解决的具体问题
- 上一轮
  `322`
  已经把：
  - `target_event_semantic_sidecar`
    生成出来
- 但它仍只是
  data artifact，
  还没有进入
  Stage3 真正会读的链路。
- 如果只停在这一步，
  后面仍会出现两个问题：
  1. teacher-label export
     继续只知道
     `weak_event_hints`
     和
     `target_special_supervision`
  2. Stage3
     training-data /
     supervision /
     calibration
     仍不会显式知道
     semantic sidecar
     已存在

## 二、本轮代码改动

### 1. `offline_mvp.data` 新增通用 semantic sidecar 工具
- 更新：
  - `src/v5vc/offline_mvp/data.py`
- 新增：
  - `load_target_event_semantic_sidecar_map(...)`
  - `attach_target_event_semantic_sidecar(...)`
  - `infer_target_event_semantic_sidecar_path(...)`
  - `build_record_semantic_overview(...)`
- 当前作用：
  - 为
    `offline_mvp`
    与
    `streaming_student`
    提供统一的：
    - sidecar 读取
    - sidecar 挂载
    - 从 `split_dir`
      推断默认 sidecar 路径
    - 从 record
      统一抽取：
      `semantic_contract_version /
      inventory_status /
      label_status /
      utterance_structure /
      final_terminal /
      clause / pause / terminal`

### 2. Stage3 数据层已真正透传 semantic sidecar
- 更新：
  - `src/v5vc/streaming_student/data.py`
- 当前行为：
  - `StreamingStudentTargetExample`
    新增：
    - `target_event_semantic_sidecar`
  - `attach_sidecars_if_available(...)`
    会优先读取配置中的：
    - `target_event_semantic_sidecar_path`
  - 若配置未写，
    则按：
    - `split_dir/../../target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl`
    做确定性推断
  - `collate_streaming_student_batch(...)`
    已把：
    - `target_event_semantic_sidecar`
    放进 batch

### 3. teacher-label export 已能消费并摘要 semantic sidecar
- 更新：
  - `src/v5vc/streaming_student/teacher_labels.py`
- 当前行为：
  - `load_target_records_by_split(...)`
    会读取：
    - checkpoint config
      里的
      `target_event_semantic_sidecar_path`
    - 若旧 checkpoint
      没有这个字段，
      则回退到
      `split_dir`
      推断
  - 每条导出的
    teacher-label index row
    现在都会额外写出：
    - `semantic_source`
    - `semantic_contract_version`
    - `semantic_label_space_version`
    - `semantic_inventory_status`
    - `semantic_label_status`
    - `semantic_utterance_structure_type`
    - `semantic_final_terminal_type`
  - summary json / md
    现在会额外统计：
    - `semantic_contract_version_counts`
    - `semantic_inventory_status_counts`
    - `semantic_label_status_counts`
    - `semantic_utterance_structure_type_counts`
    - `semantic_final_terminal_type_counts`

### 4. Stage3 plan / calibration / training-data / supervision 已知晓 semantic sidecar
- 更新：
  - `src/v5vc/streaming_student/plan_entry.py`
  - `src/v5vc/streaming_student/calibration_assets.py`
  - `src/v5vc/streaming_student/training_data_entry.py`
  - `src/v5vc/streaming_student/supervision_entry.py`
  - `configs/streaming_student_stage_template.json`
- 当前行为：
  - plan
    会显式落盘：
    - `target_event_semantic_sidecar_path`
  - calibration
    在打标时会优先消费：
    - `target_event_semantic_sidecar`
    再回退到：
    - `weak_event_hints`
  - Stage3 training-data
    dry-run summary
    会显式列出：
    - `available_target_sidecars`
    - `semantic_sidecar_summary`
  - Stage3 supervision
    dry-run summary
    也会显式列出：
    - `semantic_sidecar_summary`

### 5. future offline_mvp checkpoint 现在也能带上这条路径
- 更新：
  - `src/v5vc/train_entry.py`
- 当前行为：
  - 若 config
    写了
    `target_event_semantic_sidecar_path`
    或能从 `split_dir`
    推断出来，
    offline_mvp training plan
    现在也会落盘这条路径，
    并把 sidecar
    挂到 target records
  - 这样后续新 checkpoint
    的 config
    不会继续对这条资产失明

## 三、验证

### 1. 编译验证
- 已执行：
  - `py_compile`
- 覆盖文件：
  - `src/v5vc/offline_mvp/data.py`
  - `src/v5vc/streaming_student/data.py`
  - `src/v5vc/streaming_student/teacher_labels.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `src/v5vc/streaming_student/calibration_assets.py`
  - `src/v5vc/streaming_student/training_data_entry.py`
  - `src/v5vc/streaming_student/supervision_entry.py`
  - `src/v5vc/train_entry.py`
- 结果：
  - `py_compile_ok`

### 2. teacher-label export 最小 smoke
- 已执行：
```powershell
.\python.exe manage.py build-streaming-student-teacher-labels `
  --data-output-dir data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke `
  --report-output-dir reports/data/streaming_student_teacher_labels_semantic_smoke `
  --batch-size 1 `
  --max-records-per-slice 1
```
- 关键结果：
  - `record_count = 3`
  - 三个 slice
    都已识别到：
    - `semantic_contract_version = target_event_semantic_sidecar_v1`
    - `semantic_inventory_status = matched_inventory`
    - `semantic_label_status = pending_upgrade`
- 机器可读摘要：
  - `reports/data/streaming_student_teacher_labels_semantic_smoke/streaming_student_teacher_label_summary.json`
- markdown 摘要：
  - `reports/data/streaming_student_teacher_labels_semantic_smoke/streaming_student_teacher_label_summary.md`

### 3. Stage3 training-data / supervision 最小 smoke
- 因为上一步 teacher-label
  只导出了每个 slice
  1 条记录，
  而
  Stage3 training-data /
  supervision
  既有契约默认要求：
  - teacher-label index
    覆盖整个 split
- 所以本轮额外构造了：
  - `data_prep/round1_1/splits/semantic_smoke_subset/`
  这个仅用于 smoke
  的最小 subset split，
  让 split
  与 teacher-label index
  对齐。
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-training-data `
  --config configs/streaming_student_stage_template.json `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/plans/streaming_student_training_data_semantic_smoke `
  --batch-size 1
```
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-supervision `
  --config configs/streaming_student_stage_template.json `
  --teacher-label-index data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl `
  --calibration-asset data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json `
  --split-dir data_prep/round1_1/splits/semantic_smoke_subset `
  --output-dir reports/plans/streaming_student_supervision_semantic_smoke `
  --batch-size 1
```
- 关键结果：
  - `training_data`
    summary
    已明确写出：
    - `available_target_sidecars`
      包含
      `target_event_semantic_sidecar`
    - 每个 slice
      的
      `semantic_sidecar_summary.present_count = 1`
    - `semantic_contract_version_counts = {'target_event_semantic_sidecar_v1': 1}`
  - `supervision`
    summary
    也已明确写出：
    - 每个 slice
      的
      `semantic_sidecar_summary.present_count = 1`
    - `semantic_label_status_counts = {'pending_upgrade': 1}`
- 机器可读结果：
  - `reports/plans/streaming_student_training_data_semantic_smoke/streaming_student_training_data_plan.json`
  - `reports/plans/streaming_student_supervision_semantic_smoke/streaming_student_supervision_plan.json`

## 四、当前判断
- 这一步已经证明：
  1. `target_event_semantic_sidecar`
     不再只是离线资产
  2. Stage3
     teacher-label export
     和 student-side
     batch contract
     都已能看见它
  3. 旧 teacher checkpoint
     即使 config
     没写这条路径，
     也不会阻塞当前消费链
- 这一步还没有证明：
  1. semantic sidecar
     已经带来可听收益
  2. semantic sidecar
     已经转化成
     新 loss / 新路由 / 新监督增益

## 五、下一步
1. 不再追加 decoder-conditioning
   小结构实验。
2. 下一步应直接决定：
   - 是先给
     Stage3 supervision
     增加基于
     `target_event_semantic_sidecar`
     的 target-side
     semantic weighting / auxiliary loss
   - 还是先把这份 sidecar
     接到 Stage5
     的 target-side semantic contract
     消费链
3. 无论先做哪条，
   都必须保持当前边界：
   - semantic sidecar
     当前只证明
     target-side
     lexical / punctuation / structure
     语义底账已接入
   - 不证明
     source-side
     phone / manner / place /
     forced alignment
     已就绪
