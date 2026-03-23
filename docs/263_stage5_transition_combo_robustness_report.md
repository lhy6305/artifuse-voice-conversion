# 2026-03-23 Stage5 transition-combo robustness 报告

## 结论
- 本轮继续沿
  `docs/262`
  的
  transition-delta candidate-objective
  主轴推进，
  但把观察重点
  从 aggregate 排序
  升级到：
  - per-record robustness
  - hard-failure records
- 当前结果说明：
  - `frame_delta`
    确实是目前最有希望的方向
  - 但即使把
    `frame_delta + spectral_flux`
    一起加进 candidate score，
    现阶段也还不够稳
- 当前最佳网格点是：
  - `delta_lambda = 1.5`
  - `flux_lambda = 2.0`
  - 总 wins
    `16 / 24`
- 但这仍只意味着：
  - 对
    `oracle_sine_target_rms`
    赢
    `9 / 12`
  - 对
    `oracle_active_frame_target_rms`
    赢
    `7 / 12`
- 所以当前不能把结论写成：
  - “transition-side 组合已经足够”
- 更准确的写法应是：
  - transition-side 组合
    方向是对的，
    但稳健性还不够，
    下一步应直接盯
    hard-failure records

## 背景
- `docs/262`
  已确认：
  - 单一
    `frame_delta_unit_rms_l1`
    可以量化出：
    - 弱翻转区
    - 稳翻转区
- 但那还是 aggregate 视角，
  仍可能掩盖：
  - 少数 record
    被大幅拉赢，
    带动均值
  - 同时另一些 record
    仍稳定失败

## 本轮补充

### 1. 在 probe 中固化组合网格总结
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增：
  - `transition_combo_grid_summary`
- 当前诊断口径：
  - `score = weighted_wave_objective + λ_delta * frame_delta + λ_flux * spectral_flux`
  - `λ_delta grid = [0.3, 0.5, 0.75, 1.0, 1.5]`
  - `λ_flux grid = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0]`

### 2. 当前 probe 现在能直接输出
- 每个组合的：
  - 总 wins
  - 对
    `sine oracle`
    的 wins / margins
  - 对
    `active-frame oracle`
    的 wins / margins

## 关键结果

### 1. 最优组合仍只达到中等稳健性
- 当前总 wins
  最高的组合是：
  - `delta_lambda = 1.5`
  - `flux_lambda = 2.0`
  - `total_wins = 16 / 24`
- 细分：
  - 对
    `oracle_sine_target_rms`
    - `wins = 9 / 12`
    - `mean_margin = -0.016041`
  - 对
    `oracle_active_frame_target_rms`
    - `wins = 7 / 12`
    - `mean_margin = -0.019847`
- 这说明：
  - 加入 spectral flux
    确实能把
    per-record robustness
    稍微往上抬
  - 但当前仍远不到
    “多数 record
    稳定翻回 baseline”

### 2. 对 `active-frame oracle`
  的稳健性仍明显偏弱
- 即使在当前最优组合点：
  - `7 / 12`
    也只是刚过半
- 这说明：
  - 当前更强的 fixed-template oracle
    仍没有被可靠压制
  - 所以后续不能只看：
    - 总 wins
    - 或 aggregate mean margin

### 3. 当前 hard-failure records 已经能点名

#### A. 对 `oracle_sine_target_rms`
  最顽固的失败样本
- 在
  `delta=1.5, flux=2.0`
  下，
  margin 最差的几条是：
  - `target::chapter3_3_firefly_245`
    - `-0.060156`
  - `target::chapter3_2_firefly_163`
    - `-0.054080`
  - `target::chapter3_2_firefly_155`
    - `-0.039700`
  - `target::chapter3_2_firefly_212`
    - `-0.034612`
  - `target::chapter3_26_firefly_107`
    - `-0.032721`

#### B. 对 `oracle_active_frame_target_rms`
  最顽固的失败样本
- 同一组合下，
  margin 最差的几条是：
  - `target::chapter3_20_firefly_133`
    - `-0.133794`
  - `target::chapter3_3_firefly_245`
    - `-0.088929`
  - `target::chapter3_2_firefly_163`
    - `-0.076847`
  - `target::chapter3_2_firefly_155`
    - `-0.043574`
  - `target::chapter3_26_firefly_107`
    - `-0.024915`

### 4. 有一组 hard cases 已经重复出现
- 当前重复出现在两类 oracle
  失败名单里的记录包括：
  - `target::chapter3_3_firefly_245`
  - `target::chapter3_2_firefly_163`
  - `target::chapter3_2_firefly_155`
  - `target::chapter3_26_firefly_107`
- 这说明：
  - 当前不是“随机哪几条差一点”
  - 而是已经出现
    可复查的
    hard-failure 子集

## 当前判断
- 当前实验线的结论应再收紧一层：
  1. `frame_delta`
     是目前最像正确方向的
     candidate component
  2. 加入
     `spectral_flux`
     可以略微抬高
     per-record robustness
  3. 但现阶段最强组合
     仍不足以稳定压过
     两类 fixed-template oracle
  4. 所以下一步最值钱的工作，
     不是继续盲扫更大的权重网格，
     而是：
     - 直接围绕
       hard-failure records
       做 targeted diagnosis

## 下一步建议
1. 当前若继续实验线，
   最优先题应改成：
   - 对重复 hard-failure
     records
     做 targeted structure diagnosis
2. 优先关注：
   - `target::chapter3_3_firefly_245`
   - `target::chapter3_2_firefly_163`
   - `target::chapter3_2_firefly_155`
   - `target::chapter3_26_firefly_107`
3. 当前不建议继续优先做：
   - 更大范围的
     无目的权重扫网格
   - 或直接把当前组合
     写成“已可进训练”

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `transition_combo_grid_summary`

## 一句话结论
- 当前 transition-side
  组合已经证明：
  - 方向是对的，
  - 但稳健性还不够；
  现阶段最值得追的
  已不是继续盲扫权重，
  而是围绕重复出现的
  hard-failure records
  做 targeted diagnosis。
