# 146. Stage3 calibration asset 与 eval bridge 报告

## 背景
- `docs/145_stage3_streaming_student_scaffold_bootstrap_report.md`
  已经把 Stage3 `streaming_student` scaffold 接成正式 CLI 入口。
- 下一步真正缺的，不是再起一个空目录，
  而是两件更具体的东西:
  - 校准资产格式
  - Stage3 到 `offline_mvp` 口径的 eval bridge

## 本轮目标
- 不直接进入真实 Student 训练。
- 先把:
  - calibration asset schema
  - calibration subset
  - Stage3 summary bridge
  固定为正式落盘产物。

## 本轮实际完成

### 1. 新增 Stage3 calibration asset 构建入口
- 新增命令:
  - `.\python.exe manage.py build-streaming-student-calibration-assets`
- 当前默认输出:
  - `data_prep/round1_1/streaming_student_calibration/target_calibration_records.jsonl`
  - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_template.json`
  - `reports/data/streaming_student_calibration/streaming_student_calibration_summary.json`
  - `reports/data/streaming_student_calibration/streaming_student_calibration_summary.md`

### 2. 新增 Stage3 eval bridge 入口
- 新增命令:
  - `.\python.exe manage.py build-streaming-student-eval-bridge`
- 当前默认输出:
  - `reports/eval/streaming_student_eval_bridge/streaming_student_eval_bridge.json`
  - `reports/eval/streaming_student_eval_bridge/streaming_student_eval_bridge.md`

## calibration asset 当前格式

### 当前 machine-readable 资产包含
- `s_spk_target`
- `s_geom_target`
- `alpha`

### 当前字段状态
- `s_spk_target`
  - `dim = 16`
  - 当前值为 placeholder zero vector
- `s_geom_target`
  - `dim = 8`
  - 当前值为 placeholder zero vector
- `alpha`
  - `parameterization = global_scalar`
  - 当前值为 placeholder identity:
    - `value = 1.0`
    - `suggested_bounds = [0.85, 1.15]`

### 当前必须明确的边界
- 这不是“已经估计出的目标说话人校准结果”。
- 这只是:
  - 正式资产 schema
  - placeholder 值
  - 以及后续真实估计应回填的位置

## calibration subset 当前结果

### 当前选择口径
- 数据源:
  - `data_prep/round1_1/splits/hybrid_stratified_blocked/target_train.jsonl`
- 选择原则:
  - 先覆盖:
    - 结构类型
    - terminal 类型
    - special supervision pool
    - 时长桶
    - 文本长度桶
  - 再补足时长，
    避免只拿一堆很短的覆盖样本

### 当前实际结果
- `selected_record_count = 11`
- `selected_total_duration_sec = 135.964922`
- 已进入设计稿要求的:
  - `1-3` 分钟校准子集范围

### 当前覆盖摘要
- `utterance_structure_type_counts`:
  - `multi_clause_single_terminal = 5`
  - `multi_terminal = 3`
  - `other = 2`
  - `single_clause_terminal = 1`
- `final_terminal_type_counts`:
  - `none = 4`
  - `terminal_period = 5`
  - `terminal_question = 1`
  - `terminal_exclamation = 1`

说明:
- 这套子集当前覆盖的是:
  - 已有结构多样性
  - 已有特殊池近邻
  - 以及可用时长
- 它不是按音素级发音平衡精确筛出来的，
  因为当前仓库并没有音素级强对齐标注。

## eval bridge 当前做了什么

### 1. 当前 bridge 汇总的 Stage3 输出
- `shared_hidden`
- `z_art`
- `event_logits / event_probs`
- `coarse_log_f0`
- `vuv_logits`
- `aperiodicity`
- `energy`
- `log_f0_correction`
- `aper_correction`

### 2. 当前 bridge 的比较口径
- `target_validation`
- `target_special_eval`

### 3. 当前 bridge 产出的摘要类型
- 每个 slice 的:
  - record count
  - duration stats
  - punctuation ratio
  - group counts
  - frame-masked output stats
- 以及:
  - `target_special_eval - target_validation`
    的逐项 delta

## 当前 eval bridge 结果如何解释

### 可以解释成什么
- Stage3 前端 / Student 输出已经能被稳定汇总。
- 现有 `frame_length / hop_length` 对齐下，
  已经能形成正式 summary artifact。
- plumbing 没断。

### 不能解释成什么
- 不能解释成:
  - 目标校准已经成功
  - Stage3 模型质量已经可评估
  - `target_special_eval` 上的 delta 代表真实优劣

原因:
- 当前 conditioning 仍来自 placeholder asset。
- 当前还没有:
  - 真正的校准估计
  - teacher-label supervision
  - 真实 Student 训练

## 当前边界

### 1. calibration asset 还没有真实估计步骤
- 目前只解决了:
  - schema
  - subset
  - placeholder

### 2. eval bridge 还是 contract check
- 它当前的价值是:
  - 验证接口
  - 验证 summary 口径
  - 验证 Stage3 输出能否被汇总

### 3. 当前不能把 Stage3 bridge 指标和 offline MVP route 指标混写
- `offline_mvp` route 指标问的是:
  - 当前训练 family / anchor 谁更强
- Stage3 bridge 当前问的是:
  - 这条新骨架的输出是否能被稳定接到既有摘要口径

## 下一步建议
1. 在当前 asset template 上补真实估计步骤，
   回填:
   - `s_spk_target`
   - `s_geom_target`
   - `alpha`
2. 为 Stage3 增加 teacher-label 数据接线。
3. 让 eval bridge 的 summary keys
   逐步变成真实 Student 训练也会直接消费的中间指标。

## 一句话结论
- Stage3 现在已经不只是 scaffold；
  它已经有了:
  - 正式校准集
  - 正式校准资产模板
  - 正式 eval bridge
- 但这些产物当前仍服务于:
  - 接口定型
  - 边界确认
  而不是直接宣告“真实校准 / 真实 Student 训练已完成”。
