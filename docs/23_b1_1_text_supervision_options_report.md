# `B1.1` 文本监督细化选项报告

## 目的
- 在 `B1-offline-minimal` 已经证明“方向成立但优势不明显”的前提下，整理下一轮 target-side 文本监督可以怎么细化。
- 本报告只做事实收集和可选路线整理，不直接改默认方案。

先说人话：
- 现在不是要不要继续用文本的问题。
- 而是“既然要用，那下一版该怎么把它教得更细”。

## 当前 `B1` 监督的已知边界
当前特征版本：
- `b1_punct_v1`

当前 7 维特征：
1. token length norm
2. lexical chars per second
3. pause punctuation density
4. terminal punctuation density
5. question ratio
6. exclamation ratio
7. nonverbal-only flag

问题不在于这 7 维没接上训练，而在于它们还偏粗。

## 目标侧文本分布事实
数据来源：
- `reports/data/b1_supervision_inventory/b1_supervision_inventory.json`
- `data_prep/round1/splits/hybrid_stratified_blocked/*.jsonl`

### 基础事实
- 总记录数：`624`
- `nonverbal_only`：`8`
- 含问号记录：`152`
- 含叹号记录：`64`
- 含 pause 类标点记录：`578`
- 含多个 pause 标点记录：`349`
- 含多个 terminal 标点记录：`166`
- lexical chars `<= 6`：`84`
- lexical chars `>= 30`：`163`

### 结构分布
- `pause_and_terminal`：`470`
- `pause_only`：`108`
- `terminal_only`：`46`

### 更细的句法粗分类
- `multi_clause_single_terminal`：`314`
- `multi_terminal`：`166`
- `single_clause_terminal`：`36`
- `nonverbal`：`8`
- `other`：`100`

解释：
- 这批目标台词并不是“只有一句一停”的简单料。
- 很多记录本身就带多停顿、多终止、长短句混合结构。

先说人话：
- 现在这批台词里，真正常见的不是“一个短句一个句号”，
- 而是“中间有停顿、结尾有句末、甚至一条里有多段语气”的复杂句。
- 这说明当前 `B1` 的 7 维监督，确实可能把信息压得太扁了。

## `B1.1` 候选路线
### 方案 B1.1-A: 扩展统计特征，不改训练结构
做法：
- 保持现在的 `text_aux_head` 框架不变。
- 只把 target-side 文本特征从 7 维扩到更细的统计向量，例如：
  - lexical length bucket
  - clause count
  - terminal count
  - pause-to-lexical ratio
  - terminal-to-lexical ratio
  - multi-terminal flag
  - short-utterance flag
  - long-utterance flag
  - question-present flag
  - exclamation-present flag

优点：
- 改动最小。
- 风险最低。
- 可以直接复用现有训练入口、评估入口、ablation 口径。

缺点：
- 仍然是“整句级统计”，不是时间对齐监督。
- 对 `e_evt` 的帮助可能有限，更偏向给 `text_aux` 多一点区分度。

大白话：
- 这是“先把教案写得更细一点”，但还没到“逐字逐停顿点名教学”。

### 方案 B1.1-B: 增加 clause 级标签，但仍保持离线轻量
做法：
- 对每条 target 文本额外生成 clause-level sidecar，例如：
  - clause_count
  - longest_clause_chars
  - shortest_clause_chars
  - clause_length_variance
  - final_clause_type
  - whether_terminal_before_end exists
- 训练中仍输入整句统计，但加入更明显的“句内结构复杂度”线索。

优点：
- 比 `B1.1-A` 更贴近真实节律结构。
- 不需要 source 文本，不破坏当前不对称监督口径。

缺点：
- 仍不是帧级对齐。
- 需要新增 sidecar 和清晰的字段定义，文档工作会更多。

大白话：
- 这是把一句话拆成“几段”，让模型至少知道这句话内部有几个大拐点。

### 方案 B1.1-C: 做 target-side 弱对齐事件标签
做法：
- 不给 source 做文字。
- 只对 target 文本生成更接近事件头的弱标签，比如：
  - pause boundary hints
  - terminal boundary hints
  - question / exclamation type hints
- 再把这些标签映射到更贴近 `e_evt` 的监督支路。

优点：
- 最符合当前“要救 `e_evt`”这个目标。
- 比单纯扩大 `text_aux` 更可能真正影响控制链。

缺点：
- 实现复杂度最高。
- 没有强制对齐工具时，只能做弱标签，边界仍然是近似的。
- 需要更谨慎的验证，避免又造出一套新噪声标签。

大白话：
- 这是从“整句写评语”往“告诉模型哪里该停、哪里该收、哪里是问句语气”再走一步。

## 我的建议
推荐顺序：
1. 先做 `B1.1-A`
2. 若证据仍不够，再做 `B1.1-C`

不优先建议：
- 直接继续放大当前 `B1-offline-minimal` 到 `500 step`

原因：
- `step100` 已显示当前 `B1` 版本与无 `B1` 基线整体基本打平。
- 这说明“继续放大训练时长”未必是当前最缺的变量。
- 更像是监督内容本身还偏粗。

先说人话：
- 我更建议先把教材修一版，再去上大课。
- 现在直接多上课，未必比先把教材写清楚更值。
