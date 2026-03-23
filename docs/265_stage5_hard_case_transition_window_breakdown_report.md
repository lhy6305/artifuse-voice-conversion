# 2026-03-23 Stage5 hard-case transition-window breakdown 报告

## 结论
- 当前实验线已经把
  hard-failure diagnosis
  从：
  - “哪几条记录会重复失败”
  推进到：
  - “这些记录具体在什么时间窗失败，
     而且失败模式并不一样”
- 当前 3 条 hard cases
  可分成两类：
  1. 前边界主导型：
     - `target::chapter3_17_firefly_133`
     - `target::chapter3_3_firefly_162`
  2. 孤立高杠杆窗口型：
     - `target::chapter3_6_firefly_106`

先说人话：
- 现在不是只知道
  “这三条比较麻烦”。
- 已经能更具体地说：
  - 有两条主要输在
    句首 / 句尾边界
  - 还有一条
    主要输在
    某个非常短、
    但权重特别高的局部窗口

## 本轮工程动作

### 1. 把 hard-case 时间窗 breakdown 正式接进 probe
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增输出：
  - `transition_hard_case_breakdown`
- 每条 hard case
  现在会正式记录：
  - reference oracle
  - baseline / oracle 的 local transition score 均值
  - `positive_advantage_fraction`
  - top failure windows
    的：
    - 时间范围
    - transition index
    - `total_advantage`
    - baseline / oracle
      的 delta / flux 局部误差

## 当前 hard cases 与 reference oracle
- `target::chapter3_17_firefly_133`
  - reference oracle:
    `oracle_sine_target_rms`
  - aggregate margin:
    `+0.013104`
- `target::chapter3_3_firefly_162`
  - reference oracle:
    `oracle_sine_target_rms`
  - aggregate margin:
    `+0.048131`
- `target::chapter3_6_firefly_106`
  - reference oracle:
    `oracle_active_frame_target_rms`
  - aggregate margin:
    `+0.046881`

说明：
- 当前 hard cases
  并不是全都被同一种 oracle
  压住。
- 至少已经分成：
  - 更接近正弦模板优势的记录
  - 更接近 active-frame 模板优势的记录

## 关键结果

### 1. `chapter3_17_firefly_133`
  主要输在句首和句尾边界
- local summary:
  - baseline local mean
    `2.394277`
  - oracle local mean
    `2.392994`
  - `positive_advantage_fraction = 0.527786`
- top windows:
  - `0.000000s ~ 0.007256s`
    - `total_advantage = 2.462396`
  - `12.455329s ~ 12.469841s`
    - `2.316666`
- 这说明：
  - 这条长样本
    不是全程都差
  - 真正拉开差距的，
    主要是：
    - very early onset
    - very late ending
- 更贴近工程语言的解释：
  - 当前 baseline
    在句首 / 句尾
    transition handling
    还不如
    `sine oracle`
    稳

### 2. `chapter3_3_firefly_162`
  是非常典型的短句前边界主导型
- local summary:
  - baseline local mean
    `2.182794`
  - oracle local mean
    `2.147743`
  - `positive_advantage_fraction = 0.506024`
- top windows:
  - `0.000000s ~ 0.018141s`
    - `total_advantage = 3.852173`
  - `0.595011s ~ 0.602268s`
    - `2.786440`
- 这条记录总时长本来就只有：
  - `0.612993 sec`
- 这说明：
  - 几乎整条 hard-case 结论
    都被前后边界几个很短的窗口主导
- 人话就是：
  - 这不是中间主体内容慢慢输掉的
  - 而是
    开头一小段、
    结尾一小段
    就把分数差拉出来了

### 3. `chapter3_6_firefly_106`
  是孤立高杠杆窗口型，
  不是全程都差
- local summary:
  - baseline local mean
    `2.268548`
  - oracle local mean
    `2.276734`
  - `positive_advantage_fraction = 0.436141`
- 这说明：
  - 从局部 transition mean
    来看，
    baseline
    甚至略优于
    reference oracle
- 但它仍然整体失败，
  关键是：
  - `5.333333s ~ 5.340590s`
    这个窗口
    `total_advantage = 4.958204`
  - 且其中
    oracle 的：
    - `delta_error = 0.000000`
    - `flux_error = 0.000000`
- 这说明：
  - 这条记录
    不是“全局 transition 更差”
  - 更像是：
    - 某个极短窗口
      完全落在
      active-frame oracle
      的舒适区
    - 高杠杆局部
      直接主导了整条记录的结果

## 当前判断
- 当前 hard cases
  不能再混成一类写：
  1. `chapter3_17_firefly_133`
     与
     `chapter3_3_firefly_162`
     更像：
     - boundary-dominated hard cases
  2. `chapter3_6_firefly_106`
     更像：
     - isolated high-leverage plateau / steady-window hard case
- 这意味着：
  - 下一步 targeted diagnosis
    也不应再用同一套问题模板
    去问这三条记录

## 对下一步的直接含义
1. 对
   `chapter3_17_firefly_133`
   和
   `chapter3_3_firefly_162`
   优先怀疑：
   - onset / offset
     boundary transition
     处理缺口
2. 对
   `chapter3_6_firefly_106`
   优先怀疑：
   - 某类短 plateau /
     steady-state
     窗口，
     当前 baseline
     仍容易输给
     active-frame oracle
3. 当前不建议把这三条
   一起笼统写成：
   - “transition-side 还不够强”

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `transition_hard_case_breakdown`

## 一句话结论
- 当前 experiment line
  已经把 hard-case
  diagnosis
  推进到时间窗层面：
  - 两条记录主要输在前后边界，
  - 一条记录主要输在极短的高杠杆稳态窗口；
  下一步应按这两类模式分开继续，而不是再把三条记录混成同一种 hard case。
