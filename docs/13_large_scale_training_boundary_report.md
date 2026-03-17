# 大规模训练配置与耗时边界报告

## 目的
- 在默认训练采样方案已经切到 seeded-shuffle 后，整理下一阶段“大规模训练”应如何进入。
- 只基于当前已经跑通的小规模训练事实，给出保守边界与候选方案。
- 不把当前极小 scaffold 的速度直接当作后续真实训练的可靠承诺。

## 当前已知事实
### 1. 默认方案
- 当前默认训练模板：
  - `configs/offline_mvp_train_template.json`
- 当前默认采样：
  - `seed = 20260314`
  - `shuffle_train_records = true`
  - `sampler_mode = seeded_shuffle`

### 2. 已验证的小规模实验
#### `EXP-20260314-009-offline-mvp-seeded-shuffle`
- `num_steps = 20`
- `validation_interval = 5`
- `checkpoint_interval = 5`
- `total duration = 1.250314s`
- 平均单 step 耗时约 `0.023127s`
- 最终 validation `loss_total = 35.849232`

#### `EXP-20260314-010-offline-mvp-default-seeded-template`
- `num_steps = 3`
- `validation_interval = 1`
- `checkpoint_interval = 1`
- `total duration = 0.82421s`
- 平均单 step 耗时约 `0.035634s`
- validation `loss_total = 52.288879 -> 51.498352 -> 50.715160`

### 3. 当前代码级门禁
- 训练入口已经支持：
  - `training.run_stage`
  - `training.prerequisite_experiment_id`
- 当前规则：
  - `run_stage = large_scale` 时，必须引用成功的小规模实验。

## 这些时间数据能说明什么
- 可以说明：
  - 当前默认 seeded-shuffle 模板已经真实跑通。
  - 当前小模型、当前 batch、当前数据读取方式下，命令链路、日志、checkpoint、validation 都工作正常。
  - 当前训练 loop 没有出现明显的写盘或采样异常。

- 不能说明：
  - 后续更大模型、更长音频、更复杂 loss、更频繁评估下的真实速度。
  - 最终完整训练需要多少分钟、多少小时。
  - GPU/CPU 负载在更大 batch 或更大模型下是否仍保持近似线性。

## 当前主要限制
### 1. 当前模型仍是极小 scaffold
- hidden dim、batch size、loss 结构都还很轻。
- 因此当前时间更像“链路通畅验证”，不是“最终训练吞吐基准”。

### 2. 当前 validation 与 checkpoint 频率偏高
- 小规模实验为了看趋势，`validation_interval` 和 `checkpoint_interval` 都较密。
- 这会放大管理开销，不适合直接照抄到更长训练。

### 3. 当前还没有最佳模型选择与早停逻辑
- 如果直接做更长训练，只能依赖固定 step 间隔和人工看 loss。
- 这对资源利用率和实验比较都不够稳。

## 我建议的大规模进入方式
不建议直接从当前默认模板跳到“长时间正式训练”。  
建议分两层进入：

### 方案 A：中等规模校准 run
- 目的：
  - 先验证默认 seeded-shuffle 在更长区间内是否稳定。
  - 顺便收集更可信的单位 step 开销与 checkpoint-series 趋势。
- 建议参数：
  - `run_stage = small_scale_validation`
  - `num_steps = 100`
  - `validation_interval = 10`
  - `checkpoint_interval = 10`
- 价值：
  - 风险低。
  - 能更清楚看 `z_art / e_evt` 是否继续增强。
  - 能减少过密验证带来的干扰。

### 方案 B：首个受控 large_scale run
- 前提：
  - 先完成方案 A。
  - 明确引用成功的小规模实验为前置实验。
- 建议参数：
  - `run_stage = large_scale`
  - `prerequisite_experiment_id = <方案A成功实验>`
  - `num_steps = 500`
  - `validation_interval = 25` 或 `50`
  - `checkpoint_interval = 25` 或 `50`
- 价值：
  - 能首次测试 large_scale 门禁与更长训练段的稳定性。
  - 仍保持在可回溯、可中断、可检查的范围内。

### 当前不建议的方案
- 直接把 step 拉到数千甚至更高。
- 在还没有 100 step seeded-shuffle 校准 run 的前提下，给出完整训练耗时承诺。
- 在还没有更系统 validation 汇总前，把单一最终 checkpoint 当成正式结论。

## 配置取舍
### validation / checkpoint 频率
- 更密：
  - 优点：趋势更清楚，坏掉更早发现。
  - 缺点：写盘和评估开销更高。
- 更疏：
  - 优点：训练本体更连续。
  - 缺点：出问题时回溯粒度更粗。

### 当前建议
- `100 step` 校准 run：
  - `validation_interval = 10`
  - `checkpoint_interval = 10`
- `500 step` 受控 large_scale run：
  - `validation_interval = 25` 或 `50`
  - `checkpoint_interval = 25` 或 `50`

## 当前建议口径
- 现在最稳的下一步不是“直接上正式大规模训练”。
- 现在最稳的下一步是：
  - 先做一个 `100 step` 的 seeded-shuffle 中等规模校准 run。
  - 然后根据该 run 的时间、loss 趋势和 checkpoint-series 再决定是否进入 `500 step` large_scale。

## 需要用户拍板的事项
请用户在以下两条路线里选一条：

1. 保守路线
- 先做 `100 step` seeded-shuffle 校准 run。
- 暂不进入 `run_stage = large_scale`。

2. 激进路线
- 直接准备首个 `500 step` large_scale run。
- 但必须显式引用一个成功的小规模实验为前置实验。

## 当前建议
- 建议用户选择保守路线。
- 原因：
  - 与现有规范一致。
  - 现有速度数据还只够支撑“下一档验证”，不够支撑“长时间正式训练承诺”。
  - 当前还缺最佳 checkpoint 选择与更系统的 validation 汇总，先做 100 step 更合理。

## 2026-03-14 用户决策结果
- 用户已确认选择激进路线：
  - 直接准备并运行 `500 step` 的 `large_scale` 训练。
- 当前执行配置：
  - `configs/offline_mvp_train_large_scale_seeded_500.json`
  - `run_stage = large_scale`
  - `prerequisite_experiment_id = EXP-20260314-010-offline-mvp-default-seeded-template`
  - `validation_interval = 25`
  - `checkpoint_interval = 25`
- 当前补充口径：
  - 用户已明确表示，如速度不可接受将人工叫停。
