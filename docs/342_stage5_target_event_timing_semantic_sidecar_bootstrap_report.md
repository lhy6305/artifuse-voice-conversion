# 342. Stage5 target event timing semantic sidecar bootstrap 报告

## 结论
- 已完成第一份正式
  `target_event_timing_semantic_sidecar`
  资产。
- 这一步不是再做
  Stage5 consumer
  微调，
  而是把现有
  `C1 weak_event_hints`
  里已经存在的
  frame-level
  时间信息
  正式物化成可消费的
  sparse time-aware semantic bridge。
- 当前结论是：
  - 仓库里并不缺
    target-side
    弱时序边界线索
  - 缺的是
    统一、正式、可下游直接读取的
    timing sidecar

## 一、本轮为什么值得做
- `docs/341`
  已经说明：
  - target-only
    utterance-level static semantic
    即便进入
    Stage5 forward path，
    也不能推出人声
- 所以下一步最值钱的工作，
  不是再加几个句级特征，
  而是把：
  - pause boundary
  - terminal boundary
  - clause span
  这些已有的时序结构，
  先从隐式弱提示
  升成正式资产

## 二、本轮代码改动
- 更新：
  - `src/v5vc/event_semantics.py`
  - `src/v5vc/cli.py`
- 新增命令：
  - `build-target-event-timing-semantic-sidecar`
- 默认输入：
  - `data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl`
  - `data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl`
- 默认输出：
  - `data_prep/round1_1/target_event_timing_semantic_sidecar/`
  - `reports/data/round1_1_target_event_timing_semantic_sidecar/`

## 三、产物结构
- 新 sidecar
  保留的是
  sparse timeline assets，
  不是逐帧 dense float 数组。
- 每条记录当前包含：
  - `timing_alignment`
  - `utterance_semantic_overview`
  - `frame_event_label_space`
  - `time_aware_semantics.boundary_events`
  - `time_aware_semantics.clause_regions`
  - `time_aware_semantics.timeline_events`
  - `upgrade_status`
- 当前事件类型只有三类：
  - `clause_region`
  - `pause_boundary_window`
  - `terminal_boundary_window`
- 边界窗口默认
  `boundary_half_width_frames = 2`
  ，也就是每个弱边界中心帧两侧各扩
  `2`
  帧。

## 四、本轮实际生成结果
- 已生成：
  - `data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl`
  - `reports/data/round1_1_target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar_summary.json`
  - `reports/data/round1_1_target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar_summary.md`
- 关键统计：
  - `record_count = 666`
  - `inventory_status_counts = {'matched_semantic_sidecar': 666}`
  - `weak_time_alignment_ready_for_target_side_bootstrap_count = 658`
  - `estimated_frame_count_stats.mean = 1678.869369`
  - `clause_region_count_stats.mean = 3.010511`
  - `pause_boundary_event_count_stats.mean = 1.915916`
  - `terminal_boundary_event_count_stats.mean = 1.115616`
  - `timeline_event_count_stats.mean = 6.042042`
- 结构分布与上一版 utterance semantic
  保持一致：
  - `multi_clause_single_terminal = 307`
  - `multi_terminal = 174`
  - `single_clause_terminal = 66`
  - `other = 111`
  - `nonverbal = 8`

## 五、验证
- 已执行：
  - `.\python.exe -m py_compile src/v5vc/event_semantics.py src/v5vc/cli.py`
  - 结果：
    - `py_compile_ok`
- 已执行：
```powershell
.\python.exe manage.py build-target-event-timing-semantic-sidecar `
  --weak-event-hints-path data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl `
  --target-event-semantic-sidecar-path data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --data-output-dir data_prep/round1_1/target_event_timing_semantic_sidecar `
  --report-output-dir reports/data/round1_1_target_event_timing_semantic_sidecar
```
- 结果：
  - 产物成功落盘
  - 第一条记录已可直接看到：
    - clause spans
    - pause/terminal boundary windows
    - 合并后的 sparse timeline

## 六、当前阶段判断
- 这一步的价值不是：
  - 已经证明新的 semantic consumer
    会直接长出 speech
- 它的价值是：
  1. 正式把
     target-side
     弱时序 semantic
     从句级 sidecar
     升级为可消费的 timeline 资产
  2. 避免下一步又退回：
     - utterance-only summary
     - 或 consumer 内部临时重算时间结构
  3. 为后续真正的
     time-aware consumer
     提供一个固定输入合同

## 七、下一步
1. 下一步不应回到：
   - static target-side semantic
     broadcast
2. 更合理的直接动作是：
   - 把
     `target_event_timing_semantic_sidecar`
     接入
     Stage5 package metadata / consumer 读取路径
3. 但在进入下一轮训练前，
   仍需保持边界清晰：
   - 当前仍是
     target-side only
   - 当前 timing
     仍是 weak alignment
   - 当前还不是完整
     design-state
     `e_evt`
