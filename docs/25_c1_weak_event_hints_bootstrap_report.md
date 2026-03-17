# `C1` 弱事件提示 sidecar 启动报告

## 目的
- 在 `B1.1-A` 未形成明确主验证增益后，启动 route-C 的第一步：
  - 构建 target-side 弱对齐事件提示 sidecar。
- 这一步先不改训练结构，先把可复用的监督底账做出来。

先说人话：
- 现在开始换一种老师。
- 不再只给整句打分，而是先告诉模型“这句大概哪里该停、哪里像句末”。

## 代码与产物
### 代码入口
- `src/v5vc/c1_weak_event_hints.py`
- `src/v5vc/cli.py`

### 命令
- `build-c1-weak-event-hints`

### 产物
- data sidecar:
  - `data_prep/round1/c1_weak_event_hints/target_weak_event_hints.jsonl`
- reports:
  - `reports/data/c1_weak_event_hints/weak_event_hints_summary.json`
  - `reports/data/c1_weak_event_hints/weak_event_hints_summary.md`

## 当前 sidecar 内容
每条 target 记录当前会生成：
- `record_id`
- `split`
- `duration_sec`
- `sample_rate`
- `estimated_frame_count`
- `lexical_char_count`
- `nonverbal_only`
- `pause_boundaries`
- `terminal_boundaries`
- `final_terminal_type`
- `structure_flags`

边界位置当前来自：
- clean text 标点
- lexical progress ratio
- 固定 `frame_length / hop_length` 下的帧索引估计

解释：
- 这不是 forced alignment。
- 这是“文本驱动的弱事件位置提示”。

## 当前统计结果
- 总记录数：`624`
- `nonverbal_only_count`: `8`
- `records_with_pause_boundaries`: `549`
- `records_with_terminal_boundaries`: `516`
- `pause_boundary_total`: `1209`
- `terminal_boundary_total`: `701`

句末类型：
- `terminal_period`: `317`
- `terminal_question`: `99`
- `terminal_exclamation`: `41`
- `none`: `167`

先说人话：
- 这批 sidecar 不是稀疏到没法用。
- 大多数目标台词都能给出可用的停顿点和句末点提示。

## 当前结论
- route-C 的第一批 target-side 监督底账已经落盘。
- 这批 sidecar 足以支持下一步尝试：
  - 把弱边界提示接入 target-side `event_target` 或 event loss。
- 当前仍要保持的边界：
  - source-side 继续保持 audio-only
  - `target_special_eval` 的 nonverbal 子集不应被误当作普通 lexical boundary 样本

## 下一步
- `C1.1`：
  - 尝试把当前弱边界提示以“target-side event loss bias / target override”的方式接入训练
  - 再做一轮 `100 step` 对照验证
