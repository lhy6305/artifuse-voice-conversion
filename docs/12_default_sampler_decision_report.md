# 默认训练采样方案决策报告

## 目的
- 对比当前两条都已跑通的小规模训练路径：
  - 顺序采样 `EXP-20260314-008-offline-mvp-longer-smallscale`
  - 固定 seed 的 shuffled 采样 `EXP-20260314-009-offline-mvp-seeded-shuffle`
- 给出默认训练采样方案的事实依据、优缺点和建议口径。
- 保持决策权在用户侧，本报告不直接替用户改默认方案。

## 对比对象
### 方案 A：顺序采样
- 配置：`configs/offline_mvp_train_smallscale_longer.json`
- 训练模式：
  - `shuffle_train_records = false`
  - manifest 顺序轮转
- 实验：
  - `EXP-20260314-008-offline-mvp-longer-smallscale`

### 方案 B：seeded-shuffle
- 配置：`configs/offline_mvp_train_smallscale_seeded_shuffle.json`
- 训练模式：
  - `seed = 20260314`
  - `shuffle_train_records = true`
  - `target_sampler_seed = 20260314`
  - `source_sampler_seed = 20260315`
- 实验：
  - `EXP-20260314-009-offline-mvp-seeded-shuffle`

## 对齐条件
- 两个实验都使用：
  - 相同 round1 数据
  - 相同 `hybrid_stratified_blocked` 正式 split
  - 相同模型骨架
  - 相同 `learning_rate = 0.0003`
  - 相同 `num_steps = 20`
  - 相同 `validation_interval = 5`
  - 相同 `checkpoint_interval = 5`
- 因此本报告可以把“采样方式”视为主要变量。

## 核心结果
### 1. 固定 validation loss
#### 方案 A：顺序采样
- step 5: `47.142235`
- step 10: `43.031590`
- step 15: `38.626499`
- step 20: `33.901825`
- 总耗时：`1.237681s`

#### 方案 B：seeded-shuffle
- step 5: `49.157608`
- step 10: `45.160576`
- step 15: `40.778854`
- step 20: `35.849232`
- 总耗时：`1.250314s`

#### 当前事实
- 在这组一一对齐的小规模实验里，顺序采样的固定 validation loss 更低。
- 两者耗时几乎相同，当前没有看到 shuffled 会显著拖慢训练。

### 2. checkpoint 系列消融趋势
#### 方案 A：顺序采样
- `zero_z_art.delta_target_loss_total`
  - `-0.004283 -> 0.020028 -> 0.046879 -> 0.079066`
- `zero_e_evt.delta_target_loss_total`
  - `0.290621 -> 0.625010 -> 0.868924 -> 1.015739`
- `zero_z_art.delta_source_loss_total`
  - `-0.008403 -> 0.024396 -> 0.063001 -> 0.114091`
- `zero_e_evt.delta_source_loss_total`
  - `0.394811 -> 0.861151 -> 1.231779 -> 1.504668`

#### 方案 B：seeded-shuffle
- `zero_z_art.delta_target_loss_total`
  - `0.048894 -> 0.096982 -> 0.150881 -> 0.207483`
- `zero_e_evt.delta_target_loss_total`
  - `1.053401 -> 1.295615 -> 1.530421 -> 1.737457`
- `zero_z_art.delta_source_loss_total`
  - `0.069221 -> 0.132976 -> 0.209152 -> 0.299056`
- `zero_e_evt.delta_source_loss_total`
  - `1.368172 -> 1.709776 -> 2.074558 -> 2.455875`

#### 当前事实
- 两种方案都呈现“训练越往后，`z_art / e_evt` 越被模型用上”的趋势。
- 但 seeded-shuffle 的趋势更早出现、幅度更大、单调性更清晰。
- 尤其在 `step 5`：
  - 顺序采样的 `zero_z_art` 还是负值，说明 `z_art` 作用还不稳定。
  - seeded-shuffle 的 `zero_z_art` 已经是正退化，说明它更早变成有效控制量。

### 3. special_eval 行为
#### 方案 A：顺序采样
- `target_validation.loss_total = 14.974206`
- `target_special_eval.loss_total = 11.146732`
- `delta_loss_total = -3.827474`
- `delta_loss_text_aux = 0.642243`

#### 方案 B：seeded-shuffle
- `target_validation.loss_total = 15.770239`
- `target_special_eval.loss_total = 11.934946`
- `delta_loss_total = -3.835293`
- `delta_loss_text_aux = 0.650545`

