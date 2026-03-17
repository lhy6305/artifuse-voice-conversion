# round1 训练/验证拆分方案分析

## 目的
本页记录 round1 正式训练/验证集拆分前的事实收集结果。

当前目标不是立即改写训练 manifest，而是先回答两个问题：

1. 当前固定验证切片是否已经足够代表 round1 数据分布
2. 如果不够，下一版应优先采用哪类拆分策略供用户决策

## 命令与产物
当前新增命令：

- `.\python.exe manage.py analyze-round1-splits`

当前报告目录：

- `reports/data/round1_split_analysis/`

当前关键产物：

- `split_analysis_summary.md`
- `split_analysis_summary.json`
- `options/current_tail_holdout.json`
- `options/random_split_seed20260314.json`
- `options/hybrid_stratified_blocked.json`

## 已确认的数据事实
### 目标说话人数据
- 总量 `624` 条。
- 其中主分布 `<root>` 为 `616` 条。
- `no_text_voice` 子组为 `8` 条。
- 当前训练入口使用的固定尾部验证切片，目标侧 `8` 条全部来自 `no_text_voice`。

### 源说话人数据
- 总量 `537` 条。
- 记录来自同一长录音。
- 当前固定尾部验证切片，源侧 `8` 条全部位于录音尾部约 `3612s` 到 `3667s`。

## 三个候选方案
### 1. current_tail_holdout
- 含义：
  - 继续沿用当前实现，目标/源都取尾部 `8` 条。
- 优点：
  - 实现最简单，当前训练已验证可跑。
  - 源侧连续切片，时间边界少。
- 缺点：
  - 目标验证集完全偏到 `no_text_voice` 子组。
  - 源验证集只覆盖录音尾部。
  - 样本数过少，不适合做正式训练/验证拆分。

### 2. random_split_seed20260314
- 含义：
  - 目标/源都按约 `10%` 做固定随机拆分。
- 优点：
  - 验证样本规模更接近正式训练需要。
  - 分布覆盖通常好于固定尾部切片。
- 缺点：
  - 源侧相邻片段会被打散到 train/val，泄漏风险高。
  - 难以单独观察 `no_text_voice` 子组。

### 3. hybrid_stratified_blocked
- 含义：
  - 目标主集 `<root>` 做分布覆盖抽样，取 `62` 条做常规验证。
  - `no_text_voice` 的 `8` 条单独作为 challenge eval。
  - 源侧按时间轴做跨全局 blocked holdout，取 `54` 条做验证。
- 优点：
  - 目标主验证集更接近主训练分布。
  - `no_text_voice` 不再污染常规验证集，同时还能单独观察。
  - 源侧分布覆盖明显好于尾部切片，且相邻泄漏比随机方案低。
- 缺点：
  - 实现和维护复杂度高于随机拆分。
  - 仍需用户确认是否接受“blocked holdout 不是严格语义分层”这一点。

## 当前建议
当前建议是 `hybrid_stratified_blocked`，原因如下：

- 当前固定尾部方案已经被证实明显偏分布。
- 随机方案虽然覆盖更广，但对单录音源数据的相邻泄漏问题过重。
- hybrid 方案在“分布覆盖”和“避免明显泄漏”之间更平衡。

## 当前边界
- 以上分析只生成候选拆分方案，不修改正式训练 manifest。
- 本页最初用于候选分析；当前用户已确认采用 `hybrid_stratified_blocked`。
- 正式 split 已物化到 `data_prep/round1/splits/hybrid_stratified_blocked/`。
- 训练入口已切换为读取正式 split，而不是固定验证切片。

## 下一步
1. 为 `target_special_eval` 增加单独评估入口。
2. 将后续训练与评估都统一到正式 split 目录。
