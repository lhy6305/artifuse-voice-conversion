# 2026-03-23 Stage5 hard-failure targeted diagnosis 报告

## 结论
- 本轮围绕
  `docs/263`
  的
  best transition combo
  做了修正后的
  targeted diagnosis，
  当前结论是：
  - 真正会在
    `delta=1.5 + flux=2.0`
    下对两类 oracle
    都重复失败的，
    不是上轮肉眼误判的那批，
    而是：
    - `target::chapter3_17_firefly_133`
    - `target::chapter3_3_firefly_162`
    - `target::chapter3_6_firefly_106`
- 当前这 3 条 hard failures
  的共同特征更接近：
  - baseline 自己的
    transition penalty
    偏高
  - 但 target 的短时结构
    又相对更平滑、
    更接近可被模板近似
- 更贴近人话的解释是：
  - 这些 hard cases
    不是“特别乱、特别复杂，
    baseline 跟不上”
  - 更像是：
    - target 本身就比较平滑
    - 所以 fixed-template oracle
      不太容易被
      transition-side penalty
      狠狠拉开

## 先纠正一个口径坑
- 本轮先修正了
  `margin = baseline_score - other_score`
  的符号解释：
  - `margin < 0`
    才表示
    baseline 赢
  - `margin > 0`
    才表示
    baseline 输
- 上一轮如果只看
  数值绝对值、
  不看符号，
  很容易把：
  - best wins
    误写成
    hard failures

## 当前 best combo
- 当前 probe
  自动汇总出的
  best combo
  仍是：
  - `delta_lambda = 1.5`
  - `flux_lambda = 2.0`
  - `total_wins = 16 / 24`

## 修正后的 repeated hard-failure / easy-win 子集

### 1. repeated hard failures
- 在两类 oracle
  下都为
  `margin > 0`
  的记录：
  - `target::chapter3_17_firefly_133`
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_6_firefly_106`

### 2. repeated easy wins
- 在两类 oracle
  下都为
  `margin < 0`
  的记录：
  - `target::chapter3_20_firefly_133`
  - `target::chapter3_26_firefly_107`
  - `target::chapter3_2_firefly_155`
  - `target::chapter3_2_firefly_163`
  - `target::chapter3_2_firefly_212`
  - `target::chapter3_3_firefly_174`
  - `target::chapter3_3_firefly_245`

## 组间对照结果

### 1. hard failures 的 baseline `frame_delta` 反而更高
- hard:
  - `loss_frame_delta_unit_rms_l1 = 1.024148`
- easy:
  - `0.920796`
- 这说明：
  - 当前 hard failures
    不是因为
    baseline 本身太静态、
    delta 太小
  - 相反，
    baseline 在这些样本上
    的 transition mismatch
    还更大

### 2. hard failures 的 normalized static logspec
  反而更低
- hard:
  - `loss_frame_unit_rms_logspec_l1 = 0.699598`
- easy:
  - `0.795229`
- 这说明：
  - 这些 hard cases
    在“去包络后的静态频谱形状”
    上，
    并没有更难
  - 更像是：
    - static shape
      本来就更容易被模板近似

### 3. target 自身更平滑，
  更接近模板友好区
- hard:
  - `aligned_frame_template_cosine_mean = 0.032674`
  - `aligned_frame_adjacent_cosine_mean = 0.083340`
- easy:
  - `0.020260`
  - `0.120370`
- 这说明：
  - hard failures
    对应的 aligned target
    自己就更平滑，
    相邻帧变化更弱，
    更接近“可被固定模板近似”
    的一侧
- 这正好解释：
  - 为什么 transition-side penalty
    在这些记录上
    拉不开足够优势

### 4. duration 不是主解释
- hard 平均时长：
  - `6.149131 sec`
- easy 平均时长：
  - `5.325274 sec`
- 但 hard 内部同时包含：
  - `0.612993 sec`
  - `5.352993 sec`
  - `12.481406 sec`
- 这说明：
  - 当前还不能把
    hard failure
    直接归因成：
    - 太短
    - 或太长

## 当前判断
- 当前更准确的 targeted diagnosis
  结论应写成：
  1. 真正的 hard failures
     是：
     - `chapter3_17_firefly_133`
     - `chapter3_3_firefly_162`
     - `chapter3_6_firefly_106`
  2. 它们不是单纯
     “transition 太复杂”
  3. 更像是：
     - target 本身
       更平滑、更模板友好
     - 而 baseline
       在这些样本上的
       delta mismatch
       又偏大
  4. 所以单靠
     transition-side penalty
     还不足以在这些样本上
     稳定拉开 oracle

## 下一步建议
1. 当前若继续实验线，
   下一题应优先转向：
   - 对这 3 条 hard failures
     单独做
     per-record structure breakdown
2. 优先看：
   - baseline / oracle / aligned
     在这些 record
     上的帧级 transition 轨迹
   - 哪些时间段
     transition penalty
     没能把模板 oracle
     拉开
3. 当前不建议回退去优先做：
   - 更大范围的
     权重扫网格
   - 或继续只看 aggregate

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `transition_targeted_hard_failure_summary`

## 一句话结论
- 当前实验线已经把
  “transition-side 组合还不够稳”
  进一步收紧成：
  - 真正重复失败的是
    `chapter3_17_firefly_133 / chapter3_3_firefly_162 / chapter3_6_firefly_106`
  - 且它们更像是
    target 本身更平滑、
    更模板友好的 hard cases；
    下一步应直接对这 3 条
    做 per-record structure breakdown。
