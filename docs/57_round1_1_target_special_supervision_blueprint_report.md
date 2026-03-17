# `round1.1` target special supervision blueprint 报告

## 目的
- 在 checkpoint gate 已证明“不能单独救回主线”之后，正式把下一步数据/监督路线落成可复核 sidecar。
- 本轮目标不是直接改训练，而是先回答：
  - `target_special_eval` 到底对应怎样的目标样本形态；
  - 训练/验证里有哪些最接近它的 proxy pool；
  - 哪些更大规模的结构型子集值得被拆成独立 supervision 轴。

先说人话：
- 现在终于不是“凭感觉猜下一轮该喂什么样本”了。
- 这轮已经把 special 邻域池和结构池落成正式产物，后面实验可以直接复用。

## 代码与命令
### 代码入口
- `src/v5vc/target_special_supervision.py`
- `src/v5vc/cli.py`

### 命令
- `manage.py analyze-round1-target-special-supervision`

### 输入
- `data_prep/round1_1/splits/hybrid_stratified_blocked/*.jsonl`
- `data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl`

### 产物
- data sidecar:
  - `data_prep/round1_1/target_special_supervision/target_special_supervision_sidecar.jsonl`
  - `data_prep/round1_1/target_special_supervision/target_special_supervision_pools.json`
- reports:
  - `reports/data/round1_1_target_special_supervision/target_special_supervision_summary.json`
  - `reports/data/round1_1_target_special_supervision/target_special_supervision_summary.md`

## special slice 当前画像
- `target_special_eval` 记录数: `8`
- 时长范围: `0.470998 ~ 2.114989` 秒
- 时长中位数: `0.956985` 秒
- lexical char 全部为 `0`
- pause / terminal / clause 全部为 `0`
- `utterance_structure_type = nonverbal` 共 `8`
- `final_terminal_type = none` 共 `8`

结论：
- `round1.1` 的 special slice 仍然是纯 nonverbal challenge。
- 它必须继续保持 `eval-only`，不能直接回流训练。

## 新增 supervision pools
### 1. `challenge_proxy_core`
- 记录数: `16`
- 全部来自 `target_train`
- lexical char 中位数: `1`
- 时长中位数: `0.920998` 秒
- clause 中位数: `1`
- pause / terminal 中位数: `1 / 0`
- `utterance_structure_type` 全部为 `other`
- `final_terminal_type` 全部为 `none`

典型样本：
- `一，`
- `二，`
- `三，`
- `欸，`

解释：
- 这是当前训练/验证里最接近 special challenge 的代理池。
- 它们不是纯 nonverbal，但已经很接近“短、轻、非终止、标点驱动”的运行条件。

### 2. `challenge_proxy_relaxed`
- 记录数: `48`
- `target_train = 43`，`target_validation = 5`
- lexical char 中位数: `4`
- 时长中位数: `1.265986` 秒
- terminal 中位数开始升到 `0.5`

解释：
- 这是 `challenge_proxy_core` 的放宽版。
- 可以作为第二层 proxy pool，但不能拿来替代 core pool。

### 3. `short_pause_no_terminal`
- 记录数: `19`
- lexical char 中位数: `2`
- 时长中位数: `1.001995` 秒
- `final_terminal_type` 全部为 `none`

解释：
- 它几乎就是 `challenge_proxy_core` 的可解释子族。
- 说明当前最像 special 的训练样本，本质上是一批短 pause-tail 片段。

### 4. `short_terminal_burst`
- 记录数: `49`
- lexical char 中位数: `5`
- 时长中位数: `1.359977` 秒
- terminal 中位数: `1`

解释：
- 这批样本已经不是 near-nonverbal proxy。
- 它们更适合被当作短促 terminal 表达池，而不是 special 邻域池。

### 5. 三条大规模结构轴
- `structural_multi_terminal`: `174`
  - lexical char 中位数: `30`
  - 时长中位数: `8.527483` 秒
- `structural_question_exclaim`: `144`
  - lexical char 中位数: `14`
  - 时长中位数: `3.675488` 秒
- `structural_clause_ge4`: `206`
  - lexical char 中位数: `37`
  - 时长中位数: `10.615488` 秒

解释：
- 这三池都足够大，适合作为正式 supervision bucket。
- 但它们和 `challenge_proxy_core` 不是同一种问题：
  - 前者是“结构复杂度/句末形状/表达型终止”；
  - 后者是“special 邻域的近非言语短片段”。

## 当前结论
- checkpoint gate 之后，最有价值的数据路线已经不再是“继续全量加一个新 aux”。
- 下一轮更应该：
  1. 继续把 `target_special_eval` 保持为 `eval-only`
  2. 把 `challenge_proxy_core` 当作 special-adjacent proxy pool
  3. 把 `structural_multi_terminal / structural_question_exclaim / structural_clause_ge4` 当作三条独立 supervision 轴

## 当前建议
- 不要把 `challenge_proxy_core` 和大结构池混成一个统一的“special-focused bucket”。
- 若下一轮用 `EXP-032` 骨架做最小实验，最值得先试的是：
  - 基于 `challenge_proxy_core` 的 proxy-aware sampling / supervision
  - 同时只额外引入一条独立结构轴，而不是三条全开

先说人话：
- 这轮最重要的不是又多了一个 sidecar。
- 而是终于把“special 邻域”和“结构复杂句”这两件事彻底拆开了。
