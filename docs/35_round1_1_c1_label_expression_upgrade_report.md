# `round1.1` `C1` 标签表达升级报告

## 目的
- 在 `A2-min` 已基本证明“纯约束小修补救不回 `step50`”之后，先把下一层需要的标签底座补起来。
- 当前不直接改训练接法，只先升级 `C1` weak-event sidecar 的表达能力。

先说人话：
- 现在不是继续拧 loss 旋钮。
- 是先把“老师手里的标签”从几个边界点，升级成更像句内结构的表达。

## 当前升级内容
### 1. clause 级跨度已补入 sidecar
- 每条 target 记录现在除了：
  - `pause_boundaries`
  - `terminal_boundaries`
- 还会额外生成：
  - `clause_count`
  - `clause_spans`
  - `utterance_structure_type`

### 2. `clause_spans` 当前包含
- `clause_index`
- `char_start_index / char_end_index`
- `lexical_start_index / lexical_end_index`
- `lexical_char_count`
- `lexical_start_ratio / lexical_end_ratio`
- `frame_start_index / frame_end_index`
- `closing_symbol / closing_symbol_type`
- `role`
  - `single / initial / middle / final`

### 3. 句型粗分类已补入
- 当前 `utterance_structure_type` 分为：
  - `nonverbal`
  - `single_clause_terminal`
  - `multi_clause_single_terminal`
  - `multi_terminal`
  - `other`

## 当前 `round1.1` 统计
- 记录数：
  - `666`
- `utterance_structure_type_counts`：
  - `multi_clause_single_terminal = 307`
  - `multi_terminal = 174`
  - `single_clause_terminal = 66`
  - `other = 111`
  - `nonverbal = 8`
- `clause_count_stats`：
  - `min = 0`
  - `max = 10`
  - `mean = 3.010511`

先说人话：
- 这批 target 台词大多数都不是“一个短句一个句号”。
- 句内本来就有不少多分句、多终止结构，所以旧 sidecar 确实偏扁。

## 当前意义
- 这一步还没有直接改变训练行为。
- 但它已经把下一轮真正可做的事情准备出来了，比如：
  - clause-role 区分
  - pause / terminal 的位置层级区分
  - 更结构化的 boundary pre/post supervision

## 当前结论
- 这不是最终监督升级，只是第一步。
- 但它已经把 route-C 从“只有边界点提醒”推进到“有边界点 + clause 级结构底账”。

## 下一步建议
- 若继续按当前总计划推进：
  - 下一轮优先尝试把这些 clause / structure 字段接入更明确的事件监督定义
  - 而不是再做同层的 loss 小调参
