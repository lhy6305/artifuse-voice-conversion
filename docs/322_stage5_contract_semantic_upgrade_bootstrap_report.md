# 322. Stage5 contract / semantic 升级路线第一步 bootstrap 报告

## 结论
- 按用户最新决策，
  当前已正式停止继续追加
  decoder-conditioning
  小结构实验，
  转入
  contract / semantic
  升级路线。
- 本轮不是直接开新训练，
  而是先把“当前到底有什么 semantic、没有什么 semantic”
  收成正式资产，
  避免后续继续把旧
  `event_probs`
  误写成设计态
  `e_evt`。
- 已完成两部分落地：
  1. 给
     teacher contract /
     vocoder scaffold
     增加当前
     `event_probs`
     的 heuristic 语义元数据
  2. 新增正式
     `target_event_semantic_sidecar`
     生成器，
     把
     `B1 supervision inventory`
     与
     `C1 weak_event_hints`
     合并成独立的
     target-side
     semantic 资产

## 一、为什么现在要先做这一步
- 当前仓库里的
  `contractv2_normfix`
  已经把
  `f0_hz / vuv / aper / E`
  接进了 Stage5，
  但 audible bundle
  仍没有 clean voice emergence。
- 同时旧
  `event_probs(8D)`
  的真实语义仍是：
  - `energy_gate`
  - `abs_delta_gate`
  - `high_zero_cross`
  - `low_zero_cross_voiced_like`
  - `high_zero_cross_voiced_like`
  - `delta_energy_rise`
  - `delta_energy_fall`
  - `energy_norm`
- 这套维度来自旧 heuristic frame target，
  不是设计稿里的命名
  `e_evt`
  语义。
- 如果继续不分层，
  后面无论是接新的 target-side semantic supervision，
  还是讨论更高层 contract，
  都会混淆：
  - 当前 runtime
    真正输出了什么
  - 未来 semantic route
    还缺什么

## 二、本轮代码改动

### 1. 新增事件语义共享模块
- 新增：
  - `src/v5vc/event_semantics.py`
- 作用：
  - 固化当前 runtime
    `event_probs`
    的 heuristic 语义版本
  - 提供
    `build_current_runtime_event_semantics_meta()`
  - 提供
    `build_target_event_semantic_sidecar(...)`

### 2. teacher contract / scaffold 增加语义元数据
- 更新：
  - `src/v5vc/offline_teacher_downstream_contract.py`
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
- 当前行为：
  - contract json / md /
    tensor payload
    会明确写出：
    - `event_probs_version = offline_mvp_heuristic_event_target_v1`
    - 当前 8 维名字
    - `semantic_status = heuristic_frame_targets_not_design_e_evt`
  - scaffold summary
    也同步落盘这份元数据，
    避免下游再把
    `event_probs`
    当成最终设计态语义

### 3. 新增 CLI 入口
- 更新：
  - `src/v5vc/cli.py`
- 新命令：
  - `build-target-event-semantic-sidecar`
- 默认输入：
  - `data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl`
  - `data_prep/round1_1/b1_supervision/target_supervision_inventory.jsonl`
- 默认输出：
  - `data_prep/round1_1/target_event_semantic_sidecar/`
  - `reports/data/round1_1_target_event_semantic_sidecar/`

## 三、本轮实际生成的资产

### 1. `round1.1` supervision inventory
- 先重建：
  - `data_prep/round1_1/b1_supervision/`
  - `reports/data/round1_1_b1_supervision_inventory/`
- 关键结果：
  - target 记录数：
    `666`
  - source 记录数：
    `537`
  - target 有文本：
    `666 / 666`
  - source 有文本：
    `0 / 537`

### 2. 新的 target semantic sidecar
- 已生成：
  - `data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl`
  - `reports/data/round1_1_target_event_semantic_sidecar/target_event_semantic_sidecar_summary.json`
  - `reports/data/round1_1_target_event_semantic_sidecar/target_event_semantic_sidecar_summary.md`
- 关键统计：
  - `record_count = 666`
  - `inventory_status_counts = {'matched_inventory': 666}`
  - `clean_text_available_count = 666`
  - `phone_sequence_available_count = 0`
  - `manner_sequence_available_count = 0`
  - `place_sequence_available_count = 0`
  - `forced_alignment_available_count = 0`
  - `future_label_status_counts = {'pending_upgrade': 666}`
- 结构分布：
  - `multi_clause_single_terminal = 307`
  - `multi_terminal = 174`
  - `single_clause_terminal = 66`
  - `other = 111`
  - `nonverbal = 8`

## 四、验证
- 已执行：
  - `.\python.exe - <<py_compile ...>>`
    对以下文件做
    `py_compile`
    检查：
    - `src/v5vc/event_semantics.py`
    - `src/v5vc/cli.py`
    - `src/v5vc/offline_teacher_downstream_contract.py`
    - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  - 结果：
    - `py_compile_ok`
- 已执行：
```powershell
.\python.exe manage.py build-b1-supervision-inventory `
  --split-dir data_prep/round1_1/splits/hybrid_stratified_blocked `
  --data-output-dir data_prep/round1_1/b1_supervision `
  --report-output-dir reports/data/round1_1_b1_supervision_inventory
```
- 耗时：
  - `3.143s`
- 已执行：
```powershell
.\python.exe manage.py build-target-event-semantic-sidecar `
  --weak-event-hints-path data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl `
  --target-supervision-inventory-path data_prep/round1_1/b1_supervision/target_supervision_inventory.jsonl `
  --data-output-dir data_prep/round1_1/target_event_semantic_sidecar `
  --report-output-dir reports/data/round1_1_target_event_semantic_sidecar
```
- 耗时：
  - `3.094s`

## 五、当前阶段判断
- 这一步的意义不是：
  - 已经证明 semantic 升级会直接长出 clean voice
- 它的意义是：
  1. 正式停止继续把旧
     `event_probs`
     误称为设计态
     `e_evt`
  2. 把 target-side
     lexical / punctuation / clause
     语义独立落盘
  3. 明确写死：
     - 当前 semantic route
       只有 target-side bootstrap
     - source-side
       phone / manner / place /
       forced alignment
       仍然没有

## 六、下一步
1. 不再继续开
   decoder-conditioning
   同层小实验。
2. 下一步优先决定：
   - 先把
     `target_event_semantic_sidecar`
     接到
     Stage3 teacher-label /
     student supervision
   - 还是先把它接到
     Stage5 contract
     的 target-side semantic 辅助消费链
3. 无论选哪条，
   都必须保持当前边界：
   - target-side semantic
     已有
   - source-side semantic
     仍缺
   - 不能把这份 sidecar
     误写成“源/目标对称语义合同已完成”