#### 当前事实
- 两种方案在 `target_special_eval` 上的行为非常接近。
- 当前没有证据表明 seeded-shuffle 会让 nonverbal challenge slice 明显变好或变坏。
- 这也说明默认采样方案的决策重点不在 `special_eval`，而在：
  - 主 validation loss
  - 控制量是否被更稳定地学会

## 优缺点汇总
### 方案 A：顺序采样
#### 优点
- 当前这组 20 step 对比里，主 validation loss 更低。
- 行为最直观，调试容易。
- 对 batch 构成的解释最简单，适合继续做最小闭环排障。

#### 缺点
- 采样顺序更依赖 manifest 排列。
- 在当前结果里，`z_art / e_evt` 的使用增强虽然存在，但更慢、更弱。
- 若 manifest 排列本身带局部结构偏置，顺序采样更容易继承这种偏置。

### 方案 B：seeded-shuffle
#### 优点
- 可复现性更好，`seed` 和 sampler seed 已显式落盘。
- `z_art / e_evt` 的控制使用趋势更强、更稳定。
- 更符合后续正式训练和重复实验对“可比较性”的要求。

#### 缺点
- 在当前这组单次 20 step 对比里，主 validation loss 略高于顺序采样。
- batch 内容打散后，单步波动解释成本更高。
- 目前还只有一组 seed，尚不能证明这是稳定统计优势，而不是单 seed 偶然结果。

## 风险判断
- 现在直接把 seeded-shuffle 设成默认方案，风险不在“跑不通”，而在“主验证 loss 当前并未赢过顺序采样”。
- 现在继续坚持顺序采样，风险不在“完全错误”，而在“控制量被学会的证据更弱，后续实验复现和横向对比也更差”。
- 当前最重要的事实是：
  - 这不是“一个明显更强、另一个明显更差”的局面。
  - 这是“validation loss 略偏向顺序采样，控制学习证据明显偏向 seeded-shuffle”的取舍。

## 建议口径
### 如果当前目标是
- 优先维持最小 validation loss 并减少解释复杂度：
  - 更偏向方案 A。
- 优先建立后续正式实验的可复现性，并更早验证控制变量是否真的被用到：
  - 更偏向方案 B。

### 当前我的建议
- 建议将 `seeded-shuffle` 作为后续正式实验默认方案。
- 原因不是它已经在主 validation loss 上取胜，而是：
  - 它已经证明可复现；
  - 它对 `z_art / e_evt` 的学习趋势更清晰；
  - 这更符合当前阶段“先验证控制主链是否真的成立”的优先级。
- 但考虑到当前单次 20 step 对比里顺序采样的 loss 更低，若用户更看重“先把最小 loss 压下来”，也可以暂时继续保留顺序采样为默认。

## 需要用户拍板的事项
请用户在以下两种默认策略里二选一：

1. 保持顺序采样为默认
- seeded-shuffle 作为对照实验能力保留，但不切默认。

2. 切换 seeded-shuffle 为默认
- 后续正式训练默认要求：
  - 记录 `seed`
  - 记录 `target_sampler_seed / source_sampler_seed`
  - 以 checkpoint-series 和主 validation loss 同时判断训练效果

## 当前状态
- 本报告只做事实整理和建议，不自动改默认配置。
- 在用户确认前，当前仓库仍保持“顺序采样模板 + seeded-shuffle 对照模板并存”的状态。

## 2026-03-14 用户决策结果
- 用户已确认选择：
  - 切换 `seeded-shuffle` 为默认训练采样方案。
- 当前执行动作：
  - 默认训练模板切换为 `shuffle_train_records = true`
  - 顺序采样保留为对照与回退能力，不再是默认
  - 已完成默认模板验证实验 `EXP-20260314-010-offline-mvp-default-seeded-template`

## 默认模板验证结果
- 实验：
  - `EXP-20260314-010-offline-mvp-default-seeded-template`
- 配置：
  - `configs/offline_mvp_train_template.json`
- 当前验证结论：
  - 默认模板已实际按 `seeded_shuffle` 运行
  - `reproducibility.seed = 20260314`
  - `reproducibility.target_sampler_seed = 20260314`
  - `reproducibility.source_sampler_seed = 20260315`
  - 标准输出已打印开始时间、step 时间和结束时间
  - 训练计划、step log、实验 metrics 已同步落盘
- 当前 3 step validation `loss_total`
  - `52.288879 -> 51.498352 -> 50.715160`
