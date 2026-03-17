# 训练输入标准与评估基线骨架

## 目的
本页定义当前 round1 阶段进入训练前需要稳定下来的两件事：

1. 统一的训练输入 manifest 格式
2. 可持续追加的评估基线与实验记录模板

## round1 训练输入 manifest
当前由以下命令生成：

- `.\python.exe manage.py build-round1-manifests`

当前输出目录：

- `data_prep/round1/manifests/`
- `data_prep/round1/splits/hybrid_stratified_blocked/`

当前 manifest 文件：

- `target_train.jsonl`
  - 目标说话人训练记录。
  - 包含原始文本和清洗文本。
- `source_train.jsonl`
  - 源说话人训练候选记录。
  - 当前不含文本。
- `combined_round1.jsonl`
  - 统一索引，便于后续训练和检查工具复用。
- `splits/hybrid_stratified_blocked/target_train.jsonl`
  - 用户已确认的目标训练集。
- `splits/hybrid_stratified_blocked/target_validation.jsonl`
  - 用户已确认的目标常规验证集。
- `splits/hybrid_stratified_blocked/target_special_eval.jsonl`
  - 单独保留的 `no_text_voice` challenge eval。
- `splits/hybrid_stratified_blocked/source_train.jsonl`
  - 用户已确认的源训练集。
- `splits/hybrid_stratified_blocked/source_validation.jsonl`
  - 用户已确认的源验证集。

## manifest 字段约定
### 通用字段
- `record_id`
- `dataset`
- `role`
- `split`
- `audio_path`
- `audio.sample_rate`
- `audio.channels`
- `audio.sample_width_bytes`
- `audio.duration_sec`

### 文本字段
- `text.raw`
- `text.clean`
- `text.cleaned_lab_path`

### 标签字段
- `labels.has_text`
- `labels.text_is_runtime_required`

### 溯源字段
- `source_metadata`

## 当前边界
- 当前 manifest 只服务于 round1 离线 MVP。
- 当前不处理 source-target 配对策略，只提供稳定记录索引。
- 当前不把文本作为推理必选输入。
- 当前 `target_special_eval.jsonl` 已接入独立数据级评估命令，但尚未接入模型级推理评估。

## 评估基线模板
当前已提供：

- `configs/eval_baseline_template.json`
- `reports/templates/experiment_record_template.md`

这两份模板的作用是：

- 让后续实验记录结构固定下来
- 强制保留 `z_art / e_evt / r_res` 的消融位置
- 防止进入训练后只留口头结论、不留实验记录

## 当前建议
下一步进入评估基线实现时，应优先做：

1. 数据完整性检查命令
2. manifest 统计检查命令
3. 首版实验记录初始化命令或流程

## 当前状态更新
- 已实现：
  - `.\python.exe manage.py check-round1-data`
  - `.\python.exe manage.py init-experiment --slug offline-mvp-baseline`
- 当前完整性检查结果：
  - `reports/data/round1_integrity/integrity_summary.md`
  - 结果为 `overall_ok: True`
- 当前首份实验记录：
  - `reports/experiments/EXP-20260314-001-offline-mvp-baseline.md`
  - `reports/experiments/EXP-20260314-001-offline-mvp-baseline.metrics.json`

## 补充状态
- 已实现：
  - `.\python.exe manage.py evaluate-round1-baseline`
  - `.\python.exe manage.py train-offline-mvp --experiment-id EXP-... --dry-run`
  - `.\python.exe manage.py analyze-round1-splits`
  - `.\python.exe manage.py materialize-round1-split`
  - `.\python.exe manage.py evaluate-round1-special-eval`
- 当前结果：
  - baseline 评估结果位于 `reports/eval/round1_baseline/`
  - 训练 dry-run 计划位于 `reports/training/offline_mvp/`
  - 用户已确认的正式 split 位于 `data_prep/round1/splits/hybrid_stratified_blocked/`
  - `target_special_eval` 独立评估结果位于 `reports/eval/round1_special_eval/`
