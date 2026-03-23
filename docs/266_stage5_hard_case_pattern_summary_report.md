# 2026-03-23 Stage5 hard-case pattern summary 报告

## 结论
- 本轮在
  `docs/265`
  的
  hard-case window list
  之上，
  又补了一层自动 pattern summary。
- 当前结果把上一轮的人工分型
  再收紧了一步：
  1. 真正明确的
     `boundary_dominated`
     只有：
     - `target::chapter3_3_firefly_162`
  2. `target::chapter3_17_firefly_133`
     虽然句首/句尾窗口很醒目，
     但按全局 share
     更准确应写成：
     - `mixed_failure`
     - 且 dominant window
       在 onset
  3. `target::chapter3_6_firefly_106`
     也不是纯边界型，
     更准确应写成：
     - `mixed_failure`
     - 但
       `interior_share = 0.751336`
       且 dominant window
       落在末段稳态窗口

先说人话：
- 上一轮“先按人工看起来分两类”
  还不够严。
- 现在更准确的状态是：
  - 一条是标准边界型
  - 一条是边界很显眼但不能算纯边界型
  - 还有一条是典型 interior / steady-window 型

## 本轮工程动作

### 1. 把 pattern summary 正式接进 probe
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增：
  - `pattern_summary`
- 每条 hard case
  现在会正式输出：
  - `boundary_advantage_share`
  - `interior_advantage_share`
  - `max_window_share`
  - `dominant_region`
  - `dominant_window_sec_range`
  - `pattern_label`

## 当前 hard-case pattern summary

### 1. `target::chapter3_3_firefly_162`
  是唯一清晰的 `boundary_dominated`
- `pattern_label = boundary_dominated`
- `boundary_share = 0.848822`
- `interior_share = 0.151178`
- `max_window_share = 0.446955`
- `dominant_region = onset`
- 这说明：
  - 它的 hard-case
    优势几乎都集中在边界
  - 继续诊断时，
    最优先应视为
    onset / offset
    问题样本

### 2. `target::chapter3_17_firefly_133`
  不能再写成纯 boundary 型
- `pattern_label = mixed_failure`
- `boundary_share = 0.090681`
- `interior_share = 0.909319`
- `max_window_share = 0.043447`
- `dominant_region = onset`
- 这说明：
  - 虽然最显眼的窗口
    的确在句首，
    且句尾也有大窗口
  - 但从总 share
    来看，
    它的失败并不是
    主要由边界独占
  - 更准确的写法应是：
    - mixed
    - 但带明显 edge anchors

### 3. `target::chapter3_6_firefly_106`
  更像 interior / steady-window 主导
- `pattern_label = mixed_failure`
- `boundary_share = 0.248664`
- `interior_share = 0.751336`
- `max_window_share = 0.161233`
- `dominant_region = offset`
- dominant window:
  - `5.333333s ~ 5.340590s`
- 这说明：
  - 虽然 dominant window
    落在末段，
  - 但从整体 share
    看，
    当前仍应把它归到：
    - interior-heavy /
      steady-window
      hard case

## 当前判断
- 当前最该避免的误写是：
  - 把
    `chapter3_17_firefly_133`
    和
    `chapter3_3_firefly_162`
    一起都写成
    “边界型”
- 当前更准确的模式划分应写成：
  1. `chapter3_3_firefly_162`
     - clean boundary-dominated
  2. `chapter3_17_firefly_133`
     - mixed failure
       with edge anchors
  3. `chapter3_6_firefly_106`
     - mixed failure
       with interior/steady-window dominance

## 对下一步的直接含义
1. `chapter3_3_firefly_162`
   可直接作为：
   - pure boundary case
2. `chapter3_17_firefly_133`
   下一步不要只盯边界，
   还要看：
   - interior transition
     为什么也持续贡献失败
3. `chapter3_6_firefly_106`
   仍优先按：
   - steady-window /
     plateau
     hard case
   继续

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `pattern_summary`

## 一句话结论
- 当前 hard-case 模式已经进一步收紧成：
  - 只有 `chapter3_3_firefly_162`
    是标准边界型；
  - `chapter3_17_firefly_133`
    和
    `chapter3_6_firefly_106`
    都更应视为 mixed，
    只是一个带 edge anchors，
    一个偏 interior / steady-window。
